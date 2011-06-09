"""
computes Glicko-2 rating of a player

player data:
    * rating:  (initial 1500) (from Glicko)
    * RD:      level of certainty (initial 350) (Ratings Deviation) (from Glicko)
    * sigma:   player's rating volatility (initial 0.06)
    * mu:      rating
    * phi:     deviation

constants:
    * tau:    constrains volatility over time (chosen for each game - between 0.3 and 1.2)
    * precision:  desired precision
    * RDconst = 173.7178

outcome:
    * 0: player 1 lost
    * 0.5: draw
    * 1: player 1 win
"""
import math

# tau = 0.5

precision = 10

def getPrecision():
    """
    returns desired precision
    e.g. precision = 3 --> getPrecision() = 0.001

    :return: desired precision
    :rtype: float
    """
    return 10**( -1 * precision )

def glickoToGlicko2rating(rating):
    """
    converts Glicko rating to Glicko-2 mu

    :param rating: Glicko rating
    :type rating: float
    :return: Glicko-2 mu
    :rtype: float
    """
    return (rating - 1500)/173.7178

def glickoToGlicko2RD(RD):
    """
    converts Glicko RD to Glicko-2 phi

    :param RD: Glicko RD
    :type RD: float
    :return: Glicko-2 phi
    :rtype: float
    """
    return RD/173.7178

def glicko2ToGlickoMu(mu):
    """
    converts Glicko-2 mu to Glicko rating

    :param mu: Glicko-2 mu
    :type mu: float
    :return: Glicko rating
    :rtype: float
    """
    return (173.7178 * mu) + 1500

def glicko2ToGlickoPhi(phi):
    """
    converts Glicko-2 phi to Glicko RD

    :param phi: Glicko-2 phi
    :type phi: float
    :return: Glicko RD
    :rtype: float
    """
    return 173.7178 * phi

def g(phi):
    """
    Glicko-2 helper function

    :param phi: Glicko-2 phi
    :type phi: float
    :return: intermediate result
    :rtype: float
    """
    return (math.sqrt( 1 + (( 3 * ( phi**2 ))/(math.pi * math.pi))))**-1

def v(muOwn, muList, phiList):
    """
    estimated variance of player

    :param muOwn: player's mu
    :param muList: list of opponents' mu
    :param phiList: list of opponents' phi
    :type muOwn: float
    :type muList: list of floats
    :type phiList: list of floats
    :return: estimated variance of player for following matches
    :rtype: float
    """
    assert muList and phiList and len(muList) == len(phiList)
    sum = 0.0
    for phi in phiList:
        g2 = g(phi)**2
        sum += g2 * expectation(muOwn, muList[phiList.index(phi)], phi) * ( 1.0 - expectation(muOwn, muList[phiList.index(phi)], phi) )
    result = sum**-1
    return result

def delta(muOwn, muList, phiList, outcomeList):
    """
    estimated improvement

    :param muOwn: player's mu
    :param muList: list of opponents' mu
    :param phiList: list of opponents' phi
    :param outcomeList: list of match outcomes
    :type muOwn: float
    :type muList: list of floats
    :type phiList: list of floats
    :type outcomeList: list of floats (0, 0.5, 1)
    :return: estimated improvement of player for following matches
    :rtype: float
    """
    assert muList and phiList and outcomeList and len(muList) == len(phiList) and len(phiList) == len(outcomeList)
    vr = v(muOwn, muList, phiList)
    sum = 0.0
    for phi in phiList:
        sum += g(phi) * ( outcomeList[phiList.index(phi)] - expectation(muOwn, muList[phiList.index(phi)], phi) )
    return vr * sum

def expectation(muOwn, muOpponent, phiOpponent):
    """
    returns expected outcome of a match

    :param muOwn: player's mu
    :param muOpponent:  opponent's mu
    :param phiOpponent: opponent's phi
    :type muOwn: float
    :type muOpponent: float
    :type phiOpponent: float
    :return: expected outcome
    :rtype: float
    """
    result = (1.0 + math.exp(-g(phiOpponent) * (muOwn - muOpponent)))**-1
    return result

def h1(x, a, tau, d, delta):
    """
    helper function for newSigma()

    :param x: x of current iteration
    :param a: math.log(sigmaOwn**2) / x of first iteration
    :param tau: tau constant of game
    :param d: intermediate result
    :param delta: estimated improvement
    :type x: float
    :type a: float
    :type tau: float
    :type d: float
    :type delta: float
    :return: intermediate result
    :rtype: float
    """
    al = (- (x - a) / tau**2) - ((0.5 * math.exp(x)) / d)
    bl = 0.5 * math.exp(x) * (delta / d)**2
    return al + bl

def h2(tau, x, phi, v, d, delta):
    """
    helper function for newSigma()

    :param tau: tau constant of game
    :param x: x of current iteration
    :param phi: player's phi
    :param v: estimated variance
    :param d: intermediate result
    :param delta: estimated improvement
    :type tau: float
    :type x: float
    :type phi: float
    :type v: float
    :type d: float
    :type delta: float
    :return: intermediate result
    :rtype: float

    """
    al = -1 / tau**2
    bl = (0.5 * math.exp(x) * (phi**2 + v)) / d**2
    cl = phi**2 + v - math.exp(x)
    dl = (0.5 * delta**2 * math.exp(x) * cl) / d**3
    return al - bl + dl

