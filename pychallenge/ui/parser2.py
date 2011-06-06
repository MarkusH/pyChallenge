import sys
import argparse
from pychallenge.algorithms import elo

def elo1on1(args):
    outcome = {
        0.0: "Player 1 won",
        1.0: "Player 2 won",
        0.5: "Draw"
    }
    print "Performing ELO 1on1 with:"
    print "\tRating of player 1:", args.elo1
    print "\tRating of player 2:", args.elo2
    print "\tOutcome:           ", outcome[args.outcome] 
    print "-----------------------------"

    result = elo.elo1on1(args.elo1, args.elo2, args.outcome, args.factor, lambda x: (1 / (1 + (10 ** (x / 400.0)))))


def parse():
    parser = argparse.ArgumentParser(prog='pyChallenge')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_elo1on1 = subparsers.add_parser('elo1on1', help='Calculare 1on1 match with ELO')
    parser_elo1on1.add_argument('elo1', type=int, help='ELO rating of player 1')
    parser_elo1on1.add_argument('elo2', type=int, help='ELO rating of player 2')
    parser_elo1on1.add_argument('outcome', type=float, help="Outcome of the game: 0 = player 1 lost; 0.5 = draw; 1 = player 1 won")
    parser_elo1on1.set_defaults(func=elo1on1)


    args = parser.parse_args()
    args.func(args)
