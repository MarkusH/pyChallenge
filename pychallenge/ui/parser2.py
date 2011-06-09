import sys
import argparse
from pychallenge.algorithms import elo
import csv

#####################################################################
#                           ELO sub commands                        #
#####################################################################
def elo_prepare_args(args):
    if (args.game == None):
        args.game = "chess"
    elif (not args.game in ['chess']):
        print "Error:", args.game, "is not a valid game for ELO"
        return False
    return True 
        

def elo_add_result(args):
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

def elo_import(args):
    if (not elo_prepare_args(args)):
        return

    outcome = {
        0.0: "Player 1 won",
        1.0: "Player 2 won",
        0.5: "Draw"
    }

    print "Importing results to ELO", args.game
    print "\tFile:", args.file

    try:
        line = 0
        reader = csv.reader(open(args.file, 'rb'), delimiter=',')
        print "Importing the following data:"
        for row in reader:
            if line != 0:
                print "Player1: " + row[1] + "; Player2: " + row[2] + "; " + outcome[float(row[3])]
            line = line + 1
    except:
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
    subparsers = parser.add_subparsers(help='sub-command help')
    
    # ELO sub-commands
    p_elo = subparsers.add_parser('elo', help='Commands for the ELO algorithm')
    p_elo.add_argument('--game', help='Choose a game for ELO')
    p_elo_sub = p_elo.add_subparsers(help='sub-command help for ELO')
   

    # ELO add result
    p_elo_add_result = p_elo_sub.add_parser('addresult', help='Add a result to the ELO table')
    p_elo_add_result.add_argument('player1', type=int, help='ID of player 1')
    p_elo_add_result.add_argument('player2', type=int, help='ID of player 2')
    p_elo_add_result.add_argument('outcome', type=float, help='Outcome of the game: 0 = player 1 lost; 0.5 = draw; 1 = player 1 won')
    p_elo_add_result.set_defaults(func=elo_add_result)

    # ELO import
    p_elo_import = p_elo_sub.add_parser('import', help='Import data to the ELO table')
    p_elo_import.add_argument('file', help='The file to import')
    p_elo_import.set_defaults(func=elo_import)    

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
