from generala import Generala

# Run "make" and then "./Generala"

# Creates default game of Generala, precomputing possible rerolls and roll probabilities.
# Generala is like Yahtzee, but with 10 scoring categories (ONES, TWOS, THREES, FOURS, FIVES, SIXES, STRAIGHT, 
# FULL-HOUSE, FOUR-OF-A-KIND, GENERALA). Each turn players can roll up to 3 times, and keep dice in between each roll.
# The goal of this algorithm is to use dynamic programming and Markov decision processes
# to maximize the expected score from a given state, therefore finding the optimal move
# from a given state as well. The state consists of which categories are used/unused, our roll in hand, and number of rolls we 
# have left. There is also a bonus, DOUBLE GENERALA, which can be used once a game if we roll a generala 
# after already rolling it before in the game. Note that this will count as a "scoring" even though categories do not change.
# Have fun experimenting! 
game = Generala()

# EXAMPLE TEST CASES (make sure roll is sorted): 
# Score DOUBLE GENERALA even when ONES is open
print(game.find_best_action([0,1,1,1,1,1,1,1,1,1], [1,1,1,1,1], 2))
# Cannot score DOUBLE GENERALA even if we have a generala roll since we scratched, so score ONES
print(game.find_best_action([0,1,1,1,1,1,1,1,1,2], [1,1,1,1,1], 2))
# Choose FOUR-OF-A-KIND over SIXES given 0 rolls left
print(game.find_best_action([1,1,1,1,1,0,1,1,0,1], [1,6,6,6,6], 0))
# Keep [1, 2, 3, 4] over scoring or keeping other dice because we want to try to get a STRAIGHT
print(game.find_best_action([1,0,1,1,1,0,0,1,0,1], [1,1,2,3,4], 1))
# Score FULL-HOUSE over TWOS, SIXES, or trying to keep the 3 6's for FOUR-OF-A-KIND
print(game.find_best_action([1,0,1,1,1,0,1,0,0,1], [2,2,6,6,6], 1))
# Can add any other test cases here (or use USER TESTING section after)


# USER TESTING:
# NOTE: Testing from an initial state (all categories unused) can take around ~45 minutes (on my computer)
# NOTE: In addition to using the function find_best_action, the user can also used find_expected_score for 
# a given state. 
categories = []
roll = []
rolls_left = 0
# Input from user of current categories used/unsed, current roll, and number of rolls left 

# Categories (except GENERALA) can be 0 (unused) or 1 (used). 
# For GENERALA case, category can be 0 (unused), 1 (used and scored (50 points)), 2 (used and scratched),
# or 3 (used double generala, can only be used once per game)
# Input format as 10 1-digit numbers (0, 1, 2, or 3) corresponding to the categories 
# ONES, TWOS, THREES, FOURS, FIVES, SIXES, STRAIGHT, FULL-HOUSE, FOUR-OF-A-KIND, GENERALA and their usage. 
# E.g. 0111111103 means ONES and FOUR-OF-A-KIND are unused, GENERALA used double generala already, and rest 
# of the categories are used.
categories_str = input('Enter categories used/unused (10 numbers, no space, q to quit): ')

# Input format as 5 1-digit numbers (1-6) corresponding to the rolls of 5 dice.
# E.g. 41523 means our current roll is a 4, 1, 5, 2, 3.
roll_str = input('Enter current roll (5 numbers, no space): ')

# Input format as digit (0-2) corresponding to how many rerolls we have left in our turn.
# E.g. 1 means we have one reroll left in our turn. 
rolls_left_str = input('Enter how many rolls left (0-2): ')

while categories_str != 'q':
    # Format input as arrays/numbers to pass as parameters. 
    for char in categories_str:
        categories.append(int(char))

    for char in roll_str:
        roll.append(int(char))

    rolls_left = int(rolls_left_str)

    # Sort the roll so we can access the precomputed tables easier later
    roll.sort()

    # Finds the best action to do (keep certain die or score a category)
    # given current state of categories used/unused, roll, and rolls left.
    print(game.find_best_action(categories, roll, rolls_left))

    # reset values
    categories = []
    roll = []
    rolls_left = 0

    categories_str = input('Enter categories used/unused (10 numbers, no space, q to quit): ')
    roll_str = input('Enter current roll (5 numbers, no space): ')
    rolls_left_str = input('Enter how many rolls left (0-2): ')