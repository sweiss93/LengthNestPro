import numpy as np
import time
import math
from PyQt5.QtCore import pyqtSignal, QObject
# from matplotlib import pyplot as plt
# import matplotlib
from column_sort import ColumnSorter
import copy
# matplotlib.use('Agg')


# Create calculate thread class
class CalculateThread(QObject):
    def __init__(self, window):
        super().__init__()
        self.calculation_was_canceled = 0
        self.window = window

    results_signal = pyqtSignal(list)

    @staticmethod
    def union(a, b):
        for item in a:
            if item not in b:
                b.append(item)
        return b

    def find_adj_matrix(self, patterns):
        adj_matrix_ = np.zeros((self.num_parts, self.num_parts))
        for row_index, row in enumerate(patterns):
            for term_index, term in enumerate(row):
                if term:
                    for item_index, item in enumerate(patterns.T[term_index]):
                        if item:
                            adj_matrix_[row_index][item_index] = 1
        for i in range(self.num_parts):
            adj_matrix_[i][i] = 0
        return adj_matrix_

    # noinspection PyUnusedLocal
    @staticmethod
    def find_cycling(original_list):
        # Reverse the order of the list to make it easier to work with since repetitions would happen at end
        reversed_list = original_list[::-1]

        # Create generator to find next item in list
        index_generator = (i for i, e in enumerate(reversed_list) if e == reversed_list[0])

        # Check for first index before entering loop to prevent false positive
        first_index = next(index_generator)

        # Check for periodic nature in loop until function exits with return
        while 1:
            # Find next element that matches the first element
            try:
                next_match = next(index_generator)
            except StopIteration:
                return False

            if next_match < -1:
                pass
            else:
                if np.all(reversed_list[0:next_match] == reversed_list[next_match:(2 * next_match)]) and \
                        next_match > 10:
                    return True

    def adjust_max_iterations(self, adjustment_factor):
        self.max_iterations *= adjustment_factor
        if adjustment_factor >= 1:
            self.max_iterations += 1
        elif adjustment_factor <= 1:
            self.max_iterations -= 1

    def check_for_bonus_condition(self):
        bonus = 1
        for check_index in range(len(self.bonus_sublist_sorted)):
            if self.bonus_sublist_sorted[check_index] == 1:  # Indicates parts that fulfill uff parts
                if self.row_copy[check_index + 1]:
                    continue
                else:
                    bonus = 0
                    break
            elif self.bonus_sublist_sorted[check_index] == -1:  # Prevents creation of more uff parts
                if not self.row_copy[check_index + 1]:
                    continue
                else:
                    bonus = 0
                    break
        return bonus

    def branch_bound(self, bandwidth, max_parts_per_nest, part_quantities, parts_sublist, mode, current_part_index=0):
        # Find pi vector from patterns (Step #2)
        if mode == 0:
            self.patterns_inv = np.linalg.inv(self.patterns)
            self.patterns_trans_inv = np.transpose(self.patterns_inv)
            self.ones_vector = np.ones((len(self.patterns[0]), 1))
        # elif mode == 1:
        #     self.patterns_inv = np.linalg.solve(self.patterns.T.dot(self.patterns), self.patterns.T)
        #     self.patterns_trans_inv = np.transpose(self.patterns_inv)
        #     self.ones_vector = np.ones((len(self.patterns[0]), 1))
        if mode == 0:
            self.pi = np.dot(self.patterns_trans_inv, self.ones_vector)
        elif mode == 1 or mode == 2:
            self.pi = self.nested_lengths / self.nestable_length

        # Adjust pi slightly to prioritize longer parts
        for i in range(len(self.pi)):
            self.pi[i] = self.pi[i] + 0.0001 * self.nested_lengths[i] / self.nestable_length

        # Calculate allocations of each pattern
        self.allocation = np.dot(self.patterns_inv, part_quantities)

        # Find value vector that can be used to prioritize the "usefulness" of nesting each part
        self.values = np.divide(self.pi, self.nested_lengths)

        if mode == 1:
            part_quantities[self.part_index] = self.remaining_part_quantities[self.part_index].copy()
            for part in self.unavailable_parts[1:]:
                part_quantities[part] = self.remaining_part_quantities[part].copy()

        self.values_sublist = self.values[parts_sublist[self.container_counter].astype(int)]
        self.pi_sublist = self.pi[parts_sublist[self.container_counter].astype(int)]
        self.nested_lengths_sublist = self.nested_lengths[parts_sublist[self.container_counter].astype(int)]
        self.part_quantities_sublist = part_quantities[parts_sublist[self.container_counter].astype(int)]

        # Sort from "most valuable to nest" to "least valuable to nest" so that optimum solution is reached sooner.
        self.index_order = (np.argsort((self.values * -1).transpose()))[0]
        self.pi_sorted = self.pi[self.index_order]
        self.values_sorted = self.values[self.index_order]
        self.nested_lengths_sorted = self.nested_lengths[self.index_order]
        self.part_quantities_sorted = part_quantities[self.index_order]

        # Sort sublist data from "most valuable to nest" to "least valuable to nest" so that optimum solution is
        # reached sooner.
        self.sublist_index_order = (np.argsort((self.values_sublist * -1).transpose()))[0]
        if mode == 1:
            self.sublist_index_order = np.delete(self.sublist_index_order,
                                                 np.where(self.sublist_index_order == current_part_index)[0])
            self.sublist_index_order = np.insert(self.sublist_index_order, 0, current_part_index)
        self.pi_sublist_sorted = self.pi_sublist[self.sublist_index_order]
        self.values_sublist_sorted = self.values_sublist[self.sublist_index_order]
        self.nested_lengths_sublist_sorted = self.nested_lengths_sublist[self.sublist_index_order]
        self.part_quantities_sublist_sorted = self.part_quantities_sublist[self.sublist_index_order]
        self.parts_sublist_sorted = np.zeros((self.num_parts - bandwidth + 1, bandwidth))
        if mode == 1 or mode == 2:
            self.parts_sublist_sorted = np.zeros((1, bandwidth))
        if mode == 1:
            self.bonus_sublist_sorted = self.bonus_sublist[0][self.sublist_index_order]
        self.parts_sublist_sorted[self.container_counter] = \
            parts_sublist[self.container_counter][self.sublist_index_order]
        # old_index_order = np.argsort(index_order)

        # Initialize branch and bound matrix, bbm, with level 1 node
        #   Row will be [level a0_1 a0_2 ... a0_n rem LP IP]
        #   bbm will consist of all nodes that may still be explored
        self.bbm = np.zeros((1, bandwidth + 4))
        self.bbm[0, 0] = 1  # level
        # Entries 1 through num_parts will remain at 0 for the first node because no parts have been nested
        self.bbm[0, bandwidth + 1] = self.nestable_length  # Calculate rem, remaining nestable length
        self.bbm[0, bandwidth + 2] = self.bbm[0, bandwidth + 1] * self.values_sublist_sorted[0]  # Calculate
        # value of LP, linear programming maximum value
        # bbm[0, num_parts + 3] = 0  # Value of IP, will remain at 0 since no parts are nested

        # Initialize lp_best and ip_best
        self.lp_best = self.bbm[0, bandwidth + 2]
        self.ip_best = 0

        # Initialize ip_best_row to keep track of best node (the one with highest IP value)
        self.ip_best_row = self.bbm[0]

        # Initialize lp_best_index at 0 since there is only one node
        self.lp_best_index = 0

        # Initialize loop_count
        self.loop_count = 0

        # Begin loop to start branching nodes, and allow for rounding error
        while self.lp_best > self.ip_best - 0.00000001:
            # Check if calculation has been canceled.
            if self.calculation_was_canceled == 1:
                # Zero out all outputs and exit function
                self.final_patterns = []
                self.final_allocations = 0
                return 0
            #     return self.required_lengths, self.allocation, self.patterns
            #     # return self.final_patterns, self.final_allocations

            # Extract the row to be explored
            self.row = self.bbm[self.lp_best_index, :]

            # Extract the level of the row to be explored
            self.level = int(self.row[0])

            # Extract the remaining length for the row to be explored
            self.rem = self.row[bandwidth + 1]

            # Extract length of part being considered at current level (level 1 corresponds to part 1 and so on)
            self.p_length = self.nested_lengths_sublist_sorted[self.level - 1]

            # Check how many of the part can be nested on remaining length rem
            self.num = math.floor(self.rem / self.p_length)

            # Reduce num if there are not enough parts available in the job to add to the nest
            self.part_max = int(math.floor(self.part_quantities_sublist_sorted[self.level - 1].item()))
            if self.part_max < self.num:
                self.num = self.part_max

            # Allow node to be explored by default
            # Set a variable to 1 to allow the node to be branched into sub-nodes
            self.branch_node = 1

            # Limit the number of parts that can be used in a pattern
            if self.level > max_parts_per_nest:
                # Count number of different parts in the pattern so far
                self.parts_in_pattern = 0
                for i in range(self.level):
                    if self.row[i + 1] != 0:
                        self.parts_in_pattern += 1
                # Check when only one more part can be added to the pattern
                if self.parts_in_pattern == max_parts_per_nest - 1:
                    # Copy the node 1 time, and iterate a0_level to num since no other parts will be nested later
                    self.row_copy = self.row.copy()  # copy row
                    self.row_copy[self.level] = self.num  # iterate a0_level
                    self.row_copy[bandwidth + 1] = self.rem - self.num * self.p_length  # subtract nested parts from rem
                    self.row_copy[bandwidth + 3] = np.dot([self.row_copy[1:bandwidth + 1]],
                                                          self.pi_sublist_sorted)  # calculate IP for new node

                    # Check if current pattern fulfills subsequent uff parts without creating more uff parts
                    #  upstream.  Give bonus IP when this occurs.
                    if mode == 1:

                        bonus = self.check_for_bonus_condition()

                        if bonus == 1:
                            self.row_copy[bandwidth + 3] += 0.08

                    # Add slight incentive to reduce number of different parts in each pattern (prevents unnecessary
                    #   mixing
                    num_parts_in_nest = 0
                    for value in self.row_copy[1:(bandwidth + 1)]:
                        if value:
                            num_parts_in_nest += 1
                    if num_parts_in_nest > 0:
                        self.row_copy[bandwidth + 3] += 1 - num_parts_in_nest / (num_parts_in_nest - 0.001)

                    if self.row_copy[bandwidth + 3] > self.ip_best:
                        self.ip_best = self.row_copy[bandwidth + 3]
                        self.ip_best_row = self.row_copy

                    # If no parts were added to the nest, keep branching.
                    if self.num == 0:
                        self.branch_node = 1
                    else:
                        self.branch_node = 0
                        # Remove the explored node from bbm
                        self.bbm = np.delete(self.bbm, self.lp_best_index, 0)
                        # Iterate original row to next level to allow for other parts to be added as final part instead
                        if self.level != bandwidth:
                            self.row[0] = self.level + 1
                            self.bbm = np.append(self.bbm, [self.row], axis=0)  # add new node to bbm

                elif self.parts_in_pattern == max_parts_per_nest:
                    self.bbm = np.delete(self.bbm, self.lp_best_index, 0)
                    self.branch_node = 0

            if self.branch_node == 1:
                # Copy the node (num + 1) times to explore it, and iterate the qty for the current part from 0 to num
                selected_range = range(self.num + 1)
                # Only consider the option of using all remaining parts if considering the current unfulfilled part
                if mode == 1 and self.level == 1:
                    selected_range = range(self.num, self.num + 1)
                for i in selected_range:
                    self.row_copy = self.row.copy()  # copy row
                    self.row_copy[self.level] = i  # iterate qty for the current part
                    self.row_copy[bandwidth + 1] = self.rem - i * self.p_length  # subtract nested parts from rem
                    self.row_copy[bandwidth + 3] = np.dot([self.row_copy[1:bandwidth + 1]],
                                                          self.pi_sublist_sorted)  # calculate IP for new node

                    # Check if current pattern fulfills subsequent uff parts without creating more uff parts
                    #  upstream.  Give bonus IP when this occurs.
                    if mode == 1:

                        bonus = self.check_for_bonus_condition()

                        if bonus == 1:
                            self.row_copy[bandwidth + 3] += 0.08

                    # Add slight incentive to reduce number of different parts in each pattern (prevents unnecessary
                    #   mixing
                    num_parts_in_nest = 0
                    for value in self.row_copy[1:(bandwidth + 1)]:
                        if value:
                            num_parts_in_nest += 1
                    if num_parts_in_nest > 0:
                        self.row_copy[bandwidth + 3] += 1 - num_parts_in_nest / (num_parts_in_nest - 0.001)

                    if self.row_copy[bandwidth + 3] > self.ip_best:
                        self.ip_best = self.row_copy[bandwidth + 3]
                        self.ip_best_row = self.row_copy
                    if self.level < bandwidth:
                        self.row_copy[bandwidth + 2] = self.row_copy[bandwidth + 3] + self.row_copy[
                            bandwidth + 1] * self.values_sublist_sorted[
                                                           self.level]  # calculate LP for new node
                        if self.row_copy[bandwidth + 2] > self.ip_best:
                            self.row_copy[0] = self.level + 1  # increment level of copy
                            self.bbm = np.append(self.bbm, [self.row_copy], axis=0)  # add new node to bbm

                # Remove the explored node from bbm
                self.bbm = np.delete(self.bbm, self.lp_best_index, 0)

            # Every 100 iterations, check for any nodes with an LP less than ip_best and remove them
            if self.loop_count / 100 == round(self.loop_count / 100):
                for i in (range(len(self.bbm[:, bandwidth + 2])))[::-1]:
                    if self.bbm[i, bandwidth + 2] < self.ip_best:
                        self.bbm = np.delete(self.bbm, i, 0)

            # Check to make sure bbm is not empty
            if np.size(self.bbm) > 0:

                # TODO Find a faster way to choose next node without cycling through all of bbm
                # Decide which node to explore next by searching for the node in bbm with highest LP
                self.lp_best_index = np.argmax(self.bbm[:, bandwidth + 2])
                self.lp_best = self.bbm[self.lp_best_index, bandwidth + 2]
            else:
                break

            if self.loop_count == 10000:
                break

            # Keep track of how many times the loop is executed
            self.loop_count += 1

    def column_gen(self, bandwidth, max_parts_per_nest, part_quantities, parts_sublist, limit_iterations):

        # Initialize patterns matrix (single part nesting patterns)
        self.patterns = np.zeros((self.num_parts, self.num_parts))
        for i in range(self.num_parts):
            self.patterns[i, i] = min(self.window.part_quantities[i],
                                      math.floor(self.nestable_length / self.nested_lengths[i]))

        # start_time_cg = time.time() + 1000
        # start_time_cg = time.time()

        # Reset counters
        self.container_counter = 0
        self.iteration_count = 0

        # Initialize a tracker to check for periodic cycling in ip_best
        # TODO make this less arbitrary, should be based on bandwidth too
        ip_best_history = np.array(range(self.num_parts * 20))

        # TODO find a way to check if minimum is global or local, try different initial conditions?

        # Execute main program loop until optimum solution is reached
        # while time.time() - start_time_cg < time_limit:
        while self.iteration_count < self.max_iterations:
            if self.calculation_was_canceled == 1:
                # Zero out all outputs and exit function
                self.final_patterns = []
                self.final_allocations = 0
                return self.required_lengths, self.allocation, self.patterns

            self.branch_bound(bandwidth, max_parts_per_nest, part_quantities, parts_sublist, 0)
            if self.iteration_count % 10 == 0:
                print(f"Number of passes during branch_bound: {self.loop_count}")

            # Check if calculation has been canceled.
            if self.calculation_was_canceled == 1:
                # Zero out all outputs and exit function
                self.final_patterns = []
                self.final_allocations = 0
                return self.required_lengths, self.allocation, self.patterns

            if self.ip_best >= 1:
                # Extract the best pattern from ip_best_row
                self.best_pattern_sorted_sublist = np.transpose([self.ip_best_row[1:(bandwidth + 1)]])

                # Initialize best_pattern_sorted
                self.best_pattern_sorted = np.zeros((self.num_parts, 1))

                # Add pattern values from the sublist to the main list
                for i in range(bandwidth):
                    # Find index in main list corresponding to ith index of parts_sublist_sorted
                    self.corr_index = \
                        np.where(self.index_order == self.parts_sublist_sorted[self.container_counter][i])[0].item()
                    self.best_pattern_sorted[self.corr_index] = self.best_pattern_sorted_sublist[i]

                # Reorder best_pattern vector
                self.old_index_order = np.argsort(self.index_order)
                self.best_pattern = self.best_pattern_sorted[self.old_index_order]

                # Determine which pattern to replace in patterns
                # Solve for p_bar_j (proportion of each existing pattern that 1 instance of best_pattern can replace)
                self.p_bar_j = np.dot(self.patterns_inv, self.best_pattern)

                # Initialize theta_limits
                self.theta_limits = np.zeros((self.num_parts, 1))

                # Calculate required_lengths before adding new pattern to patterns
                self.required_lengths = np.sum(np.dot(self.patterns_inv, part_quantities))

                # Find limiting pattern when replacing current nests with the max number of instances of best_pattern
                for i in range(self.num_parts):
                    # Solve for the reciprocal of the limits on Theta for each pattern
                    self.theta_limits[i] = self.p_bar_j[i] / (self.allocation[i] + 0.00000001)

                # Replace the pattern with the largest value of theta_limits
                self.index_to_replace = np.argmax(self.theta_limits)
                self.patterns[:, self.index_to_replace] = self.best_pattern.transpose()[0]

                # Fixes issue with allocation not matching new version of pattern TODO figure out why
                self.patterns_inv = np.linalg.inv(self.patterns)
                self.allocation = np.dot(self.patterns_inv, part_quantities)

            # Update ip_best_history
            ip_best_history = np.append(ip_best_history[1:], self.ip_best)
            self.iteration_count += 1

            # If repetitions are found in ip_best_history, then exit the column generation function with results.
            if self.find_cycling(ip_best_history):
                # print(time.time() - start_time_cg)
                print(f"cycling found after {self.iteration_count} iterations")
                # decrement max_iterations to make cycling less likely
                if limit_iterations == 1:
                    if self.max_iterations == 1000000:  # TODO recode since this condition is only met on first loop
                        self.max_iterations = self.iteration_count
                    else:
                        self.adjust_max_iterations(0.95)
                return self.required_lengths, self.allocation, self.patterns

            # Reset container_counter when it reaches num_parts - bandwidth + 1
            self.container_counter += 1
            if self.container_counter == self.num_parts - bandwidth + 1:
                self.container_counter = 0

        print(f"reached maximum iterations of {self.max_iterations}")
        # increment max_iterations to make cycling more likely
        if limit_iterations == 1:
            self.adjust_max_iterations(1.01)
        return self.required_lengths, self.allocation, self.patterns

    # def decrease_max_iterations(self):
    #     new_max_iterations = math.floor(self.max_iterations * 0.95)
    #     if self.max_iterations == new_max_iterations:
    #         self.max_iterations -= 1
    #     else:
    #         self.max_iterations = new_max_iterations

    def run(self):
        nesting_start_time = time.time()
        [final_patterns, final_allocations] = self.length_nest_pro_calculate()
        results = [final_patterns, final_allocations]
        print(f"nesting time was {time.time() - nesting_start_time}")
        self.results_signal.emit(results)

    # TODO add algorithm/option that tends to pick nests that use up a single part faster (reduces the dependency of the
    #  patterns on the part quantities)

    # TODO add algorithm/option to reduce the number of containers needed (completely finish first 3 parts before
    #  starting on the next parts.  Never cut the nth part if the (num_parts-3)th part is not completed.  Allow user
    #  to adjust 3 to other values.

    # TODO add functionality to calculate optimum stock length (by iterating with different stock lengths?)

    # TODO allow user to select multiple stock lengths and quantities/priorities

    # TODO remove timers

    # TODO add file about for version info and help

    # Create function to nest parts
    def length_nest_pro_calculate(self):

        ##########################
        # Pre-processing section #
        ##########################

        # Start timer
        # nesting_start_time = time.time()

        self.max_iterations = 1000000

        # Check how many different parts are needed (num_parts)
        self.num_parts = len(self.window.part_lengths)

        # Set precision for printing
        np.set_printoptions(precision=3)

        # Remove any parts where the part quantity is 0 (remove entries from self.window.part_names,
        # self.window.part_lengths, and self.window.part_quantities)
        for i in range(len(self.window.part_quantities))[::-1]:
            if self.window.part_quantities[i] == 0:
                self.window.part_quantities = np.delete(self.window.part_quantities, i, 0)
                self.window.part_lengths = np.delete(self.window.part_lengths, i, 0)
                self.window.part_names = np.delete(self.window.part_names, i, 0)

        initial_part_quantities = self.window.part_quantities.copy()
        initial_part_lengths = self.window.part_lengths.copy()
        initial_part_names = self.window.part_names.copy()

        # Update number of parts after removing parts with qty 0
        self.num_parts = len(self.window.part_lengths)

        # Make sure max_containers is not higher than num_parts, and make sure it was not a string.
        if self.window.max_containers > self.num_parts or self.window.max_containers == -2:
            self.window.max_containers = self.num_parts

        # Make sure max_parts_per_nest is not greater than max_containers since that wouldn't make sense.
        # Also make sure it was not entered as a string
        if self.window.max_parts_per_nest > self.window.max_containers or self.window.max_parts_per_nest == -2:
            self.window.max_parts_per_nest = self.window.max_containers

        # TODO Combine parts with same length?  Must still consider quantities...

        # TODO Find all optimum nodes, not just one

        # Solve for nestable length with extra spacing adjustment since blank includes spacing
        initial_nestable_length = \
            self.window.stock_length \
            - self.window.left_waste \
            - self.window.right_waste \
            + self.window.spacing

        self.nestable_length = initial_nestable_length

        # Construct length vector by adding part spacing
        self.nested_lengths = np.zeros((self.num_parts, 1))
        for i in range(self.num_parts):
            self.nested_lengths[i, 0] = self.window.part_lengths[i, 0] + self.window.spacing

        initial_nested_lengths = self.nested_lengths.copy()

        # Initialize patterns matrix (Step #1) (single part nesting patterns)
        self.patterns = np.zeros((self.num_parts, self.num_parts))
        for i in range(self.num_parts):
            self.patterns[i, i] = math.floor(self.nestable_length / self.nested_lengths[i])

            # Check if each part can be nested on the available length
            if self.patterns[i, i] == 0 or self.window.stock_length < self.window.left_waste + self.window.right_waste:
                # Zero out all outputs and exit function
                self.final_patterns = []
                self.final_allocations = 0
                self.window.error = 1  # error code 1 signifies that a part is too long
                return self.final_patterns, self.final_allocations

        # Find required number of lengths if everything nests ideally (only possible if parts nest perfectly on nestable
        # length)
        self.ideal_num = (np.dot(np.transpose(self.nested_lengths),
                                 self.window.part_quantities) / self.nestable_length).item()
        print("\nIdeally, the job would only require " + str(round(self.ideal_num, 2)) + " lengths. (zero scrap)\n")

        # Find required number of lengths in worst case scenario (single part nests only)
        self.patterns_inv = np.linalg.inv(self.patterns)
        self.patterns_trans_inv = np.transpose(self.patterns_inv)
        self.ones_vector = np.ones((self.num_parts, 1))

        # pi is a measure of how much of a stock length is used to cut a given part (if the 3rd term is 0.25, that
        # would indicate that the third part uses 1/4 of a stock length when considering the entire nest with all parts)
        self.pi = np.dot(self.patterns_trans_inv, self.ones_vector)
        self.worst_case = np.dot(np.transpose(self.window.part_quantities), self.pi)
        self.required_lengths = self.worst_case.copy()
        print("If only single part nests are used, the job would require a maximum of " + str(
            round(self.worst_case.item(), 2))
              + " lengths.\n")

        # Initialize parts_sublist (will restrain column generation to only consider parts spanning range of
        # max_containers)
        self.parts_sublist = np.zeros((self.num_parts - self.window.max_containers + 1, self.window.max_containers))
        self.parts_sublist_sorted = np.zeros((1, self.num_parts))
        self.container_counter = 0
        self.remaining_iterations = -1

        # TODO remove this feature if it is not desired (speeds up convergence, but results are less consistent)
        # # Initialize the part ordering if it doesn't exist yet
        # try:
        #     print(self.window.current_sequence)
        # except AttributeError:
        #     self.window.current_sequence = np.array(range(self.num_parts))

        # Initialize the part ordering
        self.window.current_sequence = np.arange(self.num_parts)

        for sub_i in range(self.num_parts - self.window.max_containers + 1):
            self.parts_sublist[sub_i] = np.array(range(sub_i, sub_i + self.window.max_containers))
            # self.parts_sublist[sub_i] = self.window.current_sequence[sub_i:(sub_i + self.window.max_containers)]

        # Iterate the part sequence to find the part ordering for which scrap is minimized
        self.part_sequence_is_optimum = 0
        self.current_part_index = 0

        self.window.part_quantities = initial_part_quantities[self.window.current_sequence].copy()
        self.window.part_lengths = initial_part_lengths[self.window.current_sequence].copy()
        self.window.part_names = initial_part_names[self.window.current_sequence].copy()

        self.parts_sublist_sorted = np.zeros((self.num_parts - self.window.max_containers + 1,
                                              self.window.max_containers))

        best_sequence = self.window.current_sequence.copy()
        # best_required_lengths = self.worst_case.copy()
        # part_sequence_is_optimum = 0
        # ij_best = [-1, -1]

        # # Don't enter while loop if max_containers is 1
        # if self.window.max_containers == 1:
        #     part_sequence_is_optimum = 1

        # sequencing_loop_counter = 0
        # sequencing_loop_counter_best = 0
        # x = []
        # y = []

        # # Loop to find best sequence of parts
        # while part_sequence_is_optimum == 0:
        #     for i in range(self.num_parts):
        #         if sequencing_loop_counter - sequencing_loop_counter_best >= 6:
        #             part_sequence_is_optimum = 1
        #             break
        #         if part_sequence_is_optimum == 1:
        #             break
        #         starting_sequence = self.window.current_sequence.copy()
        #         for j in range(self.num_parts):
        #             if part_sequence_is_optimum == 1:
        #                 break
        #             index_to_move = np.where(starting_sequence == i)[0]
        #
        #             # Move current part to jth position (swap)
        #             term_a = starting_sequence[index_to_move].copy()
        #             term_b = starting_sequence[j].copy()
        #             self.window.current_sequence = starting_sequence.copy()
        #             self.window.current_sequence[index_to_move] = term_b.copy()
        #             self.window.current_sequence[j] = term_a.copy()
        #
        #             self.window.part_quantities = initial_part_quantities[self.window.current_sequence].copy()
        #             self.window.part_lengths = initial_part_lengths[self.window.current_sequence].copy()
        #             self.window.part_names = initial_part_names[self.window.current_sequence].copy()
        #
        #             self.nested_lengths = initial_nested_lengths[self.window.current_sequence].copy()
        #
        #             # Reinitialize nestable length
        #             self.nestable_length = initial_nestable_length
        #
        #             # Reinitialize patterns matrix (single part nesting patterns)
        #             self.patterns = np.zeros((self.num_parts, self.num_parts))
        #             for k in range(self.num_parts):
        #                 self.patterns[k, k] = math.floor(self.nestable_length / self.nested_lengths[k])
        #
        #             # Run the column generation algorithm to find the best set of nest patterns for the job quantities
        #             [self.required_lengths, self.allocation, self.patterns] = \
        #                 self.column_gen(self.window.max_containers, self.window.part_quantities,
        #                                 self.parts_sublist, 0)
        #
        #             # Check if i and j match from the last time a best sequence was found
        #             if [i, j] == ij_best:
        #                 part_sequence_is_optimum = 1
        #
        #             if self.required_lengths < best_required_lengths - 0.00001:
        #                 print("new best")
        #                 print(self.required_lengths)
        #                 best_required_lengths = self.required_lengths.copy()
        #                 ij_best = [i, j]
        #                 sequencing_loop_counter_best = sequencing_loop_counter
        #                 best_sequence = self.window.current_sequence.copy()
        #
        #                 x = np.append(x, time.time())
        #                 y = np.append(y, self.required_lengths)
        #
        #             # Is this needed?  It seems to help reduce scrap in some cases.
        #             elif self.required_lengths == best_required_lengths:
        #                 print("tied best")
        #                 print(self.required_lengths)
        #                 best_required_lengths = self.required_lengths.copy()
        #                 best_sequence = self.window.current_sequence.copy()
        #
        #         self.window.current_sequence = best_sequence.copy()
        #
        #     sequencing_loop_counter += 1
        #
        # x = np.append(x, time.time())
        # y = np.append(y, self.required_lengths)
        #
        # plt.plot(x, y)
        # plt.savefig("mygraph.png")

        # Run through one more time using best sequence to get best patterns
        self.window.part_quantities = initial_part_quantities[best_sequence].copy()
        self.window.part_lengths = initial_part_lengths[best_sequence].copy()
        self.window.part_names = initial_part_names[best_sequence].copy()

        self.nested_lengths = initial_nested_lengths[best_sequence].copy()

        # Reinitialize nestable length
        self.nestable_length = initial_nestable_length

        # Reinitialize patterns matrix (single part nesting patterns)
        self.patterns = np.zeros((self.num_parts, self.num_parts))
        for k in range(self.num_parts):
            self.patterns[k, k] = math.floor(self.nestable_length / self.nested_lengths[k])

        # Run the column generation algorithm to find the best set of nest patterns for the job quantities
        # Decrease max parts per nest until max containers is fulfilled.
        for i in range(1, 1 + self.window.max_parts_per_nest)[::-1]:
            temp_max_parts_per_nest = i
            [self.required_lengths, self.allocation, self.patterns] = \
                self.column_gen(self.num_parts, temp_max_parts_per_nest, self.window.part_quantities,
                                np.array([np.arange(self.num_parts)]), 0)

            # Check if calculation has been canceled.
            if self.calculation_was_canceled == 1:
                # Zero out all outputs and exit function
                self.final_patterns = []
                self.final_allocations = 0
                return self.final_patterns, self.final_allocations

            # Round all of the allocations down, but allow for rounding error
            self.int_allocation = self.allocation.copy()
            for ii in range(len(self.allocation))[::-1]:
                self.int_allocation[ii] = math.floor(self.allocation[ii] + 0.0000001)
                # Remove unused patterns
                if self.int_allocation[ii] == 0:
                    self.int_allocation = np.delete(self.int_allocation, ii, 0)
                    self.allocation = np.delete(self.allocation, ii, 0)
                    self.patterns = np.delete(self.patterns.T, ii, 0).T

            # TODO move this to a better place
            cs = ColumnSorter(self.num_parts, len(self.allocation), self)

            [new_column_order, required_containers] = cs.optimize_sequence(self.patterns, 100, 0)

            # TODO remove second condition later?
            if required_containers <= self.window.max_containers or temp_max_parts_per_nest == 2:
                self.patterns = self.patterns.T[new_column_order].T
                self.int_allocation = self.int_allocation[new_column_order]

                chosen_required_lengths = self.required_lengths.copy()
                chosen_int_allocation = self.int_allocation.copy()
                chosen_patterns = self.patterns.copy()
                print(f"Acceptable solution found with 'Max parts per nest' constrained to {i}")
                print(f"Requires about {self.required_lengths} lengths")
                break

        # TODO check for best solution before filling remaining parts

        self.required_lengths = chosen_required_lengths.copy()
        self.int_allocation = chosen_int_allocation.copy()
        self.patterns = chosen_patterns.copy()

        # Create active parts matrix, and find start_pattern and end_pattern for each part inside pre_process function
        self.active_parts = self.patterns.copy()
        self.active_parts = cs.pre_process(self.active_parts)

        # TODO analyze how well this bug fix works and improve
        # Fix cs.start_pattern and cs.end_pattern if they contain terms that are out of bounds
        acceptable_values = np.arange(len(self.int_allocation))
        for num_index, num in enumerate(cs.start_pattern):
            if num not in acceptable_values:
                cs.start_pattern[num_index] = 0
                cs.end_pattern[num_index] = 0
        # cs.start_pattern
        # cs.end_pattern

        # Sort parts (rows) by end_pattern (earliest to latest)
        sorted_by_start = np.argsort(cs.start_pattern)
        cs.end_pattern_sorted = cs.end_pattern[sorted_by_start]
        cs.end_pattern_sorted = cs.end_pattern_sorted.astype(float)
        for item_index, item in enumerate(cs.end_pattern_sorted):
            cs.end_pattern_sorted[item_index] = item + item_index * 0.0000000001
        sorted_by_end = np.argsort(cs.end_pattern_sorted)
        self.active_parts = self.active_parts[sorted_by_start][sorted_by_end]
        self.patterns = self.patterns[sorted_by_start][sorted_by_end]
        self.window.part_quantities = self.window.part_quantities[sorted_by_start][sorted_by_end]
        self.window.part_names = self.window.part_names[sorted_by_start][sorted_by_end]
        self.window.part_lengths = self.window.part_lengths[sorted_by_start][sorted_by_end]
        self.nested_lengths = self.nested_lengths[sorted_by_start][sorted_by_end]
        cs.start_pattern = cs.start_pattern[sorted_by_start][sorted_by_end]
        cs.end_pattern = cs.end_pattern[sorted_by_start][sorted_by_end]
        self.frozen_pi = self.pi[sorted_by_start][sorted_by_end]

        containers = cs.count_containers(self.active_parts)
        containers_equals_max = containers == self.window.max_containers

        # Subtract quantities of fully allocated sticks to find remaining_part_quantities
        self.nested = np.dot(self.patterns, self.int_allocation)
        self.remaining_part_quantities = self.window.part_quantities.copy()
        self.remaining_part_quantities = self.remaining_part_quantities - self.nested

        # Initialize with 2 dummy terms
        self.additional_patterns = np.zeros((self.num_parts, 2))
        self.additional_allocations = np.zeros((1, 2))

        # Initialize with dummy term
        bridge_position_tracker = np.array([[0]])

        # Loop through parts (top to bottom)
        for self.part_index, active_parts_row in enumerate(self.active_parts):
            # If part is unfulfilled, generate a bridge pattern to fulfill it without breaking max_containers req
            # Use the nest with the lowest possible scrap rate (greedy algorithm),
            #   but add preference for fulfilling other unfulfilled parts
            # Stop early if remaining parts can be nested without breaking max_containers requirement
            if self.part_index >= (self.num_parts - self.window.max_containers):
                break
            if self.remaining_part_quantities[self.part_index]:
                # Find index of next unfulfilled part after current part
                next_uff_part = self.num_parts - 1
                for ii in range(self.part_index + 1, self.num_parts):
                    if self.remaining_part_quantities[ii]:
                        next_uff_part = ii
                        break

                # Define left and right bounds for current parts
                left_bound = int(cs.start_pattern[self.part_index])
                right_bound = int(cs.end_pattern[next_uff_part])

                # Adjust right bound to avoid breaking max_containers requirement
                for j in range(left_bound, right_bound):
                    # Using j as the left pattern under the below conditions would break the max_containers requirement
                    if containers_equals_max[j] and active_parts_row[j] == 0:
                        right_bound = j
                        break

                if left_bound == right_bound:
                    left_is_same_as_right = 1
                else:
                    left_is_same_as_right = 0

                # Loop through pairs of patterns within bounds to define parts that may be included in bridge patterns
                bridge_sublist = np.zeros((right_bound + left_is_same_as_right - left_bound, self.num_parts))
                for j_index, j in enumerate(range(left_bound, right_bound + left_is_same_as_right)):
                    left_active = self.active_parts[:, j]
                    right_active = self.active_parts[:, j + 1 - left_is_same_as_right]

                    # Current part should always be used in bridge pattern
                    bridge_sublist[j_index][self.part_index] = 1

                    # Other parts are allowed in bridge pattern if they are adjacent to an active part
                    # Other parts must be below current part
                    for ii in range(self.part_index + 1, self.num_parts):
                        if left_active[ii] or right_active[ii]:
                            bridge_sublist[j_index][ii] = 1

                # bridge_sublist = np.unique(bridge_sublist, axis=0)
                # print(bridge_sublist)  # TODO add similar functionality later

                self.unavailable_parts = [[-1]]
                try_expanding_right_bound = 0
                num_extra_parts = 0

                while self.remaining_part_quantities[self.part_index]:  # Finds additional bridge pattern if needed
                    if try_expanding_right_bound == 1 and right_bound < np.shape(self.active_parts)[1] - 2:
                        right_bound += 1
                        bridge_sublist = np.append(bridge_sublist, np.zeros((1, self.num_parts)), axis=0)

                        # Loop through pairs of adjacent patterns within bounds to define parts that may be included in
                        #   each bridge patterns
                        left_active = self.active_parts[:, right_bound]
                        right_active = self.active_parts[:, right_bound + 1]

                        # Current part should always be used in bridge pattern
                        bridge_sublist[-1][self.part_index] = 1

                        # Other parts are allowed in bridge pattern if they are adjacent to an active part
                        # Other parts must be below current part
                        for ii in range(self.part_index + 1, self.num_parts):
                            if left_active[ii] or right_active[ii]:
                                bridge_sublist[j_index][ii] = 1

                    best_bridge_pattern = []
                    best_bridge_ip = 0
                    for sublist_index, sublist in enumerate(bridge_sublist):
                        parts_sublist = np.array([])
                        for bit_index, bit in enumerate(sublist):
                            if bit == 1:
                                parts_sublist = np.append(parts_sublist, bit_index)
                        parts_sublist = np.array([parts_sublist.astype(int)])
                        self.container_counter = 0

                        # Create new sublist that helps branch bound function decide which nests are best
                        self.bonus_sublist = parts_sublist.copy()
                        for item_index, item in enumerate(self.bonus_sublist[0]):
                            if item == self.part_index or item == next_uff_part:
                                self.bonus_sublist[0][item_index] = 1
                            elif item > next_uff_part:
                                self.bonus_sublist[0][item_index] = 0
                            else:
                                self.bonus_sublist[0][item_index] = -1

                        self.branch_bound(len(parts_sublist[0]), self.window.max_parts_per_nest + num_extra_parts,
                                          self.window.part_quantities.copy(), parts_sublist, 1,
                                          np.where(parts_sublist[0] == self.part_index)[0].item())

                        # Check if calculation has been canceled.
                        if self.calculation_was_canceled == 1:
                            # Zero out all outputs and exit function
                            self.final_patterns = []
                            self.final_allocations = 0
                            return self.final_patterns, self.final_allocations

                        # Extract the best pattern from ip_best_row
                        self.best_pattern_sorted_sublist = \
                            np.transpose([self.ip_best_row[1:(len(parts_sublist[0]) + 1)]])

                        # Initialize best_pattern_sorted
                        self.best_pattern_sorted = np.zeros((self.num_parts, 1))

                        # Add pattern values from the sublist to the main list
                        for iii in range(len(parts_sublist[0])):
                            # Find index in main list corresponding to ith index of parts_sublist_sorted
                            self.corr_index = \
                                np.where(self.index_order == self.parts_sublist_sorted[self.container_counter][iii])[
                                    0].item()
                            self.best_pattern_sorted[self.corr_index] = self.best_pattern_sorted_sublist[iii]

                        # Reorder best_pattern vector
                        self.old_index_order = np.argsort(self.index_order)
                        self.best_pattern = self.best_pattern_sorted[self.old_index_order]

                        if self.ip_best > best_bridge_ip:
                            best_bridge_ip = self.ip_best
                            best_bridge_pattern = self.best_pattern.copy()
                            insertion_position = cs.start_pattern[self.part_index] + sublist_index + 1

                    # Check if any downstream unfulfilled parts could have fit on current bridge pattern
                    remaining_length = self.window.stock_length - self.window.left_waste - self.window.right_waste
                    remaining_length -= np.dot(best_bridge_pattern.T, self.nested_lengths)

                    downstream_parts = np.arange(self.part_index + 1, self.num_parts)

                    find_new_best = 0
                    for p_index, part in enumerate(downstream_parts):
                        if not best_bridge_pattern[part][0]:  # If the part is not in the bridge pattern
                            if self.nested_lengths[p_index] < remaining_length:  # and if there is room to nest it
                                if right_bound < np.shape(self.active_parts)[1] - 2:  # and the right bound can be
                                    # extended
                                    try_expanding_right_bound = 1
                                    find_new_best = 1
                                    num_parts_in_nest = 0
                                    for p in best_bridge_pattern:
                                        if p[0]:
                                            num_parts_in_nest += 1
                                    if num_parts_in_nest == self.window.max_parts_per_nest + num_extra_parts:
                                        num_extra_parts += 1
                                    break

                    if find_new_best == 1:
                        continue
                    else:
                        num_extra_parts = 0

                    # Save copies of changing variables in case they have to change back
                    backup_vars = [bridge_position_tracker.copy(),
                                   self.additional_patterns.copy(),
                                   self.additional_allocations.copy(),
                                   self.remaining_part_quantities.copy(),
                                   self.int_allocation.copy()
                                   ]

                    bridge_position_tracker = np.append(bridge_position_tracker, insertion_position)
                    self.additional_patterns = np.append(self.additional_patterns.T, best_bridge_pattern.T, axis=0).T
                    self.additional_allocations = np.append(self.additional_allocations.T, [[1]], axis=0).T
                    self.remaining_part_quantities -= best_bridge_pattern

                    do_not_adjust_allocations = 0
                    # Loop to decide which patterns to borrow from
                    while np.any(self.remaining_part_quantities < 0):
                        for pattern_qty_index, pattern_qty in enumerate(best_bridge_pattern):
                            if pattern_qty:
                                if pattern_qty_index <= self.part_index:  # Catches part_index part
                                    continue
                                # Borrow from the rightmost possible pattern if there are negative parts remaining
                                if self.remaining_part_quantities[pattern_qty_index] < 0:
                                    rightmost_pattern_index = cs.end_pattern[pattern_qty_index]
                                    # Make sure there are patterns available to pull from before borrowing parts
                                    if self.int_allocation[rightmost_pattern_index] == 0:
                                        # Keep trying patterns to the left until there are allocations for that pattern
                                        #   and it uses the part with negative qty remaining
                                        while self.int_allocation[rightmost_pattern_index] == 0 or \
                                                self.patterns[pattern_qty_index][rightmost_pattern_index] == 0:
                                            rightmost_pattern_index = rightmost_pattern_index - 1

                                            for qty_index, qty in enumerate(self.patterns.T[rightmost_pattern_index]):
                                                if qty:
                                                    highest_in_pattern = qty_index
                                                    break

                                            # If pattern contains any parts with index <= self.part_index (higher
                                            # than current part)
                                            if highest_in_pattern <= self.part_index:
                                                # Restore variables if no downstream parts can be borrowed
                                                [bridge_position_tracker,
                                                 self.additional_patterns,
                                                 self.additional_allocations,
                                                 self.remaining_part_quantities,
                                                 self.int_allocation
                                                 ] = backup_vars.copy()
                                                self.unavailable_parts = np.append(self.unavailable_parts,
                                                                                   [[pattern_qty_index]],
                                                                                   axis=0)
                                                do_not_adjust_allocations = 1
                                                break

                                    if do_not_adjust_allocations == 0:
                                        self.int_allocation[rightmost_pattern_index] -= 1
                                        self.remaining_part_quantities += np.expand_dims(self.patterns.T[
                                            rightmost_pattern_index], axis=0).T

        # Delete dummy term
        bridge_position_tracker = np.delete(bridge_position_tracker, 0, axis=0)

        if sum(self.remaining_part_quantities) == 0:
            self.parts_need_nested = 0
        else:
            self.parts_need_nested = 1

        num_extra_parts = 0

        while self.parts_need_nested == 1:

            final_parts_sublist = np.arange(self.num_parts - self.window.max_containers, self.num_parts)
            final_parts_sublist = np.expand_dims(final_parts_sublist, axis=0)
            self.branch_bound(self.window.max_containers, self.window.max_parts_per_nest + num_extra_parts,
                              self.remaining_part_quantities, final_parts_sublist, 2)

            # Check if calculation has been canceled.
            if self.calculation_was_canceled == 1:
                # Zero out all outputs and exit function
                self.final_patterns = []
                self.final_allocations = 0
                return self.final_patterns, self.final_allocations

            # Extract the best pattern from ip_best_row
            self.best_pattern_sorted_sublist = np.transpose([self.ip_best_row[1:(len(self.ip_best_row) - 3)]])

            # Initialize best_pattern_sorted
            self.best_pattern_sorted = np.zeros((self.num_parts, 1))

            # Add pattern values from the sublist to the main list
            for iii in range(len(self.ip_best_row) - 4):
                # Find index in main list corresponding to ith index of parts_sublist_sorted
                self.corr_index = \
                    np.where(self.index_order == self.parts_sublist_sorted[self.container_counter][iii])[
                        0].item()
                self.best_pattern_sorted[self.corr_index] = self.best_pattern_sorted_sublist[iii]

            # Reorder best_pattern vector
            self.old_index_order = np.argsort(self.index_order)
            self.best_pattern = self.best_pattern_sorted[self.old_index_order]

            # TODO add above to branch_bound function? see other occurances

            # Check if any downstream unfulfilled parts could have fit on current bridge pattern
            remaining_length = self.window.stock_length - self.window.left_waste - self.window.right_waste
            remaining_length -= np.dot(self.best_pattern.T, self.nested_lengths)

            downstream_parts = np.arange(self.part_index, self.num_parts)

            find_new_best = 0
            for p_index, part in enumerate(downstream_parts):
                if self.nested_lengths[p_index] < remaining_length:  # check if there is room to nest it
                    if self.window.max_parts_per_nest + num_extra_parts <= len(downstream_parts):
                        find_new_best = 1
                        num_extra_parts += 1
                        break

            if find_new_best == 1:
                continue
            else:
                num_extra_parts = 0

            self.additional_patterns = np.append(self.additional_patterns.T, self.best_pattern.T, axis=0).T
            self.additional_allocations = np.append(self.additional_allocations.T, [[1]], axis=0).T

            self.remaining_part_quantities -= self.best_pattern

            # While loop to add additional patterns with remaining parts
            self.too_many_nested = 0
            while self.too_many_nested == 0 and self.parts_need_nested == 1:
                self.check_totals = self.remaining_part_quantities - self.best_pattern

                for i in range(self.num_parts):
                    if self.check_totals[i] < 0:
                        self.too_many_nested = 1

                if self.too_many_nested == 0:
                    if len(self.additional_allocations) == 1:
                        self.additional_allocations[0][len(self.additional_allocations) - 1] += 1
                    else:
                        self.additional_allocations[len(self.additional_allocations) - 1] += 1

                    self.remaining_part_quantities = self.check_totals
                    self.additional_allocations[0][-1] += 1

                if (self.remaining_part_quantities == np.zeros((self.num_parts, 1))).all():
                    self.parts_need_nested = 0

        self.additional_patterns = np.delete(self.additional_patterns, 0, axis=1)
        self.additional_patterns = np.delete(self.additional_patterns, 0, axis=1)
        self.additional_allocations = np.delete(self.additional_allocations, 0, axis=1)
        self.additional_allocations = np.delete(self.additional_allocations, 0, axis=1)
        self.additional_allocations = self.additional_allocations.T

        self.final_patterns = self.patterns.copy()
        self.final_allocations = self.int_allocation.copy()

        insertion_order = np.argsort(bridge_position_tracker)[::-1]

        # Insert additional patterns into main patterns according to bridge_position_tracker
        if len(bridge_position_tracker) > 0:
            bridge_position_tracker = np.concatenate((np.array([bridge_position_tracker]), np.array([np.arange(len(
                bridge_position_tracker))])), axis=0)
            bridge_position_tracker[0] = bridge_position_tracker[0][insertion_order]
            bridge_position_tracker[1] = bridge_position_tracker[1][insertion_order]
            for tracker_element_index, tracker_element in enumerate(bridge_position_tracker[0]):
                self.final_patterns = np.insert(self.final_patterns.T, tracker_element, self.additional_patterns.T[
                    bridge_position_tracker[1][tracker_element_index]].T, axis=0).T
                self.final_allocations = np.insert(self.final_allocations, tracker_element, self.additional_allocations[
                    bridge_position_tracker[1][tracker_element_index]], axis=0)

            # Remove bridge patterns from additional_patterns and additional_allocations
            for index in range(len(bridge_position_tracker[0])):
                self.additional_patterns = np.delete(self.additional_patterns.T, 0, axis=0).T
                self.additional_allocations = np.delete(self.additional_allocations, 0, axis=0)

        # Concatenate remaining additional patterns to main patterns if they were added
        if len(self.additional_allocations) != 0:
            self.final_patterns = np.concatenate((self.final_patterns, self.additional_patterns), axis=1)
            self.final_allocations = np.concatenate((self.final_allocations, self.additional_allocations))

        # Remove any patterns with final allocations of zero
        for i in range(len(self.final_allocations))[::-1]:
            if self.final_allocations[i] == 0:
                self.final_patterns = np.delete(self.final_patterns, i, 1)
                self.final_allocations = np.delete(self.final_allocations, i, 0)

        # Combine any duplicate patterns
        for i in range(np.size(self.final_allocations))[::-1]:
            for j in range(i)[::-1]:
                if np.all(self.final_patterns[:, i] == self.final_patterns[:, j]):
                    self.final_allocations[j] += self.final_allocations[i]
                    self.final_patterns = np.delete(self.final_patterns, i, 1)
                    self.final_allocations = np.delete(self.final_allocations, i, 0)
                    break

        nested_qtys = np.sum(np.dot(self.final_patterns, self.final_allocations))
        original_qtys = np.sum(initial_part_quantities)
        if nested_qtys != original_qtys:
            print("Nested qtys did not match original qtys!!!  Code needs to be debugged")

        # Find scrap rates for each nest and overall
        self.scrap_rates = 1 - np.dot(self.window.part_lengths.T, self.final_patterns) / self.window.stock_length
        self.overall_scrap = np.dot(self.scrap_rates, self.final_allocations) / np.sum(self.final_allocations)
        self.overall_scrap = self.overall_scrap[0][0]

        index_largest_drop = np.argmax(self.scrap_rates)
        self.max_drop_length = self.window.stock_length - self.window.right_waste
        self.max_drop_length -= np.dot(self.final_patterns.T[index_largest_drop].T, self.nested_lengths)[0]
        scrap_adjustment = self.max_drop_length / self.window.stock_length / np.sum(self.final_allocations)
        self.scrap_without_drop = self.overall_scrap - scrap_adjustment

        self.actual_max_containers = int(np.max(cs.count_containers(self.final_patterns)))
        self.final_required_lengths = int(np.sum(self.final_allocations))
        self.final_required_lengths_minus_drop = \
            self.final_required_lengths - self.max_drop_length / self.window.stock_length

        if np.size(self.final_patterns) >= 3:
            drop_at_end_sequence = np.arange(len(self.final_allocations))
            drop_at_end_sequence = np.delete(drop_at_end_sequence, index_largest_drop)
            drop_at_end_sequence = np.append(drop_at_end_sequence, index_largest_drop)
            drop_at_end_patterns = self.final_patterns.T[drop_at_end_sequence].T

            # Improve max containers further if possible
            final_sequence_adjustment = cs.optimize_sequence(drop_at_end_patterns, 1, 1)[0]
            possible_pattern_replacement = drop_at_end_patterns.T[final_sequence_adjustment].T
            possible_pattern_replacement = cs.pre_process(possible_pattern_replacement)

            # TODO allow for more than max containers in bridge patterns

            self.final_patterns = drop_at_end_patterns.T[final_sequence_adjustment].T
            self.final_allocations = self.final_allocations[drop_at_end_sequence][final_sequence_adjustment]
            self.scrap_rates = self.scrap_rates[0][drop_at_end_sequence][final_sequence_adjustment]
            print(cs.count_containers(possible_pattern_replacement))
            self.actual_max_containers = int(np.max(cs.count_containers(possible_pattern_replacement)))
            self.final_required_lengths = int(np.sum(self.final_allocations))
            self.final_required_lengths_minus_drop = \
                self.final_required_lengths - self.max_drop_length / self.window.stock_length

            # Sort parts (rows) by start_pattern (earliest to latest)
            cs.pre_process(self.final_patterns)
            sorted_by_start = np.argsort(cs.start_pattern)
            self.final_patterns = self.final_patterns[sorted_by_start]
            self.window.part_quantities = self.window.part_quantities[sorted_by_start]
            self.window.part_names = self.window.part_names[sorted_by_start]
            self.window.part_lengths = self.window.part_lengths[sorted_by_start]
            self.nested_lengths = self.nested_lengths[sorted_by_start]

        print(self.final_patterns)

        adj_matrix = self.find_adj_matrix(self.final_patterns)
        connected_parts_lists = []
        for i in range(self.num_parts):
            connected_parts_list = [i]
            for sublist_index, sublist in enumerate(connected_parts_lists):
                if i in sublist:
                    connected_parts_list = sublist
                    connected_parts_lists.pop(sublist_index)
            for element_index, element in enumerate(adj_matrix[i]):
                if element != 0:
                    for sublist_index, sublist in enumerate(connected_parts_lists.copy()):
                        if element_index in sublist:
                            connected_parts_list = self.union(connected_parts_list, sublist)
                            connected_parts_lists.pop(sublist_index)
                        else:
                            if element_index not in connected_parts_list:
                                connected_parts_list.append(element_index)
            connected_parts_lists.append(connected_parts_list)

        # Find sublist containing the parts in the pattern with the highest scrap.  Move to end.
        index_largest_drop = np.argmax(self.scrap_rates)
        for part_index, item in enumerate(self.final_patterns.T[index_largest_drop]):
            if item != 0:
                for sublist_index, sublist in enumerate(connected_parts_lists):
                    if part_index in sublist:
                        connected_parts_lists.pop(sublist_index)
                        connected_parts_lists.append(sublist)
                        break

        for sublist in connected_parts_lists:
            sublist.sort()

        reordered_connected_parts_lists = copy.deepcopy(connected_parts_lists)

        i = 0
        for sublist_index, sublist in enumerate(reordered_connected_parts_lists):
            for element_index, element in enumerate(sublist):
                reordered_connected_parts_lists[sublist_index][element_index] = i
                i += 1

        self.sequenced_by_networks = [item for sublist in connected_parts_lists for item in sublist]

        self.final_patterns = self.final_patterns[self.sequenced_by_networks]
        self.window.part_quantities = self.window.part_quantities[self.sequenced_by_networks]
        self.window.part_names = self.window.part_names[self.sequenced_by_networks]
        self.window.part_lengths = self.window.part_lengths[self.sequenced_by_networks]
        self.nested_lengths = self.nested_lengths[self.sequenced_by_networks]

        intermediate_pattern_sequence = []
        for sublist_index, sublist in enumerate(reordered_connected_parts_lists):
            for pattern_index, pattern in enumerate(self.final_patterns.T):
                for i in range(len(sublist)):
                    if pattern[sublist[i]] != 0:
                        if pattern_index not in intermediate_pattern_sequence:
                            intermediate_pattern_sequence.append(pattern_index)
                            break

        self.final_patterns = self.final_patterns.T[intermediate_pattern_sequence].T
        self.final_allocations = self.final_allocations[intermediate_pattern_sequence]

        cs.pre_process(self.final_patterns)
        split_points = np.array([0])

        adj_matrix = self.find_adj_matrix(self.final_patterns)

        for i in range(self.num_parts - 1):
            if adj_matrix[i][i + 1] == 0:
                if np.any(adj_matrix[0:i + 1, i + 1:self.num_parts - 1] != 0):
                    continue
                else:
                    split_points = np.append(split_points, i + 1)

        split_points = np.append(split_points, self.num_parts)

        largest_in_set = np.zeros((1, len(split_points) - 1))

        for split_point_index, split_point in enumerate(split_points[:-1]):
            for i in range(split_point, split_points[split_point_index + 1]):
                if self.nested_lengths[i][0] > largest_in_set[0][split_point_index]:
                    largest_in_set[0][split_point_index] = self.nested_lengths[i][0]

        pattern_split_points = split_points.copy()

        for i in range(len(pattern_split_points) - 1):
            pattern_split_points[i] = cs.start_pattern[split_points[i]]

        pattern_split_points[-1] = len(self.final_allocations)

        order_of_chains = np.argsort(largest_in_set[0][:-1])[::-1]
        order_of_chains = np.append(order_of_chains, len(order_of_chains))

        unchanged_sequence = np.arange(len(self.final_allocations))
        chains = cs.list_of_lists(len(order_of_chains), 0)
        for i in range(len(order_of_chains)):
            chains[i] = unchanged_sequence[pattern_split_points[i]:pattern_split_points[i + 1]]

        organized_sequence = []
        for i in range(len(order_of_chains)):
            organized_sequence = np.append(organized_sequence, chains[order_of_chains[i]])

        organized_sequence = organized_sequence.astype(int)

        self.final_patterns = self.final_patterns.T[organized_sequence].T
        self.final_allocations = self.final_allocations[organized_sequence]

        # Sort parts (rows) by start_pattern (earliest to latest)
        cs.pre_process(self.final_patterns)
        sorted_by_start = np.argsort(cs.start_pattern)
        self.final_patterns = self.final_patterns[sorted_by_start]
        self.window.part_quantities = self.window.part_quantities[sorted_by_start]
        self.window.part_names = self.window.part_names[sorted_by_start]
        self.window.part_lengths = self.window.part_lengths[sorted_by_start]
        self.nested_lengths = self.nested_lengths[sorted_by_start]

        # Sort rows by shortest part to longest part so that shorter parts end up on left
        self.sorted_by_length = np.argsort(self.nested_lengths.T[0])
        self.final_patterns = self.final_patterns[self.sorted_by_length]
        self.window.part_lengths = self.window.part_lengths[self.sorted_by_length]
        self.window.part_names = self.window.part_names[self.sorted_by_length]
        self.window.part_quantities = self.window.part_quantities[self.sorted_by_length]

        return self.final_patterns, self.final_allocations