def newSigma(muOwn, muList, phiList, outcomeList, sigmaOwn):
    """
    returns updated sigma (rating volatility)

    :param muOwn: player's mu
    :param muList: list of opponents' mu
    :param phiList: list of opponents' phi
    :param outcomeList: list of match outcomes
    :param sigmaOwn: player's sigma
    :type muOwn: float
    :type muList: list of floats
    :type phiList: list of floats
    :type outcomeList: list of floats (0, 0.5, 1)
    :type sigmaOwn: float
    :return: updated sigma
    :rtype: float
    """
    assert muList and phiList and outcomeList and len(muList) == len(phiList) and len(phiList) == len(outcomeList)
    deltar = delta(muOwn, muList, phiList, outcomeList)
    vr = v(muOwn, muList, phiList)
    a = math.log(sigmaOwn**2)
    x = a
    xi = 0.0
    # repeat until x and xi are close
    while getPrecision() >= math.fabs(x - xi):
        dr = phi**2 + vr + math.exp(x)
        h1r = h1(x, a, tau, dr, deltar)
        h2r = h2(tau, x, phiOwn, vr, dr, deltar)
        xi = x
        x = x - ( h1r / h2r )
    return math.exp( x / 2 )

def phiStar(phiOwn, sigmaOwn):
    """
    computes new rating deviation/phi for a player
    that hasn't participated in any matches during the rating period
    also helper function for newPhi()

    :param phiOwn: player's phi
    :param sigmaOwn: player's sigma
    :type phiOwn: float
    :type sigmaOwn: float
    :return: phiStar / intermediate result
    :rtype: float
    """
    ps = math.sqrt(phiOwn**2 + sigmaOwn**2)
    return ps

def newPhi(phiOwn, newSigma, variance):
    """
    computes new rating deviation/phi

    :param phiOwn: player's phi
    :param newSigma: updated sigma
    :param variance: estimated variance of player
    :type phiOwn: float
    :type newSigma: float
    :type variance: float
    :return: updated phi
    :rtype: float
    """
    ps = phiStar(phiOwn, newSigma)
    phi = math.sqrt(( 1 / ps**2 ) + ( 1 / variance ))**-1
    return phi

def newMu(muOwn, newPhi, muList, phiList, outcomeList):
    """
    computes new rating/mu

    :param muOwn: player's mu
    :param newPhi: new phi (computation of mu is dependant on phi)
    :param muList: list of opponents' mu
    :param phiList: list of opponents' phi
    :param outcomeList: list of match outcomes
    :type muOwn: float
    :type newPhi: float
    :type muList: list of floats
    :type phiList: list of floats
    :type outcomeList: list of floats (0, 0.5, 1)
    :return: updated mu
    :rtype: float
    """
    assert muList and phiList and outcomeList and len(muList) == len(phiList) and len(phiList) == len(outcomeList)
    sum = 0.0
    for phi in phiList:
        sum += (g(phi) * (outcomeList[phiList.index(phi)] - expectation(muOwn, muList[phiList.index(phi)], phi)))
    e = newPhi**2 * sum
    mu = muOwn + e
    return mu

############################################################################
# for testing purposes only                                                #
############################################################################
def testGlicko2():
    """
    test function printing out actual and expected values
    not be be used in production code
    can be refactored for unit tests

    :rtype: void
    """

    # constants
    tau = 0.5

    # match data
    ratingList = [1400, 1550, 1700]
    RDList = [30, 100, 300]
    outcomeList = [1, 0, 0]
    # added later
    phiList = []
    muList = []

    # player data
    sigmaOwn = 0.06
    ratingOwn = 1500
    RDOwn = 200

    # convert to Glicko-2
    muOwn = glickoToGlicko2rating(ratingOwn)
    print "Player rating " + str(muOwn) + " expected 0.0"
    phiOwn = glickoToGlicko2RD(RDOwn)
    print "Player RD " + str(phiOwn) + " expected 1.1513"
    print ""

    # g() function for opponents
    print "phi          | g(phi)"
    for RD in RDList:
        print str(glickoToGlicko2RD(RD)) + " | " + str(g(glickoToGlicko2RD(RD)))
        phiList.append(glickoToGlicko2RD(RD))

    print ""

    for rating in ratingList:
        muList.append(glickoToGlicko2rating(rating))

    # expectation function
    print "expectation"
    print "mu muj phij | E(mu, muj, phij)"
    for phi in phiList:
        e = expectation(muOwn, muList[phiList.index(phi)], phi)
        print str(muOwn) + " " + str(muList[phiList.index(phi)]) + " " + str(phi) +  " | " + str(e)

    print ""

    # variance
    print "variance v"
    print "expected 1.7785"
    variance = v(muOwn, muList, phiList)
    print str(variance)

    print ""

    # delta
    print "delta"
    print "expected -0.4834"
    print str(delta(muOwn, muList, phiList, outcomeList))

    print ""

    # new sigma
    print "sigma"
    print "expected 0.05999"
    nsigma = newSigma(muOwn, muList, phiList, outcomeList, sigmaOwn)
    print str(nsigma)

    print ""

    # phi*
    print "phi*"
    print "expected 1.152862"
    ps = phiStar(phiOwn, sigmaOwn)
    print str(ps)

    print ""

    # new phi
    print "new phi"
    print "expected 0.8722"
    nphi = newPhi(phiOwn, nsigma, variance)
    print str(nphi)

    print ""

    # new mu
    print "new mu"
    print "expected -0.2069"
    nmu = newMu(muOwn, nphi, muList, phiList, outcomeList)
    print str(nmu)

    print ""

    # new rating
    print "new rating"
    print "expected 1464.06"
    print str(glicko2ToGlickoMu(nmu))

    print ""

    # new RD
    print "new RD"
    print "expected 151.52"
    print str(glicko2ToGlickoPhi(nphi))

    print ""

############################################################################
# for testing purposes only END                                            #
############################################################################
