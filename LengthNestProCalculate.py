import math
import numpy as np
import time as time
import sys
import random as random
from scipy.sparse.csgraph import reverse_cuthill_mckee
from scipy import sparse


def length_nest_pro(part_lengths, b, part_names, spacing, left_waste, right_waste, stock_length):
    # Start timer
    start_time = time.time()

    # Set precision for printing
    np.set_printoptions(precision=3)

    # Set data
    # spacing = 0.29
    # left_waste = .12
    # right_waste = 4.75
    # stock_length = 288
    pattern_max = 100  # TODO remove this feature?
    lp_time = 0
    inv_time = 0
    append_time = 0
    # ComparisonTime = 0
    # part_numbers = np.array([["1"], ["2"], ["3"], ["4"], ["5"], ["6"], ["7"]])
    # part_lengths = np.array([[26.559], [9.5], [48.622], [15.791]])
    # b = np.array([[400], [200], [200], [200]])  # part quantities vector

    # part_lengths = np.array([[.5], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12], [13], [14], [15],
    # [16], [17], [18], [19], [20], [10.5], [11.5], [12.5], [13.5], [14.5], [15.5], [16.5], [17.5], [18.5],
    # [19.5]]) b = np.array([[2000], [30], [40], [10], [5], [35], [78], [2], [39], [15], [20], [30], [40], [10], [5],
    # [35], [78], [2], [39], [15], [20], [30], [40], [10], [5], [35], [78], [2], [39], [15]])  # part quantities vector

    # part_lengths = np.array([[19], [11], [3], [4], [10], [2], [18], [15], [1], [6], [0.5], [1.5], [2.5], [3.5],
    # [4.5], [5.5], [6.5], [7.5], [8.5], [9.5], [10.5], [11.5], [12.5]]) b = np.array([[20], [30], [40], [10], [5],
    # [35], [78], [2], [39], [15], [20], [30], [40], [10], [5], [35], [78], [2], [39], [15], [20], [30],
    # [40]])  # part quantities vector

    # part_lengths = np.array([[19], [11], [3], [4], [10], [2], [18], [15], [1], [6], [0.5], [1.5], [2.5], [3.5],
    # [4.5], [5.5], [6.5], [7.5], [8.5], [9.5]]) b = np.array([[20], [30], [40], [10], [5], [35], [78], [2], [39],
    # [15], [20], [30], [40], [10], [5], [35], [78], [2], [39], [15]])  # part quantities vector

    # part_lengths = np.array(np.transpose([np.linspace(.5, 20, 39, endpoint=False)]))
    # n = len(part_lengths)
    # b = np.ones((n, 1))*100

    # n = 15
    # part_numbers = np.zeros((n, 1))
    # part_lengths = np.zeros((n, 1))
    # b = np.zeros((n, 1))
    # for i in range(n):
    #     part_numbers[i] = i + 1
    #     part_lengths[i] = random.random()*3+2
    #     b[i] = round(random.random()*1000)

    # # #
    # Remove any parts where PartQty is 0 (remove entries from part_lengths and b)
    for i in range(len(b))[::-1]:
        if b[i] == 0:
            b = np.delete(b, i, 0)
            part_lengths = np.delete(part_lengths, i, 0)
            part_names = np.delete(part_names, i, 0)

    b_modified = b

    # # #
    # Combine parts with same length?  Must still consider quantities...

    # # #
    # Find all optimum nodes, not just one

    # Check how many different parts are needed (n)
    n = len(part_lengths)

    # Solve for nestable length with extra spacing adjustment since blank includes spacing
    nestable_length = stock_length - left_waste - right_waste + spacing

    # Construct length vector
    length = np.zeros((n, 1))
    for i in range(n):
        length[i, 0] = part_lengths[i, 0] + spacing

    # Initialize patterns matrix (Step #1) (single part nesting patterns)
    patterns = np.zeros((n, n))
    for i in range(n):
        patterns[i, i] = math.floor(nestable_length / length[i])
        # Check if each part can be nested on the available length
        if patterns[i, i] == 0 or stock_length < left_waste + right_waste:
            print("One or more of the parts is too long for the available nesting length")
            final_patterns = []
            final_allocations = 0
            part_lengths = 0
            b = 0
            part_names = 0
            spacing = 0
            left_waste = 0
            right_waste = 0
            stock_length = 0
            return final_patterns, final_allocations, part_lengths, part_names, spacing, left_waste, right_waste, stock_length
            sys.exit()

    # Make dummy copies of patterns to check for cycling
    patterns_copy1 = patterns.copy()
    patterns_copy2 = patterns.copy()-1
    patterns_copy3 = patterns.copy()-2
    patterns_copy4 = patterns.copy()-3
    patterns_copy5 = patterns.copy()-4
    patterns_copy6 = patterns.copy()-5
    patterns_copy7 = patterns.copy()-6
    patterns_copy8 = patterns.copy()-7

    # Find required number of lengths if everything nests ideally (only possible if parts nest perfectly on nestable
    # length)
    ideal_num = (np.dot(np.transpose(length), b) / nestable_length).item()
    print("Ideally, the job would only require " + str(round(ideal_num, 2)) + " lengths.\n")

    # Find required number of lengths in worst case scenario (single part nests only)
    # print(patterns)
    patterns_inv = np.linalg.inv(patterns)
    patterns_trans_inv = np.transpose(patterns_inv)
    ones_vector = np.ones((n, 1))
    pi = np.dot(patterns_trans_inv, ones_vector)
    worst_case = np.dot(np.transpose(b), pi)
    print("If only single part nests are used, the job would require a maximum of " + str(round(worst_case.item(), 2))
          + " lengths.\n")

    # Execute main program loop until optimum solution is reached
    while 1:
        # Find pi vector from patterns (Step #2)
        t1 = time.time()
        patterns_inv = np.linalg.inv(patterns)
        t2 = time.time()
        inv_time += (t2 - t1)
        patterns_trans_inv = np.transpose(patterns_inv)
        ones_vector = np.ones((n, 1))
        pi = np.dot(patterns_trans_inv, ones_vector)

        # Adjust pi slightly to prioritize longer parts
        for i in range(len(pi)):
            pi[i] = pi[i] + 0.0001 * length[i] / nestable_length

        # Calculate allocations of each pattern
        allocation = np.dot(patterns_inv, b)

        # Warn user if any allocations are negative, but allow for rounding error
        for i in range(n):
            if allocation[i] < -0.000001:
                print("Warning: There are negative allocations")

        # Find value vector that can be used to prioritize the "usefulness" of nesting each part
        values = np.divide(pi, length)

        # Reorder vectors pi, values, length, and b to get pi0, values0, length0, and b0
        print(patterns)
        print(sparse.csc_matrix(patterns))
        rcm_permutation = reverse_cuthill_mckee(sparse.csc_matrix(patterns))
        rcm_value = np.argsort(rcm_permutation)

        rcm_patterns = patterns[rcm_permutation, :]
        rcm_patterns = rcm_patterns[:, rcm_permutation]
        print(rcm_patterns)

        index_order = (np.argsort((values * -1).transpose()))[0]
        pi0 = pi[index_order]
        values0 = values[index_order]
        length0 = length[index_order]
        b0 = b[index_order]
        rcm_value0 = rcm_value[index_order]

        patterns0 = np.zeros((n, n))
        for i in range(n):
            patterns0[:, i] = patterns[:, index_order[i]]
            # allocation0 = allocation[index_order]
        # print(patterns0)

        # Initialize branch and bound matrix, bbm, with level 1 node
        #   Row will be [level a0_1 a0_2 ... a0_n rem LP IP]
        #   bbm will consist of all nodes that may still be explored
        bbm = np.zeros((1, n + 4))
        bbm[0, 0] = 1  # level
        # Entries 1 through n will remain at 0 for the first node because no parts have been nested
        bbm[0, n + 1] = nestable_length  # Calculate rem, remaining nestable length
        bbm[0, n + 2] = bbm[0, n + 1] * values0[0]  # Calculate value of LP, linear programming maximum value
        # bbm[0, n + 3] = 0  # Value of IP, int programming maximum value, will remain at 0 since no parts are nested

        # Initialize lp_best and ip_best
        lp_best = bbm[0, n + 2]
        ip_best = 0

        # Initialize ip_best_row to keep track of best node
        ip_best_row = bbm[0]

        # Initialize lp_best_index at 0 since there is only one node
        lp_best_index = 0

        # Initialize loop_count
        loop_count = 0

        # Start timer for branch bound process
        # BBstart_time = time.time()

        # Begin loop to start branching nodes and allow for rounding error
        while lp_best > ip_best - 0.00000001:

            # Check timer and exit branch bound if solution is taking too long
            # if time.time() - BBstart_time > 1 and ip_best > 1.0000001:
            #       break

            # Extract the row to be explored
            row = bbm[lp_best_index, :]

            # Extract the level of the row to be explored
            level = int(row[0])

            # Extract the remaining length for the row to be explored
            rem = row[n + 1]

            # Extract length of part being considered at current level (level 1 corresponds to part 1 and so on)
            p_length = length0[level - 1]

            # Check how many of the part can be nested on remaining length rem
            num = math.floor(rem / p_length)

            # Reduce num if there are not enough parts to nest
            part_max = int(math.floor(b0[level - 1].item()))
            if part_max < num:
                num = part_max

            # Add columns of patterns0 corresponding to the parts that are used in each node
            # If the number of nonzero terms is greater than mixing_max, remove the node from bbm
            # If the number of nonzero terms is equal to the mixing_max, only consider the largest # of the last part
            # pattern_sum = np.zeros((n, 1))
            # for i in range(level - 1):
            #     pattern_sum += np.transpose([patterns0[:, i]]) * row[i + 1]
            #     # print(pattern_sum)
            # #
            # # pattern_sum += np.transpose([patterns[:, level]]) ????
            # mixing_count = 0
            # for i in range(n):
            #     if pattern_sum[i] != 0:
            #         mixing_count += 1
            #
            # branch_node = 1
            # if mixing_count >= mixing_max:
            #     # Remove node from bbm if it has too many connections with other patterns in the basis
            #     bbm = np.delete(bbm, lp_best_index, 0)
            #     branch_node = 0
            # # elif mixing_count == mixing_max: TODO to speed up code
            # #     pass

            # Allow node to be explored by default
            branch_node = 1

            # If more than 1 part is included in pattern that has not been previously included, do not use the pattern
            # new_parts_in_pattern = 0
            # for i in range(level):
            #     if row[i + 1] != 0:
            #         new_parts_in_pattern += 1

            if level > pattern_max:
                parts_in_pattern = 0
                for i in range(level):
                    if row[i + 1] != 0:
                        parts_in_pattern += 1
                if parts_in_pattern == pattern_max:
                    bbm = np.delete(bbm, lp_best_index, 0)
                    branch_node = 0
                elif parts_in_pattern == pattern_max - 1:
                    # Copy the node 1 time, and iterate a0_level to num
                    row_copy = row.copy()  # copy row
                    row_copy[level] = num  # iterate a0_level
                    row_copy[n + 1] = rem - num * p_length  # subtract nested parts from rem
                    row_copy[n + 3] = np.dot([row_copy[1:n + 1]], pi0)  # calculate IP for new node
                    if row_copy[n + 3] > ip_best:
                        ip_best = row_copy[n + 3]
                        ip_best_row = row_copy

                    # Remove the explored node from bbm
                    bbm = np.delete(bbm, lp_best_index, 0)
                    branch_node = 0

            if branch_node == 1:
                # Copy the node (num + 1) times to explore it, and iterate a0_level from 0 to num
                for i in range(num + 1):
                    row_copy = row.copy()  # copy row
                    row_copy[level] = i  # iterate a0_level
                    row_copy[n + 1] = rem - i * p_length  # subtract nested parts from rem
                    row_copy[n + 3] = np.dot([row_copy[1:n + 1]], pi0)  # calculate IP for new node
                    if row_copy[n + 3] > ip_best:
                        ip_best = row_copy[n + 3]
                        ip_best_row = row_copy
                    if level < n:
                        t1 = time.time()
                        row_copy[n + 2] = row_copy[n + 3] + row_copy[n + 1] * values0[level]  # calculate LP for new node
                        if row_copy[n + 2] > ip_best:
                            row_copy[0] = level + 1  # increment level of copy
                            bbm = np.append(bbm, [row_copy], axis=0)  # add new node to bbm
                        t2 = time.time()
                        append_time += (t2 - t1)

                # Remove the explored node from bbm
                bbm = np.delete(bbm, lp_best_index, 0)

            # Every 100 iterations, check for any nodes with an LP less than ip_best and remove them
            if loop_count / 100 == round(loop_count / 100):
                for i in (range(len(bbm[:, n + 2])))[::-1]:
                    if bbm[i, n + 2] < ip_best:
                        bbm = np.delete(bbm, i, 0)

            # Check to make sure bbm is not empty
            if np.size(bbm) > 0:

                # # # Find a faster way to choose next node without cycling through all of bbm
                # Decide which node to explore next by searching for the node in bbm with highest LP
                t1 = time.time()
                lp_best_index = np.argmax(bbm[:, n + 2])
                lp_best = bbm[lp_best_index, n + 2]
                t2 = time.time()
                lp_time += (t2 - t1)
            else:
                break

            # Keep track of how many times the loop is executed
            loop_count += 1

            # print number of rows in bbm
            if loop_count / 10000 == round(loop_count / 10000):
                print(len(bbm[:, n + 2]))

        # Extract the best pattern from ip_best_row
        best_pattern0 = np.transpose([ip_best_row[1:(n + 1)]])

        # # # Make sure this will always be optimum, see if omitting leads to choosing existing pattern as best
        # replacement
        # Exit the loop if no improvement can be found
        if ip_best < 1.00000000001:
            print("ip_best = 1")
            break

        # Reorder best_pattern vector
        old_index_order = np.argsort(index_order)
        best_pattern = best_pattern0[old_index_order]

        # Determine which pattern to replace in patterns
        # Solve for p_bar_j (proportion of each existing pattern that 1 instance of best_pattern can replace)
        p_bar_j = np.dot(patterns_inv, best_pattern)

        # Initialize theta_limits
        theta_limits = np.zeros((n, 1))

        # Calculate required_lengths before adding new pattern to patterns
        required_lengths = np.sum(np.dot(patterns_inv, b))

        # Print data for loop
        print(required_lengths)
        # print(lp_time)
        # print(inv_time)
        # print(append_time)
        # total_time = time.time() - start_time
        # print(total_time)

        # Find the limiting pattern when replacing current nests with the maximum number of instances of best_pattern
        for i in range(n):
            # Solve for the reciprocal of the limits on Theta for each pattern
            theta_limits[i] = (p_bar_j[i]) / (allocation[i] + 0.00000001)
        # print(theta_limits)

        # Replace the pattern with the largest value of theta_limits
        index_to_replace = np.argmax(theta_limits)

        # # # This warning seems unnecessary since it simply means that you're replacing a pattern that isn't being used
        # if theta_limits[index_to_replace] > 10000:
        #     print("Theta Limit is large")
        #     print(p_bar_j[index_to_replace])
        #     print(allocation[index_to_replace])

        # # # This warning could probably be removed since it would probably be caught by the cycling warning
        # Replace old pattern with new pattern unless they are already the same
        if (patterns[:, index_to_replace] == best_pattern.transpose()[0]).all():
            print("Newly calculated pattern matches current pattern.")
            break
        else:
            patterns[:, index_to_replace] = best_pattern.transpose()[0]

        # print(best_pattern)
        # print(patterns)

        # Check for cycling
        patterns_copy9 = patterns_copy8
        patterns_copy8 = patterns_copy7
        patterns_copy7 = patterns_copy6
        patterns_copy6 = patterns_copy5
        patterns_copy5 = patterns_copy4
        patterns_copy4 = patterns_copy3
        patterns_copy3 = patterns_copy2
        patterns_copy2 = patterns_copy1
        patterns_copy1 = patterns.copy()
        # print((patterns_copy1 == patterns_copy3).all())
        # print(patterns_copy2)
        # print(patterns_copy1)

        # Check comparison time
        # t1 = time.time()

        if (patterns_copy1 == patterns_copy2).all() or (patterns_copy1 == patterns_copy3).all() or \
                (patterns_copy1 == patterns_copy4).all() or (patterns_copy1 == patterns_copy5).all() or \
                (patterns_copy1 == patterns_copy6).all() or (patterns_copy1 == patterns_copy7).all() or \
                (patterns_copy1 == patterns_copy8).all() or (patterns_copy1 == patterns_copy9).all():
            print("Cycling has occurred")
            break

        # t2 = time.time()
        # ComparisonTime += (t2 - t1)

        # # # Time limit is disabled but could be useful
        # Check time to see if it has been too long
        # total_time = time.time() - start_time
        # TimeLimit = 100
        # if total_time > TimeLimit:
        #     print("Nesting time limit of " + str(TimeLimit) + " seconds has been reached.")
        #     break

    # Calculate final allocations of each pattern
    allocation = np.dot(patterns_inv, b)

    required_lengths = float(np.sum(allocation))
    print("If the optimum nesting is used, the job would require " + str(round(required_lengths, 2)) + " lengths.\n")
    # print(allocation)

    # Check final time
    total_time = time.time() - start_time
    print(total_time)
    # print(ComparisonTime)
    print(patterns)
    print(allocation)

    # Round all of the allocations down, but allow for rounding error
    int_allocation = allocation.copy()
    for i in range(len(allocation)):
        int_allocation[i] = math.floor(allocation[i]+0.0000001)

    print(int_allocation)

    # Subtract quantities of fully allocated sticks
    nested = np.dot(patterns, int_allocation)
    new_totals = b.copy()
    new_totals = new_totals - nested
    # print(new_totals)

    b = new_totals

    ##############

    # TODO - final loop might not be optimum

    # TODO - check for duplicates from patterns matrix

    ##############

    if sum(b) == 0:
        parts_need_nested = 0
    else:
        parts_need_nested = 1

    additional_patterns = np.array([])
    additional_allocations = np.array([])

    while parts_need_nested == 1:

        # Find pi vector from patterns (Step #2)
        patterns_inv = np.linalg.inv(patterns)
        patterns_trans_inv = np.transpose(patterns_inv)
        ones_vector = np.ones((n, 1))
        pi = np.dot(patterns_trans_inv, ones_vector)

        # Adjust pi slightly to prioritize longer parts
        for i in range(len(pi)):
            pi[i] = pi[i] + 0.0001 * length[i] / nestable_length

        # Calculate allocations of each pattern
        # allocation = np.dot(patterns_inv, b)

        # Warn user if any allocations are negative, but allow for rounding error
        # for i in range(n):
        #     if allocation[i] < -0.000001:
        #         print("Warning: There are negative allocations")

        # Find value vector that can be used to prioritize the "usefulness" of nesting each part
        values = np.divide(pi, length)

        # Reorder vectors pi, values, length, and b to get pi0, values0, length0, and b0
        index_order = (np.argsort((values * -1).transpose()))[0]
        pi0 = pi[index_order]
        values0 = values[index_order]
        length0 = length[index_order]
        b0 = b[index_order]
        # patterns0 = np.zeros((n, n))
        # for i in range(n):
        #     patterns0[:, i] = patterns[:, index_order[i]]
        #     allocation0 = allocation[index_order]

        # Initialize branch and bound matrix, bbm, with level 1 node
        #   Row will be [level a0_1 a0_2 ... a0_n rem LP IP]
        #   bbm will consist of all nodes that may still be explored
        bbm = np.zeros((1, n + 4))
        bbm[0, 0] = 1  # level
        # Entries 1 through n will remain at 0 for the first node because no parts have been nested
        bbm[0, n + 1] = nestable_length  # Calculate rem, remaining nestable length
        bbm[0, n + 2] = bbm[0, n + 1] * values0[0]  # Calculate value of LP, linear programming maximum value
        # bbm[0, n + 3] = 0  # Value of IP, int programming maximum value, will remain at 0 since no parts are nested

        # Initialize lp_best and ip_best
        lp_best = bbm[0, n + 2]
        ip_best = 0

        # Initialize ip_best_row to keep track of best node
        ip_best_row = bbm[0]

        # Initialize lp_best_index at 0 since there is only one node
        lp_best_index = 0

        # Initialize loop_count
        loop_count = 0

        # Begin loop to start branching nodes and allow for rounding error
        while lp_best > ip_best - 0.00000001:

            # Extract the row to be explored
            row = bbm[lp_best_index, :]

            # Extract the level of the row to be explored
            level = int(row[0])

            # Extract the remaining length for the row to be explored
            rem = row[n + 1]

            # Extract length of part being considered at current level (level 1 corresponds to part 1 and so on)
            p_length = length0[level - 1]

            # Check how many of the part can be nested on remaining length rem
            num = math.floor(rem / p_length)

            # Reduce num if there are not enough parts to nest
            part_max = int(math.floor(b0[level - 1].item()))
            if part_max < num:
                num = part_max
                # num_was_limited = 1

            # Allow node to be explored by default
            branch_node = 1

            # Check if too many parts are being used in the pattern
            # if level > pattern_max:
            #     parts_in_pattern = 0
            #     for i in range(level):
            #         if row[i + 1] != 0:
            #             parts_in_pattern += 1
            #     if parts_in_pattern == pattern_max:
            #         print("too many parts")
            #         print(row[1:n+1])
            #         bbm = np.delete(bbm, lp_best_index, 0)
            #         branch_node = 0
            #     elif parts_in_pattern == pattern_max - 1:
            #         # Copy the node 1 time, and iterate a0_level to num
            #         row_copy = row.copy()  # copy row
            #         row_copy[level] = num  # iterate a0_level
            #         row_copy[n + 1] = rem - num * p_length  # subtract nested parts from rem
            #         row_copy[n + 3] = np.dot([row_copy[1:n + 1]], pi0)  # calculate IP for new node
            #         if row_copy[n + 3] > ip_best:
            #             ip_best = row_copy[n + 3]
            #             ip_best_row = row_copy
            #
            #         # Remove the explored node from bbm
            #         bbm = np.delete(bbm, lp_best_index, 0)
            #         branch_node = 0

            if branch_node == 1:
                # Copy the node (num + 1) times to explore it, and iterate a0_level from 0 to num
                for i in range(num + 1):
                    row_copy = row.copy()  # copy row
                    row_copy[level] = i  # iterate a0_level
                    row_copy[n + 1] = rem - i * p_length  # subtract nested parts from rem
                    row_copy[n + 3] = np.dot([row_copy[1:n + 1]], pi0)  # calculate IP for new node
                    if row_copy[n + 3] > ip_best:
                        ip_best = row_copy[n + 3]
                        ip_best_row = row_copy
                    if level < n:
                        row_copy[n + 2] = row_copy[n + 3] + row_copy[n + 1] * values0[level]  # calculate LP for new node
                        if row_copy[n + 2] > ip_best:
                            row_copy[0] = level + 1  # increment level of copy
                            bbm = np.append(bbm, [row_copy], axis=0)  # add new node to bbm

                # Remove the explored node from bbm
                bbm = np.delete(bbm, lp_best_index, 0)

            # Every 100 iterations, check for any nodes with an LP less than ip_best and remove them
            if loop_count / 100 == round(loop_count / 100):
                for i in (range(len(bbm[:, n + 2])))[::-1]:
                    if bbm[i, n + 2] < ip_best:
                        bbm = np.delete(bbm, i, 0)

            # Check to make sure bbm is not empty
            if np.size(bbm) > 0:

                # # # Find a faster way to choose next node without cycling through all of bbm
                # Decide which node to explore next by searching for the node in bbm with highest LP
                lp_best_index = np.argmax(bbm[:, n + 2])
                lp_best = bbm[lp_best_index, n + 2]
            else:
                break

            # Keep track of how many times the loop is executed
            loop_count += 1

            # print number of rows in bbm
            if loop_count / 10000 == round(loop_count / 10000):
                print(len(bbm[:, n + 2]))

        # Extract the best pattern from ip_best_row
        best_pattern0 = np.transpose([ip_best_row[1:(n + 1)]])

        # # # Make sure this will always be optimum, see if omitting leads to choosing existing pattern as best
        # replacement
        # Exit the loop if no improvement can be found
        # if ip_best < 1.00000000001:
        #     print("ip_best = 1")
        #     break

        # Reorder best_pattern vector
        old_index_order = np.argsort(index_order)
        best_pattern = best_pattern0[old_index_order]

        if additional_patterns.size == 0:
            additional_patterns = best_pattern
            additional_allocations = [[0]]
        else:
            additional_patterns = np.append(additional_patterns, best_pattern, axis=1)
            additional_allocations = np.append(additional_allocations, [[0]], axis=0)

        too_many_nested = 0
        parts_need_nested = 1

        while too_many_nested == 0 and parts_need_nested == 1:
            check_totals = b - best_pattern

            for i in range(n):
                if check_totals[i] < 0:
                    too_many_nested = 1

            if too_many_nested == 0:
                if len(additional_allocations) == 1:
                    additional_allocations[0][len(additional_allocations) - 1] += 1
                else:
                    additional_allocations[len(additional_allocations) - 1] += 1
                b = check_totals

            if (b == np.zeros((n, 1))).all():
                parts_need_nested = 0

    for i in range(np.size(additional_allocations))[::-1]:
        for j in range(n):
            if (additional_patterns[:, i] == patterns[:, j]).all():
                int_allocation[j] += additional_allocations[i]
                additional_patterns = np.delete(additional_patterns, i, 1)
                additional_allocations = np.delete(additional_allocations, i, 0)
                break

    # Concatenate new patterns to old patterns if they were added
    if len(additional_allocations) != 0:
        final_patterns = np.concatenate((patterns, additional_patterns), axis=1)
        final_allocations = np.concatenate((int_allocation, additional_allocations))
    else:
        final_patterns = patterns
        final_allocations = int_allocation

    # Remove any patterns with final allocations of zero
    for i in range(len(final_allocations))[::-1]:
        if final_allocations[i] == 0:
            final_patterns = np.delete(final_patterns, i, 1)
            final_allocations = np.delete(final_allocations, i, 0)

    return final_patterns, final_allocations, part_lengths, part_names, b_modified, spacing, left_waste, right_waste, stock_length

    # Write to file
    # with open('output.csv', 'w') as csvfile:
    #     csvwriter = csv.writer(csvfile)
    #     for row in patterns:
    #         print(row)
    #         csvwriter.writerow(row)


# length_nest_pro([], [])
