import sys
from pychallenge.models import Match1on1, Player, Rank_Elo, Config

def get_rating(args):
    def rating_elo():
        return Rank_Elo.query().get(player_id=args.player)
    def rating_glicko():
        return None
    def rating_glicko2():
        return None

    """
    Queries the rating of a given player.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    :return: The player for the given player id (in args)
    """

    rating_funcs = {
        'elo' : rating_elo,
        'glicko' : rating_glicko,
        'glicko2' : rating_glicko2
    }

    return rating_funcs[args.algorithm]()
