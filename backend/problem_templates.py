"""
Dynamic Problem Template Generator & Language Stubs
Extracts parameters, signatures, and data structures (TreeNodes, ListNode, etc.)
from question text and synthesizes authentic LeetCode-style starter code
for Python, JavaScript, TypeScript, C++, Java, Go, and Rust.
"""
import re
from typing import Dict, Any, Optional, Tuple, List

# Catalog of known DSA problems with exact canonical signatures
CANONICAL_SIGNATURES: Dict[str, Dict[str, Any]] = {
    "lowest common ancestor": {
        "fn": "lowestCommonAncestor",
        "params": [("root", "TreeNode"), ("p", "TreeNode"), ("q", "TreeNode")],
        "return_type": "TreeNode",
        "needs_tree": True,
        "test_call": "lowestCommonAncestor(root, p, q)"
    },
    "valid palindrome": {
        "fn": "isPalindrome",
        "params": [("s", "str")],
        "return_type": "bool",
        "test_call": "isPalindrome('A man, a plan, a canal: Panama')"
    },
    "palindrome": {
        "fn": "isPalindrome",
        "params": [("s", "str")],
        "return_type": "bool",
        "test_call": "isPalindrome('racecar')"
    },
    "two sum": {
        "fn": "twoSum",
        "params": [("nums", "List[int]"), ("target", "int")],
        "return_type": "List[int]",
        "test_call": "twoSum([2, 7, 11, 15], 9)"
    },
    "maximum subarray": {
        "fn": "maxSubArray",
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "maxSubArray([-2,1,-3,4,-1,2,1,-5,4])"
    },
    "climbing stairs": {
        "fn": "climbStairs",
        "params": [("n", "int")],
        "return_type": "int",
        "test_call": "climbStairs(3)"
    },
    "container with most water": {
        "fn": "maxArea",
        "params": [("height", "List[int]")],
        "return_type": "int",
        "test_call": "maxArea([1,8,6,2,5,4,8,3,7])"
    },
    "merge intervals": {
        "fn": "merge",
        "params": [("intervals", "List[List[int]]")],
        "return_type": "List[List[int]]",
        "test_call": "merge([[1,3],[2,6],[8,10],[15,18]])"
    },
    "group anagrams": {
        "fn": "groupAnagrams",
        "params": [("strs", "List[str]")],
        "return_type": "List[List[str]]",
        "test_call": "groupAnagrams(['eat','tea','tan','ate','nat','bat'])"
    },
    "trapping rain water": {
        "fn": "trap",
        "params": [("height", "List[int]")],
        "return_type": "int",
        "test_call": "trap([0,1,0,2,1,0,1,3,2,1,2,1])"
    },
    "valid anagram": {
        "fn": "isAnagram",
        "params": [("s", "str"), ("t", "str")],
        "return_type": "bool",
        "test_call": "isAnagram('anagram', 'nagaram')"
    },
    "reverse linked list": {
        "fn": "reverseList",
        "params": [("head", "ListNode")],
        "return_type": "ListNode",
        "needs_list": True,
        "test_call": "reverseList(head)"
    },
    "binary search": {
        "fn": "search",
        "params": [("nums", "List[int]"), ("target", "int")],
        "return_type": "int",
        "test_call": "search([-1,0,3,5,9,12], 9)"
    },
    "merge two sorted lists": {
        "fn": "mergeTwoLists",
        "params": [("list1", "ListNode"), ("list2", "ListNode")],
        "return_type": "ListNode",
        "needs_list": True,
        "test_call": "mergeTwoLists(l1, l2)"
    },
    "valid parentheses": {
        "fn": "isValid",
        "params": [("s", "str")],
        "return_type": "bool",
        "test_call": "isValid('()[]{}')"
    },
    "best time to buy and sell stock": {
        "fn": "maxProfit",
        "params": [("prices", "List[int]")],
        "return_type": "int",
        "test_call": "maxProfit([7,1,5,3,6,4])"
    },
    "course schedule": {
        "fn": "canFinish",
        "params": [("numCourses", "int"), ("prerequisites", "List[List[int]]")],
        "return_type": "bool",
        "test_call": "canFinish(2, [[1,0]])"
    },
    "number of islands": {
        "fn": "numIslands",
        "params": [("grid", "List[List[str]]")],
        "return_type": "int",
        "test_call": "numIslands([['1','1','0'],['1','1','0'],['0','0','1']])"
    },
    "longest substring without repeating characters": {
        "fn": "lengthOfLongestSubstring",
        "params": [("s", "str")],
        "return_type": "int",
        "test_call": "lengthOfLongestSubstring('abcabcbb')"
    },
    "string compression": {
        "fn": "compress",
        "params": [("chars", "List[str]")],
        "return_type": "int",
        "test_call": "compress(['a','a','b','b','c','c','c'])"
    },
    "meeting rooms": {
        "fn": "canAttendMeetings",
        "params": [("intervals", "List[List[int]]")],
        "return_type": "bool",
        "test_call": "canAttendMeetings([[0,30],[5,10],[15,20]])"
    },
    "reorder data in log files": {
        "fn": "reorderLogFiles",
        "params": [("logs", "List[str]")],
        "return_type": "List[str]",
        "test_call": "reorderLogFiles(['dig1 8 1 5 1','let1 art can'])"
    },
    "maximal square": {
        "fn": "maximalSquare",
        "params": [("matrix", "List[List[str]]")],
        "return_type": "int",
        "test_call": "maximalSquare([['1','0'],['1','1']])"
    },
    "median of two sorted arrays": {
        "fn": "findMedianSortedArrays",
        "params": [("nums1", "List[int]"), ("nums2", "List[int]")],
        "return_type": "float",
        "test_call": "findMedianSortedArrays([1,3], [2])"
    },
    "sliding window maximum": {
        "fn": "maxSlidingWindow",
        "params": [("nums", "List[int]"), ("k", "int")],
        "return_type": "List[int]",
        "test_call": "maxSlidingWindow([1,3,-1,-3,5,3,6,7], 3)"
    },
    "product of array except self": {
        "fn": "productExceptSelf",
        "params": [("nums", "List[int]")],
        "return_type": "List[int]",
        "test_call": "productExceptSelf([1,2,3,4])"
    },
    "3sum": {
        "fn": "threeSum",
        "params": [("nums", "List[int]")],
        "return_type": "List[List[int]]",
        "test_call": "threeSum([-1,0,1,2,-1,-4])"
    },
    "search in rotated sorted array": {
        "fn": "search",
        "params": [("nums", "List[int]"), ("target", "int")],
        "return_type": "int",
        "test_call": "search([4,5,6,7,0,1,2], 0)"
    },
    "spiral matrix": {
        "fn": "spiralOrder",
        "params": [("matrix", "List[List[int]]")],
        "return_type": "List[int]",
        "test_call": "spiralOrder([[1,2,3],[4,5,6],[7,8,9]])"
    },
    "coin change": {
        "fn": "coinChange",
        "params": [("coins", "List[int]"), ("amount", "int")],
        "return_type": "int",
        "test_call": "coinChange([1,2,5], 11)"
    },
    "subdomain visit count": {
        "fn": "subdomainVisits",
        "params": [("cpdomains", "List[str]")],
        "return_type": "List[str]",
        "test_call": "subdomainVisits(['9001 discuss.leetcode.com'])"
    },
    "first unique character": {
        "fn": "firstUniqChar",
        "params": [("s", "str")],
        "return_type": "int",
        "test_call": "firstUniqChar('leetcode')"
    },
    "two city scheduling": {
        "fn": "twoCitySchedCost",
        "params": [("costs", "List[List[int]]")],
        "return_type": "int",
        "test_call": "twoCitySchedCost([[10,20],[30,200],[400,50],[30,20]])"
    },
    "validate binary search tree": {
        "fn": "isValidBST",
        "params": [("root", "TreeNode")],
        "return_type": "bool",
        "needs_tree": True,
        "test_call": "isValidBST(root)"
    },
    "invert binary tree": {
        "fn": "invertTree",
        "params": [("root", "TreeNode")],
        "return_type": "TreeNode",
        "needs_tree": True,
        "test_call": "invertTree(root)"
    },
    "missing number": {
        "fn": "findMissing",
        "params": [("arr", "List[int]"), ("n", "int")],
        "return_type": "int",
        "test_call": "findMissing([3, 7, 1, 2, 8, 4, 5, 6], 9)"
    },
    "findmissing": {
        "fn": "findMissing",
        "params": [("arr", "List[int]"), ("n", "int")],
        "return_type": "int",
        "test_call": "findMissing([3, 7, 1, 2, 8, 4, 5, 6], 9)"
    },
    "missing": {
        "fn": "findMissing",
        "params": [("arr", "List[int]"), ("n", "int")],
        "return_type": "int",
        "test_call": "findMissing([3, 7, 1, 2, 8, 4, 5, 6], 9)"
    },
    "diameter of binary tree": {
        "fn": "diameterOfBinaryTree",
        "params": [("root", "TreeNode")],
        "return_type": "int",
        "needs_tree": True,
        "test_call": "diameterOfBinaryTree(root)"
    }
}


