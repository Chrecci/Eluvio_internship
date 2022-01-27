from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit, jit
from difflib import SequenceMatcher 
import time
from numba.typed import List
from operator import itemgetter

# normally I wouldn't write such redundant code but it's only ten files so eh
with open("data/sample.1", "rb") as file1, open("data/sample.2", "rb") as file2, open("data/sample.3", "rb") as file3, open("data/sample.4", "rb") as file4, open("data/sample.5", "rb") as file5, open("data/sample.6", "rb") as file6, open("data/sample.7", "rb") as file7, open("data/sample.8", "rb") as file8, open("data/sample.9", "rb") as file9, open("data/sample.10", "rb") as file10:
    file_1 = file1.read()
    file_2 = file2.read()
    file_3 = file3.read()
    file_4 = file4.read()
    file_5 = file5.read()
    file_6 = file6.read()
    file_7 = file7.read()
    file_8 = file8.read()
    file_9 = file9.read()
    file_10 = file10.read()
# we can see that the length of encoded array matches exactly the file size. E.g, sample.1 is 17.408 kb
# that's exact same length of encoded_array_1 (17408)
encoded_array_1 = bytearray(file_1)
encoded_array_2 = bytearray(file_2)
encoded_array_3 = bytearray(file_3)
encoded_array_4 = bytearray(file_4)
encoded_array_5 = bytearray(file_5)
encoded_array_6 = bytearray(file_6)
encoded_array_7 = bytearray(file_7)
encoded_array_8 = bytearray(file_8)
encoded_array_9 = bytearray(file_9)
encoded_array_10 = bytearray(file_10)

encoded_arrays = [encoded_array_1, encoded_array_2, encoded_array_3, encoded_array_4,
                 encoded_array_5, encoded_array_6, encoded_array_7, encoded_array_8,
                  encoded_array_9, encoded_array_10
                 ]
print("Size of sample.1 in bytes: ", Path('data/sample.1').stat().st_size)

for val, i in enumerate(encoded_arrays):
    print("Length of sample." + str(val+1) + " byte array: ", len(i))

# helper function that pads all rows so they are same length as longest row
def pad_numpy_matrix(matrix):
    
    l = [len(a) for a in matrix]
    max_len = max(l)

    # np.pad is much more space efficient than alternatives
    c = np.asarray([np.pad(a, (0, max_len - len(a)), 'constant', constant_values=0) for a in matrix])
    # c = np.asarray([np.hstack((a, np.zeros(max_len-a.shape[0], dtype = np.int8))) for a in matrix])
    return c

# Solution using CPython difflib
# ~30s for bytes
def longest_Substring(s1,s2): 
     seq_match = SequenceMatcher(None,s1,s2) 
     match = seq_match.find_longest_match(0, len(s1), 0, len(s2)) 

     # return the longest substring 
     if (match.size!=0): 
          return (s1[match.a: match.a + match.size])  
     else: 
          return ('Longest common sub-string not present') 

def check_all(arrays):
     
     # https://github.com/python/cpython/blob/0daf72194bd4e31de7f12020685bb39a14d6f45e/Lib/difflib.py#L305
     array_copy = arrays.copy()
     maxes = []
     count = 0

     # no need to compare the same two arrays twice, 1+2+3+...+10 = 45 comparisons only
     for i in range(len(array_copy)):
          a = array_copy[0]
          del array_copy[0]
          count += 1
          next_count = 0
          for j in range(len(array_copy)):
               next_count += 1
               add = count+next_count
               longest = longest_Substring(a, array_copy[j])
               maxes.append((count,(count+next_count),len(longest)))
          
     return maxes

str_arrays = []
bytes_arrays = []
for i in encoded_arrays:
     str_arrays.append(str(bytes(i)))
     bytes_arrays.append(bytes(i))
answer_str = check_all(str_arrays)
str_pair = max(answer_str,key=itemgetter(2))[0:2]
str_max_length = max(answer_str,key=itemgetter(2))[2]

print("The longest common substring(str) length is: ", str_max_length)
print("The longest common substring(str) origin files are: ", str_pair, '\n')

start = time.time()
answer_bytes = check_all(bytes_arrays)
end = time.time()
bytes_pair = max(answer_bytes,key=itemgetter(2))[0:2]
bytes_max_length = max(answer_bytes,key=itemgetter(2))[2]
cpython_runtime = end-start
print("The longest common substring(bytes) length is: ", bytes_max_length)
print("The longest common substring(bytes) origin files are: ", bytes_pair, '\n')
print("CPython runtime (bytes): ", cpython_runtime)

# Testing CPython Solutions to show that a string of max length does actually exist. If so, then new solution only has to match CPython solution

s1 = np.array(encoded_arrays[1])
s2 = np.array(encoded_arrays[2])
# print(len(s1), len(s2))

x = 27648
seq_match = SequenceMatcher(None,s1,s2) 
match = seq_match.find_longest_match(0, len(s1), 0, len(s2))
print("Is CPython solution correct? ", np.all(s1[match[0]:match[0]+x]==s2[match[1]:match[1]+x]))

# let's make everything a numpy array of arrays. Looping to append to 
# np arrays is actually very inefficient so convert at end instead
def create_np_array(list_arrays):
    allArrays = []
    for i in list_arrays:
        allArrays.append(np.array(i))
    # test that everything went ok
    #print(len(allArrays), len(allArrays[0])==len(allArrays[1]), type(allArrays[0]))
    main_array = []
    for i in range(256):
        main_array.append([[], []])

    # repeat this for each file (10x)
    for val, i in enumerate(allArrays):
        new_i = i
        # add each possible array
        for j in range(len(i)):
            head = new_i[0]
            # each array in 256 main arrays will have the original file in position 0 followed by actual substring content
            # to_append = np.concatenate(([val], new_i))
            a = len(new_i)
            main_array[head][0].append([val+1, a, j])
            main_array[head][1].append(new_i)
            new_i = new_i[1:]
    print('complete enumeration')
    return(main_array)

