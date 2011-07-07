import sys
import argparse
import pychallenge
from pychallenge.algorithms import elo
from pychallenge.models import Match1on1, Player, Rank_Elo, Config
from pychallenge.ui import utils
import csv

supported_games = ['chess']
supported_algorithms = {
    'chess' : ['elo', 'glicko', 'glicko2']
}

outcomes = {
    0.0: "Player 1 lost",
    1.0: "Player 1 won",
    0.5: "Draw"
}

def prepare_args(args):
    """
    Prepares the arguments and checks if they  are valid. If not, prints an
    error message. If some arguments are optional and were not set by the
    user, it inserts the default values.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    :return: True, if the arguments are valid, False otherwise
    :rtype: bool
    """
    if (args.game == None):
        args.game = "chess"
    elif (not args.game in ['chess']):
        print "Error:", args.game, "is not a valid game! Choose from", supported_games
        return False

    if (args.algorithm == None):
        args.algorithm = "elo"
    elif (not args.algorithm in supported_algorithms[args.game]):
        print "Error:", args.algorithm, "is not a valid algorithm for", args.game + "! Choose from", supported_algorithms[args.game]
        return False
    return True

#####################################################################
#                               sub commands                        #
#####################################################################

def add_result(args):
    """
    Adds a result row to the result table.
    
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    print "Adding a result for %s" % args.game
    print "\tPlayer 1:", args.player1
    print "\tPlayer 2:", args.player2
    print "\tOutcome: ", outcomes[args.outcome]
    print "\tDate: ", args.date

    player1 = utils.add_player(args.player1, commit=False)
    player2 = utils.add_player(args.player2, commit=False)

    pid1 = player1.getdata('player_id')
    pid2 = player2.getdata('player_id')

    dbRow = Match1on1(player1=pid1, player2=pid2, outcome=args.outcome, date=args.date)
    dbRow.save(commit=True)

    print "Player id for %s is %s" % (args.player1, pid1)
    print "Player id for %s is %s" % (args.player2, pid2)
    print "Done"

def import_config(args):
    """
    Imports the config data of a csv file into the config table.
    
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    Config.query().truncate()
    print "Importing config from", args.file

    try:
        line = 0
        csvfile = open(args.file, 'rb')
        sample = csvfile.read(1024)
        csvfile.seek(0)
        hasHeader = csv.Sniffer().has_header(sample)
        reader = csv.reader(csvfile, delimiter=',')
        for row in reader:
            if line != 0 or (line == 0 and not hasHeader):
                entry = Config(key=row[0], value=row[1])
                entry.save(commit=False)

            line = line + 1
        Config.commit()
        print "\nImported", line - 1, "config entries."
    except csv.Error, e:
        print "Error importing", args.file, "in line", line

def import_results(args):
    """
    Imports the match data of a csv file into the result table.
    
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    print "Importing results from", args.file

    try:
        line = 0
        csvfile = open(args.file, 'rb')
        sample = csvfile.read(1024)
        csvfile.seek(0)
        hasHeader = csv.Sniffer().has_header(sample)
        reader = csv.reader(csvfile, delimiter=',')
        nicknames = []
        for row in reader:
            if line != 0 or (line == 0 and not hasHeader):
                player1 = utils.add_player(row[1], commit=False)
                player2 = utils.add_player(row[2], commit=False)

                dbRow = Match1on1(player1=player1.getdata('player_id'), player2=player2.getdata('player_id'), outcome=row[3], date=row[0])
                dbRow.save(commit=False)

            if line % 100 == 0:
                sys.stdout.write("\r" + "Imported %d entries..." % line)
                sys.stdout.flush()
                # Match1on1.commit()
            line = line + 1
        Match1on1.commit()
        print "\rImported", line - 1, "entries."
    except csv.Error, e:
        print "Error importing", args.file, "in line", line

def update(args):
    def update_elo():
        sys.stdout.write("Query matches...")
        matches = Match1on1.query().all(date__ge=1, date__le=1)
        sys.stdout.write("\rBeginning to update %d matches" % len(matches))
        print ""


        func = eval(Config.query().get(key="elo.chess.function").getdata("value"))
        if func is None:
            func = lambda x:(1/(1+(10**(x/400.0))))
        k = float(Config.query().get(key="elo.chess.k.fide.default").getdata("value"))
        if k is None:
            k = 25
        updates = 0
        for match in matches:
            rating1 = Rank_Elo.query().get(player_id=match.getdata('player1'))
            rating2 = Rank_Elo.query().get(player_id=match.getdata('player2'))
            
            result = elo.elo1on1(rating1.getdata('value'), rating2.getdata('value'), match.getdata('outcome'), k, func)
            rating1.value = result[0]
            rating2.value = result[1]
            rating1.save(commit=False)
            rating2.save(commit=False)
            Rank_Elo.commit()
            updates = updates + 1
            if updates % 50 == 0:
                sys.stdout.write("\r" + "Updated %d matches..." % updates)
                sys.stdout.flush()
        print "\rUpdated", updates, "matches."
    """
    Updates the ratings for all players.
    
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    update_funcs = {
        'elo' : update_elo
    }

    print "Updating the ratings for all players in", args.game, "using", args.algorithm
    update_funcs[args.algorithm]();

