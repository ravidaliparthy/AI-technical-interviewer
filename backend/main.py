import os
import re
import io
import json
import logging
from typing import List, Optional, Literal, Dict, Any
from fastapi import FastAPI, HTTPException, Request, UploadFile, File, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import httpx
import pypdf
from dotenv import load_dotenv
from companies import (
    get_company_profile,
    get_company_questions,
    get_company_interviewer_intro,
    COMPANY_PROFILES
)
from code_analyzer import analyze_code_loopholes
from code_runner import execute_candidate_code, _is_empty_or_placeholder, extract_test_cases_from_text
from question_banks import EXPANDED_QUESTION_BANKS
from problem_templates import (
    generate_starter_snippets,
    is_coding_problem,
    parse_question_signature,
    extract_problem_title
)

# Load environment variables
load_dotenv()

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("ai_interviewer")

app = FastAPI(
    title="AI Interview Coach API",
    version="2.3.0",
    description="Scalable, concurrent API with direct resume-driven questions, on-demand hints, and DSA test cases.",
)

# High-concurrency HTTP connection pool
HTTPX_LIMITS = httpx.Limits(max_keepalive_connections=50, max_connections=300)

# Robust CORS Setup for Vercel, Render, and Localhost
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True if allowed_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup Banner
@app.on_event("startup")
async def startup_event():
    print("=" * 65)
    print("  🚀 AI Interview Coach Backend is ONLINE (v2.3.0)")
    print("  📡 Endpoints:")
    print("     - GET  /api/health            (Service health & readiness)")
    print("     - POST /api/interview/upload-resume (PDF Resume extraction)")
    print("     - POST /api/interview/start   (Action 1: Start interview / first Q)")
    print("     - POST /api/interview/answer  (Action 2: Submit candidate answer)")
    print("     - POST /api/interview/hint    (💡 Action: On-demand question hint)")
    print("     - POST /api/interview/report  (Action 3: Generate detailed scorecard)")
    print("  📄 Features: Direct Resume-based Qs • DSA Test Cases • On-Demand Hints")
    print("=" * 65)

# Friendly Global Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": True, "message": exc.detail, "status_code": exc.status_code},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "An unexpected error occurred while processing your request. Please try again or switch to the Built-in engine.",
            "detail": str(exc),
        },
    )

# Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

# --- Request / Response Models ---

