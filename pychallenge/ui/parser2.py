import sys
import argparse
from pychallenge.algorithms import elo
from pychallenge.models import Match1on1
import csv

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
    return True

#####################################################################
#                           ELO sub commands                        #
#####################################################################

def elo_prepare_args(args):
    """
    Prepares the arguments for the ELO algorithm and calls the generic prepare
    function. It also checks if the arguments are valid and, if not, prints an
    error message. If some arguments are optional and were not set by the user,
    it inserts the default values.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    :return: True, if the arguments are valid, False otherwise
    :rtype: bool
    """
    if (not prepare_args(args)):
        return False

    if (args.game == None):
        args.game = "chess"
    elif (not args.game in ['chess']):
        print "Error:", args.game, "is not a valid game for ELO"
        return False
    return True 
        

def elo_add_result(args):
    """
    Adds a result row to the result table.
    
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    if (not elo_prepare_args(args)):
        return
    outcome = {
        0.0: "Player 1 won",
        1.0: "Player 2 won",
        0.5: "Draw"
    }
    print "Adding a result for ELO in", args.game
    print "\tPlayer 1:", args.player1
    print "\tPlayer 2:", args.player2
    print "\tOutcome: ", outcome[args.outcome]
    print "------------------------------"

def import_results(args):
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
        reader = csv.reader(open(args.file, 'rb'), delimiter=',')
        for row in reader:
            if line != 0:
                #print "Player1: " + row[1] + "; Player2: " + row[2] + "; " + outcome[float(row[3])]
                dbRow = Match1on1(player1=row[1], player2=row[2], outcome=row[3])
                dbRow.save(commit=False)
            line = line + 1
        Match1on1.commit()
        print "Imported", line - 1, "entries."
    except csv.Error, e:
        print "Error importing", args.file, "in line", line

def elo_update(args):
    if (not elo_prepare_args(args)):
        return    
    print "Updating the ELO values for all players in", args.game

def elo_match(args):
    if (not elo_prepare_args(args)):
        return
    print "Finding a match for the player in", args.game
    print "Given player: ", args.player
    print "Best Opponent:", "...."

def elo_value(args):
    if (not elo_prepare_args(args)):
        return
    print "The ELO value for player", args.player, "is ...."

def parse():
    parser = argparse.ArgumentParser(prog='pyChallenge')
    parser.add_argument('--game', help='Specify a game for the following command. The default value is chess.')
    subparsers = parser.add_subparsers(help='sub-command help')

    p_import = subparsers.add_parser('import-results', help='Import data to the result table')
    p_import.add_argument('file', help='The file to import')
    p_import.set_defaults(func=import_results)
 
    # ELO sub-commands
    p_elo = subparsers.add_parser('elo', help='Commands for the ELO algorithm')
    p_elo_sub = p_elo.add_subparsers(help='sub-command help for ELO')

    # ELO add result
    p_elo_add_result = p_elo_sub.add_parser('add-result', help='Add a result to the ELO table')
    p_elo_add_result.add_argument('player1', type=int, help='ID of player 1')
    p_elo_add_result.add_argument('player2', type=int, help='ID of player 2')
    p_elo_add_result.add_argument('outcome', type=float, help='Outcome of the game: 0 = player 1 lost; 0.5 = draw; 1 = player 1 won')
    p_elo_add_result.set_defaults(func=elo_add_result)

    # ELO update
    p_elo_update = p_elo_sub.add_parser('update', help='Update the ELO values for all players')
    p_elo_update.set_defaults(func=elo_update)

    # ELO match
    p_elo_match = p_elo_sub.add_parser('match', help='Find a match for the given player')
    p_elo_match.add_argument('player', type=int, help='ID of the player')
    p_elo_match.set_defaults(func=elo_match)
    
    # ELO get value
    p_elo_value = p_elo_sub.add_parser('value', help='Query the ELO value of the given player')
    p_elo_value.add_argument('player', type=int, help='ID of the player')
    p_elo_value.set_defaults(func=elo_value)


    args = parser.parse_args()
    args.func(args)
