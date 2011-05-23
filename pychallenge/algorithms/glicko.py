# computes Glicko rating a player
# Glicko requires a list of information from all played matches
# during a rating period
# the length of a rating period depends on the game
# e.g.: one month
#
# player data:  rating  (initial 1500)
#               RD      level of certainty (initial 350) (Ratings Deviation)
#               t       most recent rating period (>=1)
#
# constants:    q = (ln 10)/400 = 0.0057565
#               c - uncertainty over time (choosen for each game)
#
# outcome:      0   -> player loses
#               0.5 -> player draws
#               1   -> player wins
import math

# constant
q = 0.0057565

# Glicko takes the time a player hasn't played into consideration
# this means if player hasn't played for a long time his RD rating
# will increase up to a certain treshold (350)
# call this function to get the current RD of a player
# RD    - level of certainty (maximum 350) (Ratings Deviation)
# c     - uncertainty over time (choosen for each game)
# t     - most recent raing period (>=1)
def getCurrentRD(RD, c, t):
    currentRD = math.sqrt((RD**2) + (c**2*t))
    if currentRD > 350.0:
        return 350.0
    else:
        return currentRD

# helper function
def g(RD):
    return 1/math.sqrt((1+(3*(q**2)*(RD**2)))/math.pi**2)

# return expected result for a match
def expectation(ratingOwn, ratingPlayer2, RDPlayer2):
    exponent = (-1*g(RDPlayer2)*(ratingOwn-ratingPlayer2))/400.0
    return 1/(1 + (10**exponent))

# ratingOwn     - player rating
# ratingList    - list of opponents ratings
# RDList        - list of oppenents RDs
# ratingList.length == RDList.length
def dSquared(ratingOwn, ratingList, RDList):
    sum = 0.0
    for RD in RDList:
        sum += (g(RD)**2)*(expectation(ratingOwn, ratingList[RDList.index(RD)], RD))*(1-expectation(ratingOwn, ratingList[RDList.index(RD)], RD))

    sum = (q**2)*sum
    result = 1/sum

    return result

# after a match this returns the new rating
# RDOwn         - player RD
# ratingOwn     - player rating
# ratingList    - list of opponent ratings
# RDList        - list of opponent RDs
# outcomeList   - list of match outcomes
# ratingList.length == RDList.length == outcomeList.length
def newRating(RDOwn, ratingOwn, ratingList, RDList, outcomeList):

    factor = q/((1/(RDOwn**2))+(1/dSquared(ratingOwn, ratingList, RDList)))

    sum = 0.0
    for RD in RDList:
        sum += g(RD)*(outcomeList[RDList.index(RD)] - expectation(ratingOwn, ratingList[RDList.index(RD)], RD))

    result = ratingOwn + (factor*sum)

    return result

# after a match this returns the new RD
# RDOwn         - player RD
# ratingOwn     - player rating
# ratingList    - list of opponent ratings
# RDList        - list of opponent RDs
def newRD(RDOwn, ratingOwn, ratingList, RDList):
    result = 1/((1/(RDOwn**2)) + (1/dSquared(ratingOwn, ratingList, RDList)))
    return result