class ChatMessage(BaseModel):
    role: Literal["interviewer", "candidate", "assistant", "user", "system"]
    content: str = Field(..., min_length=1)
    is_follow_up: Optional[bool] = False
    code_snippet: Optional[str] = None
    code_language: Optional[str] = None

    @field_validator("content")
    @classmethod
    def clean_content(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Message content cannot be blank.")
        return s

class StartInterviewRequest(BaseModel):
    topic: Optional[str] = Field(None, description="Topic for the interview (optional if resume provided)")
    difficulty: Literal["Easy", "Medium", "Hard"] = Field("Medium", description="Difficulty level")
    total_questions: int = Field(5, ge=5, le=20, description="Total number of interview questions (5 to 20)")
    company: Optional[str] = Field(None, description="Target company e.g. Google, Amazon, Meta, Microsoft, Apple, Netflix, Uber, Nvidia, Stripe, OpenAI")
    resume_text: Optional[str] = Field(None, description="Extracted text from candidate's PDF resume")
    provider: Optional[Literal["auto", "groq", "builtin"]] = "auto"
    api_key: Optional[str] = None

    @field_validator("topic", mode="before")
    @classmethod
    def clean_topic(cls, v: Any) -> str:
        if v is None:
            return ""
        s = str(v).strip()
        return s

class SubmitAnswerRequest(BaseModel):
    topic: str = "Technical Interview"
    difficulty: Literal["Easy", "Medium", "Hard"] = "Medium"
    total_questions: int = Field(5, ge=5, le=20, description="Total number of interview questions (5 to 20)")
    company: Optional[str] = Field(None, description="Target company e.g. Google, Amazon, Meta, Microsoft, Apple, Netflix, Uber, Nvidia, Stripe, OpenAI")
    conversation: List[ChatMessage] = Field(..., description="Full conversation transcript including latest answer")
    resume_text: Optional[str] = None
    code_snippet: Optional[str] = Field(None, description="Optional submitted code from code editor")
    code_language: Optional[str] = Field("python", description="Language of submitted code snippet")
    hints_used: Optional[int] = 0
    provider: Optional[Literal["auto", "groq", "builtin"]] = "auto"
    api_key: Optional[str] = None
    force_advance: Optional[bool] = False

    @field_validator("conversation")
    @classmethod
    def validate_conversation(cls, v: List[ChatMessage]) -> List[ChatMessage]:
        if not v:
            raise ValueError("Conversation history cannot be empty when submitting an answer.")
        return v

class RealtimeHelperRequest(BaseModel):
    current_question: str = ""
    draft_answer: str = ""
    topic: str = "Technical Interview"
    difficulty: str = "Medium"
    company: Optional[str] = None
    problem_title: Optional[str] = None

class RealtimeHelperResponse(BaseModel):
    framework_name: str
    framework_description: str
    framework_steps: List[Dict[str, str]]
    recommended_keywords: List[str]
    detected_keywords: List[str]
    missing_keywords: List[str]
    critique: str
    readiness_score: int
    readiness_label: str
    quick_tips: List[str]

class HintRequest(BaseModel):
    topic: str
    difficulty: Literal["Easy", "Medium", "Hard"] = "Medium"
    question: str
    company: Optional[str] = None
    conversation: List[ChatMessage] = Field(default_factory=list)
    hint_level: int = Field(1, ge=1, le=3, description="1: Intuition, 2: Pattern, 3: Invariant/Edge Case")
    provider: Optional[Literal["auto", "groq", "builtin"]] = "auto"
    api_key: Optional[str] = None

class HintResponse(BaseModel):
    hint: str
    hint_level: int
    category: str
    provider_used: str = "builtin"

class InterviewResponse(BaseModel):
    message: str
    is_ended: bool = False
    end_reason: Optional[str] = None
    question_number: int = 1
    total_questions: int = 5
    is_follow_up: bool = False
    provider_used: str = "builtin"
    is_coding_problem: bool = False
    problem_title: Optional[str] = None
    starter_snippets: Optional[Dict[str, str]] = None
    placeholder: Optional[str] = None
    quick_chips: Optional[List[str]] = None
    test_cases: Optional[List[Dict[str, Any]]] = None
    problem_text: Optional[str] = None

class CodeAnalysisRequest(BaseModel):
    code: str = Field(..., description="Source code to analyze for bugs, loopholes, and Big-O")
    problem: str = Field("", description="The DSA problem description or question context")
    language: str = Field("python", description="Programming language (python, javascript, typescript, cpp, java)")
    company: Optional[str] = Field(None, description="Target company e.g. Google, Amazon, Meta")
    difficulty: Literal["Easy", "Medium", "Hard"] = "Medium"
    provider: Optional[Literal["auto", "groq", "builtin"]] = "auto"
    api_key: Optional[str] = None
    test_cases: Optional[List[Dict[str, Any]]] = None

class CodeAnalysisResponse(BaseModel):
    loopholes: List[str]
    time_complexity: str
    space_complexity: str
    test_case_results: List[Dict[str, Any]]
    company_verdict: str
    interviewer_probe: str
    status: Literal["Passed", "Loopholes Found", "Error"]
    score: int
    provider_used: str = "builtin"

class RunCodeRequest(BaseModel):
    code: str = Field(..., description="Source code to execute in sandbox")
    language: str = Field("python", description="Programming language (python, javascript, typescript, cpp, java, go, rust)")
    problem: Optional[str] = Field("", description="Problem name or title context")
    custom_input: Optional[str] = Field(None, description="Optional custom test input")
    test_cases: Optional[List[Dict[str, Any]]] = Field(None, description="Structured test cases")

class RunCodeResponse(BaseModel):
    status: str
    stdout: str
    stderr: str
    execution_time_ms: float
    test_results: List[Dict[str, Any]]
    passed: bool

class ReportRequest(BaseModel):
    topic: str = "Technical Interview"
    difficulty: Literal["Easy", "Medium", "Hard"] = "Medium"
    total_questions: Optional[int] = 5
    company: Optional[str] = None
    conversation: List[ChatMessage] = Field(...)
    resume_text: Optional[str] = None
    hints_used: Optional[int] = 0
    provider: Optional[Literal["auto", "groq", "builtin"]] = "auto"
    api_key: Optional[str] = None

class ReportResponse(BaseModel):
    score: int = Field(..., ge=0, le=100)
    rating_label: Literal["Excellent", "Good", "Adequate", "Weak"]
    status: Literal["Pass", "Fail"]
    strengths: List[str]
    weaknesses: List[str]
    topics_to_revise: List[str]
    overall_verdict: str
    company_alignment: Optional[str] = None
    resume_alignment: Optional[str] = None
    dsa_complexity_analysis: Optional[str] = None
    score_breakdown: Optional[Dict[str, int]] = None
    detailed_feedback: Optional[List[Dict[str, str]]] = None
    provider_used: str = "builtin"


# --- Resume Intelligence & Question Synthesis ---

def extract_resume_highlights(resume_text: str) -> Dict[str, List[str]]:
    """Extracts projects, work experiences, and tech skills from raw resume text."""
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    projects: List[str] = []
    experience: List[str] = []
    skills: List[str] = []

    common_skills = [
        "python", "pytorch", "tensorflow", "scikit-learn", "keras", "fastapi", "django", "flask",
        "react", "next.js", "typescript", "javascript", "node.js", "sql", "postgresql", "mysql",
        "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure", "kafka", "pandas",
        "numpy", "c++", "java", "go", "rust", "graphql", "rest api", "ci/cd", "git"
    ]
    resume_lower = resume_text.lower()
    for s in common_skills:
        if re.search(r'\b' + re.escape(s) + r'\b', resume_lower):
            skills.append(s.title() if len(s) > 3 else s.upper())

    capture_mode = None
    for line in lines:
        lower = line.lower()
        if any(h in lower for h in ["projects", "personal projects", "academic projects", "key projects"]):
            capture_mode = "projects"
            continue
        elif any(h in lower for h in ["experience", "work experience", "employment history", "internships", "professional experience"]):
            capture_mode = "experience"
            continue
        elif any(h in lower for h in ["education", "certifications", "interests", "honors", "awards"]):
            capture_mode = None
            continue

        if capture_mode == "projects":
            if 3 < len(line) < 85 and not line.startswith("•") and not line.startswith("-") and not line.startswith("*"):
                cleaned = re.split(r'\||–|-|\(|\d{4}', line)[0].strip()
                if len(cleaned) > 3 and cleaned not in projects:
                    projects.append(cleaned)
        elif capture_mode == "experience":
            if 3 < len(line) < 85 and not line.startswith("•") and not line.startswith("-") and not line.startswith("*"):
                cleaned = re.split(r'\||–|-|\(|\d{4}', line)[0].strip()
                if len(cleaned) > 3 and cleaned not in experience:
                    experience.append(cleaned)

    # Fallback search if headers were structured differently
    if not projects:
        for line in lines:
            if any(term in line.lower() for term in ["built", "developed", "architected", "implemented", "designed"]) and len(line) < 100:
                cleaned = re.split(r'\||–|-|\(|\d{4}', line)[0].strip()
                if len(cleaned) > 5 and cleaned not in projects:
                    projects.append(cleaned)
                    if len(projects) >= 3:
                        break

    return {
        "projects": projects[:5],
        "experience": experience[:5],
        "skills": skills[:12]
    }

def generate_resume_questions(resume_text: str, difficulty: str, count: int = 5) -> List[str]:
    """Generates sequential technical interview questions directly based on the candidate's CV (up to 20 questions)."""
    highlights = extract_resume_highlights(resume_text)
    projects = highlights["projects"]
    experience = highlights["experience"]
    skills = highlights["skills"]

    p0 = projects[0] if projects else "your flagship application"
    p1 = projects[1] if len(projects) > 1 else (experience[0] if experience else "your core system")
    s0 = skills[0] if skills else "backend architectures"
    s1 = skills[1] if len(skills) > 1 else "distributed data storage"
    s2 = skills[2] if len(skills) > 2 else "asynchronous messaging"
    e0 = experience[0] if experience else "your past engineering roles"

    master_pool: List[str] = [
        # Q1: Architecture & primary project
        f"I see on your resume that you built **{p0}**. Can you walk me through the end-to-end architecture of this system, how data flows through it, and the primary design trade-offs you evaluated when creating it?",
        
        # Q2: Performance bottlenecks & scaling
        f"Regarding your work on **{p1}**: What were the primary performance constraints or latency bottlenecks? If tasked with redesigning that system today to handle 50x higher throughput, what architectural changes would you make?",
        
        # Q3: Production debugging & failure modes
        f"During your work in **{e0}**, describe a challenging production bug, race condition, or memory/resource leak you had to debug under pressure. How did you diagnose the root cause and implement a permanent safeguard?",
        
        # Q4: SLAs, benchmarking & metrics
        f"On your resume, you highlighted key technical deliverables. How did you benchmark that your solution met its latency, memory, or throughput SLAs under realistic high-concurrency conditions?",
        
        # Q5: Database schema & storage design
        f"In your projects utilizing **{s0}** and **{s1}**, how did you design the database schemas, indexing strategies, and caching layers to guarantee fast query performance while preventing data inconsistency?",
        
        # Q6: API contracts & versioning
        f"How did you design API contracts in your projects to ensure backward compatibility as services evolved? How did you handle API versioning, input validation, and rate limiting?",
        
        # Q7: State synchronization & concurrency
        f"When orchestrating services using **{s0}**, how did you manage state synchronization and race conditions during concurrent user operations?",
        
        # Q8: Resilience, failovers & circuit breakers
        f"In the production systems on your resume, how did you architect failover mechanisms? What strategies (such as circuit breakers, retry budgets, or dead-letter queues) did you implement to handle downstream service degradation?",
        
        # Q9: Security & authorization
        f"How did you approach security, user authentication, and data protection in your projects? How did you ensure sensitive credentials and API endpoints were secured against unauthorized access?",
        
        # Q10: Automated testing strategy
        f"Walk me through your automated testing strategy on **{p0}**. How did you balance unit tests, integration tests, and mock external dependencies to maintain high deployment confidence?",
        
        # Q11: CI/CD & zero-downtime releases
        f"Describe the continuous integration and deployment (CI/CD) pipeline for the systems on your CV. How did you achieve zero-downtime rollouts, and what was your automated rollback criteria?",
        
        # Q12: Observability & distributed tracing
        f"How did you instrument observability across the components on your resume? What metrics, structured logging, and distributed tracing did you implement to detect anomalies before users were impacted?",
        
        # Q13: Tech stack justification
        f"On your resume you selected **{s0}** alongside **{s1}**. What alternative technologies did you evaluate, and what concrete technical trade-offs justified your choice?",
        
        # Q14: Network partitions & error handling
        f"In distributed portions of your projects, how did you handle transient network timeouts and partial failure states without corrupting user transactions?",
        
        # Q15: Infrastructure cost & query optimization
        f"Can you share an instance from your experience where you profiled and optimized database queries or server resource utilization to reduce latency or cloud infrastructure costs?",
        
        # Q16: Boundary edge cases & validation
        f"In the user-facing workflows you engineered, what boundary edge cases or malicious payload formats did you have to safeguard against?",
        
        # Q17: Real-time vs batch processing
        f"Did your implementations require streaming real-time events or batch processing? How did you architect the data ingestion pipelines to prevent consumer lag?",
        
        # Q18: Third-party integrations & idempotency
        f"When integrating external APIs or webhooks in your systems, how did you guarantee idempotency so that duplicate event deliveries wouldn't create duplicate side-effects?",
        
        # Q19: Technical debt & refactoring
        f"Describe a situation in your projects where you had to refactor a complex legacy component or technical debt while continuing to deliver features on a tight deadline.",
        
        # Q20: Engineering leadership & architectural reviews
        f"Looking at your overall technical journey on your resume, how do you conduct architectural design reviews, ensure coding standards across your team, and mentor junior engineers?"
    ]

    target_count = max(5, min(count, 20))
    return master_pool[:target_count]


# --- Built-In High Reliability Question Bank with DSA & Test Cases ---

TOPIC_BANK: Dict[str, Dict[str, List[str]]] = {
    "dsa": {
        "Easy": [
            (
                "### Problem: Two Sum\n"
                "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `nums = [2, 7, 11, 15]`, `target = 9` ➔ Output: `[0, 1]` (Explanation: `nums[0] + nums[1] == 9`)\n"
                "- **Test Case 2**: Input: `nums = [3, 2, 4]`, `target = 6` ➔ Output: `[1, 2]`\n"
                "- **Test Case 3**: Input: `nums = [3, 3]`, `target = 6` ➔ Output: `[0, 1]`\n\n"
                "**Requirements:**\n"
                "Explain your approach. What is your exact **Time Complexity** ($O(...)$) and **Space Complexity** ($O(...)$)? Can you solve it in $O(N)$ time?"
            ),
            (
                "### Problem: Valid Anagram\n"
                "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `s = \"anagram\"`, `t = \"nagaram\"` ➔ Output: `true`\n"
                "- **Test Case 2**: Input: `s = \"rat\"`, `t = \"car\"` ➔ Output: `false`\n\n"
                "**Requirements:**\n"
                "Provide your algorithm. State your **Time Complexity** ($O(...)$) and **Auxiliary Space Complexity** ($O(...)$). How would you optimize if the input contains Unicode characters?"
            ),
            (
                "### Problem: Reverse Linked List\n"
                "Given the `head` of a singly linked list, reverse the list, and return the reversed list.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `head = [1, 2, 3, 4, 5]` ➔ Output: `[5, 4, 3, 2, 1]`\n"
                "- **Test Case 2**: Input: `head = [1, 2]` ➔ Output: `[2, 1]`\n"
                "- **Test Case 3**: Input: `head = []` ➔ Output: `[]`\n\n"
                "**Requirements:**\n"
                "Walk me through the pointer updates. What is the **Time Complexity** and **Auxiliary Space Complexity** of your iterative solution?"
            ),
            (
                "### Problem: Binary Search\n"
                "Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`. If `target` exists, return its index; otherwise, return `-1`.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `nums = [-1, 0, 3, 5, 9, 12]`, `target = 9` ➔ Output: `4`\n"
                "- **Test Case 2**: Input: `nums = [-1, 0, 3, 5, 9, 12]`, `target = 2` ➔ Output: `-1`\n\n"
                "**Requirements:**\n"
                "Why must mid be calculated as `left + (right - left) // 2` instead of `(left + right) // 2`? State your exact **Time Complexity** ($O(\\log N)$) and **Space Complexity**."
            )
        ],
        "Medium": [
            (
                "### Problem: Longest Substring Without Repeating Characters\n"
                "Given a string `s`, find the length of the longest substring without duplicate characters.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `s = \"abcabcbb\"` ➔ Output: `3` (Explanation: Substring `\"abc\"`)\n"
                "- **Test Case 2**: Input: `s = \"bbbbb\"` ➔ Output: `1` (Explanation: Substring `\"b\"`)\n"
                "- **Test Case 3**: Input: `s = \"pwwkew\"` ➔ Output: `3` (Explanation: Substring `\"wke\"`)\n\n"
                "**Constraints & Requirements:**\n"
                "Explain the sliding window with hash map approach. Declare your **Time Complexity** ($O(...)$) and **Space Complexity** ($O(...)$)."
            ),
            (
                "### Problem: LRU Cache Design\n"
                "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache with $O(1)$ average time for both `get(key)` and `put(key, value)`.\n\n"
                "**Test Cases:**\n"
                "- Input operations: `[\"LRUCache\", \"put\", \"put\", \"get\", \"put\", \"get\", \"put\", \"get\", \"get\", \"get\"]`\n"
                "  Arguments: `[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]`\n"
                "- Expected Output: `[null, null, null, 1, null, -1, null, -1, 3, 4]`\n\n"
                "**Requirements:**\n"
                "What two data structures do you combine to achieve $O(1)$? What is the overall **Space Complexity** in terms of capacity $C$?"
            ),
            (
                "### Problem: Number of Islands\n"
                "Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**:\n"
                "  `grid = [[\"1\",\"1\",\"1\",\"1\",\"0\"],[\"1\",\"1\",\"0\",\"1\",\"0\"],[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"0\",\"0\",\"0\",\"0\",\"0\"]]` ➔ Output: `1`\n"
                "- **Test Case 2**:\n"
                "  `grid = [[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"0\",\"0\",\"1\",\"0\",\"0\"],[\"0\",\"0\",\"0\",\"1\",\"1\"]]` ➔ Output: `3`\n\n"
                "**Requirements:**\n"
                "Compare BFS vs DFS. State your **Time Complexity** in terms of $M \\times N$ and worst-case **Space Complexity** (considering call stack / queue size)."
            ),
            (
                "### Problem: Course Schedule (Cycle Detection in Directed Graph)\n"
                "There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a_i, b_i]` indicates that you must take `b_i` first if you want to take `a_i`. Return `true` if you can finish all courses, or `false` otherwise.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `numCourses = 2`, `prerequisites = [[1, 0]]` ➔ Output: `true`\n"
                "- **Test Case 2**: Input: `numCourses = 2`, `prerequisites = [[1, 0], [0, 1]]` ➔ Output: `false` (Cycle detected)\n\n"
                "**Requirements:**\n"
                "Explain Kahn's Algorithm (topological sort with in-degrees) or DFS 3-color cycle detection. What is your exact **Time Complexity** ($O(V+E)$) and **Space Complexity**?"
            )
        ],
        "Hard": [
            (
                "### Problem: Trapping Rain Water\n"
                "Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `height = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]` ➔ Output: `6`\n"
                "- **Test Case 2**: Input: `height = [4, 2, 0, 3, 2, 5]` ➔ Output: `9`\n\n"
                "**Constraints & Requirements:**\n"
                "The solution MUST run in $O(N)$ Time Complexity. Compare the Dynamic Programming approach ($O(N)$ space) with the Two-Pointer approach ($O(1)$ auxiliary space)."
            ),
            (
                "### Problem: Median of Two Sorted Arrays\n"
                "Given two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the median of the two sorted arrays.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `nums1 = [1, 3]`, `nums2 = [2]` ➔ Output: `2.00000`\n"
                "- **Test Case 2**: Input: `nums1 = [1, 2]`, `nums2 = [3, 4]` ➔ Output: `2.50000`\n\n"
                "**Constraints & Requirements:**\n"
                "The overall run time complexity MUST be $O(\\log(\\min(m, n)))$. Explain the binary search partitioning condition and state your **Space Complexity**."
            ),
            (
                "### Problem: Sliding Window Maximum\n"
                "You are given an array of integers `nums`, there is a sliding window of size `k` which is moving from the very left of the array to the very right. Return the max sliding window.\n\n"
                "**Test Cases:**\n"
                "- **Test Case 1**: Input: `nums = [1, 3, -1, -3, 5, 3, 6, 7]`, `k = 3` ➔ Output: `[3, 3, 5, 5, 6, 7]`\n"
                "- **Test Case 2**: Input: `nums = [1]`, `k = 1` ➔ Output: `[1]`\n\n"
                "**Requirements:**\n"
                "Explain why a monotonic decreasing deque achieves amortized $O(N)$ Time Complexity instead of $O(N \\log K)$ with a max-heap. What is the **Space Complexity**?"
            )
        ]
    },
    "python": {
        "Easy": [
            "Can you explain the difference between a list and a tuple in Python, particularly regarding mutability and memory allocation?",
            "What is the Global Interpreter Lock (GIL) in CPython and how does it impact multi-threaded CPU-bound programs?",
            "How do Python dictionaries handle key collisions under the hood, and what are the requirements for an object to be used as a dictionary key?",
            "What is the difference between shallow copy (`copy.copy`) and deep copy (`copy.deepcopy`) in Python?",
            "How does Python manage memory and clean up unused objects? Can you explain reference counting and cyclic garbage collection?"
        ],
        "Medium": [
            "How would you implement a custom function decorator with arguments in Python that logs execution time in milliseconds?",
            "Explain how Python generators and the `yield` keyword work. In what production scenario would you prefer a generator over a list comprehension?",
            "When designing high-throughput I/O tasks in Python, how do you decide between `asyncio`, `multiprocessing`, and `concurrent.futures.ThreadPoolExecutor`?",
            "How does Python resolve multiple inheritance method calls (Method Resolution Order / C3 Linearization)?",
            "How would you process a 15GB CSV file in Python on a worker machine constrained to 2GB of RAM without crashing?"
        ],
        "Hard": [
            "Explain the low-level memory allocation hierarchy of CPython (arenas, pools, blocks) and how small object allocation (`PyObject_Malloc`) avoids system malloc overhead.",
            "If you were architecting a distributed asynchronous task queue like Celery from scratch in Python, how would you handle worker heartbeats, acknowledgment guarantees, and prefetch limits?",
            "Analyze the trade-offs of using `asyncio` event loops vs thread pools when integrating legacy synchronous database drivers with an asynchronous web framework like FastAPI.",
            "How would you design a hot-reloading plugin system in Python that dynamically imports modules without memory leaks or namespace contamination?",
            "Compare the performance characteristics and execution models of CPython vs PyPy vs Cython for CPU-bound computational workloads."
        ]
    },
    "machine learning": {
        "Easy": [
            "Can you explain the fundamental difference between supervised, unsupervised, and reinforcement learning with real-world examples?",
            "What is the bias-variance tradeoff, and how does model complexity directly influence underfitting vs overfitting?",
            "What is the mathematical difference between L1 (Lasso) and L2 (Ridge) regularization, and why does L1 lead to sparse feature selection?",
            "Explain precision, recall, and F1-score. When would you optimize strictly for recall over precision?",
            "Can you walk me through how gradient descent iteratively minimizes a model's loss function?"
        ],
        "Medium": [
            "In a real-time credit card fraud detection dataset where fraudulent transactions make up only 0.1% of samples, what sampling techniques and evaluation metrics would you use?",
            "Explain the core differences between bagging and boosting, specifically comparing Random Forests with Gradient Boosted Decision Trees (XGBoost/LightGBM).",
            "Walk me through the architectural and mathematical difference between Batch Normalization and Layer Normalization. Why is LayerNorm standard in Transformers?",
            "How do you detect and prevent target leakage in a multi-stage time-series feature engineering pipeline?",
            "If training loss is consistently decreasing but validation loss diverges after epoch 12, what concrete diagnostic steps and remedies would you apply?"
        ],
        "Hard": [
            "Analyze the memory bandwidth, IO-awareness, and computational efficiency improvements of FlashAttention compared to standard multi-head attention.",
            "How would you design a real-time recommendation engine serving 50,000 queries per second with sub-40ms latency, balancing two-stage retrieval (ANN/embeddings) and ranking?",
            "Compare fine-tuning strategies for Large Language Models: Full fine-tuning vs LoRA vs QLoRA vs Prefix Tuning, analyzing GPU VRAM, parameter efficiency, and catastrophic forgetting.",
            "How would you architect a distributed model training cluster across multi-node GPU instances, comparing Data Parallelism (DDP), Fully Sharded Data Parallel (FSDP), and Tensor Parallelism?",
            "Design an automated ML observability pipeline to monitor covariate shift and concept drift on high-velocity production data streams."
        ]
    },
    "system design": {
        "Easy": [
            "What is the core difference between horizontal scaling and vertical scaling, and what are their respective limits?",
            "Can you explain the CAP theorem and why distributed networks must choose between Consistency and Availability during network partitions?",
            "What is the difference between relational SQL databases and NoSQL databases, and what are common NoSQL data models?",
            "What is a reverse proxy (e.g., Nginx, Envoy) and what critical advantages does it provide in modern web architectures?",
            "How does DNS resolution translate a domain name into an IP address from browser cache to authoritative name servers?"
        ],
        "Medium": [
            "Design a URL shortening service like bit.ly capable of handling 20,000 writes/sec and 200,000 reads/sec. How do you generate unique IDs and guarantee low-latency redirects?",
            "Explain how consistent hashing works and how virtual nodes prevent hot-spotting when cache nodes are added or removed dynamically.",
            "How would you implement a distributed API rate limiter supporting 100,000 req/sec using Redis? Which algorithm (token bucket, sliding window counter) would you pick and why?",
            "Describe caching strategies (Cache-Aside, Write-Through, Write-Behind) for an e-commerce catalog, and explain how to mitigate cache stampedes (thundering herd).",
            "How does Apache Kafka guarantee message ordering, and what trade-offs exist between partition count, consumer concurrency, and strict FIFO delivery?"
        ],
        "Hard": [
            "Architect a real-time collaborative document editing system (like Google Docs) supporting concurrent offline and online edits. Compare Operational Transformation (OT) vs CRDTs.",
            "Design a globally distributed payment transaction ledger ensuring strict ACID compliance, idempotency, and multi-region disaster recovery.",
            "How would you design an event-driven stream processing platform handling 2 million events per second with exactly-once processing semantics under worker node crashes?",
            "Design a multi-region active-active database architecture with conflict resolution for a mission-critical banking application with RPO < 1s and RTO < 30s.",
            "How would you architect a distributed search and log analytics engine across petabytes of data with sub-second query latency?"
        ]
    }
}

GENERIC_TOPIC_QUESTIONS: Dict[str, List[str]] = {
    "Easy": [
        "Let's start with fundamentals: Can you define the core concepts, primitives, and primary use cases of {topic}?",
        "What are the foundational data structures and standard architectural conventions when working with {topic}?",
        "How do error handling, exception propagation, and validation typically work in {topic}?",
        "What are the best practices for structuring clean, readable, and maintainable projects in {topic}?",
        "How do testing, mocking, and quality verification standardly operate in {topic}?"
    ],
    "Medium": [
        "Let's move into practical application: How would you design and implement a production-grade feature using {topic}?",
        "Describe a challenging performance bottleneck or concurrency issue you might encounter in {topic} and how you would diagnose it.",
        "How do you handle asynchronous workflows, state synchronization, or race conditions in {topic}?",
        "When integrating external APIs, data layers, or microservices with {topic}, how do you ensure resilience and graceful degradation?",
        "How would you optimize execution latency, memory footprint, or query throughput in a high-traffic {topic} service?"
    ],
    "Hard": [
        "Let's explore architectural trade-offs: What are the fundamental scalability bottlenecks of {topic} under extreme enterprise throughput?",
        "Compare two competing paradigms or frameworks within {topic}, detailing the exact trade-offs in consistency, performance, and developer ergonomics.",
        "How would you design an automated failover, health telemetry, and distributed observability pipeline for systems built with {topic}?",
        "Walk me through how you would resolve distributed state synchronization or data drift when scaling {topic}.",
        "If you were charged with migrating an enterprise legacy monolith to a scalable architecture using {topic} with zero downtime, what strategy would you execute?"
    ]
}

def is_ml_topic(topic: str) -> bool:
    norm = (topic or "").lower().strip()
    ml_keywords = [
        "machine learning", "deep learning", "artificial intelligence", "data science",
        "neural network", "neural networks", "nlp", "natural language processing",
        "computer vision", "llm", "large language model", "reinforcement learning",
        "generative ai", "genai", "transformer", "transformers", "pytorch", "tensorflow",
        "scikit-learn", "keras", "xgboost", "gradient boosting"
    ]
    if any(k in norm for k in ml_keywords):
        return True
    words = set(norm.split())
    if "ml" in words or "ai" in words:
        return True
    return False

def is_sys_topic(topic: str) -> bool:
    norm = (topic or "").lower().strip()
    sys_keywords = [
        "system design", "distributed system", "distributed systems",
        "microservices", "microservice", "scalability", "cloud architecture",
        "high availability", "database design", "kafka", "redis"
    ]
    return any(k in norm for k in sys_keywords)

def is_dsa_topic(topic: str) -> bool:
    norm = (topic or "").lower().strip()
    # Explicitly exclude ML and System Design topics from being falsely classified as DSA
    if is_ml_topic(norm) or is_sys_topic(norm):
        return False
    dsa_keywords = [
        "dsa", "leetcode", "data structure", "data structures",
        "competitive programming", "binary tree", "graph algorithm", "dynamic programming",
        "problem solving", "problem-solving", "coding interview", "algorithm", "algorithms"
    ]
    if any(k in norm for k in dsa_keywords):
        return True
    words = set(norm.split())
    if "dsa" in words or "algo" in words or "algorithms" in words or "algorithm" in words:
        return True
    return False

ALL_DSA_SUBDOMAINS = [
    "Arrays and Two Pointers",
    "Hash Maps and Frequency Counters",
    "Sliding Window and Subarrays",
    "Binary Search and Monotonic Invariants",
    "Linked Lists and Fast/Slow Pointers",
    "Stacks and Monotonic Queues",
    "Binary Trees and Depth-First Search",
    "Breadth-First Search and Matrices",
    "Dynamic Programming and Memoization",
    "Greedy Algorithms and Interval Scheduling",
    "Backtracking, Subsets, and Combinations",
    "Heaps and Priority Queues",
    "Prefix Sums and Difference Arrays",
    "String Matching and Palindromes",
    "Bit Manipulation and Bitmasks",
    "Graph Algorithms and Topological Sort"
]

def get_next_dsa_subdomain(conversation_history: List[Any], topic: str = "") -> str:
    """
    Selects a fresh, unvisited DSA subdomain across the conversation so that questions
    never repeat and naturally jumble across the entire spectrum of DSA!
    """
    import random
    combined_text = " ".join(
        (m.content if hasattr(m, "content") else str(getattr(m, "content", "")))
        for m in conversation_history
    ).lower()

    unvisited = []
    for sub in ALL_DSA_SUBDOMAINS:
        first_word = sub.lower().split()[0]
        if first_word not in combined_text:
            unvisited.append(sub)

    if not unvisited:
        return random.choice(ALL_DSA_SUBDOMAINS)
    return random.choice(unvisited)


def get_questions_for_topic(topic: str, difficulty: str, company: Optional[str] = None, count: int = 5) -> List[str]:
    norm = (topic or "").lower().strip()
    target_count = max(5, min(count, 20))

    # 1. Company Questions Priority
    base: List[str] = []
    if company:
        comp_qs = get_company_questions(company, difficulty, target_count)
        if comp_qs and len(comp_qs) >= target_count:
            return comp_qs[:target_count]
        elif comp_qs:
            base = list(comp_qs)

    # 2. Expanded Domain Pools (DSA, ML, System Design, Python)
    import random
    domain_qs: List[str] = []
    if is_dsa_topic(norm):
        domain_qs = list(EXPANDED_QUESTION_BANKS.get("dsa", {}).get(difficulty, []))
    elif is_ml_topic(norm):
        domain_qs = list(EXPANDED_QUESTION_BANKS.get("machine learning", {}).get(difficulty, []))
    elif is_sys_topic(norm):
        domain_qs = list(EXPANDED_QUESTION_BANKS.get("system design", {}).get(difficulty, []))
    elif "python" in norm:
        domain_qs = list(EXPANDED_QUESTION_BANKS.get("python", {}).get(difficulty, []))
    else:
        for key, diff_map in EXPANDED_QUESTION_BANKS.items():
            if key in norm or norm in key:
                domain_qs = list(diff_map.get(difficulty, []))
                break

    if not domain_qs:
        template = GENERIC_TOPIC_QUESTIONS.get(difficulty, GENERIC_TOPIC_QUESTIONS["Medium"])
        domain_qs = [q.replace("{topic}", topic or "Technical Concepts") for q in template]

    # Shuffle domain questions so repeated visits are spontaneous and diverse
    random.shuffle(domain_qs)

    combined = list(base)
    for q in domain_qs:
        if q not in combined:
            combined.append(q)
        if len(combined) >= target_count:
            break

    return combined[:target_count]

def evaluate_student_answer(answer: str, is_dsa: bool = False, is_ml: bool = False, is_sys: bool = False) -> str:
    """Heuristic assessment: strong | partial | weak."""
    clean = answer.strip().lower()
    words = clean.split()
    word_count = len(words)

    struggling_signals = [
        "i don't know", "i dont know", "no idea", "not sure", "cant remember",
        "can't remember", "pass", "skip", "no clue", "never heard", "unsure"
    ]
    if any(sig in clean for sig in struggling_signals) or word_count < 5:
        return "weak"

    strong_signals = [
        "because", "specifically", "trade-off", "tradeoff", "for example",
        "under the hood", "latency", "architecture", "in practice", "whereas", "contrast", "advantage"
    ]
    if is_dsa:
        strong_signals.extend(["time complexity", "space complexity", "test case", "hash map", "pointers", "sliding window", "o(n)", "o(1)"])
    elif is_ml:
        strong_signals.extend(["validation", "loss", "overfitting", "underfitting", "regularization", "precision", "recall", "f1", "gradient", "embedding", "data leakage", "cross-validation", "bias", "variance", "convergence"])
    elif is_sys:
        strong_signals.extend(["throughput", "latency", "sharding", "replication", "partition", "caching", "redis", "kafka", "load balancer", "consistency", "availability", "failover", "idempotency"])

    hits = sum(1 for s in strong_signals if s in clean)
    if word_count >= 20 and hits >= 2:
        return "strong"
    elif word_count >= 8:
        return "partial"
    else:
        return "weak"

# Built-in Hint Generator
def get_builtin_hint(topic: str, difficulty: str, question: str, hint_level: int) -> HintResponse:
    q_lower = question.lower()
    is_dsa = is_dsa_topic(topic)

    if "two sum" in q_lower:
        if hint_level == 1:
            return HintResponse(
                hint="Think about what data structure lets you check whether a complement value (`target - num`) exists in $O(1)$ time rather than checking every pair with a nested loop.",
                hint_level=1,
                category="Intuition",
                provider_used="builtin"
            )
        elif hint_level == 2:
            return HintResponse(
                hint="Use a Hash Map (dictionary) mapping `num -> index`. As you iterate through the array, check if `target - num` is already in the map.",
                hint_level=2,
                category="Data Structure",
                provider_used="builtin"
            )
        else:
            return HintResponse(
                hint="Single-pass algorithm: for index `i`, check `diff = target - nums[i]`. If `diff in map`, return `[map[diff], i]`. Otherwise `map[nums[i]] = i`. Time: $O(N)$, Space: $O(N)$.",
                hint_level=3,
                category="Algorithm & Bounds",
                provider_used="builtin"
            )

    if "lru cache" in q_lower:
        if hint_level == 1:
            return HintResponse(
                hint="To get $O(1)$ lookup and $O(1)$ removal/addition of recently used elements, you need two collaborating data structures.",
                hint_level=1,
                category="Intuition",
                provider_used="builtin"
            )
        elif hint_level == 2:
            return HintResponse(
                hint="Combine a Hash Map (`key -> Node`) with a Doubly Linked List with dummy head and tail pointers to easily evict from the tail and insert at the head.",
                hint_level=2,
                category="Data Structure",
                provider_used="builtin"
            )
        else:
            return HintResponse(
                hint="Whenever a key is accessed or updated, unlink its node and move it to the head. When capacity exceeds, remove `tail.prev`. Both run in $O(1)$ time and $O(C)$ space.",
                hint_level=3,
                category="Algorithm & Bounds",
                provider_used="builtin"
            )

    if "trapping rain water" in q_lower:
        if hint_level == 1:
            return HintResponse(
                hint="The water trapped directly above any index `i` is determined by `min(max_left, max_right) - height[i]`. Can you maintain boundary peaks?",
                hint_level=1,
                category="Intuition",
                provider_used="builtin"
            )
        elif hint_level == 2:
            return HintResponse(
                hint="Try using Two Pointers: `left = 0`, `right = len(height) - 1`. Move the pointer that currently has the smaller height, tracking `left_max` and `right_max`.",
                hint_level=2,
                category="Pattern",
                provider_used="builtin"
            )
        else:
            return HintResponse(
                hint="If `height[left] < height[right]`, water trapped depends on `left_max - height[left]`; advance `left`. Otherwise advance `right`. Time: $O(N)$, Space: $O(1)$.",
                hint_level=3,
                category="Algorithm & Bounds",
                provider_used="builtin"
            )

    if is_dsa:
        if hint_level == 1:
            return HintResponse(
                hint="Break the problem down by identifying the core pattern: Is this a two-pointer, sliding window, hash map lookup, or graph traversal problem?",
                hint_level=1,
                category="Intuition",
                provider_used="builtin"
            )
        elif hint_level == 2:
            return HintResponse(
                hint="Consider the target Big-O bounds. If a brute force takes $O(N^2)$, can sorting + binary search bring it to $O(N \\log N)$, or a hash table to $O(N)$?",
                hint_level=2,
                category="Data Structure",
                provider_used="builtin"
            )
        else:
            return HintResponse(
                hint="Test your invariants against edge cases: empty input, single element, duplicates, and extreme boundary values. Ensure your space complexity is auxiliary only.",
                hint_level=3,
                category="Edge Cases",
                provider_used="builtin"
            )

    elif is_ml_topic(topic):
        if hint_level == 1:
            return HintResponse(
                hint="Focus on the mathematical objective: What loss function is being optimized, and how do you balance the bias-variance tradeoff or prevent overfitting?",
                hint_level=1,
                category="Model Formulation",
                provider_used="builtin"
            )
        elif hint_level == 2:
            return HintResponse(
                hint="Consider data preparation and regularization: feature normalization, L1/L2 penalties, stratified validation splits, or handling imbalance via resampling or focal loss.",
                hint_level=2,
                category="Feature & Regularization",
                provider_used="builtin"
            )
        else:
            return HintResponse(
                hint="Think about production failure modes: data leakage between splits, covariate shift, evaluation metric divergence (Precision vs Recall vs ROC-AUC), or inference latency constraints.",
                hint_level=3,
                category="Production & Validation",
                provider_used="builtin"
            )

    elif is_sys_topic(topic):
        if hint_level == 1:
            return HintResponse(
                hint="Start with traffic estimations and core constraints: Read-to-write ratio, data volume growth, and latency SLAs.",
                hint_level=1,
                category="High-Level Architecture",
                provider_used="builtin"
            )
        elif hint_level == 2:
            return HintResponse(
                hint="Deconstruct into core distributed primitives: reverse proxies, horizontal stateless app servers, distributed caching (Redis), and database replication or sharding.",
                hint_level=2,
                category="Distributed Components",
                provider_used="builtin"
            )
        else:
            return HintResponse(
                hint="Focus on resilience and consistency: Single points of failure, network partitions under CAP theorem, cache invalidation / stampede prevention, and rate-limiting safeguards.",
                hint_level=3,
                category="Resilience & Consistency",
                provider_used="builtin"
            )

    # General / Conceptual Hint
    if hint_level == 1:
        return HintResponse(
            hint=f"Focus on the core principle of {topic or 'the topic'}: How does the underlying runtime or architecture handle this mechanism under the hood?",
            hint_level=1,
            category="Conceptual Focus",
            provider_used="builtin"
        )
    elif hint_level == 2:
        return HintResponse(
            hint="Structure your answer around practical trade-offs: Memory overhead vs CPU latency, and simplicity vs scalability.",
            hint_level=2,
            category="Trade-offs",
            provider_used="builtin"
        )
    else:
        return HintResponse(
            hint="Mention a real production scenario or concrete debugging tool to substantiate your answer.",
            hint_level=3,
            category="Production Insight",
            provider_used="builtin"
        )


def build_interview_response_metadata(question_text: str, topic: str = "") -> Dict[str, Any]:
    """
    Analyzes question text and topic to determine:
    1. Whether it is an algorithmic coding problem requiring code editor
    2. Dynamic problem title and language starter snippets (Python, JS, TS, C++, Java, Go, Rust)
    3. Topic-adaptive candidate input placeholder
    4. Relevant quick chips (e.g. Big-O for DSA, pythonic keywords for Python, ML metrics for ML)
    """
    try:
        is_coding = is_coding_problem(question_text, topic)
        snippets = None
        prob_title = None

        if is_coding:
            try:
                snippets = generate_starter_snippets(question_text)
            except Exception as e:
                logger.warning(f"generate_starter_snippets warning: {e}")
                snippets = None

            prob_title = extract_problem_title(question_text, topic)
            extracted_tests = extract_test_cases_from_text(question_text)
            if not extracted_tests and prob_title:
                try:
                    from canonical_dsa import get_canonical_tests
                    extracted_tests = get_canonical_tests(prob_title)
                except Exception:
                    pass
            placeholder = "State your approach, Big-O Time & Space complexity, and write your solution in the editor..."
            quick_chips = ["+ O(N) / O(1)", "+ O(N log N) / O(N)", "+ O(log N) / O(1)", "+ O(V + E) / O(V)", "+ Two Pointers", "+ Hash Map"]
        else:
            extracted_tests = []
            norm_t = (topic or "").lower()
            if "python" in norm_t:
                placeholder = "Explain your design, Pythonic idioms, decorator mechanics, or trade-offs..."
                quick_chips = ["+ functools.wraps", "+ *args, **kwargs", "+ time.perf_counter()", "+ Generator / Yield", "+ Context Manager"]
            elif is_ml_topic(topic):
                placeholder = "Explain model formulation, loss formulation, validation strategy, or trade-offs..."
                quick_chips = ["+ Bias-Variance Tradeoff", "+ Cross-Entropy Loss", "+ Regularization (L1/L2)", "+ Data Leakage", "+ ROC-AUC / F1"]
            elif is_sys_topic(topic):
                placeholder = "Explain high-level architecture, data models, scalability bottlenecks, and trade-offs..."
                quick_chips = ["+ Horizontal Scaling", "+ Consistent Hashing", "+ Read-Through Cache", "+ Database Sharding", "+ Kafka / MQ"]
            else:
                placeholder = "Type your structured explanation, design considerations, and reasoning..."
                quick_chips = ["+ Core Mechanics", "+ Edge Cases", "+ Trade-offs", "+ Production Reliability"]

        return {
            "is_coding_problem": is_coding,
            "problem_title": prob_title,
            "starter_snippets": snippets,
            "placeholder": placeholder,
            "quick_chips": quick_chips,
            "test_cases": extracted_tests if is_coding else None,
            "problem_text": question_text if is_coding else None
        }
    except Exception as ex:
        logger.error(f"Error in build_interview_response_metadata: {ex}", exc_info=True)
        return {
            "is_coding_problem": is_dsa_topic(topic),
            "problem_title": "Algorithmic Challenge",
            "starter_snippets": None,
            "placeholder": "Type your solution...",
            "quick_chips": None,
            "test_cases": None,
            "problem_text": question_text
        }


def run_builtin_start(
    topic: str,
    difficulty: str,
    resume_text: Optional[str] = None,
    company: Optional[str] = None,
    total_questions: int = 5
) -> InterviewResponse:
    target_q = max(5, min(total_questions, 20))
    is_dsa = is_dsa_topic(topic)
    has_resume = bool(resume_text and len(resume_text.strip()) > 50)

    # 1. Company Priority Greeting
    if company:
        questions = get_questions_for_topic(topic, difficulty, company=company, count=target_q)
        greeting = get_company_interviewer_intro(company, topic, difficulty, target_q)
        first_q = questions[0] if questions else f"Let's begin with our first problem on {topic}."
        full_message = f"{greeting}\n\nLet's begin with our first question:\n\n{first_q}"
        meta = build_interview_response_metadata(first_q, topic or company)
        return InterviewResponse(
            message=full_message,
            is_ended=False,
            end_reason=None,
            question_number=1,
            total_questions=target_q,
            is_follow_up=False,
            provider_used="builtin",
            **meta
        )

    # 2. Resume Priority Greeting
    if has_resume:
        resume_questions = generate_resume_questions(resume_text, difficulty, count=target_q)
        greeting = (
            f"Hello and welcome to your technical interview!\n\n"
            f"I have reviewed your resume in detail. We will be diving straight into the actual projects, "
            f"technologies, and architectural decisions documented on your CV across {target_q} questions.\n\n"
            f"Let's begin with our first question:\n\n"
            f"{resume_questions[0]}"
        )
        meta = build_interview_response_metadata(resume_questions[0], "Resume")
        return InterviewResponse(
            message=greeting,
            is_ended=False,
            end_reason=None,
            question_number=1,
            total_questions=target_q,
            is_follow_up=False,
            provider_used="builtin",
            **meta
        )

    # 3. Standard Topic Greeting
    questions = get_questions_for_topic(topic, difficulty, count=target_q)
    import random
    random.shuffle(questions)
    greeting_parts = [
        f"Hello and welcome to your technical interview on **{topic}** ({difficulty} difficulty, {target_q} questions)."
    ]

    if is_dsa:
        greeting_parts.append(
            "For algorithmic questions, please state your approach, verify it against the given test cases, and explicitly state your **Time Complexity** ($O(...)$) and **Space Complexity** ($O(...)$). You can use the built-in code editor to write and analyze code, and click the 💡 bulb icon for hints."
        )
    elif is_ml_topic(topic):
        greeting_parts.append(
            "We'll explore core model formulations, mathematical trade-offs, validation rigor, and production ML engineering. Take your time to structure clear answers, and click the 💡 bulb icon if you'd like a conceptual hint."
        )
    elif is_sys_topic(topic):
        greeting_parts.append(
            "We'll evaluate scalability, distributed consistency, fault tolerance, and high-throughput trade-offs. Click the 💡 bulb icon anytime you'd like an architectural hint."
        )
    else:
        greeting_parts.append(
            "Take your time to structure clear, thorough answers. If you ever feel stuck on a question, you can click the 💡 bulb icon for a focused hint."
        )

    greeting_parts.append("Let's begin with our first question:\n\n" + questions[0])
    greeting = "\n\n".join(greeting_parts)
    meta = build_interview_response_metadata(questions[0], topic)

    return InterviewResponse(
        message=greeting,
        is_ended=False,
        end_reason=None,
        question_number=1,
        total_questions=target_q,
        is_follow_up=False,
        provider_used="builtin",
        **meta
    )

def is_followup_message_content(text: str) -> bool:
    """Detects whether an interviewer message was an in-place follow-up probe rather than presenting a new question."""
    t = text.lower()
    signals = [
        "probe a bit deeper", "probe deeper", "follow through", "follow-through",
        "right track", "elaborate further", "before we move on",
        "time complexity and **auxiliary space complexity**", "auxiliary space complexity",
        "customer obsession and dive deep", "at google scale, how does your logic prevent",
        "at meta scale, how would you optimize", "how does your solution handle boundary",
        "how would this model or feature pipeline behave", "how would this system maintain data consistency",
        "can you elaborate further on how that specifically functioned",
        "specifically functioned in the project", "i reviewed your code logic",
        "clarify your reasoning", "didn't quite catch", "unintelligible", "probe"
    ]
    return any(s in t for s in signals)

def is_candidate_skip(answer: str) -> bool:
    """Detects whether candidate explicitly asked to skip or bypass the current question."""
    clean = answer.strip().lower()
    skip_phrases = ["skip", "pass", "next", "next question", "skip question", "i don't know", "i dont know", "no idea", "idk", "move on", "advance", "next please"]
    return clean in skip_phrases or clean.startswith("skip") or clean.startswith("next")

def is_gibberish_or_minimal(answer: str) -> bool:
    """Detects unintelligible or low-effort keystroke submissions like 'hbj', 'gjjb'."""
    clean = answer.strip().lower()
    if len(clean) < 4:
        return True
    words = clean.split()
    if len(words) <= 2 and not any(v in clean for v in "aeiou"):
        return True
    return False

def run_builtin_answer(
    topic: str,
    difficulty: str,
    conversation: List[ChatMessage],
    resume_text: Optional[str] = None,
    company: Optional[str] = None,
    total_questions: int = 5,
    code_snippet: Optional[str] = None,
    code_language: Optional[str] = "python",
    force_advance: bool = False
) -> InterviewResponse:
    target_q = max(5, min(total_questions, 20))
    candidate_messages = [m for m in conversation if m.role in ("candidate", "user")]
    interviewer_messages = [m for m in conversation if m.role in ("interviewer", "assistant")]
    is_dsa = is_dsa_topic(topic)
    is_ml = is_ml_topic(topic)
    is_sys = is_sys_topic(topic)
    has_resume = bool(resume_text and len(resume_text.strip()) > 50)
    num_answers = len(candidate_messages)

    if num_answers == 0:
        return run_builtin_start(topic, difficulty, resume_text, company, target_q)

    # Get appropriate question list
    if has_resume:
        questions = generate_resume_questions(resume_text, difficulty, count=target_q)
    else:
        questions = get_questions_for_topic(topic, difficulty, company=company, count=target_q)

    evaluations = [evaluate_student_answer(m.content, is_dsa=is_dsa, is_ml=is_ml, is_sys=is_sys) for m in candidate_messages]
    weak_count = evaluations.count("weak")
    last_eval = evaluations[-1]
    last_answer_content = candidate_messages[-1].content
    last_answer_lower = last_answer_content.lower()

    # Determine main question index and whether the previous turn was already a follow-through
    transition_phrases = ["Let's move to our next", "Let's explore another area", "Let's begin with our first", "Let's advance to our next"]
    main_questions_count = max(1, sum(1 for m in interviewer_messages if any(tp in m.content for tp in transition_phrases)))
    
    last_interviewer_obj = interviewer_messages[-1] if interviewer_messages else None
    last_interviewer_msg = last_interviewer_obj.content if last_interviewer_obj else ""

    was_already_followed_up = (
        bool(getattr(last_interviewer_obj, "is_follow_up", False))
        or is_followup_message_content(last_interviewer_msg)
    )

    candidate_wants_skip = force_advance or is_candidate_skip(last_answer_content)
    is_gibberish = is_gibberish_or_minimal(last_answer_content)

    # If candidate asked to skip, bypass any follow-up probe and advance immediately
    if candidate_wants_skip:
        was_already_followed_up = True

    # Termination 1: Severe continuous struggle across 3+ questions
    if weak_count >= 4 and main_questions_count >= 3:
        wrap_msg = (
            f"Thank you for working through these technical problems today. We will wrap up our session here. "
            f"I appreciate your effort, and a comprehensive breakdown with revision topics and focused feedback "
            f"has been prepared for your learning."
        )
        return InterviewResponse(
            message=wrap_msg,
            is_ended=True,
            end_reason="struggling_early_wrapup",
            question_number=main_questions_count,
            total_questions=target_q,
            is_follow_up=False,
            provider_used="builtin",
            is_coding_problem=False
        )

    # Current question text
    current_q_text = questions[min(main_questions_count - 1, len(questions) - 1)]

    # Case A: Answer is WEAK or PARTIAL or GIBBERISH and we haven't asked a follow-through on this question yet!
    # (And candidate did NOT request to skip)
    if not candidate_wants_skip and not was_already_followed_up and (last_eval in ("partial", "weak") or is_gibberish):
        if is_gibberish:
            msg = (
                "I didn't quite catch your technical explanation for that question. "
                "Could you clarify your reasoning or explain your approach in a sentence or two?"
            )
        # Code Snippet Evaluation: check for empty, placeholder 'pass', or test failures
        elif code_snippet:
            if _is_empty_or_placeholder(code_snippet):
                msg = (
                    "I noticed your submitted function body is empty or contains only 'pass' without an implemented solution. "
                    "Please write your algorithm logic in the code editor and return the computed result."
                )
            else:
                exec_res = execute_candidate_code(code_snippet, code_language or "python", current_q_text)
                if not exec_res.get("passed", False):
                    status_desc = exec_res.get("status", "Execution Error")
                    err_msg = exec_res.get("stderr", "Function did not return the expected output.")
                    msg = (
                        f"I ran your submitted code ({status_desc}): {err_msg} "
                        "How would you address this failure so your function returns the expected result?"
                    )
                else:
                    code_eval = analyze_code_loopholes(code_snippet, current_q_text, code_language or "python", company, difficulty)
                    msg = code_eval.get("interviewer_probe", "Good implementation. What is the asymptotic time and space complexity?")
        # DSA Specific Follow-up: Missing Time/Space complexity on DSA problem
        elif is_dsa and ("time complexity" not in last_answer_lower and "o(" not in last_answer_lower):
            msg = (
                "Good start on your algorithmic logic. However, what is your exact **Time Complexity** and **Auxiliary Space Complexity**? "
                "Please express both in Big-O notation and explain how your solution behaves on the provided test cases."
            )
        elif company and company.lower() == "amazon":
            msg = (
                "You're touching on part of the approach. From an Amazon Leadership Principle lens (Customer Obsession and Dive Deep): "
                "How would you measure the customer impact of this solution, and what happens when concurrent transactions collide under peak Prime Day load?"
            )
        elif company and company.lower() == "google":
            msg = (
                "You're on the right track, but let's look closer at the bounds. At Google scale, how does your logic prevent subtle edge-case bounds "
                "(such as empty inputs, duplicates, or integer overflow)? Can you formalize the exact optimal Big-O bounds?"
            )
        elif company and company.lower() == "meta":
            msg = (
                "You've outlined the high-level intuition. At Meta scale, how would you optimize this to run in strict linear $O(N)$ single-pass time "
                "without extra memory allocation overhead?"
            )
        elif is_dsa:
            msg = (
                "You're on the right track, but let's follow through on your approach: "
                "How does your solution handle boundary edge cases (such as empty inputs, duplicate keys, or extreme values)? "
                "Does it satisfy all sample test cases?"
            )
        elif is_ml:
            msg = (
                "You're touching on the intuition. Let's probe a bit deeper into that: "
                "How would this model or feature pipeline behave under severe class imbalance, noisy training data, or covariate distribution shift in production?"
            )
        elif is_sys:
            msg = (
                "You're on the right track. To probe deeper into this architecture: "
                "How would this system maintain data consistency and availability during a network partition or a sudden 10x traffic spike?"
            )
        elif has_resume:
            msg = (
                "You're on the right track. Can you elaborate further on how that specifically functioned in the project from your resume—"
                "particularly regarding latency constraints, API contracts, or state synchronization?"
            )
        else:
            msg = (
                f"You're partially on the right track. To probe a bit deeper into that: "
                f"How would you address error handling, scalability, or edge-case failure conditions in {topic or 'production'}?"
            )

        meta = build_interview_response_metadata(current_q_text, topic)
        return InterviewResponse(
            message=msg,
            is_ended=False,
            end_reason=None,
            question_number=main_questions_count,
            total_questions=target_q,
            is_follow_up=True,
            provider_used="builtin",
            **meta
        )

    # Case B: Answer was STRONG OR candidate already attempted the follow-through OR requested skip -> ADVANCE TO NEXT QUESTION!
    # Check if target questions are fully completed
    if main_questions_count >= target_q:
        wrap_msg = (
            f"Thank you! That thoroughly covers all {target_q} focus areas for {topic or 'your background'} at the {difficulty} level"
            + (f" for {company}" if company else "") + ". "
            f"You demonstrated good technical problem-solving across our session today. That concludes our interview!"
        )
        return InterviewResponse(
            message=wrap_msg,
            is_ended=True,
            end_reason="completed_all_areas",
            question_number=target_q,
            total_questions=target_q,
            is_follow_up=False,
            provider_used="builtin",
            is_coding_problem=False
        )

    next_idx = min(main_questions_count, len(questions) - 1)
    next_q = questions[next_idx]

    if candidate_wants_skip:
        prefix = "Understood, moving to the next question. Let's advance to our next area:\n\n"
    elif last_eval == "strong":
        if is_dsa:
            prefix = "Good explanation of that algorithmic approach and complexity bounds. Let's advance to our next problem:\n\n"
        elif is_ml:
            prefix = "Good explanation of those core machine learning concepts and modeling trade-offs. Let's advance to our next area:\n\n"
        elif is_sys:
            prefix = "Solid architectural reasoning on scalability, consistency, and resilience. Let's advance to the next system component:\n\n"
        elif has_resume:
            prefix = "Solid breakdown of your project architecture and engineering decisions. Let's explore another area from your resume:\n\n"
        else:
            prefix = f"Good explanation of those core {topic or 'technical'} concepts. Let's advance to our next question:\n\n"
    elif is_gibberish:
        prefix = "Thank you. Let's keep our momentum going and advance to our next question:\n\n"
    else:
        # Was already followed up, note gap constructively and advance
        if is_dsa:
            prefix = "Thank you for clarifying. Note that in algorithmic interviews, evaluating boundary edge cases and optimal Big-O bounds is essential. Let's advance to our next problem:\n\n"
        elif is_ml:
            prefix = "Thank you for clarifying. Note that in machine learning pipelines, rigorous validation strategy, loss formulation, and preventing data leakage or overfitting are critical. Let's advance to our next question:\n\n"
        elif is_sys:
            prefix = "Thank you for clarifying. Note that in large-scale system design, identifying single points of failure, bottleneck analysis, and database consistency trade-offs are essential. Let's advance to our next question:\n\n"
        elif has_resume:
            prefix = "Thank you for clarifying. Note that in engineering interviews, diving deep into implementation details and justifying architecture trade-offs is key. Let's explore another area from your background:\n\n"
        else:
            prefix = f"Thank you for clarifying. Note that in production software engineering, clean modularity, fault tolerance, and comprehensive edge-case handling are essential. Let's advance to our next question:\n\n"

    meta = build_interview_response_metadata(next_q, topic)
    return InterviewResponse(
        message=prefix + next_q,
        is_ended=False,
        end_reason=None,
        question_number=main_questions_count + 1,
        total_questions=target_q,
        is_follow_up=False,
        provider_used="builtin",
        **meta
    )

def run_builtin_report(
    topic: str,
    difficulty: str,
    conversation: List[ChatMessage],
    resume_text: Optional[str] = None,
    hints_used: int = 0,
    company: Optional[str] = None
) -> ReportResponse:
    candidate_messages = [m for m in conversation if m.role in ("candidate", "user")]
    is_dsa = is_dsa_topic(topic)
    is_ml = is_ml_topic(topic)
    is_sys = is_sys_topic(topic)
    has_resume = bool(resume_text and len(resume_text.strip()) > 50)

    if not candidate_messages:
        return ReportResponse(
            score=0,
            rating_label="Weak",
            status="Fail",
            strengths=["Attempted the technical interview session."],
            weaknesses=["No candidate responses were recorded in the session."],
            topics_to_revise=[topic or "Technical Fundamentals"],
            overall_verdict="Session ended without candidate responses.",
            score_breakdown={
                ("Algorithm Accuracy" if is_dsa else "ML Fundamentals" if is_ml else "System Architecture" if is_sys else "Technical Accuracy"): 0,
                ("Problem Solving" if (is_dsa or not is_ml) else "Modeling & Validation"): 0,
                ("Complexity Analysis" if is_dsa else "Production Trade-offs" if is_ml else "Scalability & Resilience" if is_sys else "Engineering Best Practices"): 0,
                "Communication & Structure": 0
            },
            resume_alignment="No responses provided to substantiate resume claims." if has_resume else None,
            dsa_complexity_analysis="No algorithmic solutions submitted." if is_dsa else None,
            provider_used="builtin"
        )

    evaluations = [evaluate_student_answer(m.content, is_dsa=is_dsa, is_ml=is_ml, is_sys=is_sys) for m in candidate_messages]
    strong_count = evaluations.count("strong")
    partial_count = evaluations.count("partial")
    weak_count = evaluations.count("weak")
    total = len(candidate_messages)

    raw_score = ((strong_count * 92) + (partial_count * 68) + (weak_count * 38)) / max(total, 1)
    
    hint_penalty = min(10, hints_used * 2)
    score = int(round(raw_score - hint_penalty))
    score = max(10, min(98, score))

    if score >= 85:
        rating_label = "Excellent"
        status_label = "Pass"
    elif score >= 70:
        rating_label = "Good"
        status_label = "Pass"
    elif score >= 55:
        rating_label = "Adequate"
        status_label = "Pass"
    else:
        rating_label = "Weak"
        status_label = "Fail"

    strengths = []
    weaknesses = []
    detailed_feedback = []

    for i, msg in enumerate(candidate_messages):
        content = msg.content.strip()
        quoted = content[:90] + ("..." if len(content) > 90 else "")
        ev = evaluations[i]
        
        if ev == "strong":
            strengths.append(f'On Question {i+1}, you stated: "{quoted}", demonstrating solid technical clarity.')
            detailed_feedback.append({
                "question": f"Question {i+1}",
                "assessment": "Strong Performance",
                "detail": f'Your answer correctly articulated the primary approach and trade-offs: "{quoted}".'
            })
        elif ev == "partial":
            strengths.append(f'On Question {i+1}, your response ("{quoted}") identified the core intuition.')
            if is_dsa:
                weaknesses.append(f'In Question {i+1} ("{quoted}"), you could have articulated exact asymptotic bounds and edge-case handling.')
                detailed_feedback.append({
                    "question": f"Question {i+1}",
                    "assessment": "Partially Correct",
                    "detail": f'Identified key algorithmic intuition but missed Big-O asymptotic bounds or test case edge cases: "{quoted}".'
                })
            elif is_ml:
                weaknesses.append(f'In Question {i+1} ("{quoted}"), you could have elaborated on validation metrics, loss convergence, or data leakage prevention.')
                detailed_feedback.append({
                    "question": f"Question {i+1}",
                    "assessment": "Partially Correct",
                    "detail": f'Identified core ML intuition but lacked depth on validation strategy, loss formulation, or distribution drift: "{quoted}".'
                })
            elif is_sys:
                weaknesses.append(f'In Question {i+1} ("{quoted}"), you could have detailed partition tolerance, caching invalidation, or database sharding.')
                detailed_feedback.append({
                    "question": f"Question {i+1}",
                    "assessment": "Partially Correct",
                    "detail": f'Identified high-level architecture but missed deep dive into distributed bottlenecks or failover strategies: "{quoted}".'
                })
            else:
                weaknesses.append(f'In Question {i+1} ("{quoted}"), you could have provided deeper technical justification and production edge cases.')
                detailed_feedback.append({
                    "question": f"Question {i+1}",
                    "assessment": "Partially Correct",
                    "detail": f'Identified high-level concept but lacked specific implementation details: "{quoted}".'
                })
        else:
            weaknesses.append(f'When addressing Question {i+1}, your answer ("{quoted}") showed noticeable gaps.')
            detailed_feedback.append({
                "question": f"Question {i+1}",
                "assessment": "Needs Revision",
                "detail": f'Noticeable conceptual gap or brief answer provided: "{quoted}".'
            })

    if not strengths:
        strengths.append(f"Demonstrated good composure and attempted {difficulty}-level technical questions.")
    if not weaknesses:
        if is_dsa:
            weaknesses.append("Can further optimize solutions toward $O(1)$ auxiliary space and verify extreme test case boundaries.")
        elif is_ml:
            weaknesses.append("Can further elaborate on offline vs online evaluation metrics and real-time inference latency constraints.")
        elif is_sys:
            weaknesses.append("Can further explore distributed consensus protocols and multi-region disaster recovery SLAs.")
        else:
            weaknesses.append("Can provide deeper real-world production metrics and edge-case failure mitigation strategies.")

    if is_dsa:
        topics_to_revise = [
            "Optimal Big-O Time & Auxiliary Space Complexity Analysis",
            "Boundary Edge Cases & Extreme Test Case Verification",
            "Advanced Data Structures & Invariant Design"
        ]
    elif is_ml:
        topics_to_revise = [
            "Bias-Variance Tradeoff, Regularization (L1/L2, Dropout), and Overfitting Remedies",
            "Data Leakage Prevention & Cross-Validation in Imbalanced Datasets",
            "Production ML Serving, Model Drift Telemetry, and Real-Time Latency Optimization"
        ]
    elif is_sys:
        topics_to_revise = [
            "Distributed Caching Strategies & Thundering Herd Mitigation",
            "Database Partitioning, Replication, and CAP Theorem Trade-offs",
            "High-Throughput Message Queue Architecture & Exactly-Once Delivery"
        ]
    else:
        topics_to_revise = [
            f"{topic} core architectural design patterns" if topic else "System Architecture & API Design Patterns",
            f"Performance optimization and latency tuning in {topic}" if topic else "Concurrency and State Synchronization",
            "Error handling, failover, and boundary resilience"
        ]

    verdict = (
        f"The candidate completed a {difficulty}-level interview on {topic or 'their technical background'}. "
        f"Overall evaluation resulted in a score of {score}/100 ({rating_label} performance, Status: {status_label}). "
        f"The candidate successfully demonstrated practical understanding in foundational areas while identifying "
        f"specific domains for structured revision."
    )
    if hints_used > 0:
        verdict += f" (Utilized {hints_used} on-demand hints during the interview to unblock solutions)."

    resume_eval = None
    if has_resume:
        resume_eval = (
            "Resume Alignment: Candidate's technical answers generally substantiated the projects and skills claimed on their CV. "
            "Demonstrated practical familiarity with relevant architectures; recommend continuing to practice articulating architectural decisions and production trade-offs."
        )

    dsa_eval = None
    if is_dsa:
        dsa_eval = (
            "Complexity & Test Cases: Solution approaches reached satisfactory time complexity. "
            "Always state both Time and Space complexity upfront in interviews and trace logic through sample test cases."
        )

    score_breakdown = {
        ("Algorithm Accuracy" if is_dsa else "ML Fundamentals" if is_ml else "System Architecture" if is_sys else "Technical Accuracy"): max(20, min(100, int(score * 1.02))),
        ("Problem Solving" if (is_dsa or not is_ml) else "Modeling & Validation"): max(20, min(100, int(score * 0.98))),
        ("Complexity Analysis" if is_dsa else "Production Trade-offs" if is_ml else "Scalability & Resilience" if is_sys else "Engineering Best Practices"): max(20, min(100, int(score * 0.95))),
        "Communication & Structure": max(25, min(100, int(score * 1.05)))
    }

    company_eval = None
    if company:
        prof = get_company_profile(company)
        focus_text = prof.get("philosophy") or prof.get("tagline") or f"{company} engineering standards"
        company_eval = (
            f"{company} Bar Assessment: Candidate exhibited {rating_label.lower()} alignment "
            f"with {company}'s core evaluation standards ({focus_text}). "
            f"Candidate achieved a score of {score}/100."
        )

    return ReportResponse(
        score=score,
        rating_label=rating_label,
        status=status_label,
        strengths=strengths[:4],
        weaknesses=weaknesses[:4],
        topics_to_revise=topics_to_revise,
        overall_verdict=verdict,
        company_alignment=company_eval,
        resume_alignment=resume_eval,
        dsa_complexity_analysis=dsa_eval,
        score_breakdown=score_breakdown,
        detailed_feedback=detailed_feedback,
        provider_used="builtin"
    )


# --- LLM Prompts & Cloud Callers with On-Demand Hint Support ---

def format_conversation(conversation: List[ChatMessage]) -> str:
    lines = []
    for m in conversation:
        label = "Interviewer" if m.role in ("interviewer", "assistant") else "Candidate"
        lines.append(f"{label}: {m.content}")
    return "\n\n".join(lines)

def build_interviewer_system_prompt(topic: str, difficulty: str, resume_text: Optional[str] = None, company: Optional[str] = None) -> str:
    is_dsa = is_dsa_topic(topic)
    is_ml = is_ml_topic(topic)
    is_sys = is_sys_topic(topic)

    company_resume_bridge = ""
    if company and resume_text and len(resume_text.strip()) > 50:
        company_resume_bridge = f"""
CRITICAL HYBRID COMPANY + RESUME TAILORING DIRECTIVE:
You are a Lead Staff Engineer and Technical Bar Raiser at {company.upper()}.
The candidate has provided both their target company ({company.upper()}) AND their actual RESUME.
Your primary directive is to bridge their resume to {company}'s real-world engineering standards:
1. Cross-examine the actual projects, architectures, and tech stack from their resume through the lens of {company.upper()}'s production scale, latency, and reliability requirements.
2. For example, evaluate how their specific resume solutions would be architected or scaled to meet {company}'s real-world scale, performance bar, and operational failure modes.
3. Challenge their technical trade-offs from the perspective of {company.upper()}'s core engineering bar and Leadership Principles.
4. If an algorithmic problem is needed, frame it around real engineering challenges faced at {company.upper()}.
"""
    elif company:
        company_resume_bridge = f"""
TARGET COMPANY: {company.upper()}
You represent {company.upper()}'s technical hiring committee. Emphasize {company}'s engineering culture, system scale, and problem-solving bar.
"""

    resume_section = ""
    if resume_text and len(resume_text.strip()) > 50:
        resume_section = f"""
CRITICAL DIRECT RESUME INSTRUCTION:
A candidate resume has been provided below. You MUST formulate all questions directly based on the projects, work experience, achievements, and technical stack listed on their resume:
--- RESUME BEGIN ---
{resume_text[:4500]}
--- RESUME END ---
DO NOT ask generic textbook questions. Cross-examine the candidate directly on what they actually built, the architectural decisions they made, why they chose specific tools listed on their CV, and how they handled technical trade-offs.
"""

    if is_dsa:
        domain_rules = """
SPECIAL DSA CODING REQUIREMENTS:
1. Every algorithmic problem MUST clearly state its title at the very top using the exact format:
   ### Problem: <Problem Title>
   (For example: ### Problem: Generate Combinations, or ### Problem: Two Sum, or ### Problem: Trapping Rain Water)
2. Every algorithmic problem MUST include ALL 3 sections:
   - Problem Description (Explain the task, input variables, and expected output clearly)
   - Test Cases (MANDATORY: You MUST provide 2 or 3 numbered test cases formatted with:
     1. Input: <param> = <val>, ...
        Output: <expected>
        Explanation: ...
     2. Input: ...
        Output: ...)
   - Constraints
   DO NOT skip the Test Cases section.
3. Explicitly state the function signature if helpful: e.g. `fn_name(param1, param2)`.
4. ALWAYS evaluate whether the candidate declared both Time Complexity ($O(...)$) and Auxiliary Space Complexity ($O(...)$).
5. If they omitted complexity analysis or provided an unoptimized solution, probe for it directly without revealing the answer.
"""
    elif is_ml:
        domain_rules = """
DOMAIN: MACHINE LEARNING & AI INTERVIEW
1. This is a Machine Learning interview. NEVER mention Big-O notation, asymptotic time/space bounds, or LeetCode test cases.
2. Focus questions, acknowledgments, and gap notes strictly on:
   - Model formulation, objective/loss functions, and bias-variance tradeoff
   - Data preprocessing, feature engineering, and data leakage prevention
   - Evaluation metrics (Precision, Recall, ROC-AUC, F1, PR-AUC) especially for imbalanced data
   - Production ML: offline vs online metrics, covariate shift / data drift, inference latency
3. When the candidate's answer is wrong or weak, note the gap in ONE concise line strictly focused on ML principles (e.g. "Note that in machine learning pipelines, validating against data leakage and choosing the right evaluation metric are critical. Let's move to our next question:"). NEVER mention Big-O or algorithmic bounds.
"""
    elif is_sys:
        domain_rules = """
DOMAIN: SYSTEM DESIGN INTERVIEW
1. This is a System Design interview. NEVER mention Big-O algorithmic complexity or LeetCode test cases.
2. Focus questions, acknowledgments, and gap notes on:
   - High availability, horizontal scaling, throughput (QPS/RPS), and latency targets
   - Caching strategies, database sharding/replication, and CAP theorem consistency trade-offs
   - Single points of failure, load balancing, message queues, and rate limiting
3. When noting gaps for wrong/weak answers, focus on distributed architectural trade-offs. NEVER mention Big-O.
"""
    else:
        domain_rules = f"""
DOMAIN: {topic.upper()} ENGINEERING INTERVIEW
1. Focus on core architectural patterns, maintainability, production reliability, and trade-offs of {topic}.
2. DO NOT mention Big-O bounds or LeetCode test cases unless the candidate is specifically writing an algorithm.
"""

    return f"""You are a seasoned, professional, and encouraging technical interviewer conducting a mock interview on the topic "{topic or 'Resume Background'}".
Difficulty: {difficulty}
{company_resume_bridge}
{domain_rules}
{resume_section}

Interview Rules & Constraints:
1. Ask exactly ONE question at a time.
2. Evaluate the candidate's last answer based on the conversation so far:
   - If the candidate's answer is strong: Acknowledge briefly (1 short line) and move to a DIFFERENT aspect / next project.
   - If the candidate's answer is partly right: Ask ONE probing follow-up question tailored to the topic without revealing the answer.
   - If the candidate's answer is wrong: Note the gap in one concise line tailored strictly to the topic and move on to the next question.
3. ABSOLUTE PROHIBITIONS:
   - NEVER teach the candidate.
   - NEVER provide hints in standard conversation (hints are handled separately via on-demand triggers).
   - Stay strictly professional, courteous, and encouraging.
4. Interview Termination Criteria:
   - If the candidate is clearly struggling across several questions (e.g. repeatedly answering incorrectly or saying they don't know), end the interview early and kindly. Set "is_ended": true and "end_reason": "struggling_early_wrapup".
   - If the candidate is doing very well and key aspects of the topic have been covered (typically 4 to 6 questions total), wrap up the interview cleanly and positively. Set "is_ended": true and "end_reason": "completed_all_areas".
   - Otherwise, continue the interview. Set "is_ended": false and "end_reason": null.

Return your response strictly as a JSON object matching this schema:
{{
  "message": "<What the interviewer says to the candidate>",
  "is_ended": false,
  "end_reason": null
}}
"""

def build_hint_prompt(topic: str, difficulty: str, question: str, hint_level: int) -> str:
    is_dsa = is_dsa_topic(topic)
    is_ml = is_ml_topic(topic)

    if is_dsa:
        level_desc = (
            "Level 1: Conceptual intuition or high-level direction (Do NOT reveal the algorithm or code)."
            if hint_level == 1
            else (
                "Level 2: Relevant data structure or standard algorithmic pattern."
                if hint_level == 2
                else "Level 3: Specific invariant, recurrence relation, or key edge case to consider."
            )
        )
    elif is_ml:
        level_desc = (
            "Level 1: Mathematical formulation or objective function direction (Do NOT give the full formula)."
            if hint_level == 1
            else (
                "Level 2: Standard modeling, feature preparation, or regularization technique."
                if hint_level == 2
                else "Level 3: Specific failure mode (e.g. data leakage, covariate shift, metric mismatch)."
            )
        )
    else:
        level_desc = (
            "Level 1: High-level architectural or conceptual direction."
            if hint_level == 1
            else (
                "Level 2: Standard software engineering pattern or component design."
                if hint_level == 2
                else "Level 3: Edge cases, concurrency, or production trade-offs."
            )
        )

    return f"""You are a helpful technical coach providing an on-demand hint for this interview question on "{topic or 'technical problem'}" ({difficulty}):

Question:
{question}

Hint Level Requested: {hint_level} ({level_desc})

Rules:
1. Be concise, encouraging, and clear (2 to 3 sentences max).
2. Help unblock the candidate's thinking without giving away the full solution.
3. Classify category into one of: "Intuition", "Formulation", "Pattern", "Edge Case", or "General".
4. If this is a Machine Learning interview, DO NOT mention Big-O notation or LeetCode test cases.

Return JSON:
{{
  "hint": "<Encouraging hint>",
  "hint_level": {hint_level},
  "category": "..."
}}
"""

def build_report_system_prompt(topic: str, difficulty: str, resume_text: Optional[str] = None) -> str:
    is_dsa = is_dsa_topic(topic)
    is_ml = is_ml_topic(topic)
    is_sys = is_sys_topic(topic)

    resume_note = ""
    if resume_text:
        resume_note = "- Resume Alignment: Evaluate how well candidate's answers substantiated the claims on their resume."

    if is_dsa:
        domain_note = "- DSA Complexity Analysis: Specifically evaluate candidate's Time Complexity and Space Complexity accuracy against test cases."
        score_keys = '"Algorithm Accuracy": 75, "Problem Solving": 78, "Complexity Analysis": 70, "Communication & Structure": 80'
    elif is_ml:
        domain_note = "- CRITICAL: This is a Machine Learning interview. DO NOT mention Big-O bounds or LeetCode test cases. Set dsa_complexity_analysis to null. Focus strengths, weaknesses, and revision on ML model formulation, validation metrics, data leakage, and drift."
        score_keys = '"ML Fundamentals": 75, "Modeling & Validation": 78, "Production Trade-offs": 70, "Communication & Structure": 80'
    elif is_sys:
        domain_note = "- CRITICAL: This is a System Design interview. DO NOT mention Big-O bounds or LeetCode test cases. Set dsa_complexity_analysis to null. Focus strengths, weaknesses, and revision on distributed scalability, consistency trade-offs, and fault tolerance."
        score_keys = '"System Architecture": 75, "Scalability & Resilience": 78, "Data & Storage Design": 70, "Communication & Structure": 80'
    else:
        domain_note = "- CRITICAL: DO NOT mention Big-O notation or LeetCode test cases unless directly asked. Set dsa_complexity_analysis to null."
        score_keys = '"Technical Accuracy": 75, "Problem Solving": 78, "Engineering Best Practices": 70, "Communication & Structure": 80'

    return f"""You are an expert technical hiring manager evaluating an interview on "{topic or 'Resume Background'}" ({difficulty} difficulty).

Your task is to generate a comprehensive structured evaluation report.

Scoring Standards:
- Score: Integer from 0 to 100.
  - 85 and above: "Excellent" -> Status: "Pass"
  - 70 to 84: "Good" -> Status: "Pass"
  - 55 to 69: "Adequate" -> Status: "Pass"
  - Below 55: "Weak" -> Status: "Fail"
- Strengths: List of strings. CRITICAL REQUIREMENT: Each strength MUST explicitly reference or quote something the candidate ACTUALLY said in the transcript.
- Weaknesses: List of strings. CRITICAL REQUIREMENT: Each weakness MUST explicitly reference or quote something the candidate ACTUALLY said or missed.
- Topics to Revise: List of specific technical topics and subtopics for the candidate to review.
- Overall Verdict: Executive summary narrative of candidate's performance.
- Score Breakdown: Object containing scores (0-100) for the domain dimensions.
{resume_note}
{domain_note}
- Status: "Pass" if score >= 55, else "Fail".
- Rating Label: "Excellent", "Good", "Adequate", or "Weak".

Return your response strictly as a JSON object matching this schema:
{{
  "score": 75,
  "rating_label": "Good",
  "status": "Pass",
  "strengths": ["...", "..."],
  "weaknesses": ["...", "..."],
  "topics_to_revise": ["...", "..."],
  "overall_verdict": "...",
  "resume_alignment": "... or null",
  "dsa_complexity_analysis": "... or null",
  "score_breakdown": {{
    {score_keys}
  }}
}}
"""

GROQ_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "llama-3.3-70b-versatile"
]

