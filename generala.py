import constants
import roll_probabilities_result
import possible_rerolls_result
import itertools

class Generala:
    def __init__(self):
        '''
        Initializes Generala game with precomputing possible rerolls and roll probabilities.
        '''
        # memoized table in form of dictionary, with keys as (categories, roll, rolls_left) tuples
        # and values as expected score
        self.expected_scores = {}

        # PRECOMPUTED THE POSSIBLE REROLLS/ROLL PROBABILITIES WITH COMMENTED OUT CODE BELOW.
        # self.possible_rerolls = {}
        # self._precompute_possible_rerolls()

        # file = open("possible_rerolls_result.py", "w")
        # file.write("%s = %s\n" %("POSSIBLE_REROLLS", self.possible_rerolls))
        # file.close()

        # # calculated probability of going from one roll to another given which dice kept
        # # self._precompute_roll_probabilities()

        # self.roll_probabilities = {}
        # self._precompute_roll_probabilities()
        # file = open("roll_probabilities_result.py", "w")
        # file.write("%s = %s\n" %("ROLL_PROBABILITIES", self.roll_probabilities))
        # file.close()

        # dictionary of key as pair of 5-die roll and which dice to keep, 
        # and value as list of pairs of possible rerolls and frequency of duplicates
        self.possible_rerolls = possible_rerolls_result.POSSIBLE_REROLLS
        self.roll_probabilities = roll_probabilities_result.ROLL_PROBABILITIES

    def _precompute_roll_probabilities(self):
        '''
        Precomputes all the roll probabilities in a dictionary, with keys as (curr_roll, dice_keep, new_roll) tuples, and 
        values as probability of going from curr_roll to new_roll given we keep dice_keep.
        '''
        for roll_dice_keep_pair in self.possible_rerolls.keys():
            # first count total number of rerolls possible 
            total_possibilities = 0
            for reroll in self.possible_rerolls[roll_dice_keep_pair]:
                total_possibilities += reroll[1]

            # then calculate probability given current roll, the roll we want to get, and which dice to keep
            for reroll in self.possible_rerolls[roll_dice_keep_pair]:
                self.roll_probabilities[(roll_dice_keep_pair[0], roll_dice_keep_pair[1], tuple(reroll[0]))] = reroll[1] / total_possibilities

    def _find_roll_probability(self, curr_roll, new_roll, dice_keep):
        '''
        Finds the roll probability of going from curr_roll to new_roll given we keep dice_keep. 
        Searched through precomputed dictionary. 

        curr_roll -- current roll array in hand
        new_roll -- the roll we want
        dice_keep -- array of which dice from curr_roll to keep
        '''
        return self.roll_probabilities[(tuple(curr_roll), tuple(dice_keep), tuple(new_roll))]

    def _precompute_possible_rerolls(self):
        '''
        Precomputes all possible rerolls in dictionary, with keys as (roll, dice_keep) pairs and values 
        as (reroll, freq) pairs.
        '''
        # generate all possible combinations of 5 dice
        possible_rolls = list(itertools.product(range(1, 7), repeat = 5))

        for num_dice_remove in range(0, 6):
            # generate possibilities of rolling num_dice_remove dice again
            removed_dice_reroll = list(itertools.product(range(1, 7), repeat = num_dice_remove))

            for roll in possible_rolls:
                sorted_roll = tuple(sorted(roll))

                # if we remove 0 dice (aka keep all dice), we just append current roll to dictionary value 
                if num_dice_remove == 0:
                    self.possible_rerolls[(sorted_roll, sorted_roll)] = [[sorted_roll, 1]]
                    continue

                dice_keep = list(itertools.combinations(roll, 5 - num_dice_remove))

                for dice in dice_keep:
                    sorted_dice = tuple(sorted(dice))

                    # if we already calculated the possible rerolls from this position (except roll was in diff order), then no need to re-find rerolls
                    if (sorted_roll, sorted_dice) in self.possible_rerolls:
                        continue

                    for reroll_dice in removed_dice_reroll:
                        new_roll = list(dice).copy()
                        new_roll.extend(reroll_dice)
                        new_roll.sort()

                        # if not in dictionary, initialize
                        if (sorted_roll, sorted_dice) not in self.possible_rerolls:
                            self.possible_rerolls[(sorted_roll, sorted_dice)] = [[new_roll, 1]]
                        else:
                            # make sure we account for duplicates of dice roll (e.g. (1,2) same as (2, 1))
                            in_list = False
                            for i in range(len(self.possible_rerolls[(sorted_roll, sorted_dice)])):
                                # check if the two are the same 
                                if new_roll == self.possible_rerolls[(sorted_roll, sorted_dice)][i][0]:
                                    # increase frequency
                                    self.possible_rerolls[(sorted_roll, sorted_dice)][i][1] += 1 
                                    in_list = True
                                    break

                            # if not in list, then add it as a new possible reroll with frequency 1
                            if not in_list:
                                self.possible_rerolls[(sorted_roll, sorted_dice)].append([new_roll, 1])

    def _valid_categories(self, roll):
        '''
        Returns array of indices of categories that can be filled given the current dice in hand.

        roll -- the roll array we want to check
        '''
        categories = []
        is_straight = True
        is_full_house = True
        roll_dict = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}

        for die in roll:
            roll_dict[die] += 1

        for i in range(1, 7):
            # check ones-sixes
            if roll_dict[i] > 0:
                categories.append(i - 1)

            # check straight
            if is_straight and roll_dict[i] != 1:
                if i != 1 and i != 6:
                    is_straight = False
            
            # check full house
            if is_full_house and roll_dict[i] not in [0, 2, 3]:
                is_full_house = False
            
            # check four of a kind
            if roll_dict[i] == 4:
                categories.append(constants.FOUR_OF_A_KIND)

            # check generala 
            if roll_dict[i] == 5:
                categories.append(constants.GENERALA)

        if is_straight:    
            categories.append(constants.STRAIGHT)

        if is_full_house:
            categories.append(constants.FULL_HOUSE)

        return categories


    def _calculate_reward(self, categories, category, roll, rolls_left, is_scratch):
        '''
        Calculates reward of scoring in given category given current dice in hand.

        category -- one of Generala scoring categories in index format
        '''

        # converts roll array to dictionary of each value and its frequency in roll
        # easier to calculate in this format
        roll_dict = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}

        for die in roll:
            roll_dict[die] += 1

        if is_scratch:
            return 0
        elif category == constants.ONES:
            return roll_dict[1]
        elif category == constants.TWOS:
            return roll_dict[2]*2
        elif category == constants.THREES:
            return roll_dict[3]*3
        elif category == constants.FOURS:
            return roll_dict[4]*4
        elif category == constants.FIVES:
            return roll_dict[5]*5
        elif category == constants.SIXES:
            return roll_dict[6]*6
        elif category == constants.STRAIGHT:
            # first roll bonus 
            if rolls_left == 2:
                return 25
            else:
                return 20
        elif category == constants.FULL_HOUSE:
            if rolls_left == 2:
                return 35
            else:
                return 30
        elif category == constants.FOUR_OF_A_KIND:
            if rolls_left == 2:
                return 45
            else:
                return 40
        # generala 
        else:
            # if we already had a generala, we get double generala
            if categories[category] == 1:
                return 100
            else:
                return 50

    def _game_over(self, categories):
        '''
        Determines whether we are in a terminal state, which in Generala is whether we've scored 10 times. 

        categories -- array of which categories used/unused
        '''
        if categories[constants.GENERALA] in [0, 1]:
            return sum(categories) == 10
        elif categories[constants.GENERALA] in [2, 3]:
            return sum(categories) == 11

    def _get_valid_new_states(self, categories, roll, rolls_left, actions_possible):       
        '''
        Returns all possible valid states from current state of (categories, roll, roll_left), with some extra information
        including reward, probability of going into new state, and which action taken. 

        categories -- array of which categories used/unused
        roll -- current roll array 
        rolls_left -- number of rolls left in turn
        actions_possible -- array of actions possible, including which categories we can score in and which dice we can keep
        ''' 
        new_states = []

        # if we are already scored all categories, no possible new states
        if self._game_over(categories):
            return new_states

        # if we choose to score a category
        for category in range(constants.NUM_CATEGORIES):
            # if a category is open, then we can score in it
            if categories[category] == 0 or (category == constants.GENERALA and categories[category] == 1 and (category in self._valid_categories(roll))):
                new_categories = categories.copy()

                if category == constants.GENERALA:
                    # at this point categories[category] can be 0 or 1, and not 2 or 3
                    if categories[category] == 0:
                        # if we zero out generala, then we can't get double generala, so we store this as 2
                        if category not in self._valid_categories(roll):
                            new_categories[category] = 2
                        else:
                            new_categories[category] = 1
                    # categories[category] == 1 and generala is a valid category
                    else:
                        new_categories[category] = 3
                else:
                    new_categories[category] = 1
                        
                r = self._calculate_reward(categories, category, roll, rolls_left, (category not in self._valid_categories(roll)))

                # find all possible rerolls (i.e. keeping 0 die and rerolling all die)
                for new_roll_freq in self.possible_rerolls[(tuple(roll), ())]:
                    # out of 15 possible actions, we chose to score in category with index "category"
                    action_taken = category
                    # store new categories array, new roll, reward from going to s', 
                    # and probability of going to s' (essentially the new roll probability) in return
                    # in _find_roll_probability we "remove 5 die", which is basically just same thing as rolling all 5-die 
                    new_states.append((new_categories, new_roll_freq[0], r, self._find_roll_probability(roll, new_roll_freq[0], ()), action_taken, 2))

        # if we still have rolls left, we can also keep dice
        if rolls_left > 0:
            for action_idx in range(len(actions_possible)):
                action = actions_possible[action_idx]
                # don't want to check action of scoring category
                if type(action) != tuple:
                    continue

                for new_roll_freq in self.possible_rerolls[(tuple(roll), tuple(action))]:
                    # categories stays the same, since we aren't inputting any scores, but rather rerolling
                    # reward for rerolling is 0
                    new_states.append((categories, new_roll_freq[0], 0, self._find_roll_probability(roll, new_roll_freq[0], action), action_idx, rolls_left - 1))

        return new_states

    def find_expected_score(self, categories, roll, rolls_left):
        '''
        Finds expected score from current state of (categories, roll, roll_left) assuming we do optimal moves.

        categories -- array of which categories used/unused
        roll -- current roll array 
        rolls_left -- number of rolls left in turn 
        '''
        # base case, at end of game, so we don't increase score 
        if self._game_over(categories):
            # terminal states have reward of 0
            self.expected_scores[(tuple(categories), tuple(roll), rolls_left)] = 0
            return 0
        # if already calculated, then just return the value
        elif (tuple(categories), tuple(roll), rolls_left) in self.expected_scores:
            return self.expected_scores[(tuple(categories), tuple(roll), rolls_left)]
        else:
            # actions possible:
            # 1. scoring in 1 of 10 categories
            # 2. remove 1-5 die
            actions = [i for i in range(10)]

            # gets all possible dice keeping combinations
            for roll_dice_keep_pair in self.possible_rerolls.keys():
                if sorted(roll) == roll_dice_keep_pair[0]:
                    actions.append(roll_dice_keep_pair[1])

            actions_expected_scores = [0]*len(actions)

            valid_new_states = self._get_valid_new_states(categories, roll, rolls_left, actions)

            for new_state in valid_new_states:
                new_categories = new_state[0]
                new_roll = new_state[1]
                r = new_state[2]
                new_roll_probability = new_state[3]
                action_taken = new_state[4]
                new_rolls_left = new_state[5]

                actions_expected_scores[action_taken] += new_roll_probability*(r + self.find_expected_score(new_categories, new_roll, new_rolls_left))

            best_action_expected_score = max(actions_expected_scores)
            self.expected_scores[(tuple(categories), tuple(roll), rolls_left)] = best_action_expected_score
            return best_action_expected_score

    def find_best_action(self, categories, roll, rolls_left):
        '''
        Returns the best action to do (score a category or keep certain die) in current state of (categories, roll, rolls_left).

        categories -- array of which categories used/unused
        roll -- current roll array 
        rolls_left -- number of rolls left in turn
        '''
        # if already end of game, then no possible 
        if self._game_over(categories):
            return -1
        
        actions = [i for i in range(10)]

        for roll_dice_keep_pair in self.possible_rerolls.keys():
            # find all possible ways of keeping the dice in roll, excluding keeping all 5 (since that's just scoring in a category)
            if tuple(sorted(roll)) == roll_dice_keep_pair[0] and roll_dice_keep_pair[1] != roll_dice_keep_pair[0]:
                actions.append(roll_dice_keep_pair[1])

        actions_expected_scores = [0]*len(actions)

        valid_new_states = self._get_valid_new_states(categories, roll, rolls_left, actions)

        for new_state in valid_new_states:
            new_categories = new_state[0]
            new_roll = new_state[1]
            r = new_state[2]
            new_roll_probability = new_state[3]
            action_taken = new_state[4]

            # if we chose to score, update it in actions 
            if action_taken in range(10):
                # markov decision process
                actions_expected_scores[action_taken] += new_roll_probability*(r + self.find_expected_score(new_categories, new_roll, 2))
            else:
                actions_expected_scores[action_taken] += new_roll_probability*(r + self.find_expected_score(new_categories, new_roll, rolls_left - 1))

        # CAN UNCOMMENT TO VIEW EXPECTED SCORES OF EACH ACTION TO VERIFY
        # print(actions)
        # print(actions_expected_scores)

        res = actions[actions_expected_scores.index(max(actions_expected_scores))]

        if type(res) != tuple:
            if res == -1:
                return "AT TERMINAL STATE"
            elif categories[constants.GENERALA] == 1 and res == constants.GENERALA:
                return "SCORE DOUBLE " + constants.CATEGORIES[res]
            else:
                return "SCORE " + constants.CATEGORIES[res]
            
        else:
            return "KEEP " + str(res)