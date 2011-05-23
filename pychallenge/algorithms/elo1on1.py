# computes elo for two players
#
# elo1      : initial Elo rating of player 1
# elo2      : initial Elo rating of player 2
# outcome   : outcome of the match (0 -> player 1 lost; 0.5 -> draw; 1 -> player 1 won)
# k         : k factor (usually depends on players initial Elo rating and game)
# function  : Elo function e.g. chess lambda x:(1/(1+(10**(x/400.0))))

def elo1on1(elo1, elo2, outcome, k, function):

    eloDiff = elo2 - elo1

    expected = function(eloDiff)

    newelo1 = elo1 + k*(outcome - expected)

    newelo1 = round(newelo1)
    newelo2 = elo2 - (newelo1 - elo1)

    result = newelo1, newelo2

    return result