def parse_question_signature(question_text: str) -> Tuple[str, List[Tuple[str, str]], str, bool, bool]:
    """
    Parses a question and returns:
    (fn_name, [(param_name, param_type), ...], return_type, needs_tree, needs_list)
    """
    q_lower = question_text.lower()

    # 1. Check canonical catalog first
    for key, data in CANONICAL_SIGNATURES.items():
        if key in q_lower:
            return (
                data["fn"],
                data["params"],
                data.get("return_type", "Any"),
                data.get("needs_tree", False),
                data.get("needs_list", False)
            )

    # 2. Check for explicit function signature declared in text:
    # e.g. "Write a function 'findMissing(arr, n)'" or `findMissing(arr, n)`
    sig_match = re.search(r'(?:function|def|write a function)\s*[`\'"]?([a-zA-Z_]\w*)\s*\(([^)]*)\)[`\'"]?', question_text, re.IGNORECASE)
    if not sig_match:
        sig_match = re.search(r'`([a-zA-Z_]\w*)\s*\(([^)]*)\)`', question_text)

    if sig_match:
        fn_name = sig_match.group(1).strip()
        raw_args = sig_match.group(2).strip()
        if raw_args:
            parsed_params: List[Tuple[str, str]] = []
            for arg in raw_args.split(","):
                arg_name = arg.strip().split(":")[0].split("=")[0].strip()
                arg_name = re.sub(r'[`\'"]', '', arg_name)
                if arg_name:
                    if arg_name in ("root", "p", "q") and ("tree" in q_lower or "root" in q_lower):
                        t = "TreeNode"
                    elif arg_name == "head" or ("list" in arg_name and "linked" in q_lower):
                        t = "ListNode"
                    elif arg_name in ("nums", "arr", "prices", "height", "heights", "coins"):
                        t = "List[int]"
                    elif arg_name in ("intervals", "matrix", "costs"):
                        t = "List[List[int]]"
                    elif arg_name in ("grid",):
                        t = "List[List[str]]"
                    elif arg_name in ("s", "t", "word", "str", "chars"):
                        t = "str"
                    elif arg_name in ("target", "n", "k", "amount", "val", "size"):
                        t = "int"
                    else:
                        t = "Any"
                    parsed_params.append((arg_name, t))
            if parsed_params:
                needs_tree = any(p[1] == "TreeNode" for p in parsed_params) or "tree" in q_lower
                needs_list = any(p[1] == "ListNode" for p in parsed_params) or "linked list" in q_lower
                return (fn_name, parsed_params, "Any", needs_tree, needs_list)

    # 3. Extract title if present: e.g. "### Problem: Name"
    title_match = re.search(r'###\s*Problem:\s*([^\n\(\:]+)', question_text)
    fn_name = "solve"
    if title_match:
        raw_title = title_match.group(1).strip()
        words = re.sub(r'[^a-zA-Z0-9\s]', '', raw_title).split()
        if words:
            fn_name = words[0].lower() + "".join(w.capitalize() for w in words[1:])

    # 4. Dynamic parameter detection from test cases or text
    params: List[Tuple[str, str]] = []
    needs_tree = "tree" in q_lower or "root" in q_lower or "treenode" in q_lower
    needs_list = ("linked list" in q_lower or "listnode" in q_lower or "head" in q_lower) and not needs_tree

    candidates = [
        ("root", "TreeNode" if needs_tree else "Any"),
        ("p", "TreeNode" if needs_tree else "int"),
        ("q", "TreeNode" if needs_tree else "int"),
        ("head", "ListNode" if needs_list else "Any"),
        ("arr", "List[int]"),
        ("nums", "List[int]"),
        ("target", "int"),
        ("intervals", "List[List[int]]"),
        ("matrix", "List[List[int]]"),
        ("grid", "List[List[str]]"),
        ("chars", "List[str]"),
        ("logs", "List[str]"),
        ("height", "List[int]"),
        ("heights", "List[int]"),
        ("prices", "List[int]"),
        ("coins", "List[int]"),
        ("amount", "int"),
        ("costs", "List[List[int]]"),
        ("prerequisites", "List[List[int]]"),
        ("numCourses", "int"),
        ("s", "str"),
        ("t", "str"),
        ("k", "int"),
        ("n", "int"),
    ]

    for var_name, var_type in candidates:
        if re.search(rf'[`\b]{re.escape(var_name)}[`\s]*=', question_text) or re.search(rf'[`]{re.escape(var_name)}[`]', question_text):
            if var_name not in [p[0] for p in params]:
                params.append((var_name, var_type))

    # If no parameters detected, provide sensible default
    if not params:
        if needs_tree:
            params = [("root", "TreeNode")]
        elif needs_list:
            params = [("head", "ListNode")]
        elif "string" in q_lower or "word" in q_lower:
            params = [("s", "str")]
        elif "matrix" in q_lower or "grid" in q_lower:
            params = [("matrix", "List[List[int]]")]
        elif "arr" in q_lower:
            params = [("arr", "List[int]"), ("n", "int")]
        else:
            params = [("nums", "List[int]"), ("target", "int")]

    return (fn_name, params, "Any", needs_tree, needs_list)