async def call_groq_api(system_prompt: str, user_prompt: str, api_key: str, temperature: float = 0.7) -> Dict[str, Any]:
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "AI-Interviewer/2.5"
    }

    last_err = None
    for model in GROQ_MODELS:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "response_format": {"type": "json_object"},
            "temperature": temperature
        }
        try:
            async with httpx.AsyncClient(limits=HTTPX_LIMITS, timeout=25.0) as client:
                res = await client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    raw = data["choices"][0]["message"]["content"]
                    return json.loads(raw)
                else:
                    last_err = f"{model} returned {res.status_code}: {res.text}"
                    logger.warning(f"Groq model {model} HTTP {res.status_code}")
        except Exception as e:
            last_err = str(e)
            logger.warning(f"Groq model {model} request failed: {e}")
            continue

    raise RuntimeError(f"All Groq models failed. Last error: {last_err}")


# --- API Routes Exposing PDF Resume Upload, Hints, and Actions ---

@app.get("/")
def read_root():
    return {
        "name": "AI Interview Coach API",
        "status": "online",
        "version": "2.3.0",
        "endpoints": {
            "health": "/api/health",
            "upload_resume": "/api/interview/upload-resume",
            "start": "/api/interview/start",
            "answer": "/api/interview/answer",
            "hint": "/api/interview/hint",
            "report": "/api/interview/report"
        }
    }

