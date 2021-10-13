import numpy as np
# import time
# import random


class ColumnSorter:
    def __init__(self, num_rows, num_columns, calculator):
        self.num_rows = num_rows
        self.num_columns = num_columns
        self.calculator = calculator

    # Pre-processing functions

    @staticmethod
    def switch_terms(sequence, index1, index2):
        new_sequence = sequence.copy()
        (new_sequence[index2], new_sequence[index1]) = (sequence[index1], sequence[index2])
        return new_sequence

    @staticmethod
    def list_of_lists(num_lists, use_numpy):
        if num_lists >= 1:
            result = [[]]
            for i in range(num_lists - 1):
                result.append([])
        else:
            result = []
        if use_numpy:
            result = np.array(result)
        return result

    def convert_nums_to_2s(self, patterns_to_convert):
        self.num_rows = patterns_to_convert.shape[0]
        self.num_columns = patterns_to_convert.shape[1]
        patterns_1_2 = patterns_to_convert.copy()
        for i in range(self.num_rows):
            for j in range(self.num_columns):
                if patterns_to_convert[i, j] != 0:
                    patterns_1_2[i, j] = 2
                else:
                    patterns_1_2[i, j] = 1
        return patterns_1_2

    def convert_outer_1s_to_0s(self, matrix):
        self.num_columns = matrix.shape[1]
        patterns_0_1_2_func = matrix.copy()

        self.start_pattern = np.zeros(self.num_rows).astype(int)
        self.end_pattern = np.zeros(self.num_rows).astype(int)
        for i in range(self.num_rows):
            j = 0
            while j < self.num_columns and matrix[i, j] != 2:
                patterns_0_1_2_func[i, j] = 0
                j += 1
            else:
                self.start_pattern[i] = j
            j = self.num_columns - 1
            while j >= 0 and matrix[i, j] != 2:
                patterns_0_1_2_func[i, j] = 0
                j -= 1
            else:
                self.end_pattern[i] = j
        return patterns_0_1_2_func

    def pre_process(self, matrix):
        patterns_1_2 = self.convert_nums_to_2s(matrix)
        patterns_0_1_2_func = self.convert_outer_1s_to_0s(patterns_1_2)
        return patterns_0_1_2_func

    # Other functions

    def count_containers(self, patterns_0_1_2_func):
        self.num_columns = patterns_0_1_2_func.shape[1]
        # Initialize tracker for number of containers during each pattern
        containers_func = np.zeros(self.num_columns)
        # Count number of containers needed for each pattern
        for j in range(self.num_columns):
            for i in range(self.num_rows):
                if patterns_0_1_2_func[i, j] != 0:
                    containers_func[j] += 1
        return containers_func
    # 
    # def move_column(self, patterns_to_sort, column_index):
    #     self.num_columns = patterns_to_sort.shape[1]
    #     best_sum = 100000000000
    #     best_sequence = np.array(range(self.num_columns))
    # 
    #     # Remove the index that will be moved
    #     best_sequence = np.delete(best_sequence, np.where(best_sequence == column_index)[0])
    # 
    #     # Try putting the index in each position, and check which one uses the least containers
    #     for i in range(self.num_columns):
    #         test_sequence = np.insert(best_sequence, i, column_index)
    #         sorted_patterns = (patterns_to_sort.T[test_sequence]).T
    #         patterns_0_1_2_func = self.pre_process(sorted_patterns)
    #         containers = self.count_containers(patterns_0_1_2_func)
    # 
    #         if sum(containers) < best_sum:
    #             best_sum = sum(containers)
    #             best_sequence = test_sequence.copy()
    # 
    #     return best_sequence, max(containers)

    def column_sort(self, patterns_to_sort, mode):
        self.num_columns = patterns_to_sort.shape[1]
        sort_span = patterns_to_sort.shape[1]

        best_sum = 100000000000
        best_sequence = np.array(np.arange(self.num_columns))

        if mode == 1:
            # Don't move last pattern since it might have a drop
            sort_span = sort_span - 1

        sequence_is_optimum = 0
        ij_best = (-1, -1)
        while sequence_is_optimum == 0:
            for i in range(sort_span):
                for j in range(sort_span):
                    if (i, j) == ij_best:
                        sequence_is_optimum = 1
                        break
                    new_sequence = self.switch_terms(best_sequence, i, j)
                    sorted_patterns = (patterns_to_sort.T[new_sequence]).T

                    patterns_0_1_2_func = self.pre_process(sorted_patterns)
                    containers = self.count_containers(patterns_0_1_2_func)

                    if sum(containers) < best_sum:
                        best_sum = sum(containers)
                        best_sequence = new_sequence.copy()
                        ij_best = (i, j)
        return best_sequence, max(containers), sum(containers)

    # def flatten_matrix(self, patterns_to_flatten):
    #     flattened = [[]]
    #     for row in patterns_to_flatten:
    #         flattened = np.append(flattened, [row], axis=1)
    #     return flattened

    def optimize_sequence(self, patterns, num_attempts, mode):

        np.random.seed(0)

        self.num_columns = patterns.shape[1]

        current_sequence = np.arange(self.num_columns)
        best_sequence = current_sequence.copy()
        best_max_containers = 99999999999999999999
        best_sum = 99999999999999999999

        # start_time = time.time()

        if mode == 0:
            num_columns_to_sort = self.num_columns

        if mode == 1:
            # num_attempts = 1
            num_columns_to_sort = self.num_columns - 1

        for attempt in range(num_attempts):

            # Check if calculation has been canceled.
            if self.calculator.calculation_was_canceled == 1:
                # Zero out all outputs and exit function
                self.calculator.final_patterns = []
                self.calculator.final_allocations = 0
                return best_sequence, best_max_containers

            patterns_copy = patterns.copy()
            if mode == 0:
                
                # TODO For starting sequences, introduce quasi-random sampling instead of random sampling to increase 
                #  chances of matching the global optimum
                # sampler = Sobol(d=2, scramble=False)
                # sample = sampler.random_base2(m=5)
                # print(sample)
                
                np.random.shuffle(current_sequence)
                patterns_copy = patterns_copy.T[current_sequence].T

            # if mode == 1:
            #     current_sequence = np.delete(current_sequence, -1)
            #     np.random.shuffle(current_sequence)
            #     current_sequence = np.append(current_sequence, [self.num_columns - 1])
            #     print(current_sequence)
            #     patterns_copy = patterns_copy.T[current_sequence].T

            sequence_is_optimum = 0

            while sequence_is_optimum == 0:

                changes_matrix = self.list_of_lists(self.num_rows, 0)

                # Initialize changes matrices
                for i in range(self.num_rows):
                    changes_matrix[i] = np.zeros((self.num_columns, self.num_columns))

                changes_matrix = np.array(changes_matrix)
                for i, element in enumerate(changes_matrix):
                    # Initialize left position, right position, left distance, and right distance
                    lp = 0
                    rp = 0
                    ld = 0
                    rd = 0

                    # Initialize left position and left distance
                    for j, num in enumerate(patterns_copy[i]):
                        if num != 0:
                            if lp == 0:
                                lp = j + 1
                            else:
                                ld = j - lp + 1
                                break
                    if ld == 0:
                        continue

                    # Initialize right position and right distance
                    for j, num in enumerate(patterns_copy[i][::-1]):
                        if num != 0:
                            if rp == 0:
                                rp = j + 1
                            else:
                                rd = j - rp + 1
                                break

                    # Define commonly used sums for subsequent calculations
                    sum1 = self.num_columns - rp
                    sum2 = sum1 + 1
                    sum3 = lp - 1

                    # Calculate elements in changes_matrix
                    values = (np.arange(1, lp) - rd)[::-1]
                    for ii in range(0, sum3):
                        element[ii, sum1] = values[ii]
                    values = (np.arange(1, rp) - ld)
                    for jj, num in enumerate(range(sum2, self.num_columns)):
                        element[sum3, num] = values[jj]
                    values = np.arange(1, rp)
                    for ii, num in enumerate(range(lp, sum2)):
                        if patterns_copy[i][num] == 0:
                            element[num, sum1] = -min(rd, sum1 - num)
                        else:
                            for jj, numnum in enumerate(range(sum2, self.num_columns)):
                                element[num, numnum] = values[jj]
                    values = np.arange(1, lp)[::-1]
                    for jj, num in enumerate(range(sum3, sum1)):
                        if patterns_copy[i][num] == 0:
                            element[sum3, num] = -min(ld, num - sum3)
                        else:
                            for ii, numnum in enumerate(range(0, sum3)):
                                element[numnum, num] = values[ii]

                # Sum up all changes
                changes_sum = np.sum(changes_matrix, axis=0)

                if mode == 0:
                    # Determine which indices to switch in pattern sequence
                    (imin, jmin) = np.unravel_index(np.argmin(changes_sum), changes_sum.shape)

                if mode == 1:
                    trimmed_changes_sum = changes_sum[0:num_columns_to_sort, 0:num_columns_to_sort]
                    # Determine which indices to switch in pattern sequence
                    (imin, jmin) = np.unravel_index(np.argmin(trimmed_changes_sum), trimmed_changes_sum.shape)

                # Switch terms to improve sequence
                new_sequence = self.switch_terms(np.arange(0, self.num_columns), imin, jmin)
                patterns_copy = (patterns_copy.T[new_sequence]).T
                current_sequence = current_sequence[new_sequence]

                # Calculate containers required for new sequence
                patterns_0_1_2 = self.pre_process(patterns_copy)
                containers = self.count_containers(patterns_0_1_2)
                container_sum = np.sum(containers)
                current_max_containers = np.max(containers)

                # if np.sum(containers) == container_sum:
                #     sequence_is_optimum = 1
                #     current_max_containers = np.max(containers)
                if current_max_containers < best_max_containers or \
                        (current_max_containers == best_max_containers and container_sum < best_sum):
                    best_sum = container_sum.copy()
                    best_sequence = current_sequence.copy()
                    best_max_containers = current_max_containers
                elif container_sum >= best_sum:
                    sequence_is_optimum = 1

                if imin == jmin:
                    # sequence_is_optimum = 1
                    break

        patterns_0_1_2 = self.pre_process(patterns.T[best_sequence].T)
        containers = self.count_containers(patterns_0_1_2)
        print(np.max(containers))
        print(np.sum(containers))

        # print(time.time() - start_time)
        return best_sequence, best_max_containers


# n = 64
#
# cs = ColumnSorter(n, n)
#
# patterns = np.zeros((cs.num_rows, cs.num_columns))
# for j in range(cs.num_rows):
#     for k in range(cs.num_columns):
#         if random.random() > (0.7 + random.random() * 0.15):
#             patterns[j, k] = 1
#
# [best_sequence, best_max] = cs.optimize_sequence(patterns, 1000)
#
#
# patterns_0_1_2 = cs.pre_process(patterns.T[best_sequence].T)
# containers = cs.count_containers(patterns_0_1_2)
# print(best_max)
# print(np.sum(containers))