def match(args):
    def match_elo(rating):
        ratings = Rank_Elo.query().all()
        best = None
        deviation = 99999999
        for r in ratings:
            if (best is None or abs(r.getdata("value") - rating.getdata("value")) < deviation) and r.getdata("player_id") != rating.getdata("player_id"):
                best = r
                deviation = abs(r.getdata("value") - rating.getdata("value"))
        return best

    """
    Finds the best opponent for a given player.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    
    match_funcs = {
        'elo' : match_elo
    }

    rating = utils.get_rating(args)
    if rating is None:
        print "Player %s is not known." % args.player
        return

    print "Looking for the best opponent for player %s..." % args.player 

    opponent = match_funcs[args.algorithm](rating);

    if opponent is None:
        print "No opponent found."
        return

    print "Best opponent for player %s with rating %d is:" % (args.player, rating.getdata("value"))
    other = Player.query().get(player_id=opponent.getdata("player_id"))
    print "\tPlayer %s with rating %d." % (other.getdata("nickname"), opponent.getdata("value"))

def rating(args):
    """
    Queries the rating of a given player.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    player = utils.get_rating(args)

    if player is None:
        print "The rating for player %s in %s using %s is not known." % (args.player, args.game, args.algorithm)
    else:
        print "The rating for player %s in %s using %s is %d." % (args.player, args.game, args.algorithm, player.getdata("value"))
    

def import_comp(args):
    pass

def compare(args):
    """
    Compares the rating of two given players.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    if args.player1 is args.player2:
        print "You cannot compare player %s with himself" % args.player1
        return

    print "Comparing the rating of two players in %s with %s:" % (args.game, args.algorithm)

    ratings = utils.get_rating(args);
    if ratings is None:
        print "Both players are not known!"
        return

    if (ratings[0] == None):
        print "Player with nickname %s not known." % args.player1
        return
    if (ratings[1] == None):
        print "Player with nickname %s not known." % args.player2
        return

    value1 = ratings[0].getdata('value')
    value2 = ratings[1].getdata('value')
    if value1 != value2:
        winning_player = args.player1 if value1 > value2 else args.player2
        print "\tPlayer %s will (probably) win." % winning_player
        print "\tRank player %s: %d" % (args.player1, value1)
        print "\tRank player %s: %d" % (args.player2, value2)
        print "\tPlayer %s is %d points better." % (winning_player, abs(value1 - value2))
    else:
        print "Both players have the same elo rank (%d)" % value1

def create_player(args):
    """
    Creates a new player (as specified in args)
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    player, created = utils.add_player(args.nickname, args.firstname, args.lastname, True)
    if created is True:
        print "The player is now known in the database:"
        print "ID: %d;\tfirst name: %s;\tlast name: %s;\tnickname: %s" % (player.getdata('player_id'),
            args.firstname, args.lastname, args.nickname)
    else:
        print "The player with nickname %s already exists." % args.nickname

def best(args):
    def best_elo():
        ranks = Rank_Elo.query().all()
        ranks.sort()
        ranks = sorted(ranks, key=lambda x: x.getdata("value"), reverse=True)
        print "Rank\tRating\tNick\tFirst\tName"
        for i in range(min(args.amount, len(ranks))):
            player = Player().query().get(player_id=ranks[i].getdata("player_id"))
            print "%d\t%d\t%s\t%s,\t%s" % (i+1, ranks[i].getdata("value"), player.getdata("nickname"), player.getdata("firstname"), player.getdata("lastname"))

  
    best_funcs = {
        'elo' : best_elo
    }

    print "The Top %d players in %s with %s:" % (args.amount, args.game, args.algorithm)
    best_funcs[args.algorithm]()