@app.get("/api/health")
def health_check():
    groq_ready = bool(GROQ_API_KEY and GROQ_API_KEY != "your_groq_api_key_here")
    return {
        "status": "healthy",
        "message": "AI Interview Coach Backend is running smoothly.",
        "builtin_engine": "active (100% available without external keys)",
        "groq_api_key_set": groq_ready,
        "pdf_parser_ready": True,
        "hint_engine_ready": True,
        "concurrency_ready": True
    }

# PDF Resume Upload Endpoint
@app.post("/api/interview/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    """Upload a candidate's PDF resume and extract its text for resume-based interviewing."""
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Please upload a PDF file (.pdf)."
        )
    try:
        contents = await file.read()
        if len(contents) > 10 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size exceeds 10MB limit. Please upload a smaller PDF."
            )
        reader = pypdf.PdfReader(io.BytesIO(contents))
        extracted_text = ""
        for page in reader.pages:
            t = page.extract_text()
            if t:
                extracted_text += t + "\n"

        extracted_text = extracted_text.strip()
        if not extracted_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from the PDF. It might be scanned or image-only."
            )

        clean_text = extracted_text[:12000]
        highlights = extract_resume_highlights(clean_text)
        return {
            "success": True,
            "filename": file.filename,
            "page_count": len(reader.pages),
            "char_count": len(clean_text),
            "preview": clean_text[:250] + ("..." if len(clean_text) > 250 else ""),
            "highlights": highlights,
            "resume_text": clean_text
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error parsing PDF resume: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to read the PDF document. Please ensure it is a valid PDF."
        )

