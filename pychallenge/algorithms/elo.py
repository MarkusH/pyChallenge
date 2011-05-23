def elo1on1(elo1, elo2, outcome, k, function):
    """
    computes elo for two players

    :param elo1: elo value for player 1
    :param elo2: elo value for player 2
    :param outcome: defines the result of the match:

        * 0: player 1 lost
        * 0.5: draw
        * 1: player 1 win
    :param k: k factor (usually depends on players initial Elo rating and game)
    :param function: Elo function e.g. chess lambda x:(1/(1+(10**(x/400.0))))
    :type elo1: Integer
    :type elo2: Integer
    :type outcome: 0, 0.5, 1
    :type k: Float
    :type function: function
    """
    eloDiff = elo2 - elo1

    expected = function(eloDiff)

    newelo1 = elo1 + k*(outcome - expected)

    newelo1 = round(newelo1)
    newelo2 = elo2 - (newelo1 - elo1)

    result = newelo1, newelo2

    return result