def worst(args):
    def worst_elo():
        ranks = Rank_Elo.query().all()
        ranks.sort()
        ranks = sorted(ranks, key=lambda x: x.getdata("value"))
        print "Rank\tRating\tNick\tFirst\tName"
        for i in range(min(args.amount, len(ranks))):
            player = Player().query().get(player_id=ranks[i].getdata("player_id"))
            print "%d\t%d\t%s\t%s,\t%s" % (i+1, ranks[i].getdata("value"), player.getdata("nickname"), player.getdata("firstname"), player.getdata("lastname"))

  
    worst_funcs = {
        'elo' : worst_elo
    }

    print "The Worst %d players in %s with %s:" % (args.amount, args.game, args.algorithm)
    worst_funcs[args.algorithm]()

def parse():
    parser = argparse.ArgumentParser(prog='pyChallenge')
    parser.add_argument('-g', '--game', help='The game for the following command. The default value is chess.')
    parser.add_argument('-a', '--algorithm', help='The algorithm for the following command. The default value is ELO')
    parser.add_argument('-v', '--version', action='version',
        version="%s version: %s" % ("%(prog)s", pychallenge.get_version()), help='Prints out the version information of pyChallenge')
    subparsers = parser.add_subparsers(help='sub-command help')

    # import config
    p_config = subparsers.add_parser('import-config', help='Update the config with a given config file')
    p_config.add_argument('file', help='The config to import')
    p_config.set_defaults(func=import_config)

    # import results
    p_import = subparsers.add_parser('import-results', help='Import data to the result table from a csv file')
    p_import.add_argument('file', help='The file to import')
    p_import.set_defaults(func=import_results)
 
    # add result
    p_add_result = subparsers.add_parser('add-result', help='Add a result to the table specified by the --game option')
    p_add_result.add_argument('player1', help='Nickname of player 1')
    p_add_result.add_argument('player2', help='Nickname of player 2')
    p_add_result.add_argument('outcome', type=float, help='Outcome of the game: 0 = player 1 lost; 0.5 = draw; 1 = player 1 won')
    p_add_result.add_argument('date', type=int, help='The date of the game')
    p_add_result.set_defaults(func=add_result)

    # update
    p_update = subparsers.add_parser('update', help='Update the rating values for all players in the given game for the specified algorithm')
    p_update.set_defaults(func=update)

    # match
    p_match = subparsers.add_parser('match', help='Find the best opponent for the given player in the specified game with the selected algorithm')
    p_match.add_argument('player', help='Nickname of the player')
    p_match.set_defaults(func=match)
    
    # get value
    p_value = subparsers.add_parser('rating', help='Query the rating of the given player in the specified game using the selected algorithm')
    p_value.add_argument('player', help='Nickname of the player')
    p_value.set_defaults(func=rating)

    # best
    p_best = subparsers.add_parser('best', help='Query the best player(s) in the given game and algorithm')
    p_best.add_argument('amount', type=int, default=1, help='The number of player to query. 10 for Top 10')
    p_best.set_defaults(func=best)

    # worst
    p_worst = subparsers.add_parser('worst', help='Query the worst player(s) in the given game and algorithm')
    p_worst.add_argument('amount', type=int, default=1, help='The number of player to query. 10 for Worst 10')
    p_worst.set_defaults(func=best)

    # import comparison file
    p_import_comp = subparsers.add_parser('import-comparison', help='Query the comparison of several players from a csv file')
    p_import_comp.add_argument('file', help='The file to import')
    p_import_comp.set_defaults(func=import_comp)

    # compare two players
    p_compare = subparsers.add_parser('compare', help='Compare two players')
    p_compare.add_argument('player1', help='Nickname of player 1')
    p_compare.add_argument('player2', help='Nickname of player 2')
    p_compare.set_defaults(func=compare)

    # create new player
    p_create_player = subparsers.add_parser('create-player', help='Creates a new player in the database.')
    p_create_player.add_argument('nickname', help='Nickname for the new player')
    p_create_player.add_argument('firstname', type=unicode, help='First name of the new player')
    p_create_player.add_argument('lastname', type=unicode, help='Last name of the new player')
    p_create_player.set_defaults(func=create_player) 

    args = parser.parse_args()
    if (not prepare_args(args)):
        return
    print ""
    args.func(args)
    print ""
