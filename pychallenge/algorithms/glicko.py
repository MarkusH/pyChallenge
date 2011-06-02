"""
computes Glicko rating a player
Glicko requires a list of information from all played matches
during a rating period
the length of a rating period depends on the game
e.g.: one month

player data:  rating  (initial 1500)
              RD      level of certainty (initial 350) (Ratings Deviation)
              t       most recent rating period (>= 1)

constants:    q = (ln 10) / 400 = 0.0057565
              c - uncertainty over time (choosen for each game)

outcome:      0   -> player loses
              0.5 -> player draws
              1   -> player wins
"""
import math

#: glicko constant ( q = (ln 10) / 400 = 0.0057565 )
q = 0.0057565


def getCurrentRD(RD, c, t):
    """
    Glicko takes the time a player hasn't played into consideration
    this means if player hasn't played for a long time his RD rating
    will increase up to a certain treshold (350).

    call this function to get the current RD of a player

    :param RD: level of certainty (maximum 350) (Ratings Deviation)
    :param c: uncertainty over time (choosen for each game)
    :param t: most recent raing period (>=1)
    :type RD: float
    :type c: float
    :type t: integer
    :return: updated player RD that can be used for new matches
    :rtype: float
    """
    rd2 = RD * RD
    c2 = c * c * t
    currentRD = math.sqrt(rd2 + c2)

    return currentRD if currentRD < 350.0 else 350.0


def g(RD):
    """
    Glicko helper function

    :param RD: level of certainty (maximum 350) (Ratings Deviation)
    :type RD: float
    :return: intermediate result
    :rtype: float
    """
    q2 = 3.0 * q * q * RD * RD
    pi2 = math.pi * math.pi

    return (math.sqrt(1.0 + (q2 / pi2))) ** -1


def expectation(ratingOwn, ratingOpponent, RDOpponent):
    """
    This calculates the expected match result

    :param ratingOwn: own rating
    :param ratingOpponent:  rating of the opponent
    :param RDOpponent: RD of the opponent
    :type ratingOwn: float
    :type ratingOpponent: float
    :type RDOpponent: float
    :return: expected result for a match
    :rtype: float
    """
    exponent = (-1.0 * g(RDOpponent) * (ratingOwn - ratingOpponent)) / 400.0

    return 1 / (1.0 + (10.0 ** exponent))


def dSquared(ratingOwn, ratingList, RDList):
    """
    :param ratingOwn: player rating
    :param ratingList: list of opponents' ratings
    :param RDList: list of opponents' RDs
    :type ratingOwn: float
    :type ratingList: list of floats
    :type RDList: list of floats
    :return: intermediate result
    :rtype: float
    """

    #: assert that ratingList and RDList have the same length
    assert ratingList and RDList and len(ratingList) == len(RDList)
    sum = 0.0
    for RD in RDList:
        g2 = g(RD) * g(RD)
        e = expectation(ratingOwn, ratingList[RDList.index(RD)], RD)
        sum += g2 * e * (1.0 - e)

    sum = q * q * sum
    result = 1.0 / sum

    return result


def newRating(RDOwn, ratingOwn, ratingList, RDList, outcomeList):
    """
    after a match this returns the new rating

    :param RDOwn: player RD
    :param ratingOwn: player rating
    :param ratingList: list of opponent's ratings
    :param RDList: list of opponents' RDs
    :param outcomeList: list of match outcomes
    :type RDOwn: float
    :type ratingOwn: float
    :type ratingList: list of floats
    :type RDList: list of floats
    :type outcomeList: list of floats
    :return: new rating
    :rtype: float
    """
    #: assert that ratingList and RDList and outcomeList have the same length
    assert ratingList and RDList and outcomeList and \
        len(ratingList) == len(RDList) and len(ratingList) == len(outcomeList)

    d2 = dSquared(ratingOwn, ratingList, RDList)

    factor = q / ((1.0 / (RDOwn ** 2.0)) + (1.0 / d2))

    sum = 0.0
    for RD in RDList:
        e = expectation(ratingOwn, ratingList[RDList.index(RD)], RD)
        sum += g(RD) * (outcomeList[RDList.index(RD)] - e)

    result = ratingOwn + (factor * sum)

    return result


def newRD(RDOwn, ratingOwn, ratingList, RDList):
    """
    after a match this returns the new RD

    :param RDOwn: player RD
    :param ratingOwn: player rating
    :param ratingList: list of opponents' ratings
    :param RDList: list of opponents' RDs
    :type RDOwn: float
    :type ratingOwn: float
    :type ratingList: list of floats
    :type RDList: list of floats
    :return: updated player RD
    :rtype: float
    """
    d2 = dSquared(ratingOwn, ratingList, RDList)
    rd2 = RDOwn * RDOwn
    result = math.sqrt(1.0 / ((1.0 / (rd2) + (1.0 / d2))))

    return result
