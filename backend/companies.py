"""
Company-Specific Interview Intelligence & Real-World Experiences
Covers: Google, Amazon, Meta, Microsoft, Apple, Netflix, Uber
"""
from typing import Dict, List, Optional, Any

COMPANY_PROFILES: Dict[str, Dict[str, Any]] = {
    "Google": {
        "tagline": "Algorithmic Rigor, Optimal Asymptotics & Extreme Scale",
        "interviewer_title": "Google Staff Software Engineer",
        "philosophy": (
            "Focuses on Big-O optimality, boundary edge cases (empty inputs, unicode, duplicate handling), "
            "algorithmic invariants, and clean maintainable code. Demands optimal Time and Auxiliary Space bounds."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: String Compression with Run-Length Encoding\n"
                    "Given an array of characters `chars`, compress it in-place such that groups of consecutive repeating characters are replaced by the character followed by the group's length.\n\n"
                    "**Test Cases:**\n"
                    "- Test Case 1: Input: `chars = [\"a\",\"a\",\"b\",\"b\",\"c\",\"c\",\"c\"]` ➔ Output: `6`, `[\"a\",\"2\",\"b\",\"2\",\"c\",\"3\"]`\n"
                    "- Test Case 2: Input: `chars = [\"a\"]` ➔ Output: `1`, `[\"a\"]`\n"
                    "- Test Case 3: Input: `chars = [\"a\",\"b\",\"b\",\"b\",\"b\",\"b\",\"b\",\"b\",\"b\",\"b\",\"b\",\"b\",\"b\"]` ➔ Output: `4`, `[\"a\",\"b\",\"1\",\"2\"]`\n\n"
                    "**Google Standard:** Must modify in-place using $O(1)$ auxiliary space in $O(N)$ time. How do you handle write pointers?"
                ),
                (
                    "### Problem: Meeting Rooms I (Interval Overlap)\n"
                    "Given an array of meeting time intervals where `intervals[i] = [start_i, end_i]`, determine if a person could attend all meetings without overlap.\n\n"
                    "**Test Cases:**\n"
                    "- Test Case 1: Input: `intervals = [[0,30],[5,10],[15,20]]` ➔ Output: `false`\n"
                    "- Test Case 2: Input: `intervals = [[7,10],[2,4]]` ➔ Output: `true`\n\n"
                    "**Google Standard:** What is the sorting invariant? State optimal Time Complexity ($O(N \\log N)$) and Space Complexity."
                ),
                (
                    "### Problem: Logger Rate Limiter\n"
                    "Design a logger system that receives a stream of messages with timestamps. Each unique message should only be printed at most once every 10 seconds.\n\n"
                    "**Test Cases:**\n"
                    "- `shouldPrintMessage(1, \"foo\")` ➔ `true`\n"
                    "- `shouldPrintMessage(2, \"bar\")` ➔ `true`\n"
                    "- `shouldPrintMessage(3, \"foo\")` ➔ `false`\n"
                    "- `shouldPrintMessage(11, \"foo\")` ➔ `true`\n\n"
                    "**Google Standard:** How do you clean up expired timestamps so memory doesn't grow unbounded over months in production?"
                ),
                (
                    "### Problem: Isomorphic Strings\n"
                    "Given two strings `s` and `t`, determine if they are isomorphic. Two strings are isomorphic if the characters in `s` can be replaced to get `t`.\n\n"
                    "**Test Cases:**\n"
                    "- Test Case 1: `s = \"egg\", t = \"add\"` ➔ `true`\n"
                    "- Test Case 2: `s = \"foo\", t = \"bar\"` ➔ `false`\n"
                    "- Test Case 3: `s = \"paper\", t = \"title\"` ➔ `true`\n\n"
                    "**Google Standard:** Explain why a bijection requires tracking two-way mappings or last-seen index arrays."
                ),
                (
                    "### Problem: Moving Average from Data Stream\n"
                    "Given a stream of integers and a window size `size`, calculate the moving average of all integers in the sliding window.\n\n"
                    "**Test Cases:**\n"
                    "- `MovingAverage(3)`: `next(1)` ➔ `1.0`, `next(10)` ➔ `5.5`, `next(3)` ➔ `4.666`, `next(5)` ➔ `6.0`\n\n"
                    "**Google Standard:** Achieve $O(1)$ time per `next` call with a circular array or queue."
                )
            ],
            "Medium": [
                (
                    "### Problem: Word Ladder (Shortest Transformation Sequence)\n"
                    "Given two words `beginWord` and `endWord`, and a dictionary `wordList`, return the number of words in the shortest transformation sequence from `beginWord` to `endWord` where only one letter changes at a time.\n\n"
                    "**Test Cases:**\n"
                    "- Test Case 1: `beginWord = \"hit\", endWord = \"cog\", wordList = [\"hot\",\"dot\",\"dog\",\"lot\",\"log\",\"cog\"]` ➔ Output: `5`\n"
                    "- Test Case 2: `beginWord = \"hit\", endWord = \"cog\", wordList = [\"hot\",\"dot\",\"dog\",\"lot\",\"log\"]` ➔ Output: `0`\n\n"
                    "**Google Standard:** Why does Bidirectional BFS significantly reduce the search branching factor compared to standard BFS?"
                ),
                (
                    "### Problem: Evaluate Reverse Polish Notation\n"
                    "Evaluate the value of an arithmetic expression in Reverse Polish Notation. Valid operators are `+`, `-`, `*`, `/`. Each operand may be an integer or another expression.\n\n"
                    "**Test Cases:**\n"
                    "- Test Case 1: `tokens = [\"2\",\"1\",\"+\",\"3\",\"*\"]` ➔ Output: `9`\n"
                    "- Test Case 2: `tokens = [\"4\",\"13\",\"5\",\"/\",\"+\"]` ➔ Output: `6`\n"
                    "- Test Case 3: `tokens = [\"10\",\"6\",\"9\",\"3\",\"+\",\"-11\",\"*\",\"/\",\"*\",\"17\",\"+\",\"5\",\"+\"]` ➔ Output: `22`\n\n"
                    "**Google Standard:** How do you handle integer division truncation towards zero for negative numbers across languages?"
                ),
                (
                    "### Problem: Snapshot Array\n"
                    "Implement a SnapshotArray that supports `set(index, val)`, `snap()`, and `get(index, snap_id)` where taking a snapshot must not duplicate memory for unchanged elements.\n\n"
                    "**Test Cases:**\n"
                    "- `SnapshotArray(3)`: `set(0, 5)`, `snap()` ➔ `0`, `set(0, 6)`, `get(0, 0)` ➔ `5`\n\n"
                    "**Google Standard:** Use a list of historical `(snap_id, val)` tuples per index with Binary Search (`bisect_right`) to achieve $O(1)$ snap and $O(\\log S)$ get."
                ),
                (
                    "### Problem: Reorganize String (No Adjacent Identical Characters)\n"
                    "Given a string `s`, rearrange the characters of `s` so that any two adjacent characters are not the same. Return empty string `\"\"` if not possible.\n\n"
                    "**Test Cases:**\n"
                    "- Test Case 1: `s = \"aab\"` ➔ Output: `\"aba\"`\n"
                    "- Test Case 2: `s = \"aaab\"` ➔ Output: `\"\"`\n\n"
                    "**Google Standard:** Detail the max-heap frequency approach versus bucket placement. State exact time bounds."
                ),
                (
                    "### Problem: Design a Search Autocomplete System (Trie + Frequency)\n"
                    "Design a search autocomplete system for a search engine. When a user inputs a character, return the top 3 historical hot sentences that have the same prefix as the part of sentence already typed.\n\n"
                    "**Google Standard:** Compare storing top-3 sentences directly at each Trie node versus on-demand DFS traversal."
                )
            ],
            "Hard": [
                (
                    "### Problem: Alien Dictionary (Topological Sort)\n"
                    "There is a new alien language that uses the Latin alphabet. Given a list of words from the alien dictionary sorted lexicographically, derive the order of letters in this language.\n\n"
                    "**Test Cases:**\n"
                    "- Test Case 1: `words = [\"wrt\",\"wrf\",\"er\",\"ett\",\"rftt\"]` ➔ Output: `\"wertf\"`\n"
                    "- Test Case 2: `words = [\"z\",\"x\"]` ➔ Output: `\"zx\"`\n"
                    "- Test Case 3: `words = [\"z\",\"x\",\"z\"]` ➔ Output: `\"\"` (Invalid cycle detected)\n\n"
                    "**Google Standard:** How do you detect prefix invalidity (e.g., `[\"abc\", \"ab\"]`) and cycles in the directed graph?"
                ),
                (
                    "### Problem: Text Justification\n"
                    "Given an array of strings `words` and a width `maxWidth`, format the text such that each line has exactly `maxWidth` characters and is fully (left and right) justified.\n\n"
                    "**Test Cases:**\n"
                    "- Words = `[\"This\", \"is\", \"an\", \"example\", \"of\", \"text\", \"justification.\"]`, `maxWidth = 16`\n\n"
                    "**Google Standard:** Walk through space distribution math when spaces do not divide evenly across word gaps. How is the last line treated?"
                ),
                (
                    "### Problem: Sliding Window Maximum (Monotonic Queue)\n"
                    "Given an array of integers `nums` and window size `k`, return the maximum for each sliding window moving from left to right in amortized $O(N)$ time.\n\n"
                    "**Google Standard:** Explain the invariant of the double-ended queue (monotonic decreasing indices) and prove why each element is pushed/popped at most once."
                ),
                (
                    "### Problem: Design Distributed Web Crawler\n"
                    "Design a scalable distributed web crawler that can crawl 10 billion web pages per month. Address URL frontier prioritization, duplicate detection (Bloom filters), politeness per host, and distributed worker synchronization.\n\n"
                    "**Google Standard:** How do you prevent crawler traps and handle domain DNS resolution latency bottlenecks?"
                )
            ]
        }
    },
    "Amazon": {
        "tagline": "Customer Obsession, Leadership Principles & High-Scale Systems",
        "interviewer_title": "Amazon Bar Raiser & Principal SDE",
        "philosophy": (
            "Interweaves technical depth with Amazon Leadership Principles: Customer Obsession, Ownership, "
            "Invent and Simplify, Bias for Action, and Dive Deep. Expects candidate to justify operational SLAs, "
            "idempotency, and cost/latency trade-offs."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Reorder Data in Log Files\n"
                    "You have an array of `logs`. Letter-logs come before digit-logs. Letter-logs are sorted lexicographically by content, then identifier. Digit-logs maintain original order.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `logs = [\"dig1 8 1 5 1\",\"let1 art can\",\"dig2 3 6\",\"let2 own kit dig\",\"let3 art zero\"]`\n"
                    "  Output: `[\"let1 art can\",\"let3 art zero\",\"let2 own kit dig\",\"dig1 8 1 5 1\",\"dig2 3 6\"]`\n\n"
                    "**Amazon LP Context:** In high-volume CloudWatch ingestion pipelines, how does a custom sort key ensure stable and deterministic ordering?"
                ),
                (
                    "### Problem: Number of Recent Calls (Counter Window)\n"
                    "Design a counter for the number of customer requests received in the past 3000 milliseconds: `ping(t)`.\n\n"
                    "**Test Cases:**\n"
                    "- `ping(1)` ➔ `1`, `ping(100)` ➔ `2`, `ping(3001)` ➔ `3`, `ping(3002)` ➔ `3`\n\n"
                    "**Amazon LP Context:** When monitoring customer shopping traffic on Prime Day, why is a queue-based sliding window more cost-effective than continuous polling?"
                ),
                (
                    "### Problem: Most Common Word (Excluding Banned Words)\n"
                    "Given a string `paragraph` of customer reviews and an array of `banned` words, return the most frequent non-banned word in lowercase.\n\n"
                    "**Test Cases:**\n"
                    "- `paragraph = \"Bob hit a ball, the hit BALL flew far after it was hit.\", banned = [\"hit\"]` ➔ Output: `\"ball\"`\n\n"
                    "**Amazon LP Context:** How do you sanitize punctuation efficiently without regex overhead at enterprise scale?"
                )
            ],
            "Medium": [
                (
                    "### Problem: Rotten Oranges (Warehouse Spoilage Simulation)\n"
                    "You are given an `m x n` grid where each cell is empty (0), fresh orange (1), or rotten orange (2). Every minute, any fresh orange adjacent (4-directionally) to a rotten orange rots. Return minimum minutes until no fresh orange remains, or `-1`.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `grid = [[2,1,1],[1,1,0],[0,1,1]]` ➔ Output: `4`\n"
                    "- Input: `grid = [[2,1,1],[0,1,1],[1,0,1]]` ➔ Output: `-1`\n\n"
                    "**Amazon Standard:** Explain why Multi-Source BFS is strictly required rather than independent DFS traversals."
                ),
                (
                    "### Problem: K Closest Points to Fulfillment Center\n"
                    "Given an array of delivery coordinates `points` where `points[i] = [x_i, y_i]` and an integer `k`, return the `k` closest packages to the origin `(0, 0)`.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `points = [[1,3],[-2,2]], k = 1` ➔ Output: `[[-2,2]]`\n"
                    "- Input: `points = [[3,3],[5,-1],[-2,4]], k = 2` ➔ Output: `[[3,3],[-2,4]]`\n\n"
                    "**Amazon LP Context:** Compare QuickSelect ($O(N)$ average) vs Max-Heap ($O(N \\log K)$ worst-case). Why does Amazon production prefer Max-Heap for real-time delivery routing streams?"
                ),
                (
                    "### Problem: Design Amazon Locker Delivery System\n"
                    "Architect an automated package delivery locker system. Lockers come in 3 sizes (Small, Medium, Large). Packages are assigned optimal lockers based on dimensions. Support package drop-off by courier, pickup PIN generation, and expiration handling.\n\n"
                    "**Amazon LP (Customer Obsession):** How does your data model handle locker shortages when customer package volume surges?"
                ),
                (
                    "### Problem: Critical Connections in a Network (Bridges / Tarjan's Algorithm)\n"
                    "Given `n` Amazon server nodes and a list of bidirectional cable `connections`, find all critical connections whose removal leaves some servers unable to communicate.\n\n"
                    "**Amazon Standard:** Explain Tarjan's DFS bridge-finding algorithm using discovery time and lowest reachable ancestor (`low[u]`)."
                )
            ],
            "Hard": [
                (
                    "### Problem: Design Highly Available Amazon Shopping Cart Service\n"
                    "Architect the shopping cart service supporting 100M active shoppers. Requirements: Low latency read/write (< 20ms p99), 99.999% availability, and cart items must never be lost even under data center network partitions (Dynamo-style eventual consistency with vector clocks).\n\n"
                    "**Amazon LP Context:** When a concurrent conflict occurs on a shopper's cart, how do you resolve it in favor of the customer?"
                ),
                (
                    "### Problem: Trapping Rain Water II (3D Elevation Map)\n"
                    "Given an `m x n` integer matrix `heightMap` representing the height of each unit cell in a 2D elevation map, return the volume of water it can trap after raining.\n\n"
                    "**Amazon Standard:** Walk through the Priority Queue (Min-Heap) boundary shrinkage algorithm in 3D."
                )
            ]
        }
    },
    "Meta": {
        "tagline": "High-Velocity Execution, Concurrency & Distributed Graph Scale",
        "interviewer_title": "Meta Senior Infrastructure Engineer",
        "philosophy": (
            "Focuses on fast, bug-free implementation, optimal time complexity, graph traversals, and high-concurrency systems. "
            "Prefers iterative solutions, zero redundant allocations, and clear communication under time pressure."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Valid Palindrome II (At Most One Deletion)\n"
                    "Given a string `s`, return `true` if the `s` can be palindrome after deleting at most one character from it.\n\n"
                    "**Test Cases:**\n"
                    "- `s = \"aba\"` ➔ `true`\n"
                    "- `s = \"abca\"` ➔ `true` (delete 'c')\n"
                    "- `s = \"abc\"` ➔ `false`\n\n"
                    "**Meta Standard:** Provide the two-pointer greedy approach running in $O(N)$ time and $O(1)$ space."
                ),
                (
                    "### Problem: Minimum Remove to Make Valid Parentheses\n"
                    "Given a string `s` of `'('`, `')'`, and lowercase letters, remove minimum parentheses so that the remaining string is valid.\n\n"
                    "**Test Cases:**\n"
                    "- `s = \"lee(t(c)o)de)\"` ➔ `\"lee(t(c)o)de\"`\n"
                    "- `s = \"a)b(c)d\"` ➔ `\"ab(c)d\"`\n"
                    "- `s = \"))((\"` ➔ `\"\"`\n\n"
                    "**Meta Standard:** Solve in two passes or using a stack of indices without string concatenation overhead."
                )
            ],
            "Medium": [
                (
                    "### Problem: Lowest Common Ancestor of a Binary Tree\n"
                    "Given a binary tree, find the lowest common ancestor (LCA) of two given nodes `p` and `q`.\n\n"
                    "**Test Cases:**\n"
                    "- Root: `[3,5,1,6,2,0,8,null,null,7,4]`, `p = 5`, `q = 1` ➔ Output: `3`\n"
                    "- Root: `[3,5,1,6,2,0,8,null,null,7,4]`, `p = 5`, `q = 4` ➔ Output: `5`\n\n"
                    "**Meta Standard:** Explain both the bottom-up post-order traversal and the iterative parent pointer dictionary approach."
                ),
                (
                    "### Problem: Binary Tree Vertical Order Traversal\n"
                    "Given the root of a binary tree, return the vertical order traversal of its nodes' values (from top to bottom, column by column from left to right).\n\n"
                    "**Test Cases:**\n"
                    "- Root: `[3,9,20,null,null,15,7]` ➔ `[[9],[3,15],[20],[7]]`\n\n"
                    "**Meta Standard:** Why must BFS with `(node, col)` queue be used instead of DFS to guarantee top-to-bottom row ordering without extra sorting?"
                ),
                (
                    "### Problem: Design Facebook News Feed (Fan-Out Architecture)\n"
                    "Architect the Meta News Feed for 2 billion active users. Compare Fan-Out-on-Write (Push to follower feeds on publish) vs Fan-Out-on-Read (Pull on app open). How do you handle high-follower celebrities (Justin Bieber problem)?"
                )
            ],
            "Hard": [
                (
                    "### Problem: Expression Add Operators\n"
                    "Given a string `num` that contains only digits and an integer `target`, return all possibilities to insert binary operators `'+'`, `'-'`, and `'*'` between the digits of `num` so that the resultant expression evaluates to `target`.\n\n"
                    "**Meta Standard:** How do you track the previous operand to properly handle operator precedence when multiplying in backtracking?"
                ),
                (
                    "### Problem: Design Meta Messenger (Real-Time Chat at Massive Scale)\n"
                    "Design a real-time messaging system supporting 1 billion active daily users. Address WebSocket gateway connection management, message ordering across distributed nodes, offline message storage, and end-to-end encryption key exchanges."
                )
            ]
        }
    },
    "Microsoft": {
        "tagline": "Production Resilience, Design Patterns & Enterprise Software Architecture",
        "interviewer_title": "Microsoft Principal Software Architect",
        "philosophy": (
            "Values clean object-oriented architecture, SOLID principles, defensive programming, "
            "comprehensive error handling, and robust memory management across enterprise cloud workloads."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Reverse Words in a String\n"
                    "Given an input string `s`, reverse the order of the words. Return a string of words joined by a single space with leading/trailing spaces trimmed.\n\n"
                    "**Test Cases:**\n"
                    "- `s = \"the sky is blue\"` ➔ `\"blue is sky the\"`\n"
                    "- `s = \"  hello world  \"` ➔ `\"world hello\"`\n\n"
                    "**Microsoft Standard:** How do you perform this in-place in languages with mutable string buffers?"
                )
            ],
            "Medium": [
                (
                    "### Problem: Serialize and Deserialize a Binary Tree\n"
                    "Design an algorithm to serialize a binary tree into a compact string representation and deserialize it back into the original tree structure.\n\n"
                    "**Test Cases:**\n"
                    "- Tree: `[1,2,3,null,null,4,5]` ➔ Serialized: `\"1,2,null,null,3,4,null,null,5,null,null\"`\n\n"
                    "**Microsoft Standard:** Compare Pre-order DFS serialization with BFS level-order serialization. How do you handle malformed string payloads?"
                ),
                (
                    "### Problem: Design Excel Spreadsheet Formula Evaluator\n"
                    "Design the core formula evaluation engine for Excel supporting basic arithmetic (`+`, `-`, `*`, `/`) and cell references (e.g. `A1 + B2 * 3`). Address cycle detection (circular dependency) and dependency graph recalculation."
                )
            ],
            "Hard": [
                (
                    "### Problem: Merge K Sorted Lists\n"
                    "You are given an array of `k` linked-lists `lists`, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list and return it.\n\n"
                    "**Microsoft Standard:** Compare Min-Heap $O(N \\log K)$ approach with Divide-and-Conquer $O(N \\log K)$ merge sort. What are the memory cache locality differences?"
                )
            ]
        }
    },
    "Apple": {
        "tagline": "Hardware-Software Co-Design, Low-Level Efficiency & Edge Precision",
        "interviewer_title": "Apple Senior Systems Engineer",
        "philosophy": (
            "Obsesses over memory footprint, cache line efficiency, zero-copy buffers, and edge-case precision. "
            "Asks candidates to reason about bit manipulation, ring buffers, and deterministic latency."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Single Number (Bit Manipulation)\n"
                    "Given a non-empty array of integers `nums`, every element appears twice except for one. Find that single one in linear runtime and $O(1)$ extra space.\n\n"
                    "**Test Cases:**\n"
                    "- `nums = [2,2,1]` ➔ `1`\n"
                    "- `nums = [4,1,2,1,2]` ➔ `4`\n\n"
                    "**Apple Standard:** Explain why XOR ($a \\oplus a = 0$ and $a \\oplus 0 = a$) guarantees the answer without hash table allocation."
                )
            ],
            "Medium": [
                (
                    "### Problem: Design Lock-Free Circular Ring Buffer\n"
                    "Design a circular FIFO queue with fixed capacity `k` that supports concurrent single-producer single-consumer without mutex locks using atomic head/tail pointers.\n\n"
                    "**Apple Standard:** How do you differentiate between an empty buffer and a full buffer without wasting a slot?"
                )
            ],
            "Hard": [
                (
                    "### Problem: LRU Cache with Memory Footprint Constraints\n"
                    "Implement a Least Recently Used cache designed for an embedded device constrained to strictly 4MB of RAM. Profile exact pointer overheads of doubly linked list nodes vs packed struct indices."
                )
            ]
        }
    },
    "Netflix": {
        "tagline": "Chaos Engineering, Adaptive Streaming & Event-Driven Microservices",
        "interviewer_title": "Netflix Staff Distributed Systems Engineer",
        "philosophy": (
            "Focuses on multi-region active-active resilience, telemetry pipelines, circuit breaking, "
            "adaptive bitrate streaming algorithms, and automated disaster failovers."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Time-Based Key-Value Store\n"
                    "Design a time-based key-value data structure that can store multiple values for the same key at different timestamps and retrieve the key's value at a certain timestamp.\n\n"
                    "**Test Cases:**\n"
                    "- `set(\"foo\", \"bar\", 1)`, `get(\"foo\", 1)` ➔ `\"bar\"`, `get(\"foo\", 3)` ➔ `\"bar\"`\n\n"
                    "**Netflix Standard:** Use binary search (`bisect_right`) over sorted timestamp lists for $O(\\log N)$ lookup."
                )
            ],
            "Medium": [
                (
                    "### Problem: Design Video Playback Telemetry Pipeline\n"
                    "Design an event-driven telemetry ingestion service handling 5 million heartbeats per second from Netflix players worldwide. How do you buffer events, handle network drops, and compute real-time buffering ratios?"
                )
            ],
            "Hard": [
                (
                    "### Problem: Multi-Region Active-Active Database Failover\n"
                    "Architect Netflix's global user session service across AWS us-east-1 and eu-west-1. If a primary cloud region experiences a complete network blackout, how does the system fail over in under 30 seconds with zero data corruption?"
                )
            ]
        }
    },
    "Uber": {
        "tagline": "Geospatial Indexing, High-Concurrency Dispatch & Real-Time Locks",
        "interviewer_title": "Uber Staff Platform Engineer",
        "philosophy": (
            "Specializes in spatial indexing (H3 hexagons / QuadTrees), real-time driver-rider dispatch algorithms, "
            "distributed locking, and dynamic pricing pipelines."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Design Hit Counter (Sliding Window 300 Seconds)\n"
                    "Design a hit counter which counts the number of driver GPS location pings received in the past 5 minutes.\n\n"
                    "**Uber Standard:** Use circular array with 300 buckets storing `(timestamp, count)` to achieve $O(1)$ space and $O(1)$ time."
                )
            ],
            "Medium": [
                (
                    "### Problem: Driver-Rider Matching with H3 Geospatial Indexing\n"
                    "Given 100,000 active drivers moving continuously, design a dispatch engine that finds the top 5 nearest drivers to a rider pickup coordinate within 2 miles in under 15ms.\n\n"
                    "**Uber Standard:** Compare Spatial R-Tree vs H3 hexagonal cell indexing for neighbor radius expansion."
                )
            ],
            "Hard": [
                (
                    "### Problem: Distributed Ride Booking with Strict Idempotency & Locks\n"
                    "When two riders simultaneously attempt to book the last available driver in an area, how do you prevent double-dispatch using distributed locks (Redlock) while guaranteeing idempotency?"
                )
            ]
        }
    }
}

