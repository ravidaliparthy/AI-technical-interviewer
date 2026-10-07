"""
Expanded Company Interview Question Banks & Engineering Culture Profiles
Covers: Bloomberg, ByteDance, Stripe, Airbnb, LinkedIn, Salesforce, Adobe, Oracle,
Goldman Sachs, Palantir, Nvidia, Databricks, Cisco, Atlassian, Spotify, Snowflake,
DoorDash, Twitter / X
"""
from typing import Dict, Any

EXPANDED_COMPANIES: Dict[str, Dict[str, Any]] = {
    "Bloomberg": {
        "tagline": "Financial Real-Time Low Latency, Caching & Robust Invariants",
        "interviewer_title": "Bloomberg Senior Software Engineer",
        "philosophy": (
            "Tests for production robustness, memory footprint, ticker stream processing, "
            "and clean object-oriented data structures under high-frequency updates."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Two City Scheduling\n"
                    "A company is planning to interview $2N$ people. Given array `costs` where `costs[i] = [aCost_i, bCost_i]`, return the minimum cost to fly every person such that exactly $N$ people arrive in city A and $N$ people arrive in city B.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `costs = [[10,20],[30,200],[400,50],[30,20]]` ➔ Output: `110`\n"
                    "- Input: `costs = [[259,770],[448,54],[926,667],[184,139],[540,777],[115,77]]` ➔ Output: `1859`\n\n"
                    "**Bloomberg Standard:** Sort by `cost_A - cost_B` refund advantage. State optimal $O(N \\log N)$ time and $O(1)$ space complexity."
                ),
                (
                    "### Problem: Subdomain Visit Count\n"
                    "A count-paired domain is represented as `\"9001 discuss.leetcode.com\"`. Given a list of count-paired domains, calculate the total visit count for each address and subdomain.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `[\"900 google.mail.com\", \"50 yahoo.com\", \"1 intel.mail.com\", \"5 wiki.org\"]`\n"
                    "  Output includes: `\"901 mail.com\"`, `\"50 yahoo.com\"`, `\"900 google.mail.com\"`, `\"951 com\"`\n\n"
                    "**Bloomberg Standard:** Write clean string parsing without excessive string copying in the inner loop."
                ),
                (
                    "### Problem: First Unique Character in a String\n"
                    "Given a string `s`, find the first non-repeating character and return its index. If it does not exist, return `-1`.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `s = \"leetcode\"` ➔ Output: `0`\n"
                    "- Input: `s = \"loveleetcode\"` ➔ Output: `2`\n"
                    "- Input: `s = \"aabb\"` ➔ Output: `-1`\n\n"
                    "**Bloomberg Standard:** Use a fixed-size 26-element array or hash map in $O(N)$ time with $O(1)$ auxiliary space."
                )
            ],
            "Medium": [
                (
                    "### Problem: Design Underground System (Commute Statistics)\n"
                    "Design an underground subway system that tracks passenger transit times between stations: `checkIn(id, stationName, t)`, `checkOut(id, stationName, t)`, and `getAverageTime(startStation, endStation)`.\n\n"
                    "**Test Cases:**\n"
                    "- Check-in 45 at \"Leyton\" at t=3, check-out at \"Waterloo\" at t=15 (commute=12). `getAverageTime(\"Leyton\", \"Waterloo\")` ➔ `12.0`.\n\n"
                    "**Bloomberg Standard:** Guarantee $O(1)$ time for all three operations. How do you handle running averages without float precision degradation?"
                ),
                (
                    "### Problem: Online Stock Spanner (Monotonic Stack)\n"
                    "Design an algorithm that collects daily price quotes for a stock and returns the span of that stock's price for the current day (maximum consecutive days price was $\\le$ today's price).\n\n"
                    "**Test Cases:**\n"
                    "- Inputs: `[100, 80, 60, 70, 60, 75, 85]` ➔ Spans: `[1, 1, 1, 2, 1, 4, 6]`\n\n"
                    "**Bloomberg Standard:** Implement with a monotonic decreasing stack storing `(price, span)` pairs in amortized $O(1)$ time per quote."
                ),
                (
                    "### Problem: Remove All Adjacent Duplicates in String II (K-Duplicates)\n"
                    "You are given a string `s` and an integer `k`. A `k`-duplicate removal consists of choosing `k` adjacent and equal letters from `s` and removing them repeatedly.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `s = \"deeedbbcccbdaa\", k = 3` ➔ Output: `\"aa\"`\n"
                    "- Input: `s = \"pbbcggttciiippooaais\", k = 2` ➔ Output: `\"ps\"`\n\n"
                    "**Bloomberg Standard:** Use a stack of pairs `[char, count]` to achieve single-pass $O(N)$ runtime."
                )
            ],
            "Hard": [
                (
                    "### Problem: Design In-Memory Order Book / L2 Matching Engine\n"
                    "Design an order matching engine for high-frequency financial tickers that maintains Buy/Sell bids with limit prices, executes matching trades at best bid/ask, and supports order cancellations in sub-millisecond time.\n\n"
                    "**Bloomberg Standard:** Structure data with `BTreeMap` / Red-Black Tree for price tiers and Doubly Linked Lists for FIFO priority at each tier."
                )
            ]
        }
    },

    "ByteDance": {
        "tagline": "Extreme Concurrency, Graph Traversal & Dynamic Programming",
        "interviewer_title": "ByteDance / TikTok Tech Lead",
        "philosophy": (
            "Focuses heavily on dynamic programming, complex matrix traversals, high-throughput feed optimization, "
            "and flawless bug-free coding under strict time constraints."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Best Time to Buy and Sell Stock\n"
                    "You are given an array `prices` where `prices[i]` is the price of a given stock on the $i^{\\text{th}}$ day. Find the maximum profit achievable from at most one transaction.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `prices = [7,1,5,3,6,4]` ➔ Output: `5`\n"
                    "- Input: `prices = [7,6,4,3,1]` ➔ Output: `0`\n\n"
                    "**ByteDance Standard:** Single-pass tracking of `min_price` and `max_profit` in $O(N)$ time, $O(1)$ space. State the invariant."
                ),
                (
                    "### Problem: Valid Parentheses & Bracket Matching\n"
                    "Given a string `s` containing `(`, `)`, `{`, `}`, `[` and `]`, determine if the input string is valid.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `s = \"()[]{}\"` ➔ Output: `true`\n"
                    "- Input: `s = \"(]\"` ➔ Output: `false`\n"
                    "- Input: `s = \"([])\"` ➔ Output: `true`\n\n"
                    "**ByteDance Standard:** Use stack with hash map lookup. Ensure empty stack checks prevent index errors."
                )
            ],
            "Medium": [
                (
                    "### Problem: Maximal Square in Binary Matrix\n"
                    "Given an $m \\times n$ binary matrix filled with `0`'s and `1`'s, find the largest square containing only `1`'s and return its area.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `matrix = [[\"1\",\"0\",\"1\",\"0\",\"0\"],[\"1\",\"0\",\"1\",\"1\",\"1\"],[\"1\",\"1\",\"1\",\"1\",\"1\"],[\"1\",\"0\",\"0\",\"1\",\"0\"]]` ➔ Output: `4`\n\n"
                    "**ByteDance Standard:** Derive the DP transition `dp[i][j] = 1 + min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1])`. Optimize space to 1D $O(N)$ array."
                ),
                (
                    "### Problem: Course Schedule II (Topological Sort / Cycle Detection)\n"
                    "There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`. You are given an array `prerequisites` where `prerequisites[i] = [a_i, b_i]` indicates you must take `b_i` first. Return the ordering of courses you should take to finish all courses.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `numCourses = 4, prerequisites = [[1,0],[2,0],[3,1],[3,2]]` ➔ Output: `[0,2,1,3]` or `[0,1,2,3]`\n\n"
                    "**ByteDance Standard:** Kahn's algorithm using in-degree array and queue. Handle disconnected components and cycle detection."
                ),
                (
                    "### Problem: Kth Largest Element in an Array (QuickSelect vs Min-Heap)\n"
                    "Given an integer array `nums` and an integer `k`, return the $k^{\\text{th}}$ largest element in the array without full sorting.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `nums = [3,2,1,5,6,4], k = 2` ➔ Output: `5`\n"
                    "- Input: `nums = [3,2,3,1,2,4,5,5,6], k = 4` ➔ Output: `4`\n\n"
                    "**ByteDance Standard:** Compare average $O(N)$ Quickselect with three-way partition vs $O(N \\log K)$ Min-Heap."
                )
            ],
            "Hard": [
                (
                    "### Problem: Russian Doll Envelopes (2D LIS with Binary Search)\n"
                    "You are given a 2D array of integers `envelopes` where `envelopes[i] = [w_i, h_i]`. One envelope fits inside another iff width and height are strictly greater. What is the maximum number of envelopes you can Russian doll?\n\n"
                    "**ByteDance Standard:** Sort widths ascending and heights descending for equal widths, reducing to 1D Longest Increasing Subsequence in $O(N \\log N)$ using `bisect_left`."
                )
            ]
        }
    },

    "Stripe": {
        "tagline": "Financial Correctness, API Architecture, Idempotency & Clean Code",
        "interviewer_title": "Stripe Staff Infrastructure Engineer",
        "philosophy": (
            "Focuses on defensive coding, state machines, financial decimal handling, strict idempotency, "
            "and real-world API testability. Clean, readable code is prized over convoluted tricks."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Currency Invoicing & Micro-Units Parsing\n"
                    "Write a parser that converts decimal amounts in various currencies (e.g. `\"$14.50\"`, `\"€100.00\"`, `\"¥500\"`) into integer micro-cents (`1450` cents, `500` yen for zero-decimal currencies) to prevent IEEE 754 float drift in financial transactions.\n\n"
                    "**Test Cases:**\n"
                    "- `\"$10.25\"` ➔ `1025`\n"
                    "- `\"$0.01\"` ➔ `1`\n"
                    "- `\"¥5000\"` ➔ `5000` (zero-decimal currency)\n\n"
                    "**Stripe Standard:** Explain why binary floating point (`float`/`double`) should never store monetary balances."
                ),
                (
                    "### Problem: Mutual Friends & Transaction Ledger Validation\n"
                    "Given a list of payment records `[sender, receiver, amount]`, verify whether the ledger balances to zero and output any user with a negative balance.\n\n"
                    "**Stripe Standard:** Emphasize zero-sum integrity check and hash map aggregation."
                )
            ],
            "Medium": [
                (
                    "### Problem: Distributed Rate Limiter with Sliding Window Counter\n"
                    "Implement a rate limiter for Stripe API keys that permits up to $M$ requests per sliding 60-second window across multiple app servers.\n\n"
                    "**Test Cases:**\n"
                    "- Key `\"pk_test_123\"`: 100 requests in 30 seconds allowed; 101st rejected with HTTP 429 Retry-After.\n\n"
                    "**Stripe Standard:** Compare Redis Sorted Sets (`ZADD`, `ZREMRANGEBYSCORE`) with Token Bucket algorithms. How do you prevent race conditions under concurrent requests?"
                ),
                (
                    "### Problem: Currency Exchange Arbitrage Detection (Bellman-Ford / Cycle Finding)\n"
                    "Given a table of exchange rates between currencies `A -> B` with rate `R`, determine if there exists an arbitrage cycle where a trader can start with currency $X$, exchange across a loop, and end up with more money than started.\n\n"
                    "**Stripe Standard:** Convert exchange rate multiplication $\\prod R_i > 1$ into negative log-weights $-\\sum \\log(R_i) < 0$ and run Bellman-Ford negative cycle detection."
                ),
                (
                    "### Problem: Idempotent Payment State Machine\n"
                    "Design a payment processor endpoint that receives `(idempotency_key, amount, customer_id)`. If called multiple times with the same idempotency key concurrently, it must charge the card exactly once and return the identical response.\n\n"
                    "**Stripe Standard:** Walk through atomic DB lock states: `PENDING`, `PROCESSING`, `SUCCEEDED`, `FAILED`. How do you handle network timeouts before receiving confirmation?"
                )
            ],
            "Hard": [
                (
                    "### Problem: Transaction Ledger Reconciliation Engine\n"
                    "Design an event-driven ledger reconciliation system that matches internal Stripe payment authorizations against external card network settlement files (Visa/Mastercard) containing millions of daily settlement records with subtle fee discrepancies and timezone offsets."
                )
            ]
        }
    },

    "Airbnb": {
        "tagline": "Geospatial Indexing, Calendar Availability & Clean Graph Algorithms",
        "interviewer_title": "Airbnb Senior Software Engineer",
        "philosophy": (
            "Tests for production-quality object-oriented architecture, interval scheduling for listing availability, "
            "and clean modular code structure with excellent test-case coverage."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Check If All Dates in Interval Are Free (Calendar Booking)\n"
                    "Given an array of booked date ranges `[[start_1, end_1], ...]` and a desired trip `[trip_start, trip_end]`, determine if the accommodation is available.\n\n"
                    "**Test Cases:**\n"
                    "- Bookings: `[[1, 5], [10, 15]]`, Trip: `[6, 9]` ➔ Output: `true`\n"
                    "- Bookings: `[[1, 5], [10, 15]]`, Trip: `[4, 8]` ➔ Output: `false`\n\n"
                    "**Airbnb Standard:** Define strict non-overlapping condition `max(start_a, start_b) < min(end_a, end_b)`."
                )
            ],
            "Medium": [
                (
                    "### Problem: Design In-Memory File System\n"
                    "Design a data structure that simulates an in-memory file system: `ls(path)`, `mkdir(path)`, `addContentToFile(filePath, content)`, `readContentFromFile(filePath)`.\n\n"
                    "**Test Cases:**\n"
                    "- `mkdir(\"/a/b/c\")`, `addContentToFile(\"/a/b/c/d\", \"hello\")`, `ls(\"/a/b/c\")` ➔ `[\"d\"]`, `readContentFromFile(\"/a/b/c/d\")` ➔ `\"hello\"`\n\n"
                    "**Airbnb Standard:** Model as a Trie / Directory Tree where each node holds children mapping `(name -> Node)` and an optional file buffer."
                ),
                (
                    "### Problem: Pour Water (2D Terrain Simulation)\n"
                    "Given an elevation map represented by an integer array `heights` and $V$ units of water poured at index $K$, simulate how water trickles left or right into the lowest valley.\n\n"
                    "**Test Cases:**\n"
                    "- `heights = [2,1,1,2,1,2,2], V = 4, K = 3` ➔ Output: `[2,2,2,3,2,2,2]`\n\n"
                    "**Airbnb Standard:** Write clean simulation loop respecting gravity rules: fall left first, then right, otherwise stay at index $K$."
                ),
                (
                    "### Problem: IP to CIDR Block Conversion\n"
                    "Given a start IP address and the number of hosts $N$, convert the range into the minimum number of valid CIDR blocks.\n\n"
                    "**Airbnb Standard:** Use bit manipulation to find the lowest set bit (`ip & -ip`) to determine maximum allowed block size."
                )
            ],
            "Hard": [
                (
                    "### Problem: Alien Dictionary II (Lexicographical Rule Synthesis)\n"
                    "Given a set of user reviews sorted in a specific regional ranking order, reconstruct the complete partial ordering of criteria. Detect contradictory cyclic preferences."
                )
            ]
        }
    },

    "LinkedIn": {
        "tagline": "Social Graph Traversal, Caching Invariants & Production Reliability",
        "interviewer_title": "LinkedIn Staff Software Engineer",
        "philosophy": (
            "Focuses on graph distance (degrees of connection), clean object-oriented class design, "
            "nested data structures, and optimal multi-level caching strategies."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Shortest Word Distance I\n"
                    "Given an array of strings `wordsDict` and two different strings `word1` and `word2`, return the shortest distance between these two words in the list.\n\n"
                    "**Test Cases:**\n"
                    "- `wordsDict = [\"practice\", \"makes\", \"perfect\", \"coding\", \"makes\"], word1 = \"coding\", word2 = \"practice\"` ➔ Output: `3`\n\n"
                    "**LinkedIn Standard:** Single pass $O(N)$ keeping track of the last seen index for each word. Auxiliary space: $O(1)$."
                ),
                (
                    "### Problem: Can Place Flowers (Interval Adjacent Rules)\n"
                    "You have a long flowerbed in which some plots are planted, and some are not (`0` and `1`). Given integer $n$, return if $n$ new flowers can be planted without violating no-adjacent rule.\n\n"
                    "**Test Cases:**\n"
                    "- `flowerbed = [1,0,0,0,1], n = 1` ➔ Output: `true`\n"
                    "- `flowerbed = [1,0,0,0,1], n = 2` ➔ Output: `false`\n\n"
                    "**LinkedIn Standard:** Greedy scan checking `i-1` and `i+1` boundaries without array re-allocation."
                )
            ],
            "Medium": [
                (
                    "### Problem: Find Leaves of Binary Tree (Bottom-Up Heights)\n"
                    "Given the root of a binary tree, collect a tree's nodes as if you were doing this: collect and remove all leaves, repeat until the tree is empty.\n\n"
                    "**Test Cases:**\n"
                    "- Input: root `[1,2,3,4,5]` ➔ Output: `[[4,5,3],[2],[1]]`\n\n"
                    "**LinkedIn Standard:** Post-order DFS computing bottom-up node height: `height = 1 + max(left, right)`. Group nodes by height index in $O(N)$ time."
                ),
                (
                    "### Problem: Retain Best Cache (Cache with Eviction Ranking)\n"
                    "Design a fixed-capacity in-memory cache where each entry has an inherent financial rank `getRank(key)`. When evicting, always evict the entry with the lowest rank.\n\n"
                    "**LinkedIn Standard:** Combine a Hash Map with a Min-Heap or TreeMap ordered by rank to achieve $O(\\log C)$ eviction and $O(1)$ retrieval."
                ),
                (
                    "### Problem: Nested List Weight Sum II (Inverse Depth Multiplication)\n"
                    "You are given a nested list of integers. Each element is either an integer, or a list whose elements are also integers. Return the sum of each integer weighted by its inverse depth ($max\\_depth - depth + 1$).\n\n"
                    "**LinkedIn Standard:** Implement single-pass BFS without calculating $max\\_depth$ first by accumulating running sum across levels."
                )
            ],
            "Hard": [
                (
                    "### Problem: Degrees of Separation Social Graph Query (Bidirectional BFS)\n"
                    "Given a social graph with 500 million members, determine the minimum degree of separation between Member A and Member B within 5 hops. How do you scale bidirectional BFS across distributed graph shards without running into exponential node fanout?"
                )
            ]
        }
    },

    "Salesforce": {
        "tagline": "Enterprise Multitenancy, Object Relational Data & String Parsers",
        "interviewer_title": "Salesforce Principal Engineer",
        "philosophy": (
            "Emphasizes clean expression evaluators, robust LRU/LFU caching, scalable multitenant data stores, "
            "and clean code with zero memory leaks."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Merge Two Sorted Lists\n"
                    "You are given the heads of two sorted linked lists `list1` and `list2`. Merge the two lists into one sorted list in $O(N + M)$ time and $O(1)$ space.\n\n"
                    "**Salesforce Standard:** Use a dummy pre-head pointer to eliminate edge cases for empty head nodes."
                )
            ],
            "Medium": [
                (
                    "### Problem: Basic Calculator II (Multiply, Divide, Add, Subtract)\n"
                    "Given a string `s` which represents an arithmetic expression containing non-negative integers and `+`, `-`, `*`, `/`, evaluate the expression without using `eval()`.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `s = \"3+2*2\"` ➔ Output: `7`\n"
                    "- Input: `s = \" 3/2 \"` ➔ Output: `1`\n"
                    "- Input: `s = \" 3+5 / 2 \"` ➔ Output: `5`\n\n"
                    "**Salesforce Standard:** Implement in $O(N)$ time and $O(1)$ space by maintaining `current_num`, `last_num`, and `result` without a full stack."
                ),
                (
                    "### Problem: Merge Intervals\n"
                    "Given an array of `intervals` where `intervals[i] = [start_i, end_i]`, merge all overlapping intervals.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `intervals = [[1,3],[2,6],[8,10],[15,18]]` ➔ Output: `[[1,6],[8,10],[15,18]]`\n\n"
                    "**Salesforce Standard:** Sort by start time. State optimal Time ($O(N \\log N)$) and Auxiliary Space bounds."
                ),
                (
                    "### Problem: Word Break (Dictionary Dynamic Programming)\n"
                    "Given a string `s` and a dictionary of strings `wordDict`, return `true` if `s` can be segmented into a space-separated sequence of one or more dictionary words.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `s = \"leetcode\", wordDict = [\"leet\",\"code\"]` ➔ Output: `true`\n"
                    "- Input: `s = \"applepenapple\", wordDict = [\"apple\",\"pen\"]` ➔ Output: `true`\n\n"
                    "**Salesforce Standard:** Implement with 1D boolean DP array or Trie optimization."
                )
            ],
            "Hard": [
                (
                    "### Problem: All O`one Data Structure\n"
                    "Design a data structure to store the strings' count with the ability to return the strings with minimum and maximum counts in $O(1)$ time for all operations: `inc(key)`, `dec(key)`, `getMaxKey()`, `getMinKey()`.\n\n"
                    "**Salesforce Standard:** Combine a Hash Map with a Doubly Linked List of bucket nodes where each bucket stores a frequency value and a HashSet of keys."
                )
            ]
        }
    },

    "Adobe": {
        "tagline": "Geometry, Image Matrices, Matrix Transformations & Binary Search",
        "interviewer_title": "Adobe Senior Software Architect",
        "philosophy": (
            "Focuses on 2D matrix manipulation, binary search variations, string transformations, "
            "and clean mathematical logic."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Roman to Integer\n"
                    "Given a Roman numeral `s`, convert it to an integer. Handle subtraction cases (`IV = 4`, `IX = 9`, `XL = 40`, `XC = 90`, `CD = 400`, `CM = 900`).\n\n"
                    "**Test Cases:**\n"
                    "- `s = \"III\"` ➔ `3`\n"
                    "- `s = \"LVIII\"` ➔ `58`\n"
                    "- `s = \"MCMXCIV\"` ➔ `1994`\n\n"
                    "**Adobe Standard:** Single reverse scan comparing current symbol value to previous symbol value in $O(N)$ time, $O(1)$ space."
                )
            ],
            "Medium": [
                (
                    "### Problem: Search in Rotated Sorted Array\n"
                    "Given the array `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not in $O(\\log N)$ time.\n\n"
                    "**Test Cases:**\n"
                    "- `nums = [4,5,6,7,0,1,2], target = 0` ➔ Output: `4`\n"
                    "- `nums = [4,5,6,7,0,1,2], target = 3` ➔ Output: `-1`\n\n"
                    "**Adobe Standard:** Determine which half is monotonically sorted (`nums[left] <= nums[mid]`) and narrow search bounds."
                ),
                (
                    "### Problem: Spiral Matrix (Layer-by-Layer Boundary Navigation)\n"
                    "Given an $m \\times n$ matrix, return all elements of the matrix in spiral order.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]` ➔ Output: `[1,2,3,6,9,8,7,4,5]`\n\n"
                    "**Adobe Standard:** Maintain four boundary pointers: `top`, `bottom`, `left`, `right`. Prevent double-counting when rows or columns collapse."
                ),
                (
                    "### Problem: Next Permutation (In-Place Lexicographical Rearrangement)\n"
                    "Implement next permutation, which rearranges numbers into the lexicographically next greater permutation of numbers in $O(N)$ time and $O(1)$ space.\n\n"
                    "**Test Cases:**\n"
                    "- `[1,2,3]` ➔ `[1,3,2]`\n"
                    "- `[3,2,1]` ➔ `[1,2,3]`\n"
                    "- `[1,1,5]` ➔ `[1,5,1]`\n\n"
                    "**Adobe Standard:** Identify pivot where `nums[i] < nums[i+1]`, find successor to swap, then reverse the suffix."
                )
            ],
            "Hard": [
                (
                    "### Problem: Minimum Window Substring\n"
                    "Given two strings `s` and `t`, return the minimum window substring of `s` such that every character in `t` (including duplicates) is included in the window in $O(N)$ time."
                )
            ]
        }
    },

    "Goldman Sachs": {
        "tagline": "Financial Mathematics, Precision Numerics & High-Throughput Hash Maps",
        "interviewer_title": "Goldman Sachs Vice President (Engineering)",
        "philosophy": (
            "Known for mathematical problem solving, handling cyclic fractions, string compression, "
            "and clean edge-case analysis under financial calculation guidelines."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: High Five (Top 5 Test Scores Average)\n"
                    "Given a list of scores of different students, where each item `items[i] = [ID_i, score_i]`, calculate each student's top 5 average score rounded down.\n\n"
                    "**Test Cases:**\n"
                    "- Input: `[[1,91],[1,92],[2,93],[2,97],[1,60],[2,77],[1,65],[1,87],[1,100],[2,100],[2,98]]` ➔ Student 1 avg: 87, Student 2 avg: 93\n\n"
                    "**Goldman Sachs Standard:** Use min-heaps of size 5 per student ID to ensure optimal $O(N \\log 5)$ complexity."
                )
            ],
            "Medium": [
                (
                    "### Problem: Fraction to Recurring Decimal\n"
                    "Given two integers representing the `numerator` and `denominator` of a fraction, return the fraction in string format. If the fractional part is repeating, enclose the repeating part in parentheses.\n\n"
                    "**Test Cases:**\n"
                    "- `numerator = 1, denominator = 2` ➔ Output: `\"0.5\"`\n"
                    "- `numerator = 2, denominator = 1` ➔ Output: `\"2\"`\n"
                    "- `numerator = 4, denominator = 333` ➔ Output: `\"0.(012)\"`\n\n"
                    "**Goldman Sachs Standard:** Handle negative numbers, integer overflow with `long long` / 64-bit casting, and track remainder indices with a hash map."
                ),
                (
                    "### Problem: Trapping Rain Water (Two Pointers vs DP)\n"
                    "Given $n$ non-negative integers representing an elevation map where the width of each bar is 1, compute how much water it can trap after raining.\n\n"
                    "**Test Cases:**\n"
                    "- `height = [0,1,0,2,1,0,1,3,2,1,2,1]` ➔ Output: `6`\n"
                    "- `height = [4,2,0,3,2,5]` ➔ Output: `9`\n\n"
                    "**Goldman Sachs Standard:** Deliver optimal $O(N)$ time, $O(1)$ auxiliary space two-pointer solution."
                ),
                (
                    "### Problem: Maximum Subarray (Kadane's Algorithm)\n"
                    "Given an integer array `nums`, find the subarray with the largest sum, and return its sum in $O(N)$ time.\n\n"
                    "**Goldman Sachs Standard:** Explain why `current_sum = max(num, current_sum + num)` guarantees correctness even with all negative numbers."
                )
            ],
            "Hard": [
                (
                    "### Problem: Optimal Account Balancing (Debt Settlement Minimization)\n"
                    "You are given an array of transactions where `transactions[i] = [from_i, to_i, amount_i]`. Return the minimum number of transactions needed to settle all debts among participants.\n\n"
                    "**Goldman Sachs Standard:** Compute net balances and solve NP-hard partition matching using backtracking with pruning."
                )
            ]
        }
    },

    "Palantir": {
        "tagline": "Knowledge Graphs, Complex Pathfinding & Enterprise Data Invariants",
        "interviewer_title": "Palantir Lead Forward Deployed Engineer",
        "philosophy": (
            "Focuses on complex graph models, multi-source traversals, cycle resolution in ontologies, "
            "and building production-ready maintainable software."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Minimum Cost to Connect Sticks (Min-Heap Greedy)\n"
                    "You have some number of sticks with positive integer lengths. You can connect any two sticks of lengths $x$ and $y$ with cost $x + y$. Return the minimum cost to connect all sticks into one stick.\n\n"
                    "**Palantir Standard:** Proof of Huffman greedy coding via Priority Queue in $O(N \\log N)$ time."
                )
            ],
            "Medium": [
                (
                    "### Problem: Detect Cycles in Directed Graph & Topological Dependency Resolution\n"
                    "Given $N$ tasks and directed dependencies between them, verify if the execution pipeline has circular dependencies. If valid, return a valid parallel execution batch grouping.\n\n"
                    "**Palantir Standard:** Use 3-color DFS (White, Gray, Black) or Kahn's algorithm with level order BFS."
                ),
                (
                    "### Problem: Find Closest Leaf in a Binary Tree\n"
                    "Given the root of a binary tree where each node has a unique value and an integer $k$, find the value of the nearest leaf node to node $k$ in the tree.\n\n"
                    "**Palantir Standard:** Convert tree into undirected graph representation and run BFS from target node $k$."
                )
            ],
            "Hard": [
                (
                    "### Problem: Word Ladder II (Find All Shortest Transformation Paths)\n"
                    "Given two words, `beginWord` and `endWord`, and a dictionary `wordList`, find all shortest transformation sequences. Must return optimal paths without memory explosion.\n\n"
                    "**Palantir Standard:** BFS to find shortest layer distances followed by backtracking DFS to collect paths."
                )
            ]
        }
    },

    "Nvidia": {
        "tagline": "Hardware-Accelerated Algorithms, Sparse Vectors & Optimal Matrix Kernels",
        "interviewer_title": "Nvidia Principal Systems & CUDA Architect",
        "philosophy": (
            "Tests for hardware memory alignment, parallel reduction, sparse data representation, "
            "and algorithmic efficiency under extreme data scale."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Dot Product of Two Sparse Vectors\n"
                    "Given two sparse vectors, compute their dot product efficiently. Most elements are 0.\n\n"
                    "**Test Cases:**\n"
                    "- `nums1 = [1,0,0,2,3], nums2 = [0,3,0,4,0]` ➔ Output: `8`\n\n"
                    "**Nvidia Standard:** Store non-zero elements as `(index, value)` pairs and calculate dot product via two pointers in $O(L_1 + L_2)$ time."
                )
            ],
            "Medium": [
                (
                    "### Problem: Matrix Block Sum (2D Prefix Sum / Integral Image)\n"
                    "Given an $m \\times n$ matrix `mat` and integer $k$, return a matrix `answer` where each `answer[i][j]` is the sum of all elements `mat[r][c]` for $|r - i| \\le k$ and $|c - j| \\le k$.\n\n"
                    "**Nvidia Standard:** Construct 2D Prefix Sum array in $O(M \\times N)$ time. Query any sub-matrix in $O(1)$ time."
                ),
                (
                    "### Problem: Parallel Reduction / Maximum Subarray Divide & Conquer\n"
                    "Implement maximum subarray using divide-and-conquer suitable for parallel GPU thread execution across shared memory blocks in $O(\\log N)$ depth."
                )
            ],
            "Hard": [
                (
                    "### Problem: Median of Two Sorted Arrays\n"
                    "Given two sorted arrays `nums1` and `nums2` of size $m$ and $n$ respectively, return the median of the two sorted arrays in $O(\\log(\\min(m, n)))$ runtime.\n\n"
                    "**Nvidia Standard:** Binary search on the partition of the smaller array. Validate left and right boundary inequalities."
                )
            ]
        }
    },

    "Databricks": {
        "tagline": "Distributed Big Data, Query Optimizers & Multithreaded Scalability",
        "interviewer_title": "Databricks Principal Systems Engineer",
        "philosophy": (
            "Evaluates deep knowledge of concurrency, lock-free structures, segment trees, "
            "memory-mapped paging, and distributed query execution plans."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Range Sum Query - Immutable\n"
                    "Given an integer array `nums`, handle multiple queries of the form: calculate the sum of the elements between indices `left` and `right` inclusive in $O(1)$ time per query."
                )
            ],
            "Medium": [
                (
                    "### Problem: Snapshot Array with Versioned Deltas\n"
                    "Implement a SnapshotArray that supports `set(index, val)`, `snap()`, and `get(index, snap_id)` minimizing memory storage by persisting only changed deltas per version.\n\n"
                    "**Databricks Standard:** Binary search on `(snap_id, value)` historical deltas."
                ),
                (
                    "### Problem: Web Crawler Multithreaded\n"
                    "Given a URL `startUrl` and an interface `HtmlParser`, implement a multithreaded web crawler to collect all URLs that share the same hostname in minimal elapsed clock time."
                )
            ],
            "Hard": [
                (
                    "### Problem: Range Sum Query 2D - Mutable (2D Binary Indexed Tree)\n"
                    "Given a 2D matrix, handle multiple queries of update element `(row, col)` to value `val`, and calculate sum of elements inside rectangle in $O(\\log M \\cdot \\log N)$ time."
                )
            ]
        }
    },

    "Cisco": {
        "tagline": "Networking Protocols, IP Routing Trees & Minimum Spanning Trees",
        "interviewer_title": "Cisco Technical Architect",
        "philosophy": (
            "Focuses on IP prefix routing using Tries, packet buffering, graph connectivity, "
            "and network topology optimization."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Subnet Mask Calculation & Longest Common Prefix\n"
                    "Write a function to find the longest common prefix string amongst an array of strings representing network route CIDR prefixes."
                )
            ],
            "Medium": [
                (
                    "### Problem: Implement Trie for IP Longest Prefix Match Routing\n"
                    "Implement a routing table lookup engine that finds the longest matching subnet prefix for any 32-bit destination IPv4 address in $O(32) = O(1)$ lookup time."
                ),
                (
                    "### Problem: Is Graph Bipartite? (Network Frequency Assignment)\n"
                    "There is an undirected graph with $n$ nodes. Return `true` if and only if it is bipartite (can be 2-colored such that no two adjacent nodes share the same frequency channel)."
                )
            ],
            "Hard": [
                (
                    "### Problem: Network Delay Time (Dijkstra's Shortest Path)\n"
                    "You are given a network of $n$ nodes labeled from $1$ to $n$ and `times`, a list of travel times as directed edges. How long will it take for all nodes to receive the packet signal?"
                )
            ]
        }
    },

    "Atlassian": {
        "tagline": "Collaborative Document Engines, Rate Limiters & Work Hierarchy",
        "interviewer_title": "Atlassian Senior Team Lead",
        "philosophy": (
            "Focuses on clean API design, team ranking voting mechanics, logger rate limits, "
            "and operational transformation principles."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Rank Teams by Votes\n"
                    "In a special ranking system, each voter gives a rank from highest to lowest to all teams participating in the competition. Order teams according to the most first-place votes, then second-place, etc.\n\n"
                    "**Atlassian Standard:** Custom comparator with position count array in $O(N \\log N)$."
                )
            ],
            "Medium": [
                (
                    "### Problem: Design Snake Game\n"
                    "Design a Snake game that is played on a device with screen size `height x width`. The snake starts with length 1 at `(0, 0)`. Advance step by step detecting self-collision in $O(1)$ time."
                ),
                (
                    "### Problem: Meeting Rooms II (Minimum Conference Rooms Needed)\n"
                    "Given an array of meeting time intervals `intervals`, find the minimum number of conference rooms required.\n\n"
                    "**Atlassian Standard:** Min-heap of end times vs two sorted arrays for starts and ends in $O(N \\log N)$."
                )
            ],
            "Hard": [
                (
                    "### Problem: Collaborative Text Editor with Operational Transformation (CRDT)\n"
                    "Design a concurrent text document engine that supports multiple users inserting and deleting characters simultaneously without conflicting overwrites."
                )
            ]
        }
    },

    "Spotify": {
        "tagline": "Audio Streaming Recommenders, Top-K Caching & Random Shufflers",
        "interviewer_title": "Spotify Senior Systems Engineer",
        "philosophy": (
            "Tests for uniform random shuffling, continuous sliding window stream medians, "
            "and high-volume Top-K music chart aggregators."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Shuffle an Array (Fisher-Yates Modern Shuffle)\n"
                    "Given an integer array `nums`, design an algorithm to randomly shuffle the array. All permutations must be equally likely.\n\n"
                    "**Spotify Standard:** Prove why Fisher-Yates achieves $O(N)$ time with uniform $\\frac{1}{N!}$ probability distribution."
                )
            ],
            "Medium": [
                (
                    "### Problem: Top K Frequent Elements (Min-Heap vs Bucket Sort)\n"
                    "Given an integer array `nums` and integer `k`, return the $k$ most frequent elements in $O(N)$ time.\n\n"
                    "**Spotify Standard:** Implement Bucket Sort where bucket index corresponds to frequency count."
                ),
                (
                    "### Problem: Reorganize String (No Consecutive Duplicate Songs)\n"
                    "Rearrange an array of song IDs such that no two identical songs are played consecutively."
                )
            ],
            "Hard": [
                (
                    "### Problem: Find Median from Streaming Track Durations (Two Heaps)\n"
                    "The median is the unique middle value in an ordered integer list. Design a data structure that supports adding a track duration and calculating current stream median in $O(1)$ time.\n\n"
                    "**Spotify Standard:** Balance a Max-Heap for the lower half and a Min-Heap for the upper half."
                )
            ]
        }
    },

    "Snowflake": {
        "tagline": "Cloud Data Warehouses, Columnar Storage & Micro-Partition Sorting",
        "interviewer_title": "Snowflake Principal Database Architect",
        "philosophy": (
            "Specializes in large-scale external sorting, columnar compression, bitmask indexing, "
            "and sub-second range aggregations."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Number of 1 Bits (Hamming Weight)\n"
                    "Write a function that takes the binary representation of an unsigned integer and returns the number of `1` bits it has in $O(K)$ time where $K$ is the number of set bits (`n = n & (n - 1)`)."
                )
            ],
            "Medium": [
                (
                    "### Problem: Merge K Sorted Lists (K-Way External Merge Sort)\n"
                    "You are given an array of $k$ linked-lists `lists`, each linked-list is sorted in ascending order. Merge all the linked-lists into one sorted linked-list.\n\n"
                    "**Snowflake Standard:** Min-heap of size $K$ or Divide-and-Conquer merging in $O(N \\log K)$ time."
                ),
                (
                    "### Problem: Range Sum Query 2D - Immutable\n"
                    "Implement $O(1)$ query sub-matrix calculations using 2D prefix sums for columnar micro-partitions."
                )
            ],
            "Hard": [
                (
                    "### Problem: Minimum Window Substring with Micro-Indices\n"
                    "Find the minimum window substring containing all query tokens using filtered character index pairs."
                )
            ]
        }
    },

    "DoorDash": {
        "tagline": "Logistics Dispatch, Dynamic Delivery ETAs & Route TSP Approximations",
        "interviewer_title": "DoorDash Staff Logistics Engineer",
        "philosophy": (
            "Focuses on delivery routing, interval scheduling for couriers, shortest paths on city grid networks, "
            "and real-time order bundling."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Valid Anagram (Order Token Check)\n"
                    "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise in $O(N)$ time and $O(1)$ auxiliary space."
                )
            ],
            "Medium": [
                (
                    "### Problem: Shortest Path to Deliver Food on City Grid\n"
                    "You are starving and want to eat food as quickly as possible. You want to find the shortest path on an $m \\times n$ grid to arrive at any restaurant.\n\n"
                    "**DoorDash Standard:** Multi-source BFS starting from the courier position."
                ),
                (
                    "### Problem: Maximum Profit in Job Scheduling (Delivery Batching)\n"
                    "We have $n$ delivery jobs where every job is scheduled to be done from `startTime[i]` to `endTime[i]`, obtaining a profit of `profit[i]`. Find the maximum profit achievable.\n\n"
                    "**DoorDash Standard:** Sort by end times, run DP with binary search (`bisect_right`) in $O(N \\log N)$ time."
                )
            ],
            "Hard": [
                (
                    "### Problem: Real-Time Multi-Courier Route Bundling (Vehicle Routing Optimization)\n"
                    "Given 100 incoming restaurant pickup and drop-off requests within a 3-mile cluster, batch orders into multi-drop routes for 20 active couriers while minimizing total customer wait latency and delivery transit time."
                )
            ]
        }
    },

    "Twitter / X": {
        "tagline": "Fanout-on-Write Social Pipelines, High-Speed Timelines & Rate Limits",
        "interviewer_title": "Twitter / X Principal Infrastructure Architect",
        "philosophy": (
            "Tests for high-fanout timeline caching, $O(1)$ random collection sampling, "
            "sliding tweet rate aggregations, and resilient distributed stream processing."
        ),
        "questions": {
            "Easy": [
                (
                    "### Problem: Intersection of Two Arrays II\n"
                    "Given two integer arrays `nums1` and `nums2`, return an array of their intersection with duplicate frequency preserved.\n\n"
                    "**Twitter Standard:** Hash map counting in $O(N + M)$ time or two pointers if already sorted."
                )
            ],
            "Medium": [
                (
                    "### Problem: Design Twitter (Timeline Generation & Follow Graph)\n"
                    "Design a simplified version of Twitter where users can post tweets, follow/unfollow another user, and see the 10 most recent tweets in the user's news feed.\n\n"
                    "**Test Cases:**\n"
                    "- `postTweet(1, 5)`, `getNewsFeed(1)` ➔ `[5]`, `follow(1, 2)`, `postTweet(2, 6)`, `getNewsFeed(1)` ➔ `[6, 5]`\n\n"
                    "**Twitter Standard:** Use Max-Heap k-way merge of recent tweets across followees. Explain Fanout-on-Write vs Fanout-on-Read trade-offs."
                ),
                (
                    "### Problem: Insert Delete GetRandom O(1)\n"
                    "Implement the `RandomizedSet` class supporting `insert(val)`, `remove(val)`, and `getRandom()` all in average $O(1)$ time.\n\n"
                    "**Twitter Standard:** Combine an array (for $O(1)$ random index lookup) and a Hash Map (value to array index). On removal, swap with last element."
                ),
                (
                    "### Problem: Tweet Counts Per Frequency (Minute, Hour, Day Bucket Aggregation)\n"
                    "Design a system that records tweet occurrences and queries tweet counts over specified time chunks in $O(\\log N + B)$ time using balanced binary search trees or TreeMap."
                )
            ],
            "Hard": [
                (
                    "### Problem: Reverse Nodes in k-Group\n"
                    "Given the head of a linked list, reverse the nodes of the list $k$ at a time, and return the modified list using $O(1)$ auxiliary space."
                )
            ]
        }
    }
}