def generate_starter_snippets(question_text: str) -> Dict[str, str]:
    """Generates tailored LeetCode-style starter code for all 7 programming languages."""
    fn_name, params, ret_type, needs_tree, needs_list = parse_question_signature(question_text)

    param_names = [p[0] for p in params]
    param_str_py = ", ".join(param_names)
    param_str_js = ", ".join(param_names)

    # 1. Python 3
    py_tree_def = (
        "# Definition for a binary tree node.\n"
        "# class TreeNode:\n"
        "#     def __init__(self, val=0, left=None, right=None):\n"
        "#         self.val = val\n"
        "#         self.left = left\n"
        "#         self.right = right\n\n"
    ) if needs_tree else ""

    py_list_def = (
        "# Definition for singly-linked list.\n"
        "# class ListNode:\n"
        "#     def __init__(self, val=0, next=None):\n"
        "#         self.val = val\n"
        "#         self.next = next\n\n"
    ) if needs_list else ""

    py_code = f"{py_tree_def}{py_list_def}def {fn_name}({param_str_py}):\n    # Optimal Bounds Target: State Time Complexity: O(?), Space Complexity: O(?)\n    # Write your solution below\n    pass\n"

    # 2. JavaScript (ES6)
    js_tree_def = (
        "/**\n"
        " * Definition for a binary tree node.\n"
        " * function TreeNode(val, left, right) {\n"
        " *     this.val = (val===undefined ? 0 : val);\n"
        " *     this.left = (left===undefined ? null : left);\n"
        " *     this.right = (right===undefined ? null : right);\n"
        " * }\n"
        " */\n"
    ) if needs_tree else ""

    js_code = f"{js_tree_def}function {fn_name}({param_str_js}) {{\n    // State Time Complexity: O(?), Space Complexity: O(?)\n    // Write your solution below\n}}\n"

    # 3. TypeScript
    ts_params = ", ".join(
        f"{name}: {('TreeNode | null' if needs_tree and name in ('root', 'p', 'q') else ('ListNode | null' if needs_list and name == 'head' else ('number[]' if 'num' in name or 'arr' in name or name in ('prices', 'height', 'coins') else ('string' if name in ('s', 't') else ('number[][]' if name in ('intervals', 'matrix', 'costs') else 'number')))))}"
        for name, _ in params
    )
    ts_code = f"function {fn_name}({ts_params}): any {{\n    // State Time Complexity: O(?), Space Complexity: O(?)\n    // Write your solution below\n    return null;\n}}\n"

    # 4. C++ (C++20)
    cpp_params = ", ".join(
        f"{('TreeNode*' if needs_tree and name in ('root', 'p', 'q') else ('ListNode*' if needs_list and name == 'head' else ('vector<int>&' if 'num' in name or 'arr' in name or name in ('prices', 'height', 'coins') else ('string' if name in ('s', 't') else ('vector<vector<int>>&' if name in ('intervals', 'matrix', 'costs') else 'int')))))} {name}"
        for name, _ in params
    )
    cpp_ret = "TreeNode*" if needs_tree and fn_name == "lowestCommonAncestor" else "int"
    cpp_code = (
        "#include <vector>\n"
        "#include <string>\n"
        "#include <unordered_map>\n"
        "using namespace std;\n\n"
        "class Solution {\n"
        "public:\n"
        f"    {cpp_ret} {fn_name}({cpp_params}) {{\n"
        "        // Time Complexity: O(?), Space Complexity: O(?)\n"
        "        // Write your solution below\n"
        "        return {};\n"
        "    }\n"
        "};\n"
    )

    # 5. Java (Java 21)
    java_params = ", ".join(
        f"{('TreeNode' if needs_tree and name in ('root', 'p', 'q') else ('ListNode' if needs_list and name == 'head' else ('int[]' if 'num' in name or 'arr' in name or name in ('prices', 'height', 'coins') else ('String' if name in ('s', 't') else ('int[][]' if name in ('intervals', 'matrix', 'costs') else 'int')))))} {name}"
        for name, _ in params
    )
    java_ret = "TreeNode" if needs_tree and fn_name == "lowestCommonAncestor" else "int[]"
    java_code = (
        "import java.util.*;\n\n"
        "class Solution {\n"
        f"    public {java_ret} {fn_name}({java_params}) {{\n"
        "        // Time Complexity: O(?), Space Complexity: O(?)\n"
        "        // Write your solution below\n"
        "        return null;\n"
        "    }\n"
        "}\n"
    )

    # 6. Go (1.22)
    go_params = ", ".join(
        f"{name} {('*TreeNode' if needs_tree and name in ('root', 'p', 'q') else ('*ListNode' if needs_list and name == 'head' else ('[]int' if 'num' in name or 'arr' in name or name in ('prices', 'height', 'coins') else ('string' if name in ('s', 't') else ('[][]int' if name in ('intervals', 'matrix', 'costs') else 'int')))))}"
        for name, _ in params
    )
    go_code = (
        "package main\n\n"
        f"func {fn_name}({go_params}) interface{{}} {{\n"
        "    // Write your solution below\n"
        "    return nil\n"
        "}\n"
    )

    # 7. Rust (1.76)
    rust_params = ", ".join(f"{name}: i32" for name in param_names)
    rust_code = (
        f"pub fn {fn_name}({rust_params}) -> i32 {{\n"
        "    // Write your solution below\n"
        "    0\n"
        "}\n"
    )

    return {
        "python": py_code,
        "javascript": js_code,
        "typescript": ts_code,
        "cpp": cpp_code,
        "java": java_code,
        "go": go_code,
        "rust": rust_code
    }