# Merge all extended tech companies
try:
    from companies_data import EXPANDED_COMPANIES
    COMPANY_PROFILES.update(EXPANDED_COMPANIES)
except ImportError:
    pass

def get_company_profile(company: Optional[str]) -> Optional[Dict[str, Any]]:
    if not company:
        return None
    for name, prof in COMPANY_PROFILES.items():
        if name.lower() == company.lower() or company.lower() in name.lower():
            return prof
    return None

def get_company_questions(company: Optional[str], difficulty: str, count: int = 5) -> List[str]:
    import random
    from question_banks import EXPANDED_QUESTION_BANKS
    prof = get_company_profile(company)
    if not prof:
        return []
    
    q_map = prof["questions"]
    pool = list(q_map.get(difficulty, q_map.get("Medium", [])))
    
    # Randomize order so candidates get spontaneous, fresh questions every visit!
    random.shuffle(pool)
    
    results = list(pool)
    if len(results) < count:
        extra: List[str] = []
        for diff in ["Medium", "Easy", "Hard"]:
            for q in q_map.get(diff, []):
                if q not in results and q not in extra:
                    extra.append(q)
        random.shuffle(extra)
        results.extend(extra)

    # If still need more questions up to requested count (5 to 20), pull from DSA expanded bank
    if len(results) < count:
        dsa_pool = list(EXPANDED_QUESTION_BANKS.get("dsa", {}).get(difficulty, []))
        random.shuffle(dsa_pool)
        for q in dsa_pool:
            if q not in results:
                results.append(q)
            if len(results) >= count:
                break

    return results[:count]

def get_company_interviewer_intro(company: str, topic: str, difficulty: str, total_q: int) -> str:
    prof = get_company_profile(company)
    if not prof:
        return (
            f"Hello and welcome to your {difficulty}-level technical interview on **{topic}**. "
            f"We will be covering {total_q} questions. Take your time to structure clear, thorough answers!"
        )
    
    title = prof["interviewer_title"]
    ethos = prof["tagline"]
    return (
        f"Hello and welcome to your **{company}** Technical Interview!\n\n"
        f"I am conducting your session today as a **{title}**. "
        f"Our evaluation bar at {company} centers on **{ethos}**.\n\n"
        f"We have structured **{total_q} questions** for your session today. "
        f"State your approaches clearly, consider edge cases, and explain your trade-offs. "
        f"If coding, make sure to write clean, production-grade solutions."
    )
