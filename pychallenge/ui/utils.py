import sys
from pychallenge.models import Match1on1, Player, Rank_Elo, Config

def get_rating(args):
    def rating_elo(player):
        return Rank_Elo.query().get(player_id=player)
    def rating_glicko():
        return None
    def rating_glicko2():
        return None

    """
    Queries the rating of a given player or two given players. Returns one
    rank table, if "args.player" is defined. Returns a tupel of two rank tables,
    if "args.player1" and "args.player2" is defined.
 
    :param args: A list with arguments from the argument parser
    :type args: namespace
    :return: The player for the given player id (in args)
    """

    rating_funcs = {
        'elo' : rating_elo,
        'glicko' : rating_glicko,
        'glicko2' : rating_glicko2
    }

    if args.__dict__.get("player", None):
        return rating_funcs[args.algorithm](args.player)
    elif args.__dict__.get("player1", None) and args.__dict__.get("player2", None):
        return (rating_funcs[args.algorithm](args.player1), rating_funcs[args.algorithm](args.player2))

    return rating_funcs[args.algorithm]()

def add_player(nickname, commit=False):
    """
    Adds a player and the corresponding ranks to the database. If the player
    already exsits, this function does nothing.
    :param nickname: The nickname of the player to add
    :type player: int
    :return: The player model
    """
    player = Player.query().get(nickname=nickname)
    if player == None:
        player = Player(firstname="", lastname="", nickname=nickname)
        player.save(commit)
        rank = Rank_Elo(player_id=player.getdata('player_id'))
        rank.save(commit)
    return player
