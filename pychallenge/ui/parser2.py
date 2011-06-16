import sys
import argparse
from pychallenge.algorithms import elo
from pychallenge.models import Match1on1, Player, RankElo
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
        for row in reader:
            if line != 0 or (line == 0 and not hasHeader):
                #print "Player1: " + row[1] + "; Player2: " + row[2] + "; " + outcome[float(row[3])]
                dbRow = Match1on1(player1=row[1], player2=row[2], outcome=row[3])
                dbRow.save(commit=False)
                player = Player.get(nickname=row[1])
                if player == None:
                    player = Player(player_id=row[1], firstname="", lastname="", nickname=row[1])
                    print player.__dict__['__meta__']['fields']['player_id'].value
                    player.save(commit=False)
                    print "player_pk =", player.player_id.value
                    rank = RankElo(player_id=player.player_id, game_id=0, value=1500)
                player = Player.get(nickname=row[2])
                if player == None:
                    player = Player(player_id=row[1], firstname="", lastname="", nickname=row[2])
                    player.save(commit=False)
                    print "player_id =", player.player_id
                    rand = RankElo(player_id=player.player_id, game_id=0, value=1500)
            line = line + 1
        Match1on1.commit()
        print "Imported", line - 1, "entries."
    except csv.Error, e:
        print "Error importing", args.file, "in line", line

def update(args):
    def update_elo():
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

def parse():
    parser = argparse.ArgumentParser(prog='pyChallenge')
    parser.add_argument('-g', '--game', help='The game for the following command. The default value is chess.')
    parser.add_argument('-a', '--algorithm', help='The algorithm for the following command. The default value is ELO')
    subparsers = parser.add_subparsers(help='sub-command help')

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


    args = parser.parse_args()
    args.func(args)