# Action 1: Start an interview
@app.post("/api/interview/start", response_model=InterviewResponse)
async def start_interview(req: StartInterviewRequest):
    """Action 1: Start interview. If resume_text provided, questions derive directly from candidate's CV.
    If company provided, questions match company bar.
    If BOTH company and resume provided, questions bridge candidate's resume projects to company scale!"""
    api_key_to_use = req.api_key or GROQ_API_KEY
    active_provider = req.provider or "auto"
    effective_topic = req.topic or "Resume Technical Evaluation"

    if (active_provider in ("groq", "auto")) and api_key_to_use:
        try:
            import random
            import uuid

            session_id = uuid.uuid4().hex[:6]
            system_prompt = build_interviewer_system_prompt(effective_topic, req.difficulty, req.resume_text, company=req.company)
            company_ctx = f" Target Company: {req.company}." if req.company else ""

            dsa_subdomains = [
                "Arrays and Two Pointers",
                "Hash Maps and Frequency Counters",
                "Sliding Window and Subarrays",
                "Binary Search and Monotonic Invariants",
                "Linked Lists and Fast/Slow Pointers",
                "Stacks and Monotonic Queues",
                "Binary Trees and Depth-First Search",
                "Breadth-First Search and Matrices",
                "Dynamic Programming and Memoization",
                "Greedy Algorithms and Interval Scheduling",
                "Backtracking and Combinations",
                "Heaps and Priority Queues",
                "Prefix Sums and Difference Arrays",
                "String Matching and Palindromes"
            ]

            python_subdomains = [
                "CPython Memory Management and Small Object Pools",
                "Asyncio Event Loops and Concurrency Primitives",
                "Decorators, Closures, and Metaclasses",
                "Dictionary Hash Collisions and Object Interning",
                "Generators, Iterators, and Yield Semantics"
            ]

            ml_subdomains = [
                "Evaluation Metrics on Imbalanced Datasets (ROC-AUC vs PR-AUC)",
                "Data Leakage and Cross-Validation Safeguards",
                "Loss Formulations, Regularization (L1/L2), and Overfitting",
                "Model Drift, Covariate Shift, and Telemetry",
                "Production ML Serving and Real-Time Latency"
            ]

            sys_subdomains = [
                "Distributed Caching, Redis Eviction, and Thundering Herd",
                "Database Sharding, Replication, and CAP Consistency",
                "Event-Driven Architecture, Kafka, and Idempotent Consumers",
                "Rate Limiting, Token Buckets, and API Gateways"
            ]

            focus_instruction = ""
            if is_dsa_topic(effective_topic):
                chosen_sub = get_next_dsa_subdomain([], effective_topic)
                focus_instruction = (
                    f" For this interview session (Session ID: {session_id}), formulate an algorithmic challenge focusing on '{chosen_sub}'. "
                    f"Ensure the question is a distinct {req.difficulty}-level problem from this domain. "
                    f"Format the problem title prominently at the very top: ### Problem: <Problem Title>. "
                    f"Do NOT default to standard textbook problems like Missing Number or Two Sum if another interesting problem from '{chosen_sub}' can be presented."
                )
            elif is_ml_topic(effective_topic):
                chosen_sub = random.choice(ml_subdomains)
                focus_instruction = f" Focus on '{chosen_sub}' for this session (Session ID: {session_id})."
            elif is_sys_topic(effective_topic):
                chosen_sub = random.choice(sys_subdomains)
                focus_instruction = f" Focus on '{chosen_sub}' for this session (Session ID: {session_id})."
            elif "python" in effective_topic.lower():
                chosen_sub = random.choice(python_subdomains)
                focus_instruction = f" Focus on '{chosen_sub}' for this session (Session ID: {session_id})."

            if req.resume_text and req.company:
                user_msg = (
                    f"Start the technical interview for {req.company}. The candidate has provided their resume. "
                    f"Introduce yourself as an engineering interviewer at {req.company}, briefly acknowledge their background, "
                    f"and formulate the first question DIRECTLY cross-examining their flagship resume project through {req.company}'s engineering standards and scale.{focus_instruction} "
                    f"Total questions: {req.total_questions}."
                )
            elif req.resume_text:
                user_msg = (
                    f"Start the technical interview. Formulate the first question DIRECTLY based on the candidate's actual projects, "
                    f"experience, and tech stack from their resume.{focus_instruction} Introduce yourself briefly and ask. Total questions: {req.total_questions}."
                )
            else:
                user_msg = f"Start the technical interview for topic '{effective_topic}' at '{req.difficulty}' difficulty.{company_ctx}{focus_instruction} Total questions: {req.total_questions}. Introduce yourself and ask the first question."

            data = await call_groq_api(system_prompt, user_msg, api_key_to_use, temperature=0.7)
            msg = data.get("message", "Let's begin: Could you explain the core concepts of " + effective_topic + "?")
            meta = build_interview_response_metadata(msg, effective_topic)
            return InterviewResponse(
                message=msg,
                is_ended=False,
                end_reason=None,
                question_number=1,
                total_questions=req.total_questions,
                is_follow_up=False,
                provider_used="groq",
                **meta
            )
        except Exception as e:
            logger.warning(f"Groq start failed, fallback to builtin: {e}")

    return run_builtin_start(effective_topic, req.difficulty, req.resume_text, company=req.company, total_questions=req.total_questions)


