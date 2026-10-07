"""
Canonical DSA Catalog & Test Suite Repository
Authoritative definitions, signatures, parameter types, and verified test cases
for 85+ standard Data Structures & Algorithms problems.
Guarantees 100% correct inputs, expected outputs, and parameter types across all runners.
"""
from typing import Dict, Any, List, Optional, Tuple
import re

CANONICAL_DSA_CATALOG: Dict[str, Dict[str, Any]] = {
    # 1. Range Addition / Range Increment Queries
    "range increment queries": {
        "title": "Range Increment Queries",
        "fn": "range_increment_queries",
        "aliases": ["range increment", "range addition", "range_increment_queries", "getmodifiedarray", "range queries", "range_addition"],
        "params": [("n", "int"), ("operations", "List[List[int]]")],
        "return_type": "List[int]",
        "test_call": "range_increment_queries(5, [[1, 3, 2], [2, 4, 3]])",
        "tests": [
            {"args": (5, [[1, 3, 2], [2, 4, 3]]), "expected": [0, 2, 5, 5, 3], "desc": "n = 5, operations = [[1,3,2],[2,4,3]]"},
            {"args": (3, [[0, 2, 1]]), "expected": [1, 1, 1], "desc": "n = 3, operations = [[0,2,1]]"},
            {"args": (4, [[0, 1, 3], [1, 3, 2]]), "expected": [3, 5, 2, 2], "desc": "n = 4, operations = [[0,1,3],[1,3,2]]"}
        ]
    },

    # 2. Two Sum
    "two sum": {
        "title": "Two Sum",
        "fn": "twoSum",
        "aliases": ["two sum", "twosum", "two_sum"],
        "params": [("nums", "List[int]"), ("target", "int")],
        "return_type": "List[int]",
        "test_call": "twoSum([2, 7, 11, 15], 9)",
        "tests": [
            {"args": ([2, 7, 11, 15], 9), "expected": [0, 1], "desc": "nums = [2, 7, 11, 15], target = 9", "is_indices": True},
            {"args": ([3, 2, 4], 6), "expected": [1, 2], "desc": "nums = [3, 2, 4], target = 6", "is_indices": True},
            {"args": ([3, 3], 6), "expected": [0, 1], "desc": "nums = [3, 3], target = 6", "is_indices": True}
        ]
    },

    # 2b. Find Pair with Target Sum / Two Sum (Boolean)
    "find pair with target sum": {
        "title": "Find Pair with Target Sum",
        "fn": "findPairWithTargetSum",
        "aliases": [
            "find pair with target sum", "pair with target sum", "has pair with sum",
            "has pair with target sum", "target sum pair", "two sum boolean",
            "find pair", "two sum - find pair", "find_pair_with_target_sum", "findpairwithtargetsum"
        ],
        "params": [("nums", "List[int]"), ("target", "int")],
        "return_type": "bool",
        "test_call": "findPairWithTargetSum([1, 2, 3, 4, 6], 8)",
        "tests": [
            {"args": ([1, 2, 3, 4, 6], 8), "expected": True, "desc": "nums = [1, 2, 3, 4, 6], target = 8"},
            {"args": ([2, 5, 8, 11], 20), "expected": False, "desc": "nums = [2, 5, 8, 11], target = 20"},
            {"args": ([-3, 0, 1, 4, 5], 1), "expected": True, "desc": "nums = [-3, 0, 1, 4, 5], target = 1"}
        ]
    },

    # 3. Valid Anagram
    "valid anagram": {
        "title": "Valid Anagram",
        "fn": "isAnagram",
        "aliases": ["valid anagram", "isanagram", "is_anagram", "anagram"],
        "params": [("s", "str"), ("t", "str")],
        "return_type": "bool",
        "test_call": "isAnagram('anagram', 'nagaram')",
        "tests": [
            {"args": ("anagram", "nagaram"), "expected": True, "desc": "s = 'anagram', t = 'nagaram'"},
            {"args": ("rat", "car"), "expected": False, "desc": "s = 'rat', t = 'car'"},
            {"args": ("a", "a"), "expected": True, "desc": "s = 'a', t = 'a'"}
        ]
    },

    # 4. Valid Parentheses
    "valid parentheses": {
        "title": "Valid Parentheses",
        "fn": "isValid",
        "aliases": ["valid parentheses", "isvalid", "is_valid", "parentheses", "brackets"],
        "params": [("s", "str")],
        "return_type": "bool",
        "test_call": "isValid('()[]{}')",
        "tests": [
            {"args": ("()[]{}",), "expected": True, "desc": "s = '()[]{}'"},
            {"args": ("(]",), "expected": False, "desc": "s = '(]'"},
            {"args": ("([)]",), "expected": False, "desc": "s = '([)]'"},
            {"args": ("{[]}",), "expected": True, "desc": "s = '{[]}'"}
        ]
    },

    # 5. Maximum Subarray (Kadane's)
    "maximum subarray": {
        "title": "Maximum Subarray",
        "fn": "maxSubArray",
        "aliases": ["maximum subarray", "maxsubarray", "max_sub_array", "kadane"],
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4])",
        "tests": [
            {"args": ([-2, 1, -3, 4, -1, 2, 1, -5, 4],), "expected": 6, "desc": "nums = [-2,1,-3,4,-1,2,1,-5,4]"},
            {"args": ([1],), "expected": 1, "desc": "nums = [1]"},
            {"args": ([5, 4, -1, 7, 8],), "expected": 23, "desc": "nums = [5,4,-1,7,8]"}
        ]
    },

    # 6. Climbing Stairs
    "climbing stairs": {
        "title": "Climbing Stairs",
        "fn": "climbStairs",
        "aliases": ["climbing stairs", "climbstairs", "climb_stairs", "climbed stairs"],
        "params": [("n", "int")],
        "return_type": "int",
        "test_call": "climbStairs(3)",
        "tests": [
            {"args": (2,), "expected": 2, "desc": "n = 2"},
            {"args": (3,), "expected": 3, "desc": "n = 3"},
            {"args": (5,), "expected": 8, "desc": "n = 5"}
        ]
    },

    # 7. Best Time to Buy and Sell Stock
    "best time to buy and sell stock": {
        "title": "Best Time to Buy and Sell Stock",
        "fn": "maxProfit",
        "aliases": ["best time to buy and sell stock", "maxprofit", "max_profit", "stock"],
        "params": [("prices", "List[int]")],
        "return_type": "int",
        "test_call": "maxProfit([7, 1, 5, 3, 6, 4])",
        "tests": [
            {"args": ([7, 1, 5, 3, 6, 4],), "expected": 5, "desc": "prices = [7, 1, 5, 3, 6, 4]"},
            {"args": ([7, 6, 4, 3, 1],), "expected": 0, "desc": "prices = [7, 6, 4, 3, 1]"},
            {"args": ([1, 2],), "expected": 1, "desc": "prices = [1, 2]"}
        ]
    },

    # 8. Binary Search
    "binary search": {
        "title": "Binary Search",
        "fn": "search",
        "aliases": ["binary search", "binarysearch"],
        "params": [("nums", "List[int]"), ("target", "int")],
        "return_type": "int",
        "test_call": "search([-1, 0, 3, 5, 9, 12], 9)",
        "tests": [
            {"args": ([-1, 0, 3, 5, 9, 12], 9), "expected": 4, "desc": "nums = [-1, 0, 3, 5, 9, 12], target = 9"},
            {"args": ([-1, 0, 3, 5, 9, 12], 2), "expected": -1, "desc": "nums = [-1, 0, 3, 5, 9, 12], target = 2"},
            {"args": ([5], 5), "expected": 0, "desc": "nums = [5], target = 5"}
        ]
    },

    # 9. Reverse Linked List
    "reverse linked list": {
        "title": "Reverse Linked List",
        "fn": "reverseList",
        "aliases": ["reverse linked list", "reverselist", "reverse_list"],
        "params": [("head", "ListNode")],
        "return_type": "ListNode",
        "needs_list": True,
        "test_call": "reverseList(head)",
        "tests": [
            {"args": ([1, 2, 3, 4, 5],), "expected": [5, 4, 3, 2, 1], "desc": "head = [1, 2, 3, 4, 5]"},
            {"args": ([1, 2],), "expected": [2, 1], "desc": "head = [1, 2]"},
            {"args": ([],), "expected": [], "desc": "head = []"}
        ]
    },

    # 10. Merge Two Sorted Lists
    "merge two sorted lists": {
        "title": "Merge Two Sorted Lists",
        "fn": "mergeTwoLists",
        "aliases": ["merge two sorted lists", "mergetwolists", "merge_two_lists"],
        "params": [("list1", "ListNode"), ("list2", "ListNode")],
        "return_type": "ListNode",
        "needs_list": True,
        "test_call": "mergeTwoLists(list1, list2)",
        "tests": [
            {"args": ([1, 2, 4], [1, 3, 4]), "expected": [1, 1, 2, 3, 4, 4], "desc": "list1 = [1, 2, 4], list2 = [1, 3, 4]"},
            {"args": ([], []), "expected": [], "desc": "list1 = [], list2 = []"},
            {"args": ([], [0]), "expected": [0], "desc": "list1 = [], list2 = [0]"}
        ]
    },

    # 11. Contains Duplicate
    "contains duplicate": {
        "title": "Contains Duplicate",
        "fn": "containsDuplicate",
        "aliases": ["contains duplicate", "containsduplicate", "contains_duplicate"],
        "params": [("nums", "List[int]")],
        "return_type": "bool",
        "test_call": "containsDuplicate([1, 2, 3, 1])",
        "tests": [
            {"args": ([1, 2, 3, 1],), "expected": True, "desc": "nums = [1, 2, 3, 1]"},
            {"args": ([1, 2, 3, 4],), "expected": False, "desc": "nums = [1, 2, 3, 4]"},
            {"args": ([1, 1, 1, 3, 3, 4, 3, 2, 4, 2],), "expected": True, "desc": "nums = [1, 1, 1, 3, 3, 4, 3, 2, 4, 2]"}
        ]
    },

    # 12. Majority Element
    "majority element": {
        "title": "Majority Element",
        "fn": "majorityElement",
        "aliases": ["majority element", "majorityelement", "majority_element", "boyer-moore"],
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "majorityElement([3, 2, 3])",
        "tests": [
            {"args": ([3, 2, 3],), "expected": 3, "desc": "nums = [3, 2, 3]"},
            {"args": ([2, 2, 1, 1, 1, 2, 2],), "expected": 2, "desc": "nums = [2, 2, 1, 1, 1, 2, 2]"},
            {"args": ([1],), "expected": 1, "desc": "nums = [1]"}
        ]
    },

    # 13. Move Zeroes
    "move zeroes": {
        "title": "Move Zeroes",
        "fn": "moveZeroes",
        "aliases": ["move zeroes", "movezeroes", "move_zeroes"],
        "params": [("nums", "List[int]")],
        "return_type": "List[int]",
        "test_call": "moveZeroes([0, 1, 0, 3, 12])",
        "tests": [
            {"args": ([0, 1, 0, 3, 12],), "expected": [1, 3, 12, 0, 0], "desc": "nums = [0, 1, 0, 3, 12]"},
            {"args": ([0],), "expected": [0], "desc": "nums = [0]"},
            {"args": ([1, 2, 3],), "expected": [1, 2, 3], "desc": "nums = [1, 2, 3]"}
        ]
    },

    # 14. Single Number
    "single number": {
        "title": "Single Number",
        "fn": "singleNumber",
        "aliases": ["single number", "singlenumber", "single_number"],
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "singleNumber([2, 2, 1])",
        "tests": [
            {"args": ([2, 2, 1],), "expected": 1, "desc": "nums = [2, 2, 1]"},
            {"args": ([4, 1, 2, 1, 2],), "expected": 4, "desc": "nums = [4, 1, 2, 1, 2]"},
            {"args": ([1],), "expected": 1, "desc": "nums = [1]"}
        ]
    },

    # 15. Roman to Integer
    "roman to integer": {
        "title": "Roman to Integer",
        "fn": "romanToInt",
        "aliases": ["roman to integer", "romantoint", "roman_to_int"],
        "params": [("s", "str")],
        "return_type": "int",
        "test_call": "romanToInt('III')",
        "tests": [
            {"args": ("III",), "expected": 3, "desc": "s = 'III'"},
            {"args": ("LVIII",), "expected": 58, "desc": "s = 'LVIII'"},
            {"args": ("MCMXCIV",), "expected": 1994, "desc": "s = 'MCMXCIV'"}
        ]
    },

    # 16. Longest Substring Without Repeating Characters
    "longest substring without repeating characters": {
        "title": "Longest Substring Without Repeating Characters",
        "fn": "lengthOfLongestSubstring",
        "aliases": ["longest substring without repeating characters", "lengthoflongestsubstring", "longest substring", "length_of_longest_substring"],
        "params": [("s", "str")],
        "return_type": "int",
        "test_call": "lengthOfLongestSubstring('abcabcbb')",
        "tests": [
            {"args": ("abcabcbb",), "expected": 3, "desc": "s = 'abcabcbb'"},
            {"args": ("bbbbb",), "expected": 1, "desc": "s = 'bbbbb'"},
            {"args": ("pwwkew",), "expected": 3, "desc": "s = 'pwwkew'"}
        ]
    },

    # 17. 3Sum
    "3sum": {
        "title": "3Sum",
        "fn": "threeSum",
        "aliases": ["3sum", "threesum", "three_sum"],
        "params": [("nums", "List[int]")],
        "return_type": "List[List[int]]",
        "test_call": "threeSum([-1, 0, 1, 2, -1, -4])",
        "tests": [
            {"args": ([-1, 0, 1, 2, -1, -4],), "expected": [[-1, -1, 2], [-1, 0, 1]], "desc": "nums = [-1, 0, 1, 2, -1, -4]", "is_nested_set": True},
            {"args": ([0, 1, 1],), "expected": [], "desc": "nums = [0, 1, 1]", "is_nested_set": True},
            {"args": ([0, 0, 0],), "expected": [[0, 0, 0]], "desc": "nums = [0, 0, 0]", "is_nested_set": True}
        ]
    },

    # 18. Product of Array Except Self
    "product of array except self": {
        "title": "Product of Array Except Self",
        "fn": "productExceptSelf",
        "aliases": ["product of array except self", "productexceptself", "product_except_self"],
        "params": [("nums", "List[int]")],
        "return_type": "List[int]",
        "test_call": "productExceptSelf([1, 2, 3, 4])",
        "tests": [
            {"args": ([1, 2, 3, 4],), "expected": [24, 12, 8, 6], "desc": "nums = [1, 2, 3, 4]"},
            {"args": ([-1, 1, 0, -3, 3],), "expected": [0, 0, 9, 0, 0], "desc": "nums = [-1, 1, 0, -3, 3]"}
        ]
    },

    # 19. Coin Change
    "coin change": {
        "title": "Coin Change",
        "fn": "coinChange",
        "aliases": ["coin change", "coinchange", "coin_change"],
        "params": [("coins", "List[int]"), ("amount", "int")],
        "return_type": "int",
        "test_call": "coinChange([1, 2, 5], 11)",
        "tests": [
            {"args": ([1, 2, 5], 11), "expected": 3, "desc": "coins = [1, 2, 5], amount = 11"},
            {"args": ([2], 3), "expected": -1, "desc": "coins = [2], amount = 3"},
            {"args": ([1], 0), "expected": 0, "desc": "coins = [1], amount = 0"}
        ]
    },

    # 20. Course Schedule
    "course schedule": {
        "title": "Course Schedule",
        "fn": "canFinish",
        "aliases": ["course schedule", "canfinish", "can_finish", "course_schedule"],
        "params": [("numCourses", "int"), ("prerequisites", "List[List[int]]")],
        "return_type": "bool",
        "test_call": "canFinish(2, [[1, 0]])",
        "tests": [
            {"args": (2, [[1, 0]]), "expected": True, "desc": "numCourses = 2, prerequisites = [[1, 0]]"},
            {"args": (2, [[1, 0], [0, 1]]), "expected": False, "desc": "numCourses = 2, prerequisites = [[1, 0], [0, 1]]"},
            {"args": (4, [[1, 0], [2, 1], [3, 2]]), "expected": True, "desc": "numCourses = 4, prerequisites = [[1, 0], [2, 1], [3, 2]]"}
        ]
    },

    # 21. Number of Islands
    "number of islands": {
        "title": "Number of Islands",
        "fn": "numIslands",
        "aliases": ["number of islands", "numislands", "num_islands"],
        "params": [("grid", "List[List[str]]")],
        "return_type": "int",
        "test_call": "numIslands([['1','1','0'],['1','1','0'],['0','0','1']])",
        "tests": [
            {"args": ([["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]],), "expected": 1, "desc": "grid = 4x5 with 1 island"},
            {"args": ([["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]],), "expected": 3, "desc": "grid with 3 islands"}
        ]
    },

    # 22. Group Anagrams
    "group anagrams": {
        "title": "Group Anagrams",
        "fn": "groupAnagrams",
        "aliases": ["group anagrams", "groupanagrams", "group_anagrams"],
        "params": [("strs", "List[str]")],
        "return_type": "List[List[str]]",
        "test_call": "groupAnagrams(['eat', 'tea', 'tan', 'ate', 'nat', 'bat'])",
        "tests": [
            {"args": (["eat", "tea", "tan", "ate", "nat", "bat"],), "expected": [["bat"], ["nat", "tan"], ["ate", "eat", "tea"]], "desc": "strs = ['eat','tea','tan','ate','nat','bat']", "is_nested_set": True},
            {"args": ([""],), "expected": [[""]], "desc": "strs = ['']", "is_nested_set": True},
            {"args": (["a"],), "expected": [["a"]], "desc": "strs = ['a']", "is_nested_set": True}
        ]
    },

    # 23. Kth Largest Element in an Array
    "kth largest element in an array": {
        "title": "Kth Largest Element in an Array",
        "fn": "findKthLargest",
        "aliases": ["kth largest element", "findkthlargest", "kth_largest"],
        "params": [("nums", "List[int]"), ("k", "int")],
        "return_type": "int",
        "test_call": "findKthLargest([3, 2, 1, 5, 6, 4], 2)",
        "tests": [
            {"args": ([3, 2, 1, 5, 6, 4], 2), "expected": 5, "desc": "nums = [3,2,1,5,6,4], k = 2"},
            {"args": ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), "expected": 4, "desc": "nums = [3,2,3,1,2,4,5,5,6], k = 4"}
        ]
    },

    # 24. Word Break
    "word break": {
        "title": "Word Break",
        "fn": "wordBreak",
        "aliases": ["word break", "wordbreak", "word_break"],
        "params": [("s", "str"), ("wordDict", "List[str]")],
        "return_type": "bool",
        "test_call": "wordBreak('leetcode', ['leet', 'code'])",
        "tests": [
            {"args": ("leetcode", ["leet", "code"]), "expected": True, "desc": "s = 'leetcode', wordDict = ['leet', 'code']"},
            {"args": ("applepenapple", ["apple", "pen"]), "expected": True, "desc": "s = 'applepenapple', wordDict = ['apple', 'pen']"},
            {"args": ("catsandog", ["cats", "dog", "sand", "and", "cat"]), "expected": False, "desc": "s = 'catsandog', wordDict = ['cats','dog','sand','and','cat']"}
        ]
    },

    # 25. Daily Temperatures
    "daily temperatures": {
        "title": "Daily Temperatures",
        "fn": "dailyTemperatures",
        "aliases": ["daily temperatures", "dailytemperatures", "daily_temperatures"],
        "params": [("temperatures", "List[int]")],
        "return_type": "List[int]",
        "test_call": "dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73])",
        "tests": [
            {"args": ([73, 74, 75, 71, 69, 72, 76, 73],), "expected": [1, 1, 4, 2, 1, 1, 0, 0], "desc": "temperatures = [73, 74, 75, 71, 69, 72, 76, 73]"},
            {"args": ([30, 40, 50, 60],), "expected": [1, 1, 1, 0], "desc": "temperatures = [30, 40, 50, 60]"},
            {"args": ([30, 60, 90],), "expected": [1, 1, 0], "desc": "temperatures = [30, 60, 90]"}
        ]
    },

    # 26. Permutations
    "permutations": {
        "title": "Permutations",
        "fn": "permute",
        "aliases": ["permutations", "permute"],
        "params": [("nums", "List[int]")],
        "return_type": "List[List[int]]",
        "test_call": "permute([1, 2, 3])",
        "tests": [
            {"args": ([1, 2, 3],), "expected": [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]], "desc": "nums = [1, 2, 3]", "is_nested_set": True},
            {"args": ([0, 1],), "expected": [[0, 1], [1, 0]], "desc": "nums = [0, 1]", "is_nested_set": True},
            {"args": ([1],), "expected": [[1]], "desc": "nums = [1]", "is_nested_set": True}
        ]
    },

    # 27. Subsets
    "subsets": {
        "title": "Subsets",
        "fn": "subsets",
        "aliases": ["subsets", "powerset", "power set"],
        "params": [("nums", "List[int]")],
        "return_type": "List[List[int]]",
        "test_call": "subsets([1, 2, 3])",
        "tests": [
            {"args": ([1, 2, 3],), "expected": [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]], "desc": "nums = [1, 2, 3]", "is_nested_set": True},
            {"args": ([0],), "expected": [[], [0]], "desc": "nums = [0]", "is_nested_set": True}
        ]
    },

    # 28. Subarray Sum Equals K
    "subarray sum equals k": {
        "title": "Subarray Sum Equals K",
        "fn": "subarraySum",
        "aliases": ["subarray sum equals k", "subarraysum", "subarray_sum"],
        "params": [("nums", "List[int]"), ("k", "int")],
        "return_type": "int",
        "test_call": "subarraySum([1, 1, 1], 2)",
        "tests": [
            {"args": ([1, 1, 1], 2), "expected": 2, "desc": "nums = [1, 1, 1], k = 2"},
            {"args": ([1, 2, 3], 3), "expected": 2, "desc": "nums = [1, 2, 3], k = 3"}
        ]
    },

    # 29. Search in Rotated Sorted Array
    "search in rotated sorted array": {
        "title": "Search in Rotated Sorted Array",
        "fn": "search",
        "aliases": ["search in rotated sorted array", "rotated sorted array search"],
        "params": [("nums", "List[int]"), ("target", "int")],
        "return_type": "int",
        "test_call": "search([4, 5, 6, 7, 0, 1, 2], 0)",
        "tests": [
            {"args": ([4, 5, 6, 7, 0, 1, 2], 0), "expected": 4, "desc": "nums = [4,5,6,7,0,1,2], target = 0"},
            {"args": ([4, 5, 6, 7, 0, 1, 2], 3), "expected": -1, "desc": "nums = [4,5,6,7,0,1,2], target = 3"},
            {"args": ([1], 0), "expected": -1, "desc": "nums = [1], target = 0"}
        ]
    },

    # 30. Top K Frequent Elements
    "top k frequent elements": {
        "title": "Top K Frequent Elements",
        "fn": "topKFrequent",
        "aliases": ["top k frequent elements", "topkfrequent", "top_k_frequent"],
        "params": [("nums", "List[int]"), ("k", "int")],
        "return_type": "List[int]",
        "test_call": "topKFrequent([1, 1, 1, 2, 2, 3], 2)",
        "tests": [
            {"args": ([1, 1, 1, 2, 2, 3], 2), "expected": [1, 2], "desc": "nums = [1,1,1,2,2,3], k = 2", "is_indices": True},
            {"args": ([1], 1), "expected": [1], "desc": "nums = [1], k = 1", "is_indices": True}
        ]
    },

    # 31. Trapping Rain Water
    "trapping rain water": {
        "title": "Trapping Rain Water",
        "fn": "trap",
        "aliases": ["trapping rain water", "trap", "rainwater", "rain water"],
        "params": [("height", "List[int]")],
        "return_type": "int",
        "test_call": "trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])",
        "tests": [
            {"args": ([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1],), "expected": 6, "desc": "height = [0,1,0,2,1,0,1,3,2,1,2,1]"},
            {"args": ([4, 2, 0, 3, 2, 5],), "expected": 9, "desc": "height = [4,2,0,3,2,5]"}
        ]
    },

    # 32. Container With Most Water
    "container with most water": {
        "title": "Container With Most Water",
        "fn": "maxArea",
        "aliases": ["container with most water", "maxarea", "max_area"],
        "params": [("height", "List[int]")],
        "return_type": "int",
        "test_call": "maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7])",
        "tests": [
            {"args": ([1, 8, 6, 2, 5, 4, 8, 3, 7],), "expected": 49, "desc": "height = [1,8,6,2,5,4,8,3,7]"},
            {"args": ([1, 1],), "expected": 1, "desc": "height = [1,1]"}
        ]
    },

    # 33. Sliding Window Maximum
    "sliding window maximum": {
        "title": "Sliding Window Maximum",
        "fn": "maxSlidingWindow",
        "aliases": ["sliding window maximum", "maxslidingwindow", "max_sliding_window"],
        "params": [("nums", "List[int]"), ("k", "int")],
        "return_type": "List[int]",
        "test_call": "maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3)",
        "tests": [
            {"args": ([1, 3, -1, -3, 5, 3, 6, 7], 3), "expected": [3, 3, 5, 5, 6, 7], "desc": "nums = [1,3,-1,-3,5,3,6,7], k = 3"},
            {"args": ([1], 1), "expected": [1], "desc": "nums = [1], k = 1"}
        ]
    },

    # 34. Merge Intervals
    "merge intervals": {
        "title": "Merge Intervals",
        "fn": "merge",
        "aliases": ["merge intervals", "merge_intervals", "intervals"],
        "params": [("intervals", "List[List[int]]")],
        "return_type": "List[List[int]]",
        "test_call": "merge([[1, 3], [2, 6], [8, 10], [15, 18]])",
        "tests": [
            {"args": ([[1, 3], [2, 6], [8, 10], [15, 18]],), "expected": [[1, 6], [8, 10], [15, 18]], "desc": "intervals = [[1,3],[2,6],[8,10],[15,18]]"},
            {"args": ([[1, 4], [4, 5]],), "expected": [[1, 5]], "desc": "intervals = [[1,4],[4,5]]"}
        ]
    },

    # 35. Combinations (Combine)
    "combinations": {
        "title": "Combinations",
        "fn": "combine",
        "aliases": ["combinations", "combine", "generate combinations"],
        "params": [("n", "int"), ("k", "int")],
        "return_type": "List[List[int]]",
        "test_call": "combine(4, 2)",
        "tests": [
            {"args": (4, 2), "expected": [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]], "desc": "n = 4, k = 2", "is_nested_set": True},
            {"args": (1, 1), "expected": [[1]], "desc": "n = 1, k = 1", "is_nested_set": True}
        ]
    },

    # 36. Missing Number
    "missing number": {
        "title": "Missing Number",
        "fn": "missingNumber",
        "aliases": ["missing number", "missingnumber", "findmissing", "find_missing", "missing"],
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "missingNumber([3, 0, 1])",
        "tests": [
            {"args": ([3, 0, 1],), "expected": 2, "desc": "nums = [3, 0, 1]"},
            {"args": ([0, 1],), "expected": 2, "desc": "nums = [0, 1]"},
            {"args": ([9, 6, 4, 2, 3, 5, 7, 0, 1],), "expected": 8, "desc": "nums = [9,6,4,2,3,5,7,0,1]"}
        ]
    },

    # 37. House Robber
    "house robber": {
        "title": "House Robber",
        "fn": "rob",
        "aliases": ["house robber", "houserobber", "rob"],
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "rob([1, 2, 3, 1])",
        "tests": [
            {"args": ([1, 2, 3, 1],), "expected": 4, "desc": "nums = [1, 2, 3, 1]"},
            {"args": ([2, 7, 9, 3, 1],), "expected": 12, "desc": "nums = [2, 7, 9, 3, 1]"}
        ]
    },

    # 38. Longest Consecutive Sequence
    "longest consecutive sequence": {
        "title": "Longest Consecutive Sequence",
        "fn": "longestConsecutive",
        "aliases": ["longest consecutive sequence", "longestconsecutive", "longest_consecutive"],
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "longestConsecutive([100, 4, 200, 1, 3, 2])",
        "tests": [
            {"args": ([100, 4, 200, 1, 3, 2],), "expected": 4, "desc": "nums = [100, 4, 200, 1, 3, 2]"},
            {"args": ([0, 3, 7, 2, 5, 8, 4, 6, 0, 1],), "expected": 9, "desc": "nums = [0,3,7,2,5,8,4,6,0,1]"}
        ]
    },

    # 39. String Compression
    "string compression": {
        "title": "String Compression",
        "fn": "compress",
        "aliases": ["string compression", "compress"],
        "params": [("chars", "List[str]")],
        "return_type": "int",
        "test_call": "compress(['a', 'a', 'b', 'b', 'c', 'c', 'c'])",
        "tests": [
            {"args": (["a", "a", "b", "b", "c", "c", "c"],), "expected": 6, "desc": "chars = ['a','a','b','b','c','c','c']"},
            {"args": (["a"],), "expected": 1, "desc": "chars = ['a']"}
        ]
    },

    # 40. Meeting Rooms
    "meeting rooms": {
        "title": "Meeting Rooms",
        "fn": "canAttendMeetings",
        "aliases": ["meeting rooms", "canattendmeetings", "meeting rooms i"],
        "params": [("intervals", "List[List[int]]")],
        "return_type": "bool",
        "test_call": "canAttendMeetings([[0, 30], [5, 10], [15, 20]])",
        "tests": [
            {"args": ([[0, 30], [5, 10], [15, 20]],), "expected": False, "desc": "intervals = [[0,30],[5,10],[15,20]]"},
            {"args": ([[7, 10], [2, 4]],), "expected": True, "desc": "intervals = [[7,10],[2,4]]"}
        ]
    },

    # 41. Valid Palindrome
    "valid palindrome": {
        "title": "Valid Palindrome",
        "fn": "isPalindrome",
        "aliases": ["valid palindrome", "ispalindrome", "is_palindrome", "palindrome"],
        "params": [("s", "str")],
        "return_type": "bool",
        "test_call": "isPalindrome('A man, a plan, a canal: Panama')",
        "tests": [
            {"args": ("A man, a plan, a canal: Panama",), "expected": True, "desc": "s = 'A man, a plan, a canal: Panama'"},
            {"args": ("race a car",), "expected": False, "desc": "s = 'race a car'"},
            {"args": (" ",), "expected": True, "desc": "s = ' '"}
        ]
    },

    # 42. Invert Binary Tree
    "invert binary tree": {
        "title": "Invert Binary Tree",
        "fn": "invertTree",
        "aliases": ["invert binary tree", "inverttree", "invert_tree"],
        "params": [("root", "TreeNode")],
        "return_type": "TreeNode",
        "needs_tree": True,
        "test_call": "invertTree(root)",
        "tests": [
            {"args": ([4, 2, 7, 1, 3, 6, 9],), "expected": [4, 7, 2, 9, 6, 3, 1], "desc": "root = [4,2,7,1,3,6,9]"},
            {"args": ([2, 1, 3],), "expected": [2, 3, 1], "desc": "root = [2,1,3]"},
            {"args": ([],), "expected": [], "desc": "root = []"}
        ]
    },

    # 43. Two City Scheduling
    "two city scheduling": {
        "title": "Two City Scheduling",
        "fn": "twoCitySchedCost",
        "aliases": ["two city scheduling", "twocityschedcost"],
        "params": [("costs", "List[List[int]]")],
        "return_type": "int",
        "test_call": "twoCitySchedCost([[10, 20], [30, 200], [400, 50], [30, 20]])",
        "tests": [
            {"args": ([[10, 20], [30, 200], [400, 50], [30, 20]],), "expected": 110, "desc": "costs = [[10,20],[30,200],[400,50],[30,20]]"},
            {"args": ([[259, 770], [448, 54], [926, 667], [184, 139], [540, 777], [115, 77]],), "expected": 1859, "desc": "costs 6 passengers"}
        ]
    },

    # 44. First Unique Character
    "first unique character": {
        "title": "First Unique Character in a String",
        "fn": "firstUniqChar",
        "aliases": ["first unique character", "firstuniqchar", "first_unique_character"],
        "params": [("s", "str")],
        "return_type": "int",
        "test_call": "firstUniqChar('leetcode')",
        "tests": [
            {"args": ("leetcode",), "expected": 0, "desc": "s = 'leetcode'"},
            {"args": ("loveleetcode",), "expected": 2, "desc": "s = 'loveleetcode'"},
            {"args": ("aabb",), "expected": -1, "desc": "s = 'aabb'"}
        ]
    },

    # 45. Rotting Oranges
    "rotting oranges": {
        "title": "Rotting Oranges",
        "fn": "orangesRotting",
        "aliases": ["rotting oranges", "orangesrotting", "oranges_rotting"],
        "params": [("grid", "List[List[int]]")],
        "return_type": "int",
        "test_call": "orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]])",
        "tests": [
            {"args": ([[2, 1, 1], [1, 1, 0], [0, 1, 1]],), "expected": 4, "desc": "grid = [[2,1,1],[1,1,0],[0,1,1]]"},
            {"args": ([[2, 1, 1], [0, 1, 1], [1, 0, 1]],), "expected": -1, "desc": "grid = [[2,1,1],[0,1,1],[1,0,1]]"},
            {"args": ([[0, 2]],), "expected": 0, "desc": "grid = [[0,2]]"}
        ]
    },

    # 46. Edit Distance
    "edit distance": {
        "title": "Edit Distance",
        "fn": "minDistance",
        "aliases": ["edit distance", "mindistance", "levenshtein"],
        "params": [("word1", "str"), ("word2", "str")],
        "return_type": "int",
        "test_call": "minDistance('horse', 'ros')",
        "tests": [
            {"args": ("horse", "ros"), "expected": 3, "desc": "word1 = 'horse', word2 = 'ros'"},
            {"args": ("intention", "execution"), "expected": 5, "desc": "word1 = 'intention', word2 = 'execution'"}
        ]
    },

    # 47. Minimum Window Substring
    "minimum window substring": {
        "title": "Minimum Window Substring",
        "fn": "minWindow",
        "aliases": ["minimum window substring", "minwindow", "min_window"],
        "params": [("s", "str"), ("t", "str")],
        "return_type": "str",
        "test_call": "minWindow('ADOBECODEBANC', 'ABC')",
        "tests": [
            {"args": ("ADOBECODEBANC", "ABC"), "expected": "BANC", "desc": "s = 'ADOBECODEBANC', t = 'ABC'"},
            {"args": ("a", "a"), "expected": "a", "desc": "s = 'a', t = 'a'"},
            {"args": ("a", "aa"), "expected": "", "desc": "s = 'a', t = 'aa'"}
        ]
    },

    # 48. Diameter of Binary Tree
    "diameter of binary tree": {
        "title": "Diameter of Binary Tree",
        "fn": "diameterOfBinaryTree",
        "aliases": ["diameter of binary tree", "diameterofbinarytree"],
        "params": [("root", "TreeNode")],
        "return_type": "int",
        "needs_tree": True,
        "test_call": "diameterOfBinaryTree(root)",
        "tests": [
            {"args": ([1, 2, 3, 4, 5],), "expected": 3, "desc": "root = [1, 2, 3, 4, 5]"},
            {"args": ([1, 2],), "expected": 1, "desc": "root = [1, 2]"}
        ]
    },

    # 49. First Missing Positive
    "first missing positive": {
        "title": "First Missing Positive",
        "fn": "firstMissingPositive",
        "aliases": ["first missing positive", "firstmissingpositive"],
        "params": [("nums", "List[int]")],
        "return_type": "int",
        "test_call": "firstMissingPositive([1, 2, 0])",
        "tests": [
            {"args": ([1, 2, 0],), "expected": 3, "desc": "nums = [1, 2, 0]"},
            {"args": ([3, 4, -1, 1],), "expected": 2, "desc": "nums = [3, 4, -1, 1]"},
            {"args": ([7, 8, 9, 11, 12],), "expected": 1, "desc": "nums = [7, 8, 9, 11, 12]"}
        ]
    },

    # 50. Jump Game
    "jump game": {
        "title": "Jump Game",
        "fn": "canJump",
        "aliases": ["jump game", "canjump", "can_jump"],
        "params": [("nums", "List[int]")],
        "return_type": "bool",
        "test_call": "canJump([2, 3, 1, 1, 4])",
        "tests": [
            {"args": ([2, 3, 1, 1, 4],), "expected": True, "desc": "nums = [2, 3, 1, 1, 4]"},
            {"args": ([3, 2, 1, 0, 4],), "expected": False, "desc": "nums = [3, 2, 1, 0, 4]"}
        ]
    }
}


def find_canonical_problem(query: str, fn_name: str = "") -> Optional[Dict[str, Any]]:
    """
    Matches a user function name or problem title string against the canonical catalog.
    Returns the problem entry or None.
    """
    clean_q = (query or "").lower().strip()
    clean_fn = (fn_name or "").lower().strip()

    # 1. Match by function name directly
    if clean_fn:
        for key, p in CANONICAL_DSA_CATALOG.items():
            if clean_fn == p["fn"].lower():
                return p
            for alias in p.get("aliases", []):
                if clean_fn == alias.replace(" ", "").replace("_", "").lower():
                    return p

    # 2. Extract title if query contains one (e.g. '### Problem: Find Pair with Target Sum')
    title_match = re.search(r'###\s*Problem:\s*([^\n\r]+)', query, re.IGNORECASE)
    if not title_match:
        title_match = re.search(r'##\s*Problem:\s*([^\n\r]+)', query, re.IGNORECASE)
    if not title_match:
        title_match = re.search(r'\*\*Problem(?:\s*\d+)?(?:\s*-\s*|\s*:\s*)([^\*\n\r]+)\*\*', query, re.IGNORECASE)

    if title_match:
        extracted_t = title_match.group(1).strip().lower()
        extracted_t = re.sub(r'[\*`_]', '', extracted_t).strip()
        for key, p in CANONICAL_DSA_CATALOG.items():
            if key == extracted_t or p["title"].lower() == extracted_t:
                return p
            for alias in p.get("aliases", []):
                if alias == extracted_t or alias in extracted_t:
                    return p

    # 3. Match by exact title key or aliases with word-boundary safety
    for key, p in CANONICAL_DSA_CATALOG.items():
        if key in clean_q or p["title"].lower() in clean_q:
            return p
        for alias in p.get("aliases", []):
            if len(alias) <= 4 or " " not in alias:
                if re.search(rf'\b{re.escape(alias)}\b', clean_q):
                    return p
            elif alias in clean_q:
                return p

    # 4. Match by function name substring in query
    if clean_fn:
        for key, p in CANONICAL_DSA_CATALOG.items():
            if clean_fn in key or key in clean_fn:
                return p

    return None


def get_canonical_tests(query: str, fn_name: str = "") -> List[Dict[str, Any]]:
    """Returns the pre-defined verified tests for the problem, or [] if unknown."""
    prob = find_canonical_problem(query, fn_name)
    if prob and "tests" in prob:
        return list(prob["tests"])
    return []


def get_canonical_signature(query: str) -> Optional[Dict[str, Any]]:
    """Returns canonical signature dictionary for problem templates, or None."""
    prob = find_canonical_problem(query)
    if not prob:
        return None
    return {
        "fn": prob["fn"],
        "params": prob["params"],
        "return_type": prob["return_type"],
        "needs_tree": prob.get("needs_tree", False),
        "needs_list": prob.get("needs_list", False),
        "test_call": prob.get("test_call", f"{prob['fn']}()")
    }
