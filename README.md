# Eluvio_internship

Application for Eluvio Software Engineer Internship Summer 2022

- A fully pythonic solution for multi-interger-array LCS solution

Can run either from script.py, or for more modular testing + details, run through script.ipynb

This was a really fun challenge and I tried my best to complete the objective. Solution 1 is merely using pre-existing CPython libraries to quickly solve and set a benchmark. Solution 2 is more of a challenge I set out for myself that is python only. This will vary but on my device both ran at approximately 20s-30s, with a usual improvement in performance with my solution.

## Description (also in .ipynb): 

### Strategy:

"Find the longest strand of bytes that exists in at least two files."

The problem of option 1, can be reduced to the more commonly known "longest common substring" problem. Basically, given strings x and y, try to find the maximum length of [x_i, x_j] and [y_i, y_j] such that len([x_i, x_j]) == len([x_i, x_j]). i and j being the starting and end position of a substring respectively.

There are a few design questions to tackle first. Primarily, what will be our data types. The bytes given can all be translated into strings or interger values from 0-255. Assuming that memory wouldn't be an issue (which it definitely was), choosing strings severely limits my options of tools available. If I wanted any chance at completing this thing with Python (this wouldn't exactly be fun or difficult on C++/CPython), I had to use a vectorized approach. This then leads me to find a vectorized approach to solving the multi-string LCS problem for arrays of intergers, not strings. It's quite the problem reduction, but at least it worked in the end.

Next, what is the general principle, or solution guideline, that would solve this problem in optimal time-complexity? The most practical answer is probably through suffix arrays. For a quick overview on the suffix array solution for LCS see here: https://www.youtube.com/watch?v=Ic80xQFWevc 

Below I'll give more details on my high-level implementation:

- Start by creating array of 256 arrays (actually lists, no vectorization yet done at this level, only loops)
- To generate all suffixes (or substrings/subsequences of bytes, I use them interchangeably), I can create new arrays for each substring, looping through each original string of bytes, popping a value (at the front, [0]) then adding new array to the array index corresponding with its new starting value. 
- For example, an array start with [32, 45, 12, ...] would be placed into array[31]. 
- Furthermore, add a 3-list containing metadata of the substring containing:
    -   original array number (1 through 10)
    -   length of substring, that corresponds to the substring origin file
    -   index of original string where this suffix begins
- That's confusing, data structure looks like this:

```
main_array = [[[<all subarrays (0) origin file>, <all subarrays (0) length>], [<all sub-arrays starting with 0>]], [[<all subarrays (1) origin file>, <all subarrays (1) length>], [<all sub-arrays starting with 1>]],..., [[<all subarrays (100) origin file>, <all subarrays (100) length>], [<all sub-arrays starting with 100>]], ...,[[<all subarrays (255) origin file>, <all subarrays (255) length>], [<all sub-arrays starting with 255>]]]]
```
- The advantage to this data structure is that it will allow for us to conduct our sort while maintaining metadata about where that substring came from, as well as it's length and original index position (since the length will eventually be transformed so as to have even sized numpy arrays)

- Heuristics play a huge part in final performance of my solution
- For example, because of our meta-data, we can ignore sorting all substrings less than current maximum length
    - exponentially increases runtime and improves memory
- To sort all substrings of a starting number, they first have to be the same size so pad all arrays with 0's at the end until they're length of longest array for that number category 
- I can then sort numpy array by column x amount of times, x being length of arrays in the group. We can find max sub-array length (for say those starting with 165) by:

```pseudocode
# 1 indicates the array of subarrays
# this loops over all substrings beginning with 165
for i in matrix[164][1]:
    temp = []
    temp.append(len(i))
    return max(temp)
 ```  
 - in reality this portion is mostly vectorized  
- I can find longest common prefix by iterating over all pairs in sorted subarrays, comparing if each additional array adds on to total matching length.
- But even better, since my data structure knows what's the last substring for each group, and now they're all sorted, I can work backwards
- Thus, if the longest subarray is stored, I don't have to check many of the (usually) smaller subarrays ahead of it. Granted they're smaller than our max length already, it would just be redundant
- In short, the final game plan is to continually improve stored maximum value, and as it improves, sorts and searches get easier and easier (by weeding out unecessary candidates)
- I suppose this solution isn't ideal. It notably sacrifices sort time for an optimal search time. However, it gives a respectable solution that doesn't use Cython or CPython, and in fact, beating out CPython solution. (And to be fair, the brute force python approach here wouldn't even run)
- The next benefit is storage size with numpy. Each byte is a small 8-bit number, which cuts memory drastically. Something you'd have to find a workaround for even in C++
    - This is, of course assuming we're not running in the worst case scenario, where we can never weed out smaller substrings
    - However, the worse case is extremely rare. Especially since we're re-organizing separate strings, and re-combining them into separate data-structure, odds of worst case is very rare

### For anyone looking at this under a critical eye...
- The last major part to improve is the unlikely worst-case scenario outcome, where sorting matrices becomes exponentially more expensive
- In such cases, the only part to optimize is really just the sort. In my tests, in can take up to 90% of run time when no heuristic is applied
- Obviously, not great, and extremely rare scenario but still worth considering for improvements
- One such improvement could be detection of worst case scenario, where we just work backwards and now it's best case. Just fun ideas

failed ideas (ignore, just left here so I don't try them again in future):
- pandas: I tried using pandas because of it's easy .fillna function which I though would be perfect to create all needed 0's and row shapes, then sort by column from right 
to left. Terrible idea, forgot how slow pandas was in general. Barely runs.
- np.insert origin file and substring size into front of array: Not great, large numbers (string size) requires at least int32, 4x as many bites and slows performance
- apply(): primarily for search. It's better than dataframes, but ideal solutions still require full vectorizations
- np.concatenate, np.hstack, np.zeros, np.isnan, etc. basically anything to quickly pad all vectors. I think I literally must've tried everything. Final solution here is blazing fast, by far the best
- numba: This one is really unfortunate. I was really looking forward to numba working, but a) they seem to be going through updates/feature testing so some things are quite broken and b) they still don't work with certain numpy functions like np.pad and np.lexsort. The improvements with numba but also with those replacements would be questionable. Something I might explore in the future, but otherwise I'm content at this point
- no heuristic!! pound for pound, my solution doesn't quite hold up to CPython's (although to be fair they also use heuristics like automatic junk, https://docs.python.org/3/library/difflib.html). However, because my heuristic is all-inclusive (at least I believe), there's no point to not using it. Don't sort arrays that are too small to possibly be new max. Simple and elegant. It was one of my last optimizing ideas, really wish it came to me earlier.