# Action 2: Submit an answer
@app.post("/api/interview/answer", response_model=InterviewResponse)
async def submit_answer(req: SubmitAnswerRequest):
    """Action 2: Submit answer. Evaluates candidate response, code, resume, and company bar."""
    api_key_to_use = req.api_key or GROQ_API_KEY
    active_provider = req.provider or "auto"
    effective_topic = req.topic or "Resume Technical Evaluation"

    if (active_provider in ("groq", "auto")) and api_key_to_use:
        try:
            system_prompt = build_interviewer_system_prompt(effective_topic, req.difficulty, req.resume_text, company=req.company)
            transcript = format_conversation(req.conversation)
            code_ctx = f"\n\nCandidate's Submitted Code ({req.code_language}):\n{req.code_snippet}" if req.code_snippet else ""
            company_ctx = f"\nTarget Company: {req.company}" if req.company else ""
            resume_ctx = f"\nResume Active: Yes (evaluate against claimed projects and architectures)." if req.resume_text else ""

            dsa_rotation_ctx = ""
            if is_dsa_topic(effective_topic) and not req.resume_text:
                next_sub = get_next_dsa_subdomain(req.conversation, effective_topic)
                dsa_rotation_ctx = (
                    f"\n\nDSA SUBDOMAIN ROTATION DIRECTIVE:"
                    f"\nIf advancing to a new question, switch to an entirely DIFFERENT DSA domain: '{next_sub}'."
                    f"\nFormulate a fresh, original {req.difficulty}-level problem from '{next_sub}'."
                    f"\nFormat the problem title prominently at the very top: ### Problem: <Problem Title>."
                    f"\nInclude all 3 sections: Problem Description, Test Cases (with 2-3 numbered cases: Input, Output, Explanation), and Constraints."
                    f"\nDo NOT repeat any problem or stay on the same domain as earlier in the conversation!"
                )

            advance_clause = ""
            if req.force_advance or (req.code_snippet and len(req.code_snippet.strip()) > 40):
                advance_clause = "\nDIRECTIVE: The candidate has provided their code / requested advance. Acknowledge concisely in one sentence and advance to the next question now without further probing."

            user_msg = (
                f"Topic: {effective_topic}\nDifficulty: {req.difficulty}{company_ctx}{resume_ctx}\nTarget Questions: {req.total_questions}\n\n"
                f"Conversation so far:\n{transcript}{code_ctx}{dsa_rotation_ctx}{advance_clause}\n\n"
                f"Evaluate the last candidate answer. If it's weak or partial (and not advancing), ask a probing follow-through on this same topic/project before advancing. "
                f"If strong, already followed up, or advancing, acknowledge concisely and advance to the next question. "
                f"Wrap up if {req.total_questions} questions have been completed."
            )
            data = await call_groq_api(system_prompt, user_msg, api_key_to_use)
            candidate_count = sum(1 for m in req.conversation if m.role in ("candidate", "user"))
            is_follow_up = any(w in data.get("message", "").lower() for w in ["probe", "follow-through", "follow through", "loopholes", "edge case"])
            msg = data.get("message", "Thank you. Let's move on.")
            is_ended = bool(data.get("is_ended", False))
            meta = build_interview_response_metadata(msg, effective_topic) if not is_ended else {"is_coding_problem": False}
            return InterviewResponse(
                message=msg,
                is_ended=is_ended,
                end_reason=data.get("end_reason"),
                question_number=candidate_count + 1,
                total_questions=req.total_questions,
                is_follow_up=is_follow_up,
                provider_used="groq",
                **meta
            )
        except Exception as e:
            logger.warning(f"Groq answer failed, fallback to builtin: {e}")

    return run_builtin_answer(
        effective_topic,
        req.difficulty,
        req.conversation,
        req.resume_text,
        company=req.company,
        total_questions=req.total_questions,
        code_snippet=req.code_snippet,
        code_language=req.code_language,
        force_advance=bool(req.force_advance)
    )


