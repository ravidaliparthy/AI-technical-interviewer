"use client";

import React, { useState, useEffect, useRef } from "react";

interface ChatMessage {
  role: "interviewer" | "candidate" | "assistant" | "user";
  content: string;
  is_follow_up?: boolean;
  code_snippet?: string;
  code_language?: string;
}

interface QuestionFeedback {
  question: string;
  assessment: string;
  detail: string;
}

interface EvaluationReport {
  score: number;
  rating_label: "Excellent" | "Good" | "Adequate" | "Weak";
  status: "Pass" | "Fail";
  strengths: string[];
  weaknesses: string[];
  topics_to_revise: string[];
  overall_verdict: string;
  company_alignment?: string | null;
  resume_alignment?: string | null;
  dsa_complexity_analysis?: string | null;
  score_breakdown?: Record<string, number>;
  detailed_feedback?: QuestionFeedback[];
  provider_used?: string;
}

interface QuestionHint {
  hint: string;
  hint_level: number;
  category: string;
}

interface TestCaseResult {
  test_case?: number;
  case?: string;
  input: string;
  expected: string;
  actual?: string;
  status?: string;
  passed?: boolean;
}

interface CodeAnalysisResult {
  loopholes: string[];
  time_complexity: string;
  space_complexity: string;
  test_case_results: TestCaseResult[];
  company_verdict: string;
  interviewer_probe: string;
  status: "Passed" | "Loopholes Found" | "Error";
  score: number;
  provider_used?: string;
}

interface CompanyOption {
  id: string;
  name: string;
  tagline: string;
  focus: string;
  icon: string;
  category: "FAANG / Big Tech" | "Fintech & Payments" | "Cloud & Infrastructure" | "AI & Systems" | "Consumer & Platforms";
  barScore: string;
  keywords: string[];
}

interface RealtimeHelperData {
  framework_name: string;
  framework_description: string;
  framework_steps: Array<{ step: string; detail: string }>;
  recommended_keywords: string[];
  detected_keywords: string[];
  missing_keywords: string[];
  critique: string;
  readiness_score: number;
  readiness_label: string;
  quick_tips: string[];
}

interface CodeRunResult {
  status: string;
  stdout: string;
  stderr: string;
  execution_time_ms: number;
  test_results: Array<{
    test_case?: number;
    input?: string;
    output?: string;
    expected?: string;
    error?: string;
    passed?: boolean;
  }>;
  passed: boolean;
}

const TARGET_COMPANIES: CompanyOption[] = [
  { id: "Google", name: "Google", tagline: "Big-O Rigor & Systems Scale", focus: "Optimal asymptotic bounds, graph algorithms, boundary edge cases", icon: "🌐", category: "FAANG / Big Tech", barScore: "Top 5% Complexity Bar", keywords: ["google", "alphabet", "scale", "search", "graphs"] },
  { id: "Amazon", name: "Amazon", tagline: "Leadership Principles & Scale", focus: "Customer obsession, high-throughput trade-offs, concurrency race conditions", icon: "📦", category: "FAANG / Big Tech", barScore: "LPs & Production Depth", keywords: ["amazon", "aws", "ecommerce", "cloud", "lp"] },
  { id: "Meta", name: "Meta", tagline: "Fast Single-Pass Execution", focus: "Strict O(N) linear-time passes, low auxiliary memory, speed and coding fluency", icon: "♾️", category: "FAANG / Big Tech", barScore: "Fast Single-Pass Bar", keywords: ["meta", "facebook", "instagram", "threads", "social"] },
  { id: "Microsoft", name: "Microsoft", tagline: "Clean Enterprise Architecture", focus: "Design patterns, modular maintainability, defensive validation and error handling", icon: "🪟", category: "FAANG / Big Tech", barScore: "Clean Code & Reliability", keywords: ["microsoft", "azure", "windows", "enterprise", "c#"] },
  { id: "Apple", name: "Apple", tagline: "Precision & Resource Efficiency", focus: "Hardware-software co-design, memory footprint, zero leaks, user empathy", icon: "🍎", category: "FAANG / Big Tech", barScore: "High Precision Standards", keywords: ["apple", "ios", "hardware", "swift", "memory"] },
  { id: "Netflix", name: "Netflix", tagline: "Resilience & Chaos Engineering", focus: "Fault tolerance, high-concurrency event streams, circuit breakers", icon: "🎬", category: "FAANG / Big Tech", barScore: "System Resilience Bar", keywords: ["netflix", "streaming", "microservices", "chaos", "resilience"] },
  { id: "Uber", name: "Uber", tagline: "Real-time Geospatial & Dispatch", focus: "Idempotent payment transactions, geospatial indices (H3), low-latency state", icon: "🚗", category: "Consumer & Platforms", barScore: "Real-time State Bar", keywords: ["uber", "dispatch", "h3", "geospatial", "mobility"] },
  { id: "Bloomberg", name: "Bloomberg", tagline: "Financial Real-Time Low Latency", focus: "Ticker stream processing, monotonic stacks, order book matching, O(1) operations", icon: "📈", category: "Fintech & Payments", barScore: "Low-Latency Rigor", keywords: ["bloomberg", "finance", "terminal", "ticker", "trading"] },
  { id: "ByteDance", name: "ByteDance / TikTok", tagline: "Extreme Concurrency & Dynamic Programming", focus: "Dynamic programming transitions, matrix traversals, high-throughput feed optimization", icon: "🎵", category: "Consumer & Platforms", barScore: "DP & Matrix Fluency", keywords: ["bytedance", "tiktok", "feeds", "dp", "concurrency"] },
  { id: "Stripe", name: "Stripe", tagline: "Financial Correctness & Idempotency", focus: "Defensive decimal handling, distributed rate limiters, idempotency keys, state machines", icon: "💳", category: "Fintech & Payments", barScore: "Financial Accuracy Bar", keywords: ["stripe", "payments", "api", "idempotency", "fintech"] },
  { id: "Airbnb", name: "Airbnb", tagline: "Geospatial Indexing & Clean Architecture", focus: "Interval scheduling, calendar availability, in-memory file systems, clean OOP", icon: "🏠", category: "Consumer & Platforms", barScore: "Clean OOP Design Bar", keywords: ["airbnb", "booking", "travel", "calendar", "intervals"] },
  { id: "LinkedIn", name: "LinkedIn", tagline: "Social Graph Traversal & Caching", focus: "Graph distance (degrees of separation), multi-level caching, inverse depth traversal", icon: "💼", category: "Consumer & Platforms", barScore: "Distributed Graph Bar", keywords: ["linkedin", "social", "graph", "caching", "networking"] },
  { id: "Salesforce", name: "Salesforce", tagline: "Enterprise Multitenancy & Expression Parsers", focus: "Clean arithmetic expression evaluators, LRU/LFU caching, relational trees", icon: "☁️", category: "Cloud & Infrastructure", barScore: "Enterprise Scale Bar", keywords: ["salesforce", "crm", "multitenancy", "parser", "enterprise"] },
  { id: "Adobe", name: "Adobe", tagline: "2D Matrix Transforms & Binary Search", focus: "Matrix rotation/spiral boundaries, rotated binary search, string transformations", icon: "🎨", category: "Consumer & Platforms", barScore: "Matrix & Math Bar", keywords: ["adobe", "photoshop", "matrix", "graphics", "search"] },
  { id: "Goldman Sachs", name: "Goldman Sachs", tagline: "Financial Mathematics & Numerics", focus: "Recurring fraction loops, Kadane's algorithm, transaction debt settlement", icon: "🏛️", category: "Fintech & Payments", barScore: "Quantitative Math Bar", keywords: ["goldman", "gs", "finance", "banking", "quant"] },
  { id: "Palantir", name: "Palantir", tagline: "Knowledge Graphs & Pathfinding", focus: "Complex ontology modeling, 3-color cycle detection, multi-source BFS pathfinding", icon: "🛡️", category: "AI & Systems", barScore: "Graph Ontology Bar", keywords: ["palantir", "foundry", "gotham", "defense", "graphs"] },
  { id: "Nvidia", name: "Nvidia", tagline: "Hardware-Accelerated Kernels & Sparse Vectors", focus: "CUDA parallel reduction, sparse dot products, 2D prefix sums, memory alignment", icon: "⚡", category: "AI & Systems", barScore: "Hardware Optimization Bar", keywords: ["nvidia", "cuda", "gpu", "sparse", "parallel"] },
  { id: "Databricks", name: "Databricks", tagline: "Distributed Big Data & Versioned Storage", focus: "Segment trees, snapshot deltas, multithreaded web crawlers, lock-free structures", icon: "🧱", category: "Cloud & Infrastructure", barScore: "Distributed Storage Bar", keywords: ["databricks", "spark", "lakehouse", "data", "storage"] },
  { id: "Cisco", name: "Cisco", tagline: "Networking Protocols & IP Routing Tries", focus: "IP longest prefix match, network packet buffering, bipartite graphs, Dijkstra", icon: "📡", category: "Cloud & Infrastructure", barScore: "Networking Systems Bar", keywords: ["cisco", "networking", "routing", "trie", "protocols"] },
  { id: "Atlassian", name: "Atlassian", tagline: "Collaborative Engines & CRDTs", focus: "Meeting intervals, team voting ranking, Snake game simulation, rate limits", icon: "🔷", category: "Cloud & Infrastructure", barScore: "Collaborative Engine Bar", keywords: ["atlassian", "jira", "confluence", "crdt", "voting"] },
  { id: "Spotify", name: "Spotify", tagline: "Music Streaming & Top-K Aggregators", focus: "Fisher-Yates modern shuffle, Top-K frequent elements, streaming medians with two heaps", icon: "🎧", category: "Consumer & Platforms", barScore: "Audio Recommender Bar", keywords: ["spotify", "music", "streaming", "shuffle", "top-k"] },
  { id: "Snowflake", name: "Snowflake", tagline: "Columnar Warehousing & Micro-Partitions", focus: "K-way external merge sort, bitmask indexing, 2D immutable range aggregations", icon: "❄️", category: "Cloud & Infrastructure", barScore: "Columnar Database Bar", keywords: ["snowflake", "warehouse", "sql", "columnar", "sorting"] },
  { id: "DoorDash", name: "DoorDash", tagline: "Logistics Dispatch & Route Optimization", focus: "Courier multi-source BFS, dynamic job scheduling DP, route bundling approximations", icon: "🍔", category: "Consumer & Platforms", barScore: "Logistics Routing Bar", keywords: ["doordash", "delivery", "logistics", "routing", "scheduling"] },
  { id: "Twitter / X", name: "Twitter / X", tagline: "Social Fanout Pipelines & O(1) Samplers", focus: "Timeline generation fanout, RandomizedSet O(1), interval bucket aggregations", icon: "🐦", category: "Consumer & Platforms", barScore: "High Fanout Bar", keywords: ["twitter", "x", "social", "timeline", "randomized"] },
  { id: "OpenAI", name: "OpenAI", tagline: "Frontier AI & Distributed Model Serving", focus: "KV-cache management, high-throughput transformer inference, distributed lock managers", icon: "🧠", category: "AI & Systems", barScore: "Frontier AI Systems Bar", keywords: ["openai", "chatgpt", "transformer", "llm", "kv-cache", "gpu"] },
];

const PRESET_TOPICS = [
  "Data Structures & Algorithms",
  "Python",
  "System Design",
  "Machine Learning",
  "React & Frontend",
  "SQL & Databases",
];

// Clean starter templates without pre-solved answers
const STARTER_CODE: Record<string, string> = {
  python: `def solve(nums, target):\n    # Write your solution here\n    # Optimal Bounds Target: Time: O(?), Auxiliary Space: O(?)\n    pass\n`,
  javascript: `function solve(nums, target) {\n    // Write your solution here\n    // Optimal Bounds Target: Time: O(?), Auxiliary Space: O(?)\n}\n`,
  typescript: `function solve(nums: number[], target: number): number[] {\n    // Write your solution here\n    // Optimal Bounds Target: Time: O(?), Auxiliary Space: O(?)\n    return [];\n}\n`,
  cpp: `#include <vector>\n#include <iostream>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> solve(vector<int>& nums, int target) {\n        // Write your solution here\n        // Optimal Bounds Target: Time: O(?), Auxiliary Space: O(?)\n        return {};\n    }\n};\n`,
  java: `import java.util.*;\n\nclass Solution {\n    public int[] solve(int[] nums, int target) {\n        // Write your solution here\n        // Optimal Bounds Target: Time: O(?), Auxiliary Space: O(?)\n        return new int[]{};\n    }\n}\n`,
  go: `package main\n\nfunc solve(nums []int, target int) []int {\n    // Write your solution here\n    // Optimal Bounds Target: Time: O(?), Auxiliary Space: O(?)\n    return nil\n}\n`,
  rust: `pub fn solve(nums: Vec<i32>, target: i32) -> Vec<i32> {\n    // Write your solution here\n    // Optimal Bounds Target: Time: O(?), Auxiliary Space: O(?)\n    vec![]\n}\n`,
};

interface LeetCodeLang {
  id: string;
  label: string;
  badge: string;
  color: string;
}

