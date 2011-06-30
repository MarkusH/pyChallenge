import sys
import argparse
from pychallenge.algorithms import elo
from pychallenge.models import Match1on1, Player, Rank_Elo, Config
import csv

supported_games = ['chess']
supported_algorithms = {
    'chess' : ['elo', 'glicko', 'glicko2']
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
    if (not prepare_args(args)):
        return

    outcome = {
        0.0: "Player 1 won",
        1.0: "Player 2 won",
        0.5: "Draw"
    }

    print "Adding a result for", args.game
    print "\tPlayer 1:", args.player1
    print "\tPlayer 2:", args.player2
    print "\tOutcome: ", outcome[args.outcome]
    print "------------------------------"

def import_config(args):
    """
    Imports the config data of a csv file into the config table.
    
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    #Config.clear()
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
    if (not prepare_args(args)):
        return

    outcome = {
        0.0: "Player 1 won",
        1.0: "Player 2 won",
        0.5: "Draw"
    }

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
                #print "Player1: " + row[1] + "; Player2: " + row[2] + "; " + outcome[float(row[3])]

                player1 = Player.query().get(nickname=row[1])
                if player1 == None:
                    player1 = Player(firstname="", lastname="", nickname=row[1])
                    player1.save(commit=False)
                    rank1 = Rank_Elo(player_id=player1.getdata('player_id'))#, value=1500)
                    rank1.save(commit=False)

                player2 = Player.query().get(nickname=row[2])

                if player2 == None:
                    player2 = Player(firstname="", lastname="", nickname=row[2])
                    player2.save(commit=False)
                    rank2 = Rank_Elo(player_id=player2.getdata('player_id'))#, value=1500)
                    rank2.save(commit=False)

                dbRow = Match1on1(player1=player1.getdata('player_id'), player2=player2.getdata('player_id'), outcome=row[3], date=row[0])
                dbRow.save(commit=False)

            if line % 100 == 0:
                sys.stdout.write("\r" + "Imported %d entries..." % line)
                sys.stdout.flush()
                # Match1on1.commit()
            line = line + 1
        Match1on1.commit()
        print "\nImported", line - 1, "entries."
    except csv.Error, e:
        print "Error importing", args.file, "in line", line

def update(args):
    def update_elo():
        #matches = [ Match1on1(player1=1, player2=2, outcome=1, date=1), Match1on1(player1=1, player2=2, outcome=1, date=2) ]
        matches = Match1on1.query().all(date__ge=1, date__le=5)

        #rating1 = Rank_Elo(player_id=1, game_id=1, value=1500)
        #rating1.save()
        #rating2 = Rank_Elo(player_id=2, game_id=1, value=1500)
        #rating2.save()
        #Rank_Elo.commit()

        k = 25 #Config.query().get(key="elo.chess.k.fide.default").value
        for match in matches:
            # print match.__meta__['fields']
            rating1 = Rank_Elo.query().get(player_id=match.getdata('player1'))
            rating2 = Rank_Elo.query().get(player_id=match.getdata('player2'))
            func = lambda x:(1/(1+(10**(x/400.0))))
            result = elo.elo1on1(rating1.getdata('value'), rating2.getdata('value'), match.getdata('outcome'), k, func)
            print "Rating1", result[0], ", Rating2", result[1]
            rating1.value = result[0]
            rating2.value = result[1]
            rating1.save(commit=False)
            rating2.save(commit=False)
            Rank_Elo.commit()
        print "elo_update..."
    """
    Updates the ratings for all players.
    
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    if (not prepare_args(args)):
        return

    update_funcs = {
        'elo' : update_elo
    }

    print "Updating the ratings for all players in", args.game, "using", args.algorithm
    update_funcs[args.algorithm]();

def match(args):
    def match_elo():
        print "elo_match..."
    """
    Finds the best opponent for a given player.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    if (not prepare_args(args)):
        return
    
    match_funcs = {
        'elo' : match_elo
    }

    print "Finding the best opponent for the player", args.player, "in", args.game, "using", args.algorithm
    match_funcs[args.algorithm]();
    print "Best Opponent:", "...."

def rating(args):
    def rating_elo():
        print "rating_elo..."
    """
    Queries the rating of a given player.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    if (not prepare_args(args)):
        return

    rating_funcs = {
        'elo' : rating_elo
    }

    print "The rating for player", args.player, "in", args.game, "using", args.algorithm, "is", "..."
    rating_funcs[args.algorithm]()

def import_comp(args):
    pass

def compare(args):
    pass

def parse():
    parser = argparse.ArgumentParser(prog='pyChallenge')
    parser.add_argument('-g', '--game', help='The game for the following command. The default value is chess.')
    parser.add_argument('-a', '--algorithm', help='The algorithm for the following command. The default value is ELO')
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
    p_add_result.add_argument('player1', type=int, help='ID of player 1')
    p_add_result.add_argument('player2', type=int, help='ID of player 2')
    p_add_result.add_argument('outcome', type=float, help='Outcome of the game: 0 = player 1 lost; 0.5 = draw; 1 = player 1 won')
    #p_add_result.add_argument('date', help='The date of the game')
    p_add_result.set_defaults(func=add_result)

    # update
    p_update = subparsers.add_parser('update', help='Update the rating values for all players in the given game for the specified algorithm')
    p_update.set_defaults(func=update)

    # match
    p_match = subparsers.add_parser('match', help='Find the best opponent for the given player in the specified game with the selected algorithm')
    p_match.add_argument('player', type=int, help='ID of the player')
    p_match.set_defaults(func=match)
    
    # get value
    p_value = subparsers.add_parser('rating', help='Query the rating of the given player in the specified game using the selected algorithm')
    p_value.add_argument('player', type=int, help='ID of the player')
    p_value.set_defaults(func=rating)

    #import comparison file
    p_import_comp = subparsers.add_parser('import-comparison', help='Query the comparison of several players from a csv file')
    p_import_comp.add_argument('file', help='The file to import')
    p_import_comp.set_defaults(func=import_comp)

    #compare two players
    p_compare = subparsers.add_parser('compare', help='Compare two players')
    p_compare.add_argument('player1'. type=int, help='The ID of player 1')
    p_compare.add_argument('player2', type=int, help='The ID of player 2')
    p_compare.set_defaults(func=compare)

    args = parser.parse_args()
    args.func(args)