def is_coding_problem(question_text: str, topic: str = "") -> bool:
    """
    Accurately classifies if a question requires code writing in the IDE
    vs being a conceptual/discussion question (like Python decorators, ML loss functions, System Design).
    """
    norm_topic = (topic or "").lower()
    q_lower = question_text.lower()

    # Explicitly check for problem declaration syntax
    if any(k in q_lower for k in ["### problem:", "test cases", "test case 1", "constraints", "expected time complexity", "palindrome"]):
        return True

    # If the topic is explicitly Python, ML, or System Design, check if it explicitly asks for a DSA problem
    if any(t in norm_topic for t in ["system design", "machine learning", "ml", "database", "sql"]):
        return False

    if "python" in norm_topic and not any(k in q_lower for k in ["leetcode", "array", "binary tree", "linked list", "target", "matrix", "palindrome"]):
        return False

    # Check for DSA algorithmic keywords
    dsa_markers = [
        "given an array", "given a binary tree", "given a string `s`", "given two strings",
        "return the indices", "in-place", "time complexity", "big-o", "auxiliary space",
        "test cases", "lowest common ancestor", "dynamic programming", "palindrome",
        "provide your solution", "solution (code)", "input:", "output:"
    ]
    return any(m in q_lower for m in dsa_markers)