const LEETCODE_LANGUAGES: LeetCodeLang[] = [
  { id: "python", label: "Python 3", badge: "Py", color: "text-amber-400 bg-amber-500/10 border-amber-500/30" },
  { id: "javascript", label: "JavaScript (Node.js)", badge: "JS", color: "text-yellow-400 bg-yellow-500/10 border-yellow-500/30" },
  { id: "typescript", label: "TypeScript 5.x", badge: "TS", color: "text-blue-400 bg-blue-500/10 border-blue-500/30" },
  { id: "cpp", label: "C++ 20", badge: "C++", color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30" },
  { id: "java", label: "Java 21", badge: "Java", color: "text-orange-400 bg-orange-500/10 border-orange-500/30" },
  { id: "go", label: "Go 1.22", badge: "Go", color: "text-sky-400 bg-sky-500/10 border-sky-500/30" },
  { id: "rust", label: "Rust 1.76", badge: "Rust", color: "text-rose-400 bg-rose-500/10 border-rose-500/30" },
];

const BACKEND_BASE = process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000";

export default function Home() {
  // Navigation Screens: "start" | "interview" | "report"
  const [screen, setScreen] = useState<"start" | "interview" | "report">("start");

  // Track Selector: "dsa" (DSA IDE & Execution) | "resume" (Resume Deep-Dive) | "conceptual" (System Design & Concepts)
  const [interviewTrack, setInterviewTrack] = useState<"dsa" | "resume" | "conceptual">("dsa");

  // Start Screen State
  const [topic, setTopic] = useState("");
  const [difficulty, setDifficulty] = useState<"Easy" | "Medium" | "Hard">("Medium");
  const [totalQuestions, setTotalQuestions] = useState<number>(5);
  const [selectedCompany, setSelectedCompany] = useState<string>("");
  const [companySearchQuery, setCompanySearchQuery] = useState("");
  const [companyCategoryFilter, setCompanyCategoryFilter] = useState<string>("All");
  const [isCompanyDropdownOpen, setIsCompanyDropdownOpen] = useState(false);
  const [startError, setStartError] = useState<string | null>(null);
  const [isStarting, setIsStarting] = useState(false);

  // Resume PDF State
  const [resumeText, setResumeText] = useState<string | null>(null);
  const [resumeFileName, setResumeFileName] = useState<string | null>(null);
  const [resumeHighlights, setResumeHighlights] = useState<{ projects: string[]; experience: string[]; skills: string[] } | null>(null);
  const [isUploadingResume, setIsUploadingResume] = useState(false);
  const [resumeUploadError, setResumeUploadError] = useState<string | null>(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Interview Screen State
  const [conversation, setConversation] = useState<ChatMessage[]>([]);
  const [candidateInput, setCandidateInput] = useState("");
  const [isAiThinking, setIsAiThinking] = useState(false);
  const [questionCount, setQuestionCount] = useState(1);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [voiceEnabled, setVoiceEnabled] = useState(true); // Voice ON by default from question #1!
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [lastIsFollowUp, setLastIsFollowUp] = useState(false);

  // Split Sizer Layout: "balanced" (50/50) | "code" (35/65) | "chat" (65/35)
  const [splitRatio, setSplitRatio] = useState<"balanced" | "code" | "chat">("balanced");

  // DSA Coding Editor & Loophole Finder State
  const [showCodeEditor, setShowCodeEditor] = useState(false);
  const [codeLanguage, setCodeLanguage] = useState("python");
  const [codeSnippet, setCodeSnippet] = useState(STARTER_CODE["python"]);
  const [isAnalyzingCode, setIsAnalyzingCode] = useState(false);
  const [codeAnalysisResult, setCodeAnalysisResult] = useState<CodeAnalysisResult | null>(null);
  const [activeCodeTab, setActiveCodeTab] = useState<"problem" | "editor" | "output" | "loopholes">("editor");

  // Dynamic Problem, Placeholder & LeetCode UI State
  const [starterSnippets, setStarterSnippets] = useState<Record<string, string> | null>(null);
  const [currentProblemTitle, setCurrentProblemTitle] = useState<string | null>(null);
  const [dynamicPlaceholder, setDynamicPlaceholder] = useState<string | null>(null);
  const [dynamicQuickChips, setDynamicQuickChips] = useState<string[] | null>(null);
  const [isLanguageDropdownOpen, setIsLanguageDropdownOpen] = useState(false);
  const [mobileActiveTab, setMobileActiveTab] = useState<"chat" | "code">("chat");

  // Real Code Execution / Compilation State
  const [codeRunResult, setCodeRunResult] = useState<CodeRunResult | null>(null);
  const [isRunningCode, setIsRunningCode] = useState(false);
  const [customInput, setCustomInput] = useState("");
  const [activeTestCases, setActiveTestCases] = useState<any[]>([]);
  const [activeProblemText, setActiveProblemText] = useState<string>("");

  // Hints state keyed by message index
  const [hintsMap, setHintsMap] = useState<Record<number, QuestionHint>>({});
  const [hintLoadingIdx, setHintLoadingIdx] = useState<number | null>(null);
  const [totalHintsUsed, setTotalHintsUsed] = useState(0);

  // Report Screen State
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [isReportLoading, setIsReportLoading] = useState(false);
  const [reportError, setReportError] = useState<string | null>(null);
  const [showTranscript, setShowTranscript] = useState(false);
  const [copiedReport, setCopiedReport] = useState(false);

  // Settings / Provider state
  const [showSettings, setShowSettings] = useState(false);
  const [provider, setProvider] = useState<"auto" | "groq" | "builtin">("groq");
  const [apiKey, setApiKey] = useState("");
  const [serverOnline, setServerOnline] = useState<boolean | null>(null);

  const chatEndRef = useRef<HTMLDivElement>(null);
  const timerRef = useRef<NodeJS.Timeout | null>(null);

  // Realtime Helper & Live Co-Pilot State
  const [showRealtimeHelper, setShowRealtimeHelper] = useState(true);
  const [helperData, setHelperData] = useState<RealtimeHelperData | null>(null);
  const [isCritiquing, setIsCritiquing] = useState(false);
  const [showCritiqueBox, setShowCritiqueBox] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);

  // Helpers: Topic domain classification
  const topicLower = (topic || "").toLowerCase();
  const isMl = Boolean(
    topic &&
      (topicLower.includes("machine learning") ||
        topicLower.includes("deep learning") ||
        topicLower.includes("neural") ||
        topicLower.includes("data science") ||
        topicLower.includes("nlp") ||
        topicLower.includes("computer vision") ||
        topicLower.includes("llm") ||
        topicLower.includes("artificial intelligence") ||
        topicLower.split(/\s+/).includes("ml") ||
        topicLower.split(/\s+/).includes("ai"))
  );

  const isDsa = Boolean(
    interviewTrack === "dsa" ||
    (!isMl && interviewTrack !== "resume" && interviewTrack !== "conceptual" && topic &&
      (topicLower.includes("dsa") ||
        topicLower.includes("leetcode") ||
        topicLower.includes("data structure") ||
        topicLower.split(/\s+/).includes("algo") ||
        topicLower.split(/\s+/).includes("algorithms") ||
        topicLower.split(/\s+/).includes("algorithm")))
  );

  // Check backend health on mount
  useEffect(() => {
    const checkServer = async () => {
      try {
        const res = await fetch(`${BACKEND_BASE}/api/health`);
        setServerOnline(res.ok);
      } catch {
        setServerOnline(false);
      }
    };
    checkServer();
    const interval = setInterval(checkServer, 15000);
    return () => clearInterval(interval);
  }, []);

  // Load preferences from localStorage
  useEffect(() => {
    const savedKey = localStorage.getItem("ai_interview_api_key");
    const savedProv = localStorage.getItem("ai_interview_provider") as any;
    if (savedKey) setApiKey(savedKey);
    if (savedProv) setProvider(savedProv);
  }, []);

  // Session elapsed timer during interview
  useEffect(() => {
    if (screen === "interview") {
      setElapsedSeconds(0);
      timerRef.current = setInterval(() => {
        setElapsedSeconds((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [screen]);

  // Auto-scroll chat on new messages
  useEffect(() => {
    if (screen === "interview") {
      chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [conversation, isAiThinking, hintsMap, screen, showCodeEditor]);

  // Voice synthesis helpers & controls
  const stopVoice = () => {
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    setIsSpeaking(false);
  };

  const toggleVoice = () => {
    setVoiceEnabled((prev) => {
      const next = !prev;
      if (!next) {
        stopVoice();
      }
      return next;
    });
  };

  // Ensure any audio is immediately stopped when voice is muted
  useEffect(() => {
    if (!voiceEnabled) {
      stopVoice();
    }
  }, [voiceEnabled]);

  // Clean up audio on unmount or tab closing
  useEffect(() => {
    return () => {
      stopVoice();
    };
  }, []);

  const speakInterviewer = (text: string) => {
    if (!voiceEnabled || typeof window === "undefined" || !("speechSynthesis" in window)) return;
    try {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);

      const clean = text
        .replace(/[*_#`$]/g, "")
        .replace(/###.*?\n/g, "")
        .replace(/```[\s\S]*?```/g, "Code block omitted.")
        .replace(/\n+/g, " ")
        .slice(0, 350);

      const utterance = new SpeechSynthesisUtterance(clean);
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      const voices = window.speechSynthesis.getVoices();
      const englishVoice = voices.find((v) => v.lang.startsWith("en"));
      if (englishVoice) utterance.voice = englishVoice;

      utterance.onstart = () => {
        if (!voiceEnabled) {
          window.speechSynthesis.cancel();
          setIsSpeaking(false);
          return;
        }
        setIsSpeaking(true);
      };
      utterance.onend = () => {
        setIsSpeaking(false);
      };
      utterance.onerror = () => {
        setIsSpeaking(false);
      };

      window.speechSynthesis.speak(utterance);
    } catch (err) {
      console.warn("Speech synthesis error:", err);
      setIsSpeaking(false);
    }
  };

  const formatTimer = (totalSec: number) => {
    const mins = Math.floor(totalSec / 60);
    const secs = totalSec % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Switch starter code when language changes (LeetCode behavior)
  const handleLanguageChange = (lang: string) => {
    setCodeLanguage(lang);
    setIsLanguageDropdownOpen(false);
    if (starterSnippets && starterSnippets[lang]) {
      setCodeSnippet(starterSnippets[lang]);
    } else if (STARTER_CODE[lang]) {
      setCodeSnippet(STARTER_CODE[lang]);
    }
  };

  // ================= PDF RESUME UPLOAD =================
  const handleResumeFile = async (file: File) => {
    setResumeUploadError(null);
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setResumeUploadError("Please upload a PDF document (.pdf).");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setResumeUploadError("File size exceeds 10MB limit.");
      return;
    }

    setIsUploadingResume(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/upload-resume`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        throw new Error(errJson?.message || `Upload failed with status ${res.status}`);
      }

      const data = await res.json();
      setResumeText(data.resume_text);
      setResumeFileName(file.name);
      if (data.highlights) setResumeHighlights(data.highlights);
      if (!topic.trim()) setTopic("Resume Technical Evaluation");
    } catch (err: any) {
      setResumeUploadError(err.message || "Failed to process PDF resume.");
      setResumeText(null);
      setResumeFileName(null);
      setResumeHighlights(null);
    } finally {
      setIsUploadingResume(false);
    }
  };

  // ================= ACTION 1: START INTERVIEW =================
  const handleStartInterview = async () => {
    setStartError(null);
    const trimmedTopic = topic.trim();

    if (!trimmedTopic && !resumeText && !selectedCompany) {
      setStartError("Please specify a topic, select a target company, or upload your resume.");
      return;
    }

    const effectiveTopic = trimmedTopic || (selectedCompany ? `${selectedCompany} Technical Interview` : "Resume Technical Evaluation");
    setIsStarting(true);
    setHintsMap({});
    setTotalHintsUsed(0);
    setLastIsFollowUp(false);
    setCodeAnalysisResult(null);
    setCodeRunResult(null);
    setStarterSnippets(null);
    setCurrentProblemTitle(null);
    setDynamicPlaceholder(null);
    setDynamicQuickChips(null);
    setActiveTestCases([]);
    setActiveProblemText("");
    setMobileActiveTab("chat");

    // Preliminary editor visibility check (refined dynamically by backend response)
    const shouldShowEditor = interviewTrack === "dsa" || (isDsa && interviewTrack !== "resume" && interviewTrack !== "conceptual");
    setShowCodeEditor(shouldShowEditor);

    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/start`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: effectiveTopic,
          difficulty,
          total_questions: totalQuestions,
          company: selectedCompany || null,
          resume_text: resumeText || null,
          provider,
          api_key: apiKey || null,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        throw new Error(
          errJson?.message ||
            errJson?.detail?.[0]?.msg ||
            `Server returned error (${res.status}). Ensure backend is running.`
        );
      }

      const data = await res.json();
      setConversation([{ role: "interviewer", content: data.message, is_follow_up: false }]);
      setQuestionCount(1);
      setScreen("interview");

      // Initialize Realtime Helper guidance for question #1
      handleFetchRealtimeHelper(data.message, "");

      // Auto-adapt Code Editor visibility: Hide for non-DSA / conceptual, show for coding problems
      const isCoding = Boolean(data.is_coding_problem) || (Boolean(data.message) && (data.message.includes("### Problem:") || data.message.includes("Input:")));
      setShowCodeEditor(isCoding);

      if (isCoding) {
        if (data.test_cases && data.test_cases.length > 0) {
          setActiveTestCases(data.test_cases);
        }
        setActiveProblemText(data.problem_text || data.message);
      }

      // Populate dynamic templates and parameters tailored to the specific question
      if (data.starter_snippets) {
        setStarterSnippets(data.starter_snippets);
        if (data.starter_snippets[codeLanguage]) {
          setCodeSnippet(data.starter_snippets[codeLanguage]);
        }
      }
      if (data.placeholder) setDynamicPlaceholder(data.placeholder);
      if (data.quick_chips) setDynamicQuickChips(data.quick_chips);
      if (data.problem_title) setCurrentProblemTitle(data.problem_title);

      // Auto-speak question #1 immediately upon screen transition!
      speakInterviewer(data.message);
    } catch (err: any) {
      setStartError(err.message || "Failed to connect to backend server. Make sure port 8000 is running.");
    } finally {
      setIsStarting(false);
    }
  };

  // ================= CODE COMPILER & RUNNER SANDBOX ▶ =================
  const handleRunCode = async () => {
    if (isRunningCode) return;
    setActiveCodeTab("output");

    if (!codeSnippet.trim()) {
      setCodeRunResult({
        status: "No Code",
        stdout: "",
        stderr: "Error: Code editor is empty. Please type your function implementation before running test cases.",
        execution_time_ms: 0,
        test_results: [
          {
            test_case: 1,
            input: "Empty Editor",
            output: "None",
            expected: "Valid Function Implementation",
            passed: false,
            error: "No code provided. Please write your algorithm solution.",
          },
        ],
        passed: false,
      });
      return;
    }

    setIsRunningCode(true);
    let effectiveProblem = activeProblemText;
    if (!effectiveProblem || (!effectiveProblem.includes("Input:") && !effectiveProblem.includes("Test Cases"))) {
      const probMsg = conversation
        .slice()
        .reverse()
        .find((m) => m.role === "interviewer" && (m.content.includes("Input:") || m.content.includes("Problem:")));
      effectiveProblem = probMsg ? probMsg.content : (effectiveProblem || currentProblemTitle || topic);
    }

    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/run-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: codeSnippet,
          language: codeLanguage,
          problem: effectiveProblem,
          custom_input: customInput.trim() || null,
          test_cases: activeTestCases && activeTestCases.length > 0 ? activeTestCases : undefined,
        }),
      });

      if (!res.ok) throw new Error("Code execution failed on server");
      const data: CodeRunResult = await res.json();
      setCodeRunResult(data);
    } catch (err: any) {
      console.error(err);
      setCodeRunResult({
        status: "Error",
        stdout: "",
        stderr: err.message || "Failed to execute code in sandbox. Ensure backend is running.",
        execution_time_ms: 0,
        test_results: [],
        passed: false,
      });
    } finally {
      setIsRunningCode(false);
    }
  };

  // ================= CODE ANALYZER & LOOPHOLE FINDER 🔍 =================
  const handleAnalyzeCodeLoopholes = async () => {
    if (isAnalyzingCode) return;
    setActiveCodeTab("loopholes");

    if (!codeSnippet.trim()) {
      setCodeAnalysisResult({
        loopholes: ["Editor is empty: Please write your function code before scanning for algorithmic loopholes."],
        time_complexity: "N/A",
        space_complexity: "N/A",
        test_case_results: [],
        company_verdict: "No Code to Analyze",
        interviewer_probe: "Please write your solution in the editor first.",
        status: "Error",
        score: 0,
      });
      return;
    }

    setIsAnalyzingCode(true);

    let effectiveProblem = activeProblemText;
    if (!effectiveProblem) {
      const probMsg = conversation
        .slice()
        .reverse()
        .find((m) => m.role === "interviewer" && (m.content.includes("Input:") || m.content.includes("Problem:")));
      effectiveProblem = probMsg ? probMsg.content : (currentProblemTitle || topic);
    }

    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/analyze-code`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          code: codeSnippet,
          problem: effectiveProblem,
          language: codeLanguage,
          company: selectedCompany || null,
          difficulty,
          provider,
          api_key: apiKey || null,
        }),
      });

      if (!res.ok) throw new Error("Code loophole analysis failed");
      const data: CodeAnalysisResult = await res.json();
      setCodeAnalysisResult(data);
    } catch (err) {
      console.error(err);
      setCodeAnalysisResult({
        loopholes: ["Could not connect to code analyzer service. Ensure backend is running."],
        time_complexity: "O(?)",
        space_complexity: "O(?)",
        test_case_results: [],
        company_verdict: "Manual analysis recommended.",
        interviewer_probe: "Please explain your asymptotic complexity and boundary edge cases.",
        status: "Error",
        score: 50,
      });
    } finally {
      setIsAnalyzingCode(false);
    }
  };

  // ================= REAL-TIME HELPER & LIVE CO-PILOT =================
  const handleFetchRealtimeHelper = async (currentQ?: string, draft?: string) => {
    const qText = currentQ || conversation.filter((m) => m.role === "interviewer").slice(-1)[0]?.content || "";
    if (!qText) return;
    setIsCritiquing(true);
    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/realtime-helper`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          current_question: qText,
          draft_answer: draft !== undefined ? draft : candidateInput,
          topic: topic.trim() || (selectedCompany ? `${selectedCompany} Technical Interview` : "Technical Interview"),
          difficulty,
          company: selectedCompany || null,
          problem_title: currentProblemTitle || null,
        }),
      });
      if (res.ok) {
        const data: RealtimeHelperData = await res.json();
        setHelperData(data);
      }
    } catch (e) {
      console.warn("Helper fetch failed:", e);
    } finally {
      setIsCritiquing(false);
    }
  };

  const handleSkipQuestion = async () => {
    if (isAiThinking) return;
    await handleSubmitAnswer(undefined, true);
  };

  const toggleSpeechRecognition = () => {
    if (typeof window === "undefined") return;
    const SpeechRecognitionClass = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (!SpeechRecognitionClass) {
      alert("Speech recognition is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Safari.");
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        try { recognitionRef.current.stop(); } catch {}
      }
      setIsListening(false);
      return;
    }

    try {
      const recognition = new SpeechRecognitionClass();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onresult = (event: any) => {
        let finalChunk = "";
        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalChunk += event.results[i][0].transcript + " ";
          }
        }
        if (finalChunk.trim()) {
          setCandidateInput((prev) => (prev ? `${prev} ${finalChunk.trim()}` : finalChunk.trim()));
        }
      };

      recognition.onerror = (event: any) => {
        console.warn("Speech recognition notice:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err) {
      console.warn("Speech recognition start failed:", err);
      setIsListening(false);
    }
  };

  const detectedKeywordsInDraft = (helperData?.recommended_keywords || []).filter((kw) => {
    const clean = kw.toLowerCase().replace(/[/\\-]/g, " ");
    const parts = clean.split(/\s+/).filter((w) => w.length > 2);
    const inputLower = (candidateInput || "").toLowerCase();
    return parts.some((p) => inputLower.includes(p));
  });

  // ================= ACTION 2: SUBMIT ANSWER =================
  const handleSubmitAnswer = async (submittedCodeSnippet?: string, forceAdvance: boolean = false) => {
    if ((!candidateInput.trim() && !submittedCodeSnippet && !forceAdvance) || isAiThinking) return;

    // Stop active speech recognition if listening
    if (isListening && recognitionRef.current) {
      try { recognitionRef.current.stop(); } catch {}
      setIsListening(false);
    }

    const answerText = forceAdvance
      ? "Skip to the next question."
      : candidateInput.trim() || (submittedCodeSnippet ? "I have written my code solution in the editor with asymptotic bounds." : "");

    const updatedConversation: ChatMessage[] = [
      ...conversation,
      {
        role: "candidate",
        content: answerText,
        // Only attach code snippet when user explicitly clicked "Submit with Code"
        code_snippet: submittedCodeSnippet || undefined,
        code_language: submittedCodeSnippet ? codeLanguage : undefined,
      },
    ];

    setConversation(updatedConversation);
    setCandidateInput("");
    setShowCritiqueBox(false);
    setIsAiThinking(true);

    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/answer`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim() || (selectedCompany ? `${selectedCompany} Technical Interview` : "Technical Interview"),
          difficulty,
          total_questions: totalQuestions,
          company: selectedCompany || null,
          conversation: updatedConversation,
          resume_text: resumeText || null,
          code_snippet: submittedCodeSnippet || null,
          code_language: submittedCodeSnippet ? codeLanguage : null,
          hints_used: totalHintsUsed,
          provider,
          api_key: apiKey || null,
          force_advance: forceAdvance,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        throw new Error(errJson?.message || `Error status ${res.status}`);
      }

      const data = await res.json();
      const isFollowUp = Boolean(data.is_follow_up);
      setLastIsFollowUp(isFollowUp);

      const nextConversation: ChatMessage[] = [
        ...updatedConversation,
        { role: "interviewer", content: data.message, is_follow_up: isFollowUp },
      ];
      setConversation(nextConversation);
      setQuestionCount(data.question_number || questionCount);
      speakInterviewer(data.message);

      // Refresh Realtime Helper for the new question
      handleFetchRealtimeHelper(data.message, "");

      // Dynamically adapt editor visibility and question parameters
      const isCodingFollowup = Boolean(data.is_coding_problem) || (Boolean(data.message) && (data.message.includes("### Problem:") || data.message.includes("Input:")));
      if (data.is_coding_problem !== undefined || isCodingFollowup) {
        setShowCodeEditor(isCodingFollowup);
      }
      if (isCodingFollowup) {
        if (data.test_cases && data.test_cases.length > 0) {
          setActiveTestCases(data.test_cases);
        }
        setActiveProblemText(data.problem_text || data.message);
      }
      if (data.starter_snippets) {
        setStarterSnippets(data.starter_snippets);
        if (data.starter_snippets[codeLanguage]) {
          setCodeSnippet(data.starter_snippets[codeLanguage]);
        }
      }
      if (data.placeholder) setDynamicPlaceholder(data.placeholder);
      if (data.quick_chips) setDynamicQuickChips(data.quick_chips);
      if (data.problem_title) setCurrentProblemTitle(data.problem_title);

      if (data.is_ended) {
        setTimeout(() => {
          handleGenerateReport(nextConversation);
        }, 1200);
      }
    } catch (err: any) {
      const fallbackMsg = isMl
        ? "Thank you. Let's delve into our next focus area: How do you handle validation strategy, data drift, or model evaluation under realistic distribution shifts?"
        : isDsa
        ? "Thank you. Let's move to our next problem: What is your approach for handling boundary edge cases and optimizing asymptotic complexity?"
        : "Thank you. Let's delve into our next focus area: How do you handle error states, latency, or concurrency under realistic user load?";
      setConversation([
        ...updatedConversation,
        { role: "interviewer", content: fallbackMsg, is_follow_up: false },
      ]);
    } finally {
      setIsAiThinking(false);
    }
  };

  // ================= ON-DEMAND HINT (BULB ICON 💡) =================
  const handleFetchHint = async (msgIdx: number, questionText: string) => {
    const existing = hintsMap[msgIdx];
    const nextLevel = existing ? Math.min(3, existing.hint_level + 1) : 1;

    setHintLoadingIdx(msgIdx);
    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/hint`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim() || (selectedCompany ? `${selectedCompany} Technical Interview` : "Technical Interview"),
          difficulty,
          question: questionText,
          company: selectedCompany || null,
          conversation,
          hint_level: nextLevel,
          provider,
          api_key: apiKey || null,
        }),
      });

      if (!res.ok) throw new Error("Could not retrieve hint");
      const data: QuestionHint = await res.json();
      setHintsMap((prev) => ({
        ...prev,
        [msgIdx]: data,
      }));
      setTotalHintsUsed((prev) => prev + 1);
    } catch (e) {
      setHintsMap((prev) => ({
        ...prev,
        [msgIdx]: {
          hint: isMl
            ? "Focus on the ML modeling objective: consider bias-variance tradeoff, regularization (L1/L2), validation strategy, and avoiding data leakage."
            : isDsa
            ? "Focus on the algorithmic pattern: identify boundary edge cases and choose the most suitable data structure or Big-O bound."
            : "Focus on the core design principles: identify data flow, failure modes, and choose the most suitable architectural pattern.",
          hint_level: 1,
          category: isMl ? "Model Formulation" : isDsa ? "Algorithmic Pattern" : "System Direction",
        },
      }));
    } finally {
      setHintLoadingIdx(null);
    }
  };

  // ================= ACTION 3: GENERATE REPORT =================
  const handleGenerateReport = async (historyToEvaluate?: ChatMessage[]) => {
    const convoToUse = historyToEvaluate || conversation;
    setIsReportLoading(true);
    setReportError(null);
    setScreen("report");

    try {
      const res = await fetch(`${BACKEND_BASE}/api/interview/report`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          topic: topic.trim() || (selectedCompany ? `${selectedCompany} Technical Interview` : "Technical Interview"),
          difficulty,
          total_questions: totalQuestions,
          company: selectedCompany || null,
          conversation: convoToUse,
          resume_text: resumeText || null,
          hints_used: totalHintsUsed,
          provider,
          api_key: apiKey || null,
        }),
      });

      if (!res.ok) {
        const errJson = await res.json().catch(() => null);
        throw new Error(errJson?.message || `Failed to generate report (${res.status})`);
      }

      const data: EvaluationReport = await res.json();
      setReport(data);
    } catch (err: any) {
      setReportError(err.message || "Failed to generate evaluation report from server.");
    } finally {
      setIsReportLoading(false);
    }
  };

  const handleStartNewInterview = () => {
    setScreen("start");
    setConversation([]);
    setCandidateInput("");
    setHintsMap({});
    setTotalHintsUsed(0);
    setReport(null);
    setReportError(null);
    setStartError(null);
    setShowTranscript(false);
    setCodeAnalysisResult(null);
    setCodeRunResult(null);
  };

  const copyReportToClipboard = () => {
    if (!report) return;
    const text = `AI Technical Interview Report: ${topic || "Technical Assessment"}${selectedCompany ? ` [${selectedCompany}]` : ""} (${difficulty})
Score: ${report.score}/100 | Verdict: ${report.status} (${report.rating_label})

Overall Verdict:
${report.overall_verdict}

${report.company_alignment ? `Target Company Assessment:\n${report.company_alignment}\n\n` : ""}${report.dsa_complexity_analysis ? `DSA & Complexity:\n${report.dsa_complexity_analysis}\n\n` : ""}${report.resume_alignment ? `Resume Alignment:\n${report.resume_alignment}\n\n` : ""}Strengths:
${report.strengths.map((s) => `• ${s}`).join("\n")}

Areas for Improvement:
${report.weaknesses.map((w) => `• ${w}`).join("\n")}

Topics to Revise:
${report.topics_to_revise.map((t) => `• ${t}`).join("\n")}`;

    navigator.clipboard.writeText(text);
    setCopiedReport(true);
    setTimeout(() => setCopiedReport(false), 2500);
  };

  // Context-aware dynamic placeholder
  const currentPlaceholder = isAiThinking
    ? "Interviewer is evaluating your response..."
    : lastIsFollowUp
    ? "Interviewer is probing deeper: clarify your edge cases, underlying mechanics, or trade-offs..."
    : dynamicPlaceholder || (
        topicLower.includes("python")
          ? "Explain your design, Pythonic idioms, decorator mechanics, or trade-offs..."
          : isMl
          ? "Explain model formulation, loss formulation, validation strategy, or trade-offs..."
          : topicLower.includes("system design")
          ? "Explain high-level architecture, data models, scalability bottlenecks, and trade-offs..."
          : isDsa || showCodeEditor
          ? "State your approach, Big-O Time & Space complexity, and write your solution in the editor..."
          : "Type your structured answer and reasoning. Press Enter to submit."
      );

  // Context-aware dynamic quick chips
  const currentQuickChips = dynamicQuickChips || (
    isDsa || showCodeEditor
      ? ["+ O(N) / O(1)", "+ O(N log N) / O(N)", "+ O(log N) / O(1)", "+ O(V + E) / O(V)", "+ Two Pointers", "+ Hash Map"]
      : topicLower.includes("python")
      ? ["+ functools.wraps", "+ *args, **kwargs", "+ time.perf_counter()", "+ Generator / Yield", "+ Context Manager"]
      : isMl
      ? ["+ Bias-Variance Tradeoff", "+ Cross-Entropy Loss", "+ Regularization (L1/L2)", "+ Data Leakage", "+ ROC-AUC / F1"]
      : topicLower.includes("system design")
      ? ["+ Horizontal Scaling", "+ Consistent Hashing", "+ Read-Through Cache", "+ Database Sharding", "+ Kafka / MQ"]
      : ["+ Core Mechanics", "+ Edge Cases", "+ Trade-offs", "+ Production Reliability"]
  );

  const handleInsertChip = (chip: string) => {
    const cleanText = chip.startsWith("+ ") ? chip.slice(2) : chip;
    setCandidateInput((prev) => (prev ? `${prev} ${cleanText}` : cleanText));
  };

  const lastInterviewerIdx = conversation.map((m, i) => m.role === "interviewer" ? i : -1).filter((i) => i !== -1).pop() ?? -1;
  const currentQuestionText = lastInterviewerIdx !== -1 ? conversation[lastInterviewerIdx].content : "";
  const currentHint = lastInterviewerIdx !== -1 ? hintsMap[lastInterviewerIdx] : null;

  return (
    <div className={`bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500/30 selection:text-indigo-200 relative ${
      screen === "interview" ? "h-screen max-h-screen overflow-hidden" : "min-h-screen overflow-x-hidden"
    }`}>
      {/* Decorative gradient aura */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[900px] h-[350px] bg-gradient-to-b from-indigo-600/20 via-cyan-500/10 to-transparent blur-3xl pointer-events-none -z-10" />

      {/* ================= TOP NAVIGATION BAR ================= */}
      <header className="border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-xl shrink-0 z-40 px-3 sm:px-6 h-14 flex items-center justify-between shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 flex items-center justify-center font-black text-sm text-white shadow-lg shadow-indigo-500/25 ring-1 ring-white/20">
            AI
          </div>
          <div>
            <h1 className="text-sm sm:text-base font-bold text-white tracking-tight flex items-center gap-2">
              <span>AI Interview Coach</span>
              <span className="text-[10px] font-semibold tracking-wider uppercase px-2 py-0.5 rounded-full bg-gradient-to-r from-indigo-500/10 to-cyan-500/10 text-indigo-300 border border-indigo-500/20">
                PRO 2.5
              </span>
            </h1>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          {/* Voice Indicator & Quick Toggle */}
          <button
            type="button"
            onClick={toggleVoice}
            className={`px-2.5 py-1 rounded-lg border text-xs flex items-center gap-1.5 transition-all cursor-pointer shadow-sm ${
              voiceEnabled
                ? isSpeaking
                  ? "bg-indigo-600/35 border-indigo-400 text-indigo-200 ring-2 ring-indigo-500/40 animate-pulse"
                  : "bg-indigo-600/25 border-indigo-500/60 text-indigo-300 ring-1 ring-indigo-500/30"
                : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
            }`}
            title={voiceEnabled ? (isSpeaking ? "Interviewer Speaking (Click to Mute / Stop)" : "Voice Audio ON (Click to Mute)") : "Voice Audio Muted (Click to Unmute)"}
          >
            <span className="text-xs">{voiceEnabled ? (isSpeaking ? "🔊" : "🔉") : "🔇"}</span>
            <span className="text-[11px] font-semibold hidden md:inline">
              {voiceEnabled ? (isSpeaking ? "Speaking..." : "Voice ON") : "Voice Muted"}
            </span>
            {isSpeaking && (
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping ml-0.5" />
            )}
          </button>

          {/* Server status pill */}
          <div className="flex items-center gap-2 px-2.5 py-1 rounded-full border border-slate-800 bg-slate-900/90 text-xs shadow-inner">
            <span
              className={`w-2 h-2 rounded-full ${
                serverOnline === true
                  ? "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.9)]"
                  : serverOnline === false
                  ? "bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.9)]"
                  : "bg-amber-400 animate-pulse"
              }`}
            />
            <span className="text-[11px] text-slate-300 font-medium hidden sm:inline">
              {serverOnline === true ? "FastAPI Online" : serverOnline === false ? "Server Offline" : "Connecting"}
            </span>
          </div>

          {/* Engine / Key Settings Button */}
          <button
            type="button"
            onClick={() => setShowSettings(true)}
            className="px-2.5 py-1 rounded-lg border border-slate-700/80 bg-slate-800/80 hover:bg-slate-700 hover:border-slate-600 text-xs text-slate-200 flex items-center gap-1.5 transition-all cursor-pointer shadow-sm active:scale-95"
          >
            <svg className="w-3.5 h-3.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
            </svg>
            <span className="text-[11px] font-medium">Settings</span>
          </button>
        </div>
      </header>

      {/* ================= MAIN CONTAINER ================= */}
      <main className={`flex-1 min-h-0 w-full flex flex-col ${
        screen === "interview"
          ? "p-2 sm:p-3 overflow-hidden max-w-[1720px] mx-auto"
          : "max-w-3xl mx-auto p-4 sm:p-6 overflow-y-auto"
      }`}>
        {/* ================= 4. THE START SCREEN ================= */}
        {screen === "start" && (
          <div className="w-full max-w-2xl mx-auto space-y-6 py-4 animate-in fade-in duration-300">
            {/* Header / Tagline */}
            <div className="text-center space-y-2.5">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full text-[11px] font-semibold bg-indigo-500/10 text-indigo-300 border border-indigo-500/25 shadow-sm">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
                <span>5–20 Questions • Adaptive Follow-Throughs • Target Companies • DSA Code Editor</span>
              </div>
              <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
                Real-World AI Technical Interviewer
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
                Practice with multi-turn adaptive follow-through questions, company-specific interview bars, test cases, and in-depth Big-O loophole analysis.
              </p>
            </div>

            {/* Start Card */}
            <div className="bg-slate-900/80 border border-slate-800/90 rounded-2xl p-5 sm:p-7 backdrop-blur-2xl shadow-2xl space-y-6 ring-1 ring-white/5">
              {/* TRACK SELECTOR: DSA vs RESUME vs CONCEPTUAL */}
              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <span>🎯</span>
                    <span>Interview Format / Track</span>
                  </span>
                  <span className="text-[11px] text-indigo-400 font-semibold lowercase">
                    {interviewTrack === "dsa" ? "Live DSA IDE & Compiler" : interviewTrack === "resume" ? "Direct CV Evaluation" : "Conversational Architecture"}
                  </span>
                </label>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
                  <button
                    type="button"
                    onClick={() => {
                      setInterviewTrack("dsa");
                      if (!topic.trim()) setTopic("Data Structures & Algorithms");
                    }}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                      interviewTrack === "dsa"
                        ? "bg-indigo-600/20 border-indigo-500 ring-2 ring-indigo-500/40 shadow-md text-white"
                        : "bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-900"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-lg">🧩</span>
                      {interviewTrack === "dsa" && (
                        <span className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(34,211,238,0.9)]" />
                      )}
                    </div>
                    <div className="mt-2">
                      <div className="text-xs font-bold text-white">DSA & Coding</div>
                      <div className="text-[10px] text-slate-400 leading-tight mt-0.5">
                        Code Editor, Multi-Language Sandbox & Runtime Output
                      </div>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setInterviewTrack("resume");
                      if (!topic.trim() && !resumeFileName) setTopic("Resume Technical Evaluation");
                    }}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                      interviewTrack === "resume"
                        ? "bg-indigo-600/20 border-indigo-500 ring-2 ring-indigo-500/40 shadow-md text-white"
                        : "bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-900"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-lg">📄</span>
                      {interviewTrack === "resume" && (
                        <span className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.9)]" />
                      )}
                    </div>
                    <div className="mt-2">
                      <div className="text-xs font-bold text-white">Resume Deep-Dive</div>
                      <div className="text-[10px] text-slate-400 leading-tight mt-0.5">
                        Cross-examines your actual CV projects & tech stack
                      </div>
                    </div>
                  </button>

                  <button
                    type="button"
                    onClick={() => {
                      setInterviewTrack("conceptual");
                      if (!topic.trim()) setTopic("System Design");
                    }}
                    className={`p-3 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between ${
                      interviewTrack === "conceptual"
                        ? "bg-indigo-600/20 border-indigo-500 ring-2 ring-indigo-500/40 shadow-md text-white"
                        : "bg-slate-950/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-900"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-lg">🧠</span>
                      {interviewTrack === "conceptual" && (
                        <span className="w-2 h-2 rounded-full bg-purple-400 shadow-[0_0_8px_rgba(192,132,252,0.9)]" />
                      )}
                    </div>
                    <div className="mt-2">
                      <div className="text-xs font-bold text-white">System Design / ML</div>
                      <div className="text-[10px] text-slate-400 leading-tight mt-0.5">
                        Architecture, trade-offs & conceptual discussions
                      </div>
                    </div>
                  </button>
                </div>
              </div>

              {/* TARGET COMPANY SECTION WITH SEARCHABLE DROPDOWN */}
              <div className="space-y-2 relative">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                    <span>🏢</span>
                    <span>Target Company Bar (24+ Tech Giants)</span>
                  </label>
                  {selectedCompany && (
                    <button
                      type="button"
                      onClick={() => setSelectedCompany("")}
                      className="text-[11px] text-rose-400 hover:underline cursor-pointer"
                    >
                      Clear Selection
                    </button>
                  )}
                </div>

                {/* Company Combobox Trigger */}
                <div className="relative">
                  <button
                    type="button"
                    onClick={() => setIsCompanyDropdownOpen(!isCompanyDropdownOpen)}
                    className="w-full px-4 py-3 rounded-xl bg-slate-950/80 border border-slate-700/80 text-left flex items-center justify-between hover:border-indigo-500 transition-colors cursor-pointer text-sm"
                  >
                    {selectedCompany ? (
                      <div className="flex items-center gap-2.5 truncate">
                        <span className="text-lg">{TARGET_COMPANIES.find((c) => c.id === selectedCompany)?.icon}</span>
                        <div className="truncate">
                          <span className="font-bold text-white mr-2">{selectedCompany}</span>
                          <span className="text-xs text-indigo-300 truncate">
                            {TARGET_COMPANIES.find((c) => c.id === selectedCompany)?.tagline}
                          </span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-slate-400 flex items-center gap-2">
                        <span>🔍</span>
                        <span>Select or search a company (e.g. Google, Bloomberg, Stripe, Nvidia)...</span>
                      </span>
                    )}
                    <span className="text-slate-400 ml-2">▼</span>
                  </button>

                  {/* Searchable Dropdown Popup */}
                  {isCompanyDropdownOpen && (
                    <div className="absolute z-50 left-0 right-0 mt-2 p-3 bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl space-y-2.5 backdrop-blur-3xl animate-in fade-in slide-in-from-top-2">
                      {/* Search Input inside Dropdown */}
                      <div className="relative">
                        <input
                          type="text"
                          value={companySearchQuery}
                          onChange={(e) => setCompanySearchQuery(e.target.value)}
                          placeholder="Search 24+ companies by name, domain, or keyword..."
                          autoFocus
                          className="w-full px-3 py-2 pl-8 rounded-lg bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500"
                        />
                        <span className="absolute left-2.5 top-2.5 text-xs text-slate-500">🔍</span>
                        {companySearchQuery && (
                          <button
                            type="button"
                            onClick={() => setCompanySearchQuery("")}
                            className="absolute right-2.5 top-2 text-xs text-slate-400 hover:text-white cursor-pointer"
                          >
                            ✕
                          </button>
                        )}
                      </div>

                      {/* Category Filter Pills */}
                      <div className="flex flex-wrap gap-1 text-[10px]">
                        {[
                          "All",
                          "FAANG / Big Tech",
                          "Fintech & Payments",
                          "Cloud & Infrastructure",
                          "AI & Systems",
                          "Consumer & Platforms",
                        ].map((cat) => (
                          <button
                            key={cat}
                            type="button"
                            onClick={() => setCompanyCategoryFilter(cat)}
                            className={`px-2 py-0.5 rounded-md border transition-all cursor-pointer ${
                              companyCategoryFilter === cat
                                ? "bg-indigo-600 border-indigo-500 text-white font-bold"
                                : "bg-slate-950/70 border-slate-800 text-slate-400 hover:text-slate-200"
                            }`}
                          >
                            {cat}
                          </button>
                        ))}
                      </div>

                      {/* Companies Scrollable List */}
                      <div className="max-h-56 overflow-y-auto space-y-1 pr-1 divide-y divide-slate-800/40">
                        {TARGET_COMPANIES.filter((comp) => {
                          const matchesCat = companyCategoryFilter === "All" || comp.category === companyCategoryFilter;
                          const q = companySearchQuery.toLowerCase().trim();
                          const matchesQ =
                            !q ||
                            comp.name.toLowerCase().includes(q) ||
                            comp.tagline.toLowerCase().includes(q) ||
                            comp.focus.toLowerCase().includes(q) ||
                            comp.keywords.some((k) => k.toLowerCase().includes(q));
                          return matchesCat && matchesQ;
                        }).map((comp) => {
                          const isSelected = selectedCompany === comp.id;
                          return (
                            <button
                              key={comp.id}
                              type="button"
                              onClick={() => {
                                setSelectedCompany(comp.id);
                                setIsCompanyDropdownOpen(false);
                              }}
                              className={`w-full p-2 rounded-xl text-left transition-all cursor-pointer flex items-center justify-between gap-2 ${
                                isSelected
                                  ? "bg-indigo-600/30 text-white"
                                  : "hover:bg-slate-800 text-slate-300"
                              }`}
                            >
                              <div className="flex items-center gap-2.5 truncate">
                                <span className="text-lg shrink-0">{comp.icon}</span>
                                <div className="truncate">
                                  <div className="flex items-center gap-1.5">
                                    <span className="text-xs font-bold text-white">{comp.name}</span>
                                    <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-800 text-slate-400">
                                      {comp.category}
                                    </span>
                                  </div>
                                  <p className="text-[10px] text-slate-400 truncate">{comp.tagline}</p>
                                </div>
                              </div>
                              <span className="text-[10px] text-indigo-400 font-mono shrink-0 whitespace-nowrap">
                                {comp.barScore}
                              </span>
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>

                {/* Selected Company Banner */}
                {selectedCompany && (
                  <div className="p-3 rounded-xl bg-gradient-to-r from-indigo-950/60 to-slate-900 border border-indigo-500/40 text-xs flex items-center justify-between gap-3 animate-in fade-in shadow-sm">
                    <div className="space-y-0.5 truncate">
                      <div className="flex items-center gap-2">
                        <span className="text-sm">{TARGET_COMPANIES.find((c) => c.id === selectedCompany)?.icon}</span>
                        <span className="text-[11px] font-bold text-indigo-300 uppercase tracking-wider">
                          {selectedCompany} Interview Bar Active
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-300 truncate">
                        {TARGET_COMPANIES.find((c) => c.id === selectedCompany)?.focus}
                      </p>
                    </div>
                    <span className="px-2 py-0.5 rounded-md bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 text-[10px] font-mono shrink-0">
                      {TARGET_COMPANIES.find((c) => c.id === selectedCompany)?.barScore}
                    </span>
                  </div>
                )}
              </div>

              {/* QUESTION COUNT SELECTOR (5 to 20 Questions) */}
              <div className="space-y-2.5 p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
                <div className="flex items-center justify-between">
                  <label className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                    <span>🔢</span>
                    <span>Number of Questions (Choose 5 to 20)</span>
                  </label>
                  <span className="text-xs font-extrabold px-2.5 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 font-mono">
                    {totalQuestions} Questions
                  </span>
                </div>

                {/* Slider */}
                <input
                  type="range"
                  min={5}
                  max={20}
                  step={1}
                  value={totalQuestions}
                  onChange={(e) => setTotalQuestions(Number(e.target.value))}
                  className="w-full accent-indigo-500 cursor-pointer h-2 bg-slate-800 rounded-lg"
                />

                {/* Quick Selection Chips */}
                <div className="flex items-center justify-between gap-1 text-[11px]">
                  {[5, 8, 10, 15, 20].map((count) => (
                    <button
                      key={count}
                      type="button"
                      onClick={() => setTotalQuestions(count)}
                      className={`px-2.5 py-1 rounded-lg border font-semibold transition-all cursor-pointer ${
                        totalQuestions === count
                          ? "bg-indigo-600 border-indigo-500 text-white shadow-sm"
                          : "bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200"
                      }`}
                    >
                      {count} Qs
                    </button>
                  ))}
                </div>
              </div>

              {/* PDF Resume Drop Zone (Optional) */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center gap-1.5">
                    <span>📄</span>
                    <span>Upload Resume / CV (Optional)</span>
                  </label>
                  {resumeFileName && (
                    <span className="text-[11px] text-emerald-400 font-semibold flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                      Resume Cross-Examination Active
                    </span>
                  )}
                </div>

                <input
                  type="file"
                  ref={fileInputRef}
                  accept=".pdf"
                  className="hidden"
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) handleResumeFile(file);
                  }}
                />

                {!resumeFileName ? (
                  <div
                    onDragOver={(e) => {
                      e.preventDefault();
                      setIsDragOver(true);
                    }}
                    onDragLeave={() => setIsDragOver(false)}
                    onDrop={(e) => {
                      e.preventDefault();
                      setIsDragOver(false);
                      const file = e.dataTransfer.files?.[0];
                      if (file) handleResumeFile(file);
                    }}
                    onClick={() => fileInputRef.current?.click()}
                    className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all duration-200 ${
                      isDragOver
                        ? "border-indigo-400 bg-indigo-500/10 shadow-lg shadow-indigo-500/10"
                        : "border-slate-800 hover:border-slate-700 bg-slate-950/50 hover:bg-slate-950/70"
                    }`}
                  >
                    {isUploadingResume ? (
                      <div className="flex items-center justify-center gap-2 text-xs text-indigo-400 py-2">
                        <svg className="animate-spin h-5 w-5 text-indigo-400" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                        </svg>
                        <span className="font-medium">Extracting projects & technologies from PDF...</span>
                      </div>
                    ) : (
                      <div className="space-y-1 py-1">
                        <div className="text-xl">📄</div>
                        <p className="text-xs font-semibold text-slate-200">
                          Drop your Resume PDF here or <span className="text-indigo-400 underline decoration-indigo-400/50 underline-offset-2">browse files</span>
                        </p>
                        <p className="text-[11px] text-slate-400">
                          Questions will probe <strong className="text-slate-300">directly into your actual CV projects</strong>
                        </p>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="p-3.5 rounded-xl bg-gradient-to-r from-indigo-950/40 to-slate-900 border border-indigo-500/40 text-xs space-y-2 shadow-sm">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2.5 truncate">
                        <span className="text-lg">📄</span>
                        <div className="truncate">
                          <p className="font-bold text-white truncate">{resumeFileName}</p>
                          <p className="text-[11px] text-indigo-300">
                            {resumeText?.length} chars parsed • Questions will deep-dive into your CV
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setResumeText(null);
                          setResumeFileName(null);
                          setResumeHighlights(null);
                          if (fileInputRef.current) fileInputRef.current.value = "";
                        }}
                        className="px-2.5 py-1 text-[11px] text-rose-400 hover:text-rose-300 hover:bg-rose-950/60 rounded-lg transition-colors cursor-pointer shrink-0 font-medium border border-rose-500/20"
                      >
                        Remove
                      </button>
                    </div>

                    {resumeHighlights && resumeHighlights.projects.length > 0 && (
                      <div className="pt-1 border-t border-slate-800/80 flex flex-wrap gap-1 text-[10px]">
                        <span className="text-slate-400 font-semibold mr-1">Detected Projects:</span>
                        {resumeHighlights.projects.slice(0, 3).map((p, i) => (
                          <span key={i} className="px-2 py-0.5 rounded-md bg-indigo-500/10 text-indigo-300 border border-indigo-500/20">
                            {p}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {resumeUploadError && (
                  <p className="text-[11px] text-rose-400 font-medium">{resumeUploadError}</p>
                )}
              </div>

              {/* Topic Input & Chips */}
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
                    {resumeFileName ? "Topic Focus (Optional in Resume Mode)" : "Interview Topic or Domain"}
                  </label>
                  {selectedCompany && (
                    <span className="text-[10px] text-indigo-300">Blended with {selectedCompany} interview style</span>
                  )}
                </div>

                <input
                  type="text"
                  placeholder={
                    selectedCompany
                      ? `e.g. Data Structures & Algorithms, System Design at ${selectedCompany}`
                      : resumeFileName
                      ? "Optional: Target specific domain (e.g. Backend, ML, Fullstack), or leave blank"
                      : "e.g. Data Structures & Algorithms, Python, System Design"
                  }
                  value={topic}
                  onChange={(e) => {
                    setTopic(e.target.value);
                    if (startError) setStartError(null);
                  }}
                  className="w-full px-4 py-3 rounded-xl bg-slate-950/70 border border-slate-700/80 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-colors shadow-inner"
                />

                {/* Preset Chips based on Selected Track */}
                <div className="flex flex-wrap gap-1.5 pt-1">
                  {(interviewTrack === "dsa"
                    ? [
                        "Data Structures & Algorithms",
                        "Two Pointers & Sliding Window",
                        "Dynamic Programming",
                        "Trees & Graph Traversal",
                        "Binary Search & Heaps",
                        "Strings & Hash Maps",
                      ]
                    : interviewTrack === "conceptual"
                    ? [
                        "System Design",
                        "Distributed Systems",
                        "Machine Learning & AI",
                        "Microservices & Caching",
                        "React & Frontend Architecture",
                        "SQL & Database Sharding",
                      ]
                    : [
                        "Resume Technical Evaluation",
                        "Backend & Cloud Projects",
                        "AI & Machine Learning Experience",
                        "Fullstack Systems & APIs",
                      ]
                  ).map((preset) => (
                    <button
                      key={preset}
                      type="button"
                      onClick={() => {
                        setTopic(preset);
                        if (startError) setStartError(null);
                      }}
                      className={`text-xs px-2.5 py-1.5 rounded-lg border transition-all cursor-pointer ${
                        topic === preset
                          ? "bg-indigo-600/20 border-indigo-500 text-indigo-300 font-semibold shadow-sm"
                          : "bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800"
                      }`}
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>

              {/* Difficulty Selection */}
              <div className="space-y-2">
                <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
                  Difficulty Level
                </label>
                <div className="grid grid-cols-3 gap-2.5">
                  {[
                    {
                      level: "Easy" as const,
                      desc: "Warm-up & recall",
                      badge: "text-emerald-400",
                    },
                    {
                      level: "Medium" as const,
                      desc: "Applied problems & edge cases",
                      badge: "text-blue-400",
                    },
                    {
                      level: "Hard" as const,
                      desc: "Optimal bounds & scale",
                      badge: "text-purple-400",
                    },
                  ].map(({ level, desc, badge }) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setDifficulty(level)}
                      className={`p-3 rounded-xl border text-left transition-all cursor-pointer ${
                        difficulty === level
                          ? "bg-slate-800/90 border-indigo-500 shadow-md ring-1 ring-indigo-500/40"
                          : "bg-slate-950/40 border-slate-800 hover:border-slate-700"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className={`text-xs font-bold ${badge}`}>{level}</span>
                        {difficulty === level && (
                          <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shadow-[0_0_6px_rgba(129,140,248,0.8)]" />
                        )}
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1 leading-tight">{desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              {/* Validation / Server Error Message */}
              {startError && (
                <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-500/50 text-rose-300 text-xs flex items-start gap-2 animate-in fade-in">
                  <svg className="w-4 h-4 shrink-0 mt-0.5 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{startError}</span>
                </div>
              )}

              {/* HYBRID MODE PROMINENT BANNER (When both Company and Resume are selected) */}
              {selectedCompany && (resumeFileName || resumeText) && (
                <div className="p-3.5 rounded-xl bg-gradient-to-r from-purple-950/70 via-indigo-950/70 to-cyan-950/60 border border-purple-500/50 shadow-lg shadow-purple-500/10 flex items-start gap-3 animate-in fade-in">
                  <span className="text-xl shrink-0 mt-0.5">⚡</span>
                  <div className="space-y-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="text-xs font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-300 via-pink-300 to-cyan-300 uppercase tracking-wider">
                        Hybrid Interview Track Active
                      </span>
                      <span className="text-[10px] font-mono font-semibold px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-200 border border-purple-500/30">
                        {selectedCompany} Bar + Resume Projects
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-300 leading-relaxed">
                      Questions will cross-examine your actual CV projects under <strong className="text-white">{selectedCompany}</strong>&apos;s real-world production constraints, scale, and engineering principles.
                    </p>
                  </div>
                </div>
              )}

              {/* Start Interview CTA */}
              <button
                type="button"
                onClick={handleStartInterview}
                disabled={isStarting || isUploadingResume}
                className="w-full py-3.5 px-6 rounded-xl bg-gradient-to-r from-indigo-600 via-indigo-500 to-cyan-500 hover:from-indigo-500 hover:to-cyan-400 text-white font-bold text-sm shadow-lg shadow-indigo-600/30 transition-all active:scale-[0.99] disabled:opacity-50 cursor-pointer flex items-center justify-center gap-2"
              >
                {isStarting ? (
                  <>
                    <svg className="animate-spin h-4 w-4 text-white" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>{resumeFileName ? "Synthesizing Resume Questions..." : "Preparing Interview Environment..."}</span>
                  </>
                ) : (
                  <>
                    <span>
                      Start {selectedCompany ? `${selectedCompany} ` : ""}{interviewTrack === "dsa" ? "DSA " : interviewTrack === "resume" ? "Resume " : ""}{totalQuestions}-Question Interview (Voice Active 🔊)
                    </span>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* ================= 5. THE INTERVIEW SCREEN (REARRANGED & FULL-VIEWPORT RESIZED) ================= */}
        {screen === "interview" && (
          <div className="w-full flex-1 min-h-0 flex flex-col bg-slate-900/90 border border-slate-800 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-2xl animate-in fade-in duration-300 ring-1 ring-white/5">
            {/* Header: Topic, Company, Difficulty, Progress, Timer & Layout Controls */}
            <div className="shrink-0 px-3 sm:px-5 py-2.5 border-b border-slate-800/80 bg-slate-950/85 backdrop-blur-md flex items-center justify-between flex-wrap gap-2">
              <div className="flex items-center gap-2 sm:gap-3 flex-wrap">
                <span className="text-xs font-bold px-2.5 py-1 rounded-md bg-gradient-to-r from-indigo-500/20 to-cyan-500/20 text-indigo-300 border border-indigo-500/30">
                  {topic || "Technical Evaluation"}
                </span>
                {selectedCompany && (
                  <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-purple-950/80 border border-purple-500/40 text-purple-300 flex items-center gap-1">
                    <span>🏢</span> {selectedCompany}
                  </span>
                )}
                {selectedCompany && (resumeFileName || resumeText) && (
                  <span className="text-xs font-bold px-2 py-0.5 rounded-md bg-gradient-to-r from-purple-900/80 to-indigo-900/80 border border-purple-400/50 text-purple-200 flex items-center gap-1 shadow-sm">
                    <span>⚡</span> Hybrid: {selectedCompany} + CV
                  </span>
                )}
                <span className="text-xs px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700 font-medium">
                  {difficulty}
                </span>

                {/* Progress Badge */}
                <div className="flex items-center gap-1.5 px-2.5 py-0.5 rounded-md bg-slate-800/90 border border-slate-700 text-xs text-slate-300 font-mono">
                  <span>Q {questionCount} of {totalQuestions}</span>
                  <div className="w-12 bg-slate-700 h-1.5 rounded-full overflow-hidden ml-1">
                    <div
                      className="bg-indigo-400 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${Math.min(100, (questionCount / totalQuestions) * 100)}%` }}
                    />
                  </div>
                </div>

                <span className="text-xs text-slate-400 font-mono flex items-center gap-1">
                  <span>⏱</span>
                  <span>{formatTimer(elapsedSeconds)}</span>
                </span>
              </div>

              <div className="flex items-center gap-2">
                {/* Size Rearranger: Quick Split Ratio Switcher */}
                {showCodeEditor && (
                  <div className="hidden lg:flex items-center bg-slate-900 border border-slate-800 rounded-lg p-0.5 text-[11px] font-semibold text-slate-400">
                    <button
                      type="button"
                      onClick={() => setSplitRatio("chat")}
                      className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                        splitRatio === "chat" ? "bg-indigo-600 text-white font-bold" : "hover:text-slate-200"
                      }`}
                      title="Expand Chat Area (65% Chat, 35% Code)"
                    >
                      Wide Chat 💬
                    </button>
                    <button
                      type="button"
                      onClick={() => setSplitRatio("balanced")}
                      className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                        splitRatio === "balanced" ? "bg-indigo-600 text-white font-bold" : "hover:text-slate-200"
                      }`}
                      title="Balanced 50/50 Split"
                    >
                      50 / 50
                    </button>
                    <button
                      type="button"
                      onClick={() => setSplitRatio("code")}
                      className={`px-2 py-0.5 rounded transition-all cursor-pointer ${
                        splitRatio === "code" ? "bg-indigo-600 text-white font-bold" : "hover:text-slate-200"
                      }`}
                      title="Expand Code Editor (65% Code, 35% Chat)"
                    >
                      Wide Code 💻
                    </button>
                  </div>
                )}

                {/* Realtime Helper Toggle Button */}
                <button
                  type="button"
                  onClick={() => setShowRealtimeHelper(!showRealtimeHelper)}
                  className={`px-2.5 py-1 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer shadow-sm ${
                    showRealtimeHelper
                      ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-300 ring-1 ring-emerald-500/30"
                      : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700"
                  }`}
                  title="Toggle Live Real-Time Interview Helper & Concept Checklist"
                >
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.9)] animate-pulse" />
                  <span>✨ Realtime Helper</span>
                  <span className="text-[10px] px-1 rounded bg-emerald-500/30 text-emerald-200 uppercase font-mono font-bold">
                    {showRealtimeHelper ? "ON" : "OFF"}
                  </span>
                </button>

                {/* DSA Code Editor Toggle Button */}
                <button
                  type="button"
                  onClick={() => setShowCodeEditor(!showCodeEditor)}
                  className={`px-2.5 py-1 rounded-lg border text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                    showCodeEditor
                      ? "bg-cyan-500/20 border-cyan-500/50 text-cyan-300 ring-1 ring-cyan-500/30"
                      : "bg-slate-800 border-slate-700 text-slate-300 hover:bg-slate-700"
                  }`}
                  title="Toggle DSA Code Editor & Loophole Finder"
                >
                  <span>💻</span>
                  <span>{showCodeEditor ? "Hide Editor" : "Code Editor 🔍"}</span>
                </button>

                {/* Voice speech toggle */}
                <button
                  type="button"
                  onClick={toggleVoice}
                  title={voiceEnabled ? (isSpeaking ? "Mute audio (Stops voice immediately)" : "Mute audio questions") : "Read questions aloud"}
                  className={`px-2 py-1 rounded-lg border text-xs transition-colors cursor-pointer flex items-center gap-1 ${
                    voiceEnabled
                      ? isSpeaking
                        ? "bg-indigo-600/40 border-indigo-400 text-indigo-200 ring-1 ring-indigo-500/50 animate-pulse"
                        : "bg-indigo-600/30 border-indigo-500 text-indigo-300"
                      : "bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span className="text-xs">{voiceEnabled ? (isSpeaking ? "🔊" : "🔉") : "🔇"}</span>
                  <span className="text-[11px] font-semibold hidden sm:inline">
                    {voiceEnabled ? (isSpeaking ? "Stop" : "Mute") : "Unmute"}
                  </span>
                </button>

                {/* Wrap Up Button */}
                <button
                  type="button"
                  onClick={() => handleGenerateReport()}
                  disabled={conversation.filter((m) => m.role === "candidate").length === 0 || isAiThinking}
                  className="px-2.5 py-1 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 border border-amber-500/30 text-amber-300 text-xs font-semibold transition-colors disabled:opacity-40 cursor-pointer"
                >
                  Wrap Up Early
                </button>
              </div>
            </div>

            {/* Mobile Tab Switcher when Code Editor is active */}
            {showCodeEditor && (
              <div className="md:hidden flex items-center bg-slate-900 border-b border-slate-800 p-1 shrink-0 z-20">
                <button
                  type="button"
                  onClick={() => setMobileActiveTab("chat")}
                  className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                    mobileActiveTab === "chat"
                      ? "bg-indigo-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span>💬 Interview Chat</span>
                </button>
                <button
                  type="button"
                  onClick={() => setMobileActiveTab("code")}
                  className={`flex-1 py-1.5 text-xs font-bold rounded-lg transition-all flex items-center justify-center gap-1.5 cursor-pointer ${
                    mobileActiveTab === "code"
                      ? "bg-cyan-600 text-white shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  <span>💻 Code Workspace</span>
                  {currentProblemTitle && (
                    <span className="text-[10px] opacity-75 truncate max-w-[110px]">
                      ({currentProblemTitle})
                    </span>
                  )}
                </button>
              </div>
            )}

            {/* Split Screen Container: Left (Chat), Right (DSA Code Editor) */}
            <div className="flex-1 min-h-0 flex flex-col md:flex-row overflow-hidden">
              {/* Left Column: Chat Feed & Candidate Response */}
              <div className={`flex flex-col h-full min-h-0 overflow-hidden ${
                showCodeEditor
                  ? splitRatio === "balanced"
                    ? "w-full md:w-1/2 md:border-r border-slate-800"
                    : splitRatio === "code"
                    ? "w-full md:w-4/12 md:border-r border-slate-800"
                    : "w-full md:w-7/12 md:border-r border-slate-800"
                  : "w-full max-w-4xl mx-auto"
              } ${showCodeEditor && mobileActiveTab === "code" ? "hidden md:flex" : "flex"}`}>
                {/* Chat Feed */}
                <div className={`flex-1 min-h-0 overflow-y-auto ${showCodeEditor ? "p-3 sm:p-4" : "p-4 sm:p-6"} space-y-4`}>
                  {conversation.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex gap-3 ${showCodeEditor ? "max-w-2xl" : "max-w-3xl"} ${
                        msg.role === "candidate" ? "ml-auto justify-end" : "mr-auto justify-start"
                      }`}
                    >
                      {msg.role === "interviewer" && (
                        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-600 to-cyan-500 flex items-center justify-center text-[10px] font-black text-white shrink-0 mt-0.5 shadow-md shadow-indigo-500/20 ring-1 ring-white/20">
                          AI
                        </div>
                      )}

                      <div
                        className={`rounded-2xl p-4 text-xs sm:text-sm leading-relaxed transition-all shadow-md ${
                          msg.role === "candidate"
                            ? "bg-gradient-to-r from-indigo-600 via-indigo-600 to-indigo-700 text-white rounded-br-none shadow-indigo-600/20"
                            : "bg-slate-800/90 border-t border-indigo-500/40 border-slate-700/60 text-slate-100 rounded-bl-none shadow-slate-950/40"
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1.5 opacity-80 gap-3">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-300">
                              {msg.role === "interviewer" ? "Interviewer" : "You (Candidate)"}
                            </span>
                            {/* Follow-Through Probe Indicator Badge */}
                            {msg.role === "interviewer" && msg.is_follow_up && (
                              <span className="px-2 py-0.5 rounded-full bg-amber-500/20 border border-amber-500/40 text-amber-300 text-[10px] font-bold tracking-wide animate-pulse">
                                🎯 Follow-Through Probe
                              </span>
                            )}
                          </div>

                          {/* Bulb Icon 💡 on Interviewer questions */}
                          {msg.role === "interviewer" && idx === conversation.length - 1 && (
                            <button
                              type="button"
                              onClick={() => handleFetchHint(idx, msg.content)}
                              disabled={hintLoadingIdx === idx}
                              title="Get an on-demand hint to unblock your thinking without spoiling the answer"
                              className="flex items-center gap-1 px-2.5 py-0.5 rounded-full bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/40 text-amber-300 text-[11px] font-medium transition-all cursor-pointer shadow-sm active:scale-95"
                            >
                              {hintLoadingIdx === idx ? (
                                <span className="animate-spin text-xs">⟳</span>
                              ) : (
                                <span className="text-xs">💡</span>
                              )}
                              <span>
                                {hintsMap[idx] ? `Hint (L${hintsMap[idx].hint_level}/3)` : "Need a Hint?"}
                              </span>
                            </button>
                          )}
                        </div>

                        <div className="whitespace-pre-wrap font-sans leading-relaxed">{msg.content}</div>

                        {/* Candidate Code Attachment Card (if submitted with code) */}
                        {msg.code_snippet && (
                          <div className="mt-2.5 p-2.5 rounded-xl bg-slate-950/80 border border-slate-700/80 font-mono text-[11px] text-slate-200 overflow-x-auto">
                            <div className="text-[10px] font-bold text-cyan-400 mb-1 flex items-center justify-between">
                              <span>Submitted Code ({msg.code_language || "python"})</span>
                              <span>✓ Evaluated</span>
                            </div>
                            <pre className="whitespace-pre">{msg.code_snippet}</pre>
                          </div>
                        )}

                        {/* Expandable Hint Box 💡 */}
                        {hintsMap[idx] && (
                          <div className="mt-3 p-3 rounded-xl bg-amber-950/40 border border-amber-500/40 text-amber-200 text-xs space-y-1.5 animate-in slide-in-from-top-2">
                            <div className="flex items-center justify-between">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-amber-400 flex items-center gap-1">
                                <span>💡 Hint (Level {hintsMap[idx].hint_level} • {hintsMap[idx].category})</span>
                              </span>
                              {hintsMap[idx].hint_level < 3 && (
                                <button
                                  type="button"
                                  onClick={() => handleFetchHint(idx, msg.content)}
                                  className="text-[10px] text-amber-300 hover:text-amber-100 underline cursor-pointer"
                                >
                                  Next Hint Level →
                                </button>
                              )}
                            </div>
                            <p className="leading-relaxed">{hintsMap[idx].hint}</p>
                          </div>
                        )}
                      </div>

                      {msg.role === "candidate" && (
                        <div className="w-8 h-8 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-bold text-slate-300 shrink-0 mt-0.5 shadow-sm">
                          You
                        </div>
                      )}
                    </div>
                  ))}

                  {/* AI Thinking Indicator */}
                  {isAiThinking && (
                    <div className="flex items-center gap-2 text-slate-400 text-xs italic px-3 py-1.5 rounded-xl bg-slate-950/40 w-fit border border-slate-800/80 animate-pulse">
                      <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping" />
                      <span>The interviewer is evaluating your answer and formulating the next question...</span>
                    </div>
                  )}

                  <div ref={chatEndRef} />
                </div>

                {/* Candidate Answer Input Area (Always Pinned, Never Cut Off) */}
                <div className="shrink-0 p-3 border-t border-slate-800/80 bg-slate-950/95 space-y-2">
                  {/* REAL-TIME AI CO-PILOT & LIVE CONCEPT RADAR */}
                  {showRealtimeHelper && helperData && (
                    <div className="p-2.5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs space-y-2 shadow-inner animate-in fade-in duration-200">
                      {/* Helper Bar Header */}
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_6px_rgba(52,211,153,0.9)] animate-pulse" />
                          <span className="text-[11px] font-bold text-emerald-300">
                            ✨ {helperData.framework_name}
                          </span>
                          <span className="text-[10px] text-slate-400 hidden xl:inline">
                            • {helperData.framework_description}
                          </span>
                        </div>

                        <div className="flex items-center gap-1.5">
                          <button
                            type="button"
                            onClick={() => {
                              setShowCritiqueBox(!showCritiqueBox);
                              handleFetchRealtimeHelper();
                            }}
                            disabled={isCritiquing}
                            className={`px-2 py-0.5 rounded-md text-[10px] font-bold flex items-center gap-1 transition-all cursor-pointer shadow-xs active:scale-95 ${
                              showCritiqueBox
                                ? "bg-indigo-600 text-white"
                                : "bg-indigo-500/15 hover:bg-indigo-500/25 border border-indigo-500/40 text-indigo-300"
                            }`}
                          >
                            {isCritiquing ? <span className="animate-spin text-xs">⟳</span> : <span>⚡</span>}
                            <span>{showCritiqueBox ? "Hide Critique" : "Critique Draft"}</span>
                          </button>
                        </div>
                      </div>

                      {/* Live Concept Radar / Checklist */}
                      <div className="space-y-1">
                        <div className="flex items-center justify-between text-[10px]">
                          <span className="font-semibold uppercase tracking-wider text-slate-400">
                            Live Concepts ({detectedKeywordsInDraft.length}/{helperData.recommended_keywords.length} Detected):
                          </span>
                          <span className="text-emerald-400 font-mono font-bold">
                            {Math.round((detectedKeywordsInDraft.length / Math.max(helperData.recommended_keywords.length, 1)) * 100)}% Coverage
                          </span>
                        </div>

                        <div className="flex flex-wrap gap-1 max-h-16 overflow-y-auto scrollbar-none">
                          {helperData.recommended_keywords.map((kw, i) => {
                            const isMentioned = detectedKeywordsInDraft.includes(kw);
                            return (
                              <button
                                key={i}
                                type="button"
                                onClick={() => handleInsertChip(kw)}
                                title={isMentioned ? "Mentioned in your draft!" : "Click to insert keyword into answer"}
                                className={`px-2 py-0.5 rounded-md text-[10px] font-mono transition-all flex items-center gap-1 cursor-pointer active:scale-95 ${
                                  isMentioned
                                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/50 shadow-[0_0_8px_rgba(52,211,153,0.25)] font-bold"
                                    : "bg-slate-800/80 hover:bg-slate-700/80 text-slate-400 border border-slate-700/60"
                                }`}
                              >
                                <span>{isMentioned ? "✓" : "+"}</span>
                                <span>{kw}</span>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                      {/* Expandable Critique & Feedback Drawer */}
                      {showCritiqueBox && (
                        <div className="p-2.5 rounded-xl bg-slate-950 border border-indigo-500/40 space-y-2 animate-in slide-in-from-top-1">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                                Pre-Submit Readiness:
                              </span>
                              <span className="text-[11px] font-bold text-white px-2 py-0.5 rounded bg-indigo-600/30 border border-indigo-500/40">
                                {helperData.readiness_score}/100 • {helperData.readiness_label}
                              </span>
                            </div>
                            <button
                              type="button"
                              onClick={() => handleFetchRealtimeHelper()}
                              disabled={isCritiquing}
                              className="text-[10px] text-indigo-400 hover:text-indigo-200 underline cursor-pointer"
                            >
                              Re-evaluate
                            </button>
                          </div>

                          <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                            <div
                              className={`h-1.5 rounded-full transition-all duration-300 ${
                                helperData.readiness_score >= 80
                                  ? "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.7)]"
                                  : helperData.readiness_score >= 50
                                  ? "bg-indigo-400 shadow-[0_0_8px_rgba(129,140,248,0.7)]"
                                  : "bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.7)]"
                              }`}
                              style={{ width: `${Math.max(5, helperData.readiness_score)}%` }}
                            />
                          </div>

                          <p className="text-[11px] text-slate-200 leading-relaxed font-sans">
                            {helperData.critique}
                          </p>

                          {helperData.quick_tips && helperData.quick_tips.length > 0 && (
                            <div className="text-[10px] text-slate-400 border-t border-slate-800/80 pt-1 flex items-center gap-1.5">
                              <span className="text-amber-400 shrink-0">💡 Coach Tip:</span>
                              <span className="truncate">{helperData.quick_tips[0]}</span>
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Quick Insert Chips */}
                  <div className="flex items-center gap-1.5 overflow-x-auto text-[11px] pb-1 scrollbar-none">
                    <span className="text-slate-500 text-[10px] uppercase font-bold shrink-0">
                      {showCodeEditor || isDsa ? "Quick Bounds:" : "Key Concepts:"}
                    </span>
                    {currentQuickChips.map((chip, i) => (
                      <button
                        key={i}
                        type="button"
                        onClick={() => handleInsertChip(chip)}
                        className="px-2 py-0.5 rounded-md bg-slate-800/90 hover:bg-slate-700 border border-slate-700/80 text-slate-300 hover:text-white text-[10px] font-mono shrink-0 transition-all cursor-pointer active:scale-95 shadow-xs"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>

                  <div className="relative">
                    <textarea
                      rows={3}
                      disabled={isAiThinking}
                      value={candidateInput}
                      onChange={(e) => setCandidateInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" && !e.shiftKey) {
                          e.preventDefault();
                          handleSubmitAnswer();
                        }
                      }}
                      placeholder={currentPlaceholder}
                      className="w-full px-3 py-2 rounded-xl bg-slate-900/90 border border-slate-700/80 text-xs sm:text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500/30 transition-all resize-none disabled:opacity-50 shadow-inner"
                    />

                    <div className="flex items-center justify-between mt-1.5 flex-wrap gap-2">
                      <div className="flex items-center gap-2">
                        {/* Mic speech-to-text dictation button */}
                        <button
                          type="button"
                          onClick={toggleSpeechRecognition}
                          disabled={isAiThinking}
                          className={`px-2.5 py-1.5 rounded-xl border text-xs font-bold transition-all cursor-pointer flex items-center gap-1.5 active:scale-95 ${
                            isListening
                              ? "bg-rose-500/25 border-rose-500 text-rose-300 ring-2 ring-rose-500/40 shadow-md shadow-rose-500/20 animate-pulse"
                              : "bg-slate-800/90 hover:bg-slate-700 border-slate-700/80 text-slate-300"
                          }`}
                          title={isListening ? "Stop voice dictation" : "Speak your answer aloud (Web Speech API)"}
                        >
                          <span className="text-xs">{isListening ? "🔴" : "🎙️"}</span>
                          <span className="text-[11px]">
                            {isListening ? "Listening... (Click to stop)" : "Speak Answer"}
                          </span>
                        </button>

                        {/* Skip Question Button */}
                        <button
                          type="button"
                          onClick={handleSkipQuestion}
                          disabled={isAiThinking}
                          className="px-2.5 py-1.5 rounded-xl border border-slate-700/70 bg-slate-800/60 hover:bg-slate-700 text-slate-400 hover:text-slate-200 text-xs font-medium transition-all cursor-pointer flex items-center gap-1 active:scale-95"
                          title="Skip to next question immediately"
                        >
                          <span>⏭️</span>
                          <span className="text-[11px]">Skip Question</span>
                        </button>
                      </div>

                      <div className="flex items-center gap-2 ml-auto">
                        {showCodeEditor && (
                          <button
                            type="button"
                            onClick={() => handleSubmitAnswer(codeSnippet)}
                            disabled={isAiThinking || !codeSnippet.trim()}
                            className="px-3 py-1.5 rounded-xl bg-cyan-600/80 hover:bg-cyan-500 text-white text-xs font-bold transition-all cursor-pointer shadow-md flex items-center gap-1 active:scale-95"
                            title="Submit current code snippet from editor directly to interviewer"
                          >
                            <span>Submit with Code 🚀</span>
                          </button>
                        )}
                        <button
                          type="button"
                          onClick={() => handleSubmitAnswer()}
                          disabled={!candidateInput.trim() || isAiThinking}
                          className="px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-500 text-white text-xs font-bold transition-all cursor-pointer shadow-md flex items-center gap-1 active:scale-95"
                        >
                          <span>Send Answer</span>
                          <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Right Column: Full-Height DSA Coding Workspace & Loophole Finder */}
              {showCodeEditor && (
                <div className={`flex flex-col h-full min-h-0 bg-slate-950/95 border-t md:border-t-0 overflow-hidden ${
                  splitRatio === "balanced"
                    ? "w-full md:w-1/2"
                    : splitRatio === "code"
                    ? "w-full md:w-8/12"
                    : "w-full md:w-5/12"
                } ${mobileActiveTab === "chat" ? "hidden md:flex" : "flex"}`}>
                  {/* LeetCode Problem Header: Title, Difficulty Badge, Topic Tag, and 💡 Problem Hint */}
                  <div className="shrink-0 px-3.5 py-2.5 border-b border-slate-800 bg-slate-950 flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-2.5 flex-wrap">
                      <div className="flex items-center gap-1.5">
                        <span className="text-xs font-mono font-bold text-indigo-400">#{questionCount}.</span>
                        <h3 className="text-xs sm:text-sm font-bold text-white tracking-tight" title={currentProblemTitle || "Algorithmic Problem"}>
                          {currentProblemTitle || "Algorithmic Challenge"}
                        </h3>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                        difficulty === "Easy"
                          ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                          : difficulty === "Hard"
                          ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                          : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                      }`}>
                        {difficulty}
                      </span>
                      <span className="px-2 py-0.5 rounded-full bg-slate-800/90 border border-slate-700/70 text-[10px] text-slate-300 font-mono">
                        {topic || "DSA"}
                      </span>
                    </div>

                    {/* Dedicated Problem-Solving Hint Button */}
                    <div className="flex items-center gap-2">
                      <button
                        type="button"
                        onClick={() => {
                          if (lastInterviewerIdx !== -1) {
                            handleFetchHint(lastInterviewerIdx, currentQuestionText);
                          }
                        }}
                        disabled={hintLoadingIdx !== null}
                        className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 border border-amber-500/40 text-amber-300 text-xs font-bold transition-all cursor-pointer shadow-sm active:scale-95"
                        title="Get an on-demand algorithmic hint without spoiling the solution"
                      >
                        {hintLoadingIdx !== null ? (
                          <span className="animate-spin text-xs">⟳</span>
                        ) : (
                          <span>💡</span>
                        )}
                        <span>{currentHint ? `Hint (L${currentHint.hint_level}/3)` : "Problem Hint"}</span>
                      </button>
                    </div>
                  </div>

                  {/* Active Problem Hint Banner (Expandable directly in Problem Solving) */}
                  {currentHint && (
                    <div className="shrink-0 px-3.5 py-2 bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-950 border-b border-amber-500/30 text-xs text-amber-200 flex items-start justify-between gap-3 animate-in fade-in">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 font-bold text-amber-300">
                          <span>💡 Hint {currentHint.hint_level} / 3:</span>
                          <span className="text-[10px] font-mono px-1.5 py-0.2 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30">
                            {currentHint.category}
                          </span>
                        </div>
                        <p className="leading-relaxed text-amber-100/90 text-[11px] sm:text-xs">{currentHint.hint}</p>
                      </div>
                      {currentHint.hint_level < 3 && (
                        <button
                          type="button"
                          onClick={() => {
                            if (lastInterviewerIdx !== -1) {
                              handleFetchHint(lastInterviewerIdx, currentQuestionText);
                            }
                          }}
                          disabled={hintLoadingIdx !== null}
                          className="shrink-0 text-[10px] sm:text-[11px] font-semibold text-amber-400 hover:text-amber-200 underline cursor-pointer whitespace-nowrap"
                        >
                          Next Hint ({currentHint.hint_level + 1}/3) ➔
                        </button>
                      )}
                    </div>
                  )}

                  {/* Editor Sub-Header: Tabs & LeetCode Language Selector */}
                  <div className="shrink-0 px-3 py-1.5 border-b border-slate-800 bg-slate-900/90 flex items-center justify-between flex-wrap gap-2">
                    <div className="flex items-center gap-1.5 flex-wrap">
                      <button
                        type="button"
                        onClick={() => setActiveCodeTab("problem")}
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                          activeCodeTab === "problem"
                            ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        Problem 📋
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveCodeTab("editor")}
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer ${
                          activeCodeTab === "editor"
                            ? "bg-slate-800 text-white border border-slate-700 shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        Code Editor 💻
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveCodeTab("output")}
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1 ${
                          activeCodeTab === "output"
                            ? "bg-emerald-600/30 text-emerald-300 border border-emerald-500/40 shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <span>Run & Output ▶</span>
                        {codeRunResult && (
                          <span className={`w-2 h-2 rounded-full ${codeRunResult.passed ? "bg-emerald-400" : "bg-rose-400"}`} />
                        )}
                      </button>
                      <button
                        type="button"
                        onClick={() => setActiveCodeTab("loopholes")}
                        className={`px-2.5 py-1 rounded-lg text-xs font-bold transition-all cursor-pointer flex items-center gap-1 ${
                          activeCodeTab === "loopholes"
                            ? "bg-indigo-600/30 text-indigo-300 border border-indigo-500/40 shadow-sm"
                            : "text-slate-400 hover:text-slate-200"
                        }`}
                      >
                        <span>Loophole Analysis 🔍</span>
                        {codeAnalysisResult && (
                          <span className={`w-2 h-2 rounded-full ${codeAnalysisResult.status === "Passed" ? "bg-emerald-400" : "bg-amber-400"}`} />
                        )}
                      </button>
                    </div>

                    <div className="flex items-center gap-2">
                      {/* LeetCode-Style Language Selector Dropdown */}
                      <div className="relative">
                        <button
                          type="button"
                          onClick={() => setIsLanguageDropdownOpen(!isLanguageDropdownOpen)}
                          className="flex items-center gap-2 px-2.5 py-1 rounded-lg bg-slate-950 hover:bg-slate-900 border border-slate-700/80 hover:border-slate-600 text-xs text-slate-200 font-medium transition-all cursor-pointer shadow-sm active:scale-95"
                        >
                          <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold font-mono border ${
                            LEETCODE_LANGUAGES.find((l) => l.id === codeLanguage)?.color || "text-indigo-400 bg-indigo-500/10 border-indigo-500/30"
                          }`}>
                            {LEETCODE_LANGUAGES.find((l) => l.id === codeLanguage)?.badge || codeLanguage}
                          </span>
                          <span className="hidden sm:inline font-mono text-[11px]">
                            {LEETCODE_LANGUAGES.find((l) => l.id === codeLanguage)?.label || codeLanguage}
                          </span>
                          <svg className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isLanguageDropdownOpen ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>

                        {isLanguageDropdownOpen && (
                          <>
                            <div
                              className="fixed inset-0 z-40"
                              onClick={() => setIsLanguageDropdownOpen(false)}
                            />
                            <div className="absolute right-0 mt-1.5 w-52 rounded-xl bg-slate-900/95 backdrop-blur-md border border-slate-700/90 shadow-2xl py-1.5 z-50 animate-in fade-in zoom-in-95">
                              <div className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-slate-400 border-b border-slate-800">
                                Select Language
                              </div>
                              <div className="py-1">
                                {LEETCODE_LANGUAGES.map((lang) => {
                                  const isSelected = codeLanguage === lang.id;
                                  return (
                                    <button
                                      key={lang.id}
                                      type="button"
                                      onClick={() => handleLanguageChange(lang.id)}
                                      className={`w-full px-3 py-2 text-left text-xs flex items-center justify-between transition-colors cursor-pointer ${
                                        isSelected
                                          ? "bg-indigo-600/20 text-indigo-300 font-semibold"
                                          : "text-slate-300 hover:bg-slate-800 hover:text-white"
                                      }`}
                                    >
                                      <div className="flex items-center gap-2">
                                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold font-mono border ${lang.color}`}>
                                          {lang.badge}
                                        </span>
                                        <span>{lang.label}</span>
                                      </div>
                                      {isSelected && (
                                        <svg className="w-3.5 h-3.5 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M5 13l4 4L19 7" />
                                        </svg>
                                      )}
                                    </button>
                                  );
                                })}
                              </div>
                            </div>
                          </>
                        )}
                      </div>

                      {/* Run Code / Compile Button */}
                      <button
                        type="button"
                        onClick={handleRunCode}
                        disabled={isRunningCode}
                        className="px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all cursor-pointer shadow-sm flex items-center gap-1 active:scale-95"
                        title="Compile and run your solution safely in the sandbox (Ctrl+Enter)"
                      >
                        {isRunningCode ? <span className="animate-spin text-xs">⟳</span> : <span>▶</span>}
                        <span>Run</span>
                      </button>

                      {/* Analyze & Find Loopholes Button */}
                      <button
                        type="button"
                        onClick={handleAnalyzeCodeLoopholes}
                        disabled={isAnalyzingCode}
                        className="px-2.5 py-1 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all cursor-pointer shadow-sm flex items-center gap-1 active:scale-95"
                        title="Scan code for boundary bugs, quadratic loops, and company standard loopholes"
                      >
                        {isAnalyzingCode ? <span className="animate-spin text-xs">⟳</span> : <span>🔍</span>}
                        <span>Loopholes</span>
                      </button>
                    </div>
                  </div>

                  {/* Tab 0: Problem Statement Description Tab */}
                  {activeCodeTab === "problem" && (
                    <div className="flex-1 min-h-0 h-full flex flex-col p-4 space-y-3 overflow-y-auto font-sans">
                      <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                        <div className="space-y-1">
                          <h2 className="text-base font-bold text-white flex items-center gap-2">
                            <span className="text-indigo-400 font-mono">#{questionCount}.</span>
                            <span>{currentProblemTitle || "Algorithmic Challenge"}</span>
                          </h2>
                          <div className="flex items-center gap-2">
                            <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                              difficulty === "Easy"
                                ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                                : difficulty === "Hard"
                                ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                                : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                            }`}>
                              {difficulty}
                            </span>
                            <span className="px-2 py-0.5 rounded-full bg-slate-800/90 text-[10px] text-slate-300 font-mono border border-slate-700/80">
                              {topic || "DSA"}
                            </span>
                          </div>
                        </div>
                        <button
                          type="button"
                          onClick={() => setActiveCodeTab("editor")}
                          className="px-3 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold transition-all shadow-md flex items-center gap-1.5 cursor-pointer active:scale-95"
                        >
                          <span>Open Code Editor 💻</span>
                        </button>
                      </div>

                      <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-slate-200 text-xs sm:text-sm leading-relaxed whitespace-pre-wrap select-text">
                        {currentQuestionText || "Awaiting problem description..."}
                      </div>
                    </div>
                  )}

                  {/* Tab 1: Full-Height Code Editor Workspace */}
                  {activeCodeTab === "editor" && (
                    <div className="flex-1 min-h-0 h-full flex flex-col p-3 space-y-2 overflow-hidden">
                      <div className="shrink-0 flex items-center justify-between text-[11px] text-slate-400">
                        <span className="flex items-center gap-2">
                          <span>Tab indents 4 spaces.</span>
                          <span className="text-emerald-400 font-mono font-semibold">Ctrl+Enter to Run ▶</span>
                        </span>
                        {selectedCompany && (
                          <span className="text-indigo-400 font-mono font-semibold">Bar: {selectedCompany}</span>
                        )}
                      </div>

                      {/* Textarea stretches 100% of the available vertical space */}
                      <div className="flex-1 min-h-0 h-full w-full relative rounded-xl border border-slate-800/90 bg-slate-950 flex flex-col overflow-hidden shadow-inner">
                        <textarea
                          value={codeSnippet}
                          onChange={(e) => setCodeSnippet(e.target.value)}
                          onKeyDown={(e) => {
                            if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
                              e.preventDefault();
                              handleRunCode();
                              return;
                            }
                            if (e.key === "Tab") {
                              e.preventDefault();
                              const target = e.currentTarget;
                              const start = target.selectionStart;
                              const end = target.selectionEnd;
                              const next = codeSnippet.substring(0, start) + "    " + codeSnippet.substring(end);
                              setCodeSnippet(next);
                              setTimeout(() => {
                                target.selectionStart = target.selectionEnd = start + 4;
                              }, 0);
                            } else if (e.key === "Enter") {
                              e.preventDefault();
                              const target = e.currentTarget;
                              const start = target.selectionStart;
                              const end = target.selectionEnd;
                              const textBefore = codeSnippet.substring(0, start);
                              const lines = textBefore.split("\n");
                              const currentLine = lines[lines.length - 1];
                              const match = currentLine.match(/^(\s*)/);
                              let indent = match ? match[1] : "";
                              const trimmed = currentLine.trim();
                              if (trimmed.endsWith(":") || trimmed.endsWith("{") || trimmed.endsWith("[")) {
                                indent += "    ";
                              }
                              const insertion = "\n" + indent;
                              const next = codeSnippet.substring(0, start) + insertion + codeSnippet.substring(end);
                              setCodeSnippet(next);
                              setTimeout(() => {
                                target.selectionStart = target.selectionEnd = start + insertion.length;
                              }, 0);
                            }
                          }}
                          spellCheck={false}
                          className="w-full h-full flex-1 min-h-[350px] p-4 bg-transparent font-mono text-xs sm:text-sm text-emerald-300 focus:outline-none resize-none leading-relaxed selection:bg-indigo-500/30 overflow-y-auto"
                          placeholder="// Type your code solution here..."
                        />
                      </div>

                      {/* Bottom action strip */}
                      <div className="shrink-0 flex items-center justify-between pt-1 flex-wrap gap-2">
                        <button
                          type="button"
                          onClick={() => setCodeSnippet((starterSnippets && starterSnippets[codeLanguage]) || STARTER_CODE[codeLanguage] || "")}
                          className="text-[11px] text-slate-500 hover:text-slate-300 cursor-pointer"
                        >
                          Reset Clean Template
                        </button>
                        <div className="flex items-center gap-2">
                          <button
                            type="button"
                            onClick={handleRunCode}
                            disabled={isRunningCode}
                            className="px-2.5 py-1 rounded-lg bg-emerald-600/80 hover:bg-emerald-500 text-white text-xs font-semibold cursor-pointer flex items-center gap-1"
                          >
                            <span>▶ Run Code</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => {
                              if (!codeSnippet.trim()) {
                                handleRunCode();
                                return;
                              }
                              handleSubmitAnswer(codeSnippet);
                            }}
                            disabled={isAiThinking}
                            className="px-3 py-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold cursor-pointer flex items-center gap-1 shadow-sm"
                          >
                            <span>Submit Code 🚀</span>
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Tab 2: Real-Time Execution Sandbox & Output Panel */}
                  {activeCodeTab === "output" && (
                    <div className="flex-1 min-h-0 h-full overflow-y-auto p-4 space-y-3 font-mono">
                      {isRunningCode ? (
                        <div className="p-8 text-center space-y-3 font-sans">
                          <div className="w-8 h-8 border-3 border-emerald-500 border-t-transparent rounded-full animate-spin mx-auto" />
                          <p className="text-xs text-emerald-300 font-semibold">
                            Executing {codeLanguage} code in sandbox with subprocess timeout...
                          </p>
                        </div>
                      ) : !codeRunResult ? (
                        <div className="p-8 text-center space-y-2 font-sans">
                          <span className="text-2xl">▶</span>
                          <p className="text-xs text-slate-300 font-bold">No Code Run Yet</p>
                          <p className="text-[11px] text-slate-500">
                            Click "Run Code" to compile and execute your algorithm in real time to verify stdout and test cases.
                          </p>
                          <button
                            type="button"
                            onClick={handleRunCode}
                            disabled={isRunningCode}
                            className="mt-2 px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold cursor-pointer"
                          >
                            Run Code Now ▶
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-3 animate-in fade-in">
                          {/* Top Status & Runtime Bar */}
                          <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between font-sans">
                            <div className="flex items-center gap-2">
                              <span
                                className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                                  codeRunResult.passed
                                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                    : "bg-rose-500/20 text-rose-300 border border-rose-500/40"
                                }`}
                              >
                                {codeRunResult.status}
                              </span>
                              <span className="text-[11px] text-slate-300 font-mono">
                                ⚡ {codeRunResult.execution_time_ms} ms
                              </span>
                            </div>
                            <button
                              type="button"
                              onClick={handleRunCode}
                              className="text-[11px] px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold cursor-pointer"
                            >
                              Re-run ▶
                            </button>
                          </div>

                          {/* Standard Output */}
                          {codeRunResult.stdout ? (
                            <div className="space-y-1">
                              <div className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 font-sans">
                                Standard Output (stdout):
                              </div>
                              <pre className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-xs text-emerald-300 whitespace-pre-wrap overflow-x-auto leading-relaxed">
                                {codeRunResult.stdout}
                              </pre>
                            </div>
                          ) : (
                            <div className="p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-xs text-slate-500 italic">
                              No stdout generated. Use print(...) / console.log(...) to inspect intermediate variables.
                            </div>
                          )}

                          {/* Standard Error / Traceback */}
                          {codeRunResult.stderr && (
                            <div className="space-y-1">
                              <div className="text-[10px] font-bold uppercase tracking-wider text-rose-400 font-sans">
                                Errors / Traceback (stderr):
                              </div>
                              <pre className="p-3 rounded-xl bg-rose-950/40 border border-rose-500/40 text-xs text-rose-300 whitespace-pre-wrap overflow-x-auto leading-relaxed">
                                {codeRunResult.stderr}
                              </pre>
                            </div>
                          )}

                          {/* Test Cases Results */}
                          {codeRunResult.test_results && codeRunResult.test_results.length > 0 && (
                            <div className="space-y-2 font-sans">
                              <div className="flex items-center justify-between">
                                <div className="text-[10px] font-bold uppercase tracking-wider text-cyan-400">
                                  Test Case Verification:
                                </div>
                                <span
                                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                                    codeRunResult.passed
                                      ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                      : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                                  }`}
                                >
                                  {codeRunResult.test_results.filter((t) => t.passed).length} / {codeRunResult.test_results.length} Passed
                                </span>
                              </div>
                              <div className="space-y-1.5">
                                {codeRunResult.test_results.map((tr, i) => (
                                  <div
                                    key={i}
                                    className={`p-3 rounded-xl border text-xs flex flex-col gap-1.5 transition-all ${
                                      tr.passed
                                        ? "bg-emerald-950/20 border-emerald-500/30 text-emerald-200"
                                        : "bg-rose-950/25 border-rose-500/35 text-rose-200"
                                    }`}
                                  >
                                    <div className="flex items-center justify-between">
                                      <span className="font-bold text-white">Test Case #{tr.test_case || i + 1}</span>
                                      <span
                                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                          tr.passed
                                            ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                            : "bg-rose-500/25 text-rose-300 border border-rose-500/40"
                                        }`}
                                      >
                                        {tr.passed ? "Passed ✓" : "Failed ✗"}
                                      </span>
                                    </div>

                                    {tr.input && (
                                      <div className="text-[11px] text-slate-300 font-mono">
                                        <span className="text-slate-400 font-sans">Input: </span>
                                        <span>{tr.input}</span>
                                      </div>
                                    )}

                                    <div className="text-[11px] font-mono flex flex-wrap gap-x-4 gap-y-1 pt-0.5">
                                      {tr.expected && tr.expected !== "None" && tr.expected !== "null" && (
                                        <span className="text-slate-300">
                                          <span className="text-slate-400 font-sans">Expected: </span>
                                          <span className="text-emerald-300 font-bold">{tr.expected}</span>
                                        </span>
                                      )}
                                      {tr.output !== undefined && (
                                        <span className="text-slate-300">
                                          <span className="text-slate-400 font-sans">Returned: </span>
                                          <span
                                            className={
                                              tr.passed
                                                ? "text-emerald-300 font-bold"
                                                : "text-rose-300 font-bold underline"
                                            }
                                          >
                                            {String(tr.output)}
                                          </span>
                                        </span>
                                      )}
                                    </div>

                                    {tr.error && (
                                      <div className="text-[11px] text-rose-300 font-mono bg-rose-950/40 px-2.5 py-1 rounded-lg border border-rose-500/20">
                                        ⚠ {tr.error}
                                      </div>
                                    )}
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Custom Test Input Box */}
                          <div className="space-y-1.5 pt-2 border-t border-slate-800/80 font-sans">
                            <div className="flex items-center justify-between">
                              <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                                Custom Test Input (Optional):
                              </label>
                              {activeTestCases && activeTestCases.length > 0 && (
                                <div className="flex items-center gap-1.5 flex-wrap">
                                  <span className="text-[10px] text-slate-400">Cases:</span>
                                  {activeTestCases.map((tc, idx) => (
                                    <button
                                      key={idx}
                                      type="button"
                                      onClick={() => setCustomInput(tc.desc || "")}
                                      className={`px-2 py-0.5 rounded text-[10px] font-mono transition-all cursor-pointer ${
                                        customInput === tc.desc
                                          ? "bg-indigo-600 text-white font-bold shadow-sm"
                                          : "bg-slate-800 hover:bg-slate-700 text-slate-300"
                                      }`}
                                      title={`Load Test Case #${idx + 1}: ${tc.desc}`}
                                    >
                                      Case {idx + 1}
                                    </button>
                                  ))}
                                  {customInput && (
                                    <button
                                      type="button"
                                      onClick={() => setCustomInput("")}
                                      className="text-[10px] text-slate-400 hover:text-white underline cursor-pointer ml-1"
                                    >
                                      Clear
                                    </button>
                                  )}
                                </div>
                              )}
                            </div>
                            <div className="flex gap-2">
                              <input
                                type="text"
                                value={customInput}
                                onChange={(e) => setCustomInput(e.target.value)}
                                placeholder="e.g. nums=[2,7,11,15], target=9"
                                className="flex-1 px-3 py-1.5 rounded-lg bg-slate-950 border border-slate-700 text-xs text-white placeholder-slate-500 font-mono"
                              />
                              <button
                                type="button"
                                onClick={handleRunCode}
                                disabled={isRunningCode}
                                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 cursor-pointer"
                              >
                                Test Input
                              </button>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Tab 3: Loophole Analysis & Test Cases Panel */}
                  {activeCodeTab === "loopholes" && (
                    <div className="flex-1 min-h-0 h-full overflow-y-auto p-4 space-y-4">
                      {isAnalyzingCode ? (
                        <div className="p-8 text-center space-y-3">
                          <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto" />
                          <p className="text-xs text-indigo-300 font-semibold">
                            Analyzing code AST, edge-case vulnerabilities, and Big-O bounds...
                          </p>
                        </div>
                      ) : !codeAnalysisResult ? (
                        <div className="p-8 text-center space-y-2">
                          <span className="text-2xl">🔍</span>
                          <p className="text-xs text-slate-300 font-bold">No Loophole Scan Run Yet</p>
                          <p className="text-[11px] text-slate-500">
                            Click "Find Loopholes" to inspect your code for boundary vulnerabilities, edge cases, and Big-O bottlenecks.
                          </p>
                          <button
                            type="button"
                            onClick={handleAnalyzeCodeLoopholes}
                            className="mt-2 px-3 py-1.5 rounded-xl bg-indigo-600 text-white text-xs font-bold cursor-pointer"
                          >
                            Analyze Now
                          </button>
                        </div>
                      ) : (
                        <div className="space-y-4 animate-in fade-in">
                          {/* Top Verdict Bar */}
                          <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                            <div>
                              <div className="flex items-center gap-2">
                                <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                                  codeAnalysisResult.status === "Passed"
                                    ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                                    : "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                                }`}>
                                  {codeAnalysisResult.status}
                                </span>
                                <span className="text-xs font-bold text-white">Score: {codeAnalysisResult.score}/100</span>
                              </div>
                              <p className="text-[11px] text-slate-400 mt-1">{codeAnalysisResult.company_verdict}</p>
                            </div>
                            <div className="text-right font-mono text-xs">
                              <div className="text-cyan-400 font-bold">Time: {codeAnalysisResult.time_complexity}</div>
                              <div className="text-purple-400">Space: {codeAnalysisResult.space_complexity}</div>
                            </div>
                          </div>

                          {/* Loopholes Detected */}
                          <div className="space-y-2">
                            <h4 className="text-xs font-bold uppercase tracking-wider text-rose-400 flex items-center gap-1.5">
                              <span>⚠️</span> Loopholes & Edge Cases Identified
                            </h4>
                            <div className="space-y-1.5">
                              {codeAnalysisResult.loopholes.map((lh, i) => (
                                <div key={i} className="p-2.5 rounded-lg bg-rose-950/30 border border-rose-500/30 text-xs text-rose-200">
                                  {lh}
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Test Cases Matrix */}
                          {codeAnalysisResult.test_case_results.length > 0 && (
                            <div className="space-y-2">
                              <h4 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                                <span>🧪</span> Test Case Validation Matrix
                              </h4>
                              <div className="space-y-1.5 font-mono text-[11px]">
                                {codeAnalysisResult.test_case_results.map((tc, idx) => (
                                  <div key={tc.test_case ?? idx} className="p-2 rounded-lg bg-slate-900 border border-slate-800 flex items-center justify-between">
                                    <div>
                                      <span className="text-slate-400">Case #{tc.test_case ?? (idx + 1)}: </span>
                                      <span className="text-slate-200">{tc.input} ➔ Expected: {tc.expected}</span>
                                    </div>
                                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                                      (tc.status === "Passed" || tc.passed)
                                        ? "bg-emerald-500/20 text-emerald-300"
                                        : "bg-amber-500/20 text-amber-300"
                                    }`}>
                                      {tc.status || (tc.passed ? "Passed" : "Edge Review")}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Interviewer Probe Question */}
                          <div className="p-3 rounded-xl bg-indigo-950/40 border border-indigo-500/30 text-xs space-y-1">
                            <div className="text-[10px] font-bold uppercase tracking-wider text-indigo-400">
                              Interviewer Follow-up Question Generated from Code:
                            </div>
                            <p className="text-slate-200 leading-relaxed font-sans">{codeAnalysisResult.interviewer_probe}</p>
                          </div>

                          {/* Quick Action to copy/insert analysis into input */}
                          <button
                            type="button"
                            onClick={() => {
                              const note = `My solution runs in Time: ${codeAnalysisResult.time_complexity}, Space: ${codeAnalysisResult.space_complexity}.`;
                              setCandidateInput((prev) => (prev ? `${prev}\n${note}` : note));
                              setActiveCodeTab("editor");
                            }}
                            className="w-full py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors cursor-pointer"
                          >
                            Insert Complexity into Chat Answer
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* ================= 6. THE REPORT SCREEN ================= */}
        {screen === "report" && (
          <div className="w-full max-w-3xl mx-auto py-6 space-y-6 animate-in fade-in duration-300">
            {/* Loading State */}
            {isReportLoading && (
              <div className="p-12 rounded-2xl bg-slate-900/80 border border-slate-800 text-center space-y-4 shadow-2xl backdrop-blur-xl">
                <div className="w-12 h-12 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto shadow-lg shadow-indigo-500/20" />
                <h3 className="text-lg font-bold text-white">Synthesizing Comprehensive Evaluation...</h3>
                <p className="text-xs text-slate-400 max-w-sm mx-auto">
                  Compiling detailed feedback, score breakdown, technical depth, and company alignment.
                </p>
              </div>
            )}

            {/* Error State with Retry Button */}
            {reportError && !isReportLoading && (
              <div className="p-8 rounded-2xl bg-rose-950/40 border border-rose-500/50 text-center space-y-4 shadow-2xl backdrop-blur-xl">
                <div className="w-10 h-10 rounded-full bg-rose-500/20 text-rose-400 flex items-center justify-center mx-auto text-xl font-bold">
                  !
                </div>
                <h3 className="text-base font-bold text-white">Failed to Generate Report</h3>
                <p className="text-xs text-rose-300 max-w-md mx-auto">{reportError}</p>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => handleGenerateReport()}
                    className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors cursor-pointer"
                  >
                    Retry Report Generation
                  </button>
                  <button
                    type="button"
                    onClick={handleStartNewInterview}
                    className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors cursor-pointer"
                  >
                    Back to Start
                  </button>
                </div>
              </div>
            )}

            {/* Generated Report Card */}
            {report && !isReportLoading && (
              <div className="space-y-6 animate-in fade-in duration-300">
                {/* Header & Score Gauge */}
                <div className="bg-slate-900/80 border border-slate-800/90 rounded-2xl p-6 sm:p-8 backdrop-blur-2xl shadow-2xl flex flex-col sm:flex-row items-center justify-between gap-6 ring-1 ring-white/5">
                  <div className="space-y-1.5 text-center sm:text-left">
                    <span className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                      Interview Complete
                    </span>
                    <h2 className="text-2xl sm:text-3xl font-black text-white">
                      Evaluation Report
                    </h2>
                    <p className="text-xs text-slate-400">
                      Focus: <span className="text-white font-semibold">{topic || "Technical Deep-Dive"}</span>
                      {selectedCompany && (
                        <span> • Target Company: <strong className="text-indigo-300">{selectedCompany}</strong></span>
                      )}
                      {" "}• Questions: <strong className="text-white">{totalQuestions}</strong> • Difficulty:{" "}
                      <span className="text-white font-semibold">{difficulty}</span>
                      {resumeFileName && " • Resume Cross-Examined"}
                      {totalHintsUsed > 0 && ` • ${totalHintsUsed} Hint(s) Used`}
                    </p>
                  </div>

                  {/* Score & Verdict Badges */}
                  <div className="flex items-center gap-5">
                    {/* Big Score Box */}
                    <div
                      className={`w-28 h-28 rounded-2xl flex flex-col items-center justify-center border shadow-xl ${
                        report.score >= 85
                          ? "bg-emerald-950/40 border-emerald-500/60 text-emerald-400 shadow-emerald-500/20"
                          : report.score >= 70
                          ? "bg-blue-950/40 border-blue-500/60 text-blue-400 shadow-blue-500/20"
                          : report.score >= 55
                          ? "bg-amber-950/40 border-amber-500/60 text-amber-400 shadow-amber-500/20"
                          : "bg-rose-950/40 border-rose-500/60 text-rose-400 shadow-rose-500/20"
                      }`}
                    >
                      <span className="text-4xl font-black">{report.score}</span>
                      <span className="text-[10px] font-bold uppercase tracking-wider opacity-75">/ 100</span>
                      <span className="text-[10px] font-semibold mt-0.5">{report.rating_label}</span>
                    </div>

                    {/* PASS / FAIL Indicator */}
                    <div className="space-y-2">
                      <div
                        className={`px-4 py-2 rounded-xl text-sm font-black uppercase tracking-wider text-center border shadow-sm ${
                          report.status === "Pass"
                            ? "bg-emerald-500/20 border-emerald-500/50 text-emerald-300"
                            : "bg-rose-500/20 border-rose-500/50 text-rose-300"
                        }`}
                      >
                        {report.status === "Pass" ? "✓ PASS" : "✗ FAIL"}
                      </div>
                      <div className="text-[10px] text-slate-500 text-center leading-tight">
                        85+ Excellent • 70-84 Good<br />55-69 Adequate • &lt;55 Weak
                      </div>
                    </div>
                  </div>
                </div>

                {/* Target Company Alignment Section (if company selected) */}
                {report.company_alignment && (
                  <div className="bg-gradient-to-r from-purple-950/40 to-slate-900/60 border border-purple-500/40 rounded-2xl p-5 sm:p-6 backdrop-blur-sm space-y-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-purple-400 flex items-center gap-1.5">
                      <span>🏢</span> Target Company Bar Alignment ({selectedCompany})
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">
                      {report.company_alignment}
                    </p>
                  </div>
                )}

                {/* Score Breakdown Bar Gauges */}
                {report.score_breakdown && (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 backdrop-blur-sm space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400">
                      Performance Dimension Breakdown
                    </h3>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                      {Object.entries(report.score_breakdown).map(([dim, val]) => (
                        <div key={dim} className="space-y-1">
                          <div className="flex justify-between text-xs">
                            <span className="text-slate-300 font-medium">{dim}</span>
                            <span className="text-slate-200 font-bold">{val}%</span>
                          </div>
                          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
                            <div
                              className={`h-2 rounded-full transition-all duration-500 ${
                                val >= 80 ? "bg-emerald-500" : val >= 65 ? "bg-indigo-500" : "bg-amber-500"
                              }`}
                              style={{ width: `${val}%` }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Interviewer's Verdict Section */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 backdrop-blur-sm space-y-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                    Interviewer's Overall Verdict
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed">
                    {report.overall_verdict}
                  </p>
                </div>

                {/* Resume Alignment Analysis Section (if present) */}
                {report.resume_alignment && (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 backdrop-blur-sm space-y-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-indigo-400 flex items-center gap-1.5">
                      <span>📄</span> Resume Alignment Analysis
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                      {report.resume_alignment}
                    </p>
                  </div>
                )}

                {/* DSA & Complexity Analysis Section (if present) */}
                {report.dsa_complexity_analysis && (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 backdrop-blur-sm space-y-2">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                      <span>⏱️</span> DSA Time & Space Complexity Evaluation
                    </h3>
                    <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                      {report.dsa_complexity_analysis}
                    </p>
                  </div>
                )}

                {/* Question-by-Question Detailed Feedback */}
                {report.detailed_feedback && report.detailed_feedback.length > 0 && (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-3">
                    <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                      Question-by-Question Detailed Feedback
                    </h3>
                    <div className="space-y-2.5">
                      {report.detailed_feedback.map((fb, idx) => (
                        <div key={idx} className="p-3.5 rounded-xl bg-slate-950/50 border border-slate-800/90 text-xs space-y-1">
                          <div className="flex items-center justify-between">
                            <span className="font-bold text-white">{fb.question}</span>
                            <span
                              className={`text-[10px] font-semibold px-2 py-0.5 rounded-full ${
                                fb.assessment.includes("Strong")
                                  ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                                  : fb.assessment.includes("Partially")
                                  ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                                  : "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                              }`}
                            >
                              {fb.assessment}
                            </span>
                          </div>
                          <p className="text-slate-300 leading-relaxed">{fb.detail}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Strengths & Areas for Improvement */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                  {/* Strengths */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-3">
                    <div className="flex items-center gap-2 text-emerald-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-white">Strengths</h3>
                    </div>
                    <ul className="space-y-2">
                      {report.strengths.map((str, i) => (
                        <li key={i} className="text-xs text-slate-300 bg-slate-950/40 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                          {str}
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Areas for Improvement */}
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-3">
                    <div className="flex items-center gap-2 text-amber-400">
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                      </svg>
                      <h3 className="text-xs font-bold uppercase tracking-wider text-white">Areas for Improvement</h3>
                    </div>
                    <ul className="space-y-2">
                      {report.weaknesses.map((weak, i) => (
                        <li key={i} className="text-xs text-slate-300 bg-slate-950/40 p-3 rounded-xl border border-slate-800/80 leading-relaxed">
                          {weak}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                {/* Topics to Revise Section */}
                <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-5 sm:p-6 space-y-3">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400">
                    Topics to Revise
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {report.topics_to_revise.map((rev, i) => (
                      <span
                        key={i}
                        className="text-xs px-3 py-1.5 rounded-lg bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 font-medium"
                      >
                        📖 {rev}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Full Transcript Accordion */}
                <div className="bg-slate-900/40 border border-slate-800 rounded-2xl p-4">
                  <button
                    type="button"
                    onClick={() => setShowTranscript(!showTranscript)}
                    className="w-full flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white transition-colors cursor-pointer"
                  >
                    <span>{showTranscript ? "Hide Full Interview Transcript" : "View Full Interview Transcript"} ({conversation.length} messages)</span>
                    <span>{showTranscript ? "▲" : "▼"}</span>
                  </button>

                  {showTranscript && (
                    <div className="mt-4 space-y-3 pt-3 border-t border-slate-800">
                      {conversation.map((m, idx) => (
                        <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 text-xs">
                          <span className="font-bold text-indigo-400 uppercase tracking-wider block mb-1">
                            {m.role === "interviewer" ? "Interviewer:" : "You:"}
                          </span>
                          <span className="whitespace-pre-wrap text-slate-300">{m.content}</span>
                          {m.code_snippet && (
                            <pre className="mt-2 p-2 rounded bg-slate-900 text-emerald-300 font-mono text-[10px] overflow-x-auto">
                              {m.code_snippet}
                            </pre>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Action Buttons: Start New Interview, Copy Report */}
                <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-2">
                  <button
                    type="button"
                    onClick={handleStartNewInterview}
                    className="w-full sm:w-auto px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all cursor-pointer shadow-lg shadow-indigo-600/30"
                  >
                    Start New Interview
                  </button>

                  <div className="flex items-center gap-2 w-full sm:w-auto">
                    <button
                      type="button"
                      onClick={copyReportToClipboard}
                      className="flex-1 sm:flex-initial px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors cursor-pointer"
                    >
                      {copiedReport ? "✓ Copied to Clipboard" : "Copy Feedback"}
                    </button>
                    <button
                      type="button"
                      onClick={() => window.print()}
                      className="flex-1 sm:flex-initial px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700 transition-colors cursor-pointer"
                    >
                      Print Report
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </main>

      {/* ================= SETTINGS MODAL ================= */}
      {showSettings && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 space-y-5 shadow-2xl animate-in zoom-in-95">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Engine Settings</h3>
              <button
                type="button"
                onClick={() => setShowSettings(false)}
                className="text-slate-400 hover:text-white text-base font-bold cursor-pointer"
              >
                ✕
              </button>
            </div>

            <p className="text-xs text-slate-400 leading-relaxed">
              Powered by Groq ultra-fast LLM inference (Llama 3.3 / GPT-OSS) for authentic FAANG mock interview evaluations. You can also fall back to the Built-in engine anytime.
            </p>

            <div className="space-y-2">
              {[
                {
                  id: "groq" as const,
                  name: "Groq AI Engine (Recommended - Active)",
                  desc: "Ultra-fast ~500 tok/s real-time LLM for authentic FAANG questioning & code evaluation.",
                  icon: "⚡",
                },
                {
                  id: "builtin" as const,
                  name: "Built-in Intelligent Engine",
                  desc: "Zero API key required, 100% offline fallback with instant sub-millisecond responses.",
                  icon: "💻",
                },
              ].map(({ id, name, desc, icon }) => (
                <div
                  key={id}
                  onClick={() => setProvider(id)}
                  className={`p-3 rounded-xl border cursor-pointer transition-all ${
                    provider === id
                      ? "bg-indigo-600/15 border-indigo-500 ring-1 ring-indigo-500/40"
                      : "bg-slate-950/40 border-slate-800 hover:border-slate-700"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-white flex items-center gap-1.5">
                      <span>{icon}</span> {name}
                    </span>
                    {provider === id && <span className="text-[11px] text-emerald-400 font-bold">Active ✓</span>}
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{desc}</p>
                </div>
              ))}
            </div>

            {provider === "groq" && (
              <div>
                <label className="block text-[11px] font-semibold uppercase tracking-wider text-slate-300 mb-1">
                  Custom Groq API Key (Optional Override)
                </label>
                <input
                  type="password"
                  placeholder="Configured in backend .env (Leave blank to use .env key)"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl bg-slate-950 border border-slate-800 text-xs text-white placeholder-slate-600 focus:outline-none focus:border-indigo-500 font-mono"
                />
              </div>
            )}

            <div className="flex items-center justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={() => {
                  localStorage.setItem("ai_interview_api_key", apiKey);
                  localStorage.setItem("ai_interview_provider", provider);
                  setShowSettings(false);
                }}
                className="px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-md transition-colors cursor-pointer"
              >
                Save Preferences
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