def sort_matrix(main_array, global_max):
    y = np.array(main_array[0])
    lengths = y[:,1]
    max_length = np.max(lengths)

    # if the maximum length of all strings in this current matrix is less than current max substring, no need to bother. Skip this matrix
    if max_length>global_max[2]:
        
        # one of the most effective things by far. There's no need to assess strings whose original lengths < current max substring
        # so let's remove them, and only sort the rows that are larger. Easy matrix transformations
        use_rows = lengths > global_max[2]
        temp_final = np.array(main_array[1])[use_rows]
        keys_final = y[use_rows]
        #b = time.time()
        #print('make np: ', b-a)
        # make all arrays same size. Pad with 0's so sortable
        temp_padded = pad_numpy_matrix(temp_final)

        #c = time.time()
        #print('pad rows: ', c-a)

        # np.lexsort each matrix, returns the final order of rows for sort
        # by far the biggest eater of time here. ~80-95%. If we can cut this down, drastic improvement
        sort_order = np.lexsort(np.fliplr(temp_padded).T)
        #sort_order = -temp_padded[:,:].argsort(axis=0)[0]

        #d = time.time()
        #print('sort: ', d-a)
        # we also want keys to follow new order. This way we can sort rows independent of position, size (keys)
        sorted_keys = keys_final[sort_order]
        temp_sorted = temp_padded[sort_order]
        #e = time.time()
        #print('append: ', e-a)
        return [sorted_keys, temp_sorted]
    else:
        return None

def max_suffix(array, global_max, debug=False):
    # [[meta], [matrix]]
    # global_max = (x, y, length) . Both original file locations and length of current max substring
    meta = array[0]
    matrix = array[1]
    new_max = global_max

    # i is each 256 array in array: [[],[]]
    # if there isn't more than one substring beginning with that number no need to check
    if len(meta) >1:
        for j in range(1, len(matrix)):
            a = j
            b = j+1
            # avoid checking string if it's original length less than current stored max value
            if meta[-a][1] > new_max[2]:
                if debug:
                    print("a and b", a, b)
                    print("meta", meta[-a][0], meta[-b][0])
                # we want the first row working backwards that's not from same origin file
                
                if meta[-a][0] != meta[-b][0]:
                    # np.ndarray
                    # b < a in length
                    a_array = np.array(matrix[-a])
                    b_array = np.array(matrix[-b])
                    if debug:
                        print("a", a_array)
                        print("b", b_array)
                    c = a_array==b_array
                    #non_zero_array = np.nonzero(c == False)[0]
                    if debug:
                        print(c) #non_zero_array)

                    # this part threw me off so much. We have to treat perfect matches and matches separately. Perfect matches do not return anything for c==False
                    # So nothing will be returned, and skips perfect matches. Very bad. np.all() assesses perfect matches, and if there is one, use the shorter's length
                    if np.sum(c) > 0:
                        if np.all(c):
                            LCS_length = meta[-b][1]
                        else:
                            LCS_length = np.nonzero(c == False)[0][0]
                        if debug:
                            print(LCS_length)
                        if LCS_length > new_max[2]:
                            # we need the original string size precisely here. If two substrings are perfect match, we don't want all appended 0's there as well
                            # only append actual length of substring added, not padded length
                            new_max = (meta[-a][0], meta[-b][0], LCS_length, (meta[-a][2], meta[-b][2]))
                            #print("updated", new_max)
                else:
                    pass
    return new_max

# Main function that just loops through all separate original strings
# ~22s runtime. Around 25% improvement over CPython
def loop_matrix(matrix, debug=False):
    
    LCS_matrix = create_np_array(matrix)
    global_max = (0,0,0,0,0)
    #start = time.time()
    for i in range(len(LCS_matrix)):
        # print("Completed search through all sub-sequences beginning with: ", i, global_max)
        if len(LCS_matrix[i][0]) > 1:
            temp = sort_matrix(LCS_matrix[i], global_max)
        else:
            temp = None
        #end = time.time()
        #print("finished sorting in: ", end-start)
        if temp:
            global_max = max_suffix(temp, global_max, debug)
        #end = time.time()
        #print("finished group: ", i, " in ", end-start)
    return global_max

# I spent hours debugging a simple mistake... This is why testing is important. If you'd like the test, simply set debug=True. Plenty of debugging comments as well
test = [[1,3,3,4,5,6,7],
        [3,1,4,2,7,3,4,5,6,7],
        [1,5,6,7,6,7,4,2,7,3,4,3,1,4,2,7,3,4,5,6,7],
        [1,4,8,7,8,9,10],
        [3,6,1,4,2,7],
        [9,8,4,0,3,4,5]]

start = time.time()
lcs_ = loop_matrix(encoded_arrays, False)
end = time.time()
my_runtime = end-start

print("The longest common substring(bytes) length is: ", lcs_[2])
print("The longest common substring(bytes) origin files are: ", lcs_[0:2])
print("Strings begin in positions: ", lcs_[3])
# Yup it works
print("Is final answer correct? ", lcs_[2]==bytes_max_length)
print("Is my version faster? ", my_runtime<cpython_runtime, my_runtime)