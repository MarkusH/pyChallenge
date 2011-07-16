# -*- coding: utf-8 -*-
from pychallenge.models import Player, Rank_Elo, Rank_Glicko, Config
import csv


def get_rating(args, p1=None, p2=None):
    def rating_elo(player):
        if player is None:
            return None
        return Rank_Elo.query().get(player_id=player.player_id.value)

    def rating_glicko(player):
        if player is None:
            return None
        return Rank_Glicko.query().get(player_id=player.player_id.value)

    def rating_glicko2():
        return None

    """
    Queries the rating of a given player or two given players. Returns one
    rank table, if "args.player" is defined. Returns a tupel of two rank
    tables, if "args.player1" and "args.player2" is defined.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    :param p1: The nickname of a player
    :param p2: The nickname of another player
    :return: The rank for the given player(s) (either in args or in p1/p2)
    """

    rating_funcs = {
        'elo': rating_elo,
        'glicko': rating_glicko,
        'glicko2': rating_glicko2}

    if p1 is not None and p2 is not None:
        player1 = Player.query().get(nickname=p1)
        player2 = Player.query().get(nickname=p2)
        return (rating_funcs[args.algorithm](player1),
            rating_funcs[args.algorithm](player2))
    elif args.__dict__.get("player", None):
        player = Player.query().get(nickname=args.player)
        if player is None:
            return None
        return rating_funcs[args.algorithm](player)
    elif args.__dict__.get("player1", None) and args.__dict__.get("player2",
                                                                  None):
        player1 = Player.query().get(nickname=args.player1)
        player2 = Player.query().get(nickname=args.player2)
        return (rating_funcs[args.algorithm](player1),
            rating_funcs[args.algorithm](player2))

    return None


def add_player(nickname, firstname="", lastname="", commit=False):
    """
    Adds a player and the corresponding ranks to the database. If the player
    already exsits, this function does nothing.

    :param nickname: The nickname of the player to add
    :type nickname: string
    :param firstname: The first name of the player to add
    :type firstname: string
    :param lastname: The last name of the player to add
    :type lastname: string
    :param commit: True if the rows should be committed
    :type commit: bool
    :return: Tupel (the player model, False if player already existed)
    """
    player = Player.query().get(nickname=nickname)
    created = False
    if player == None:
        created = True
        player = Player(firstname=firstname, lastname=lastname,
            nickname=nickname)
        player.save(commit)
        rank = Rank_Elo(player_id=player.player_id.value)
        rank.save(commit)
        rank = Rank_Glicko(player_id=player.player_id.value)
        rank.save(commit)

    return player, created


#TODO: make this dependend on algorithm (and game)?
def get_config(args):
    """
    Returns a dictionary of config values
    """

    dict = {}

    # ELO
    func = Config.query().get(key="elo.chess.function")
    if func is None:
        func = lambda x: (1 / (1 + (10 ** (x / 400.0))))
    else:
        func = eval(func.value.value)
    dict["elo.chess.function"] = func

    k = Config.query().get(key="elo.chess.k.fide.default")
    if k is None:
        k = 25
    else:
        k = float(k.value.value)
    dict["elo.chess.k"] = k

    return dict


def print_table(table):
    def get_max_width(table, index):
        """Get the maximum width of the given column index"""

        return max([len(str(row[index])) for row in table])

    """
    Prints the given table to stdout. Automatically aligns the columns.
    """
    col_paddings = []

    for i in range(len(table[0])):
        col_paddings.append(get_max_width(table, i))

    for row in table:
        print row[0].ljust(col_paddings[0] + 1),
        for i in range(1, len(row)):
            col = str(row[i]).rjust(col_paddings[i] + 2)
            print col,
        print ""


def get_csv(filename):
    """
    Opens a csv file and returns the file, the reader and, if it has a header
    :param filename: the file name of the csv file
    :type filename: String
    :return: Tupel (file, reader, boolean hasHeader)
    """
    csvfile = open(filename, 'rb')
    sample = csvfile.read(1024)
    csvfile.seek(0)
    return (csvfile, csv.reader(csvfile, delimiter=','),
        csv.Sniffer().has_header(sample))