# --- Realtime Helper Engine (Live Co-Pilot Guidance) ---

def generate_realtime_helper(req: RealtimeHelperRequest) -> RealtimeHelperResponse:
    t_lower = (req.topic or "").lower()
    q_lower = (req.current_question or "").lower()
    is_dsa = is_dsa_topic(req.topic) or "problem:" in q_lower or "test case" in q_lower or bool(req.problem_title)
    is_ml = is_ml_topic(req.topic)
    is_sys = is_sys_topic(req.topic)
    is_resume = "resume" in t_lower or "project" in q_lower or "cv" in t_lower

    if is_dsa:
        fw_name = "UMIRE Algorithmic Framework"
        fw_desc = "Standard 5-step problem solving framework favored by FAANG interviewers"
        fw_steps = [
            {"step": "1. Understand", "detail": "Clarify inputs, edge cases (empty, negatives, duplicates), and output format."},
            {"step": "2. Match / Intuition", "detail": "Identify the data structure (Hash Map, Two Pointers, Monotonic Stack, BFS/DFS)."},
            {"step": "3. Implement", "detail": "Write clean, idiomatic code with clear variable names and loop bounds."},
            {"step": "4. Review & Trace", "detail": "Dry-run the algorithm on Sample Test Case 1 and an extreme boundary case."},
            {"step": "5. Evaluate Big-O", "detail": "Explicitly state Time Complexity O(...) and Auxiliary Space Complexity O(...)."}
        ]
        keywords = ["Time Complexity", "Space Complexity", "Edge Cases", "Hash Map", "Two Pointers", "Sliding Window", "Invariants", "Test Cases", "O(N)", "O(1)"]
    elif is_ml:
        fw_name = "FORM-EVAL Machine Learning Framework"
        fw_desc = "Comprehensive ML engineering structure from loss formulation to production telemetry"
        fw_steps = [
            {"step": "1. Problem Formulation", "detail": "Frame as classification, regression, or ranking; define the loss/objective function."},
            {"step": "2. Data & Validation", "detail": "Describe train/val/test splits, prevention of data leakage, and feature transformations."},
            {"step": "3. Model Architecture", "detail": "Select baseline vs advanced models; justify bias-variance and regularization trade-offs."},
            {"step": "4. Evaluation Metrics", "detail": "Choose offline metrics (ROC-AUC, PR-AUC, F1) aligned with class imbalance."},
            {"step": "5. Production Serving", "detail": "Address latency SLAs, online inference vs batching, and model drift telemetry."}
        ]
        keywords = ["Objective / Loss", "Bias-Variance Tradeoff", "Regularization (L1/L2)", "Validation Split", "Data Leakage", "ROC-AUC / F1", "Feature Engineering", "Model Drift"]
    elif is_sys:
        fw_name = "RADIO System Design Framework"
        fw_desc = "Industry standard architecture progression for distributed scalable systems"
        fw_steps = [
            {"step": "1. Requirements & Scope", "detail": "Establish functional requirements, DAU/QPS throughput, and latency SLAs."},
            {"step": "2. Architecture (High-Level)", "detail": "Draw clients, API Gateway, stateless service tiers, and persistent storage."},
            {"step": "3. Data Model & Storage", "detail": "SQL vs NoSQL, sharding keys, indexing strategies, and caching layers (Redis)."},
            {"step": "4. Interfaces & Contracts", "detail": "Define REST/gRPC endpoints, payload schemas, and idempotency guarantees."},
            {"step": "5. Optimizations & Bottlenecks", "detail": "Address single points of failure, partition tolerance (CAP), and rate limiting."}
        ]
        keywords = ["Scalability & QPS", "Latency SLAs", "Sharding & Replication", "Consistent Hashing", "Message Queue / Kafka", "Cache Invalidation", "CAP Theorem", "Single Point of Failure"]
    elif is_resume:
        fw_name = "STAR-E Resume Engineering Framework"
        fw_desc = "Deep-dive framework proving hands-on engineering ownership and technical decisions"
        fw_steps = [
            {"step": "1. Situation & Context", "detail": "Briefly describe the business need, system scale, and your exact role."},
            {"step": "2. Technical Architecture", "detail": "Detail the services, protocols (HTTP/gRPC/Kafka), and data flow."},
            {"step": "3. Concrete Action", "detail": "Explain specific components, algorithms, or schemas you authored."},
            {"step": "4. Results & Metrics", "detail": "Quote concrete numbers: latency reduction %, throughput increase, or uptime SLA."},
            {"step": "5. Engineering Trade-offs", "detail": "Explain alternative technologies evaluated and why this was chosen."}
        ]
        keywords = ["System Architecture", "Latency & Throughput", "Trade-offs", "Database & Indexing", "Caching", "State Sync & Race Conditions", "Failover & Resilience", "Concrete Metrics"]
    else:
        fw_name = "IDOM Technical Framework"
        fw_desc = "Structured engineering communication for software topics"
        fw_steps = [
            {"step": "1. Core Intent", "detail": "Define what the mechanism does and why it exists."},
            {"step": "2. Under-the-Hood Design", "detail": "Explain how the runtime, memory, or engine executes it."},
            {"step": "3. Practical Trade-offs", "detail": "Highlight pros, cons, and performance implications."},
            {"step": "4. Production Best Practices", "detail": "Share clean idioms, error handling, and testing strategies."}
        ]
        keywords = ["Core Mechanics", "Memory & Performance", "Edge Cases", "Trade-offs", "Production Reliability", "Best Practices"]

    # Analyze draft
    draft = (req.draft_answer or "").strip()
    draft_lower = draft.lower()
    words = draft_lower.split()
    word_count = len(words)

    detected = []
    missing = []
    for kw in keywords:
        kw_clean = kw.lower().replace("/", " ").replace("-", " ")
        subwords = [w.strip() for w in kw_clean.split() if len(w.strip()) > 2]
        if any(sw in draft_lower for sw in subwords):
            detected.append(kw)
        else:
            missing.append(kw)

    # Readiness Score
    if word_count == 0:
        score = 0
        label = "Not Started"
        critique = "Type your response in the candidate box or speak using the 🎙️ mic button. Structure your thoughts using the framework steps."
    elif word_count < 15:
        score = 30
        label = "Initial Outline"
        critique = "Your draft is very brief. Expand on the underlying mechanics and address edge cases or trade-offs."
    elif word_count < 45:
        score = 60
        label = "Developing Draft"
        critique = f"Good start! You've touched on {len(detected)} key concepts. Consider incorporating: {', '.join(missing[:2])}."
    elif len(detected) >= 3 and word_count >= 50:
        score = 92
        label = "Interview-Ready"
        critique = "Excellent structure! You've addressed core mechanics, trade-offs, and critical technical terminology. Ready to submit!"
    else:
        score = 78
        label = "Solid Draft"
        critique = f"Solid reasoning. To elevate to an exceptional answer, substantiate with: {', '.join(missing[:2])}."

    quick_tips = [
        "Be direct: State your primary thesis or architectural decision in the first 1-2 sentences.",
        "Quantify where possible: mention Big-O bounds, latency SLAs (ms), or throughput (RPS).",
        "Acknowledge trade-offs: every architectural or algorithmic decision has concrete trade-offs."
    ]

    return RealtimeHelperResponse(
        framework_name=fw_name,
        framework_description=fw_desc,
        framework_steps=fw_steps,
        recommended_keywords=keywords,
        detected_keywords=detected,
        missing_keywords=missing,
        critique=critique,
        readiness_score=score,
        readiness_label=label,
        quick_tips=quick_tips
    )

@app.post("/api/interview/realtime-helper", response_model=RealtimeHelperResponse)
async def realtime_helper_endpoint(req: RealtimeHelperRequest):
    """Provides real-time co-pilot guidance, live concept checklist detection, and pre-submit draft critique."""
    return generate_realtime_helper(req)


# Code Analyzer Endpoint: Find Loopholes, Big-O, Test Cases
@app.post("/api/interview/analyze-code", response_model=CodeAnalysisResponse)
async def analyze_code(req: CodeAnalysisRequest):
    """Analyzes candidate DSA code solution for loopholes, edge-case vulnerabilities, Big-O bounds, and company standards."""
    res = analyze_code_loopholes(
        code=req.code,
        problem=req.problem,
        language=req.language,
        company=req.company,
        difficulty=req.difficulty,
        test_cases=req.test_cases
    )
    return CodeAnalysisResponse(
        loopholes=res["loopholes"],
        time_complexity=res["time_complexity"],
        space_complexity=res["space_complexity"],
        test_case_results=res["test_case_results"],
        company_verdict=res["company_verdict"],
        interviewer_probe=res["interviewer_probe"],
        status=res["status"],
        score=res["score"],
        provider_used="code_analyzer"
    )


# Code Execution & Compilation Sandbox
@app.post("/api/interview/run-code", response_model=RunCodeResponse)
async def run_code(req: RunCodeRequest):
    """Executes candidate's code in Python, JavaScript/Node.js, or statically checks compiled languages, returning real output, runtime ms, and test feedback."""
    res = execute_candidate_code(
        code=req.code,
        language=req.language,
        problem_title=req.problem or "",
        custom_input=req.custom_input,
        test_cases=req.test_cases
    )
    return RunCodeResponse(
        status=res["status"],
        stdout=res["stdout"],
        stderr=res["stderr"],
        execution_time_ms=res["execution_time_ms"],
        test_results=res.get("test_results", []),
        passed=res.get("passed", False)
    )


# All Supported Companies API for searchable dropdown
@app.get("/api/interview/companies")
async def list_companies():
    """Returns all available company interview profiles for searchable dropdown list."""
    from companies import COMPANY_PROFILES
    result = []
    from companies import COMPANY_PROFILES
    from company_online_fetcher import AUTHENTIC_COMPANY_POOLS
    result = []
    seen = set()
    for name, prof in COMPANY_PROFILES.items():
        seen.add(name.lower())
        result.append({
            "name": name,
            "tagline": prof.get("tagline", ""),
            "interviewer_title": prof.get("interviewer_title", ""),
            "question_counts": {diff: len(qs) for diff, qs in prof.get("questions", {}).items()}
        })
    for name, pools in AUTHENTIC_COMPANY_POOLS.items():
        if name.lower() not in seen:
            result.append({
                "name": name,
                "tagline": f"Authentic Interview Loops at {name}",
                "interviewer_title": f"{name} Senior Engineer",
                "question_counts": {diff: len(qs) for diff, qs in pools.items()}
            })
    return {"companies": result}


# Bulb Icon 💡 Action: Drop On-Demand Hint
@app.post("/api/interview/hint", response_model=HintResponse)
async def get_hint(req: HintRequest):
    """Provides an encouraging on-demand hint (💡) when clicked by candidate without spoiling solution."""
    api_key_to_use = req.api_key or GROQ_API_KEY
    active_provider = req.provider or "auto"

    if (active_provider in ("groq", "auto")) and api_key_to_use:
        try:
            system_prompt = "You are a friendly technical mentor. Return only JSON."
            user_msg = build_hint_prompt(req.topic, req.difficulty, req.question, req.hint_level)
            data = await call_groq_api(system_prompt, user_msg, api_key_to_use)
            return HintResponse(
                hint=data.get("hint", "Consider the optimal data structure or architectural principle for this problem."),
                hint_level=req.hint_level,
                category=data.get("category", "Intuition"),
                provider_used="groq"
            )
        except Exception as e:
            logger.warning(f"Groq hint failed, fallback to builtin: {e}")

    return get_builtin_hint(req.topic, req.difficulty, req.question, req.hint_level)


# Action 3: Generate the report
@app.post("/api/interview/report", response_model=ReportResponse)
async def generate_report(req: ReportRequest):
    """Action 3: Generate structured report with Score, Pass/Fail, Strengths, Weaknesses, Company Alignment, and DSA / Resume evaluation."""
    api_key_to_use = req.api_key or GROQ_API_KEY
    active_provider = req.provider or "auto"
    effective_topic = req.topic or "Resume Technical Evaluation"

    if (active_provider in ("groq", "auto")) and api_key_to_use:
        try:
            transcript = format_conversation(req.conversation)
            system_prompt = build_report_system_prompt(effective_topic, req.difficulty, req.resume_text)
            company_ctx = f" Target Company: {req.company}." if req.company else ""
            user_msg = f"Analyze the interview transcript below:{company_ctx}\n\n{transcript}\n\nGenerate the complete evaluation report in JSON format."
            data = await call_groq_api(system_prompt, user_msg, api_key_to_use)

            score = int(data.get("score", 70))
            score = max(0, min(100, score))
            rating_label = "Excellent" if score >= 85 else ("Good" if score >= 70 else ("Adequate" if score >= 55 else "Weak"))
            status_label = "Pass" if score >= 55 else "Fail"

            return ReportResponse(
                score=score,
                rating_label=rating_label,
                status=status_label,
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                topics_to_revise=data.get("topics_to_revise", []),
                overall_verdict=data.get("overall_verdict", "Candidate completed the interview."),
                company_alignment=data.get("company_alignment"),
                resume_alignment=data.get("resume_alignment"),
                dsa_complexity_analysis=data.get("dsa_complexity_analysis"),
                score_breakdown=data.get("score_breakdown"),
                provider_used="groq"
            )
        except Exception as e:
            logger.warning(f"Groq report failed, fallback to builtin: {e}")

    return run_builtin_report(
        effective_topic,
        req.difficulty,
        req.conversation,
        req.resume_text,
        req.hints_used or 0,
        company=req.company
    )
