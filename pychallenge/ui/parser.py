import sys
from pychallenge.algorithms import elo


def add(value):
    print "executing add with ", value

def delete(value):
    print "executing delete with ", value

def elo1on1(value):
    if len(value) is 4:
        elo_values = (int(value[0]), int(value[1]))
        outcome = float(value[2])
        factor = float(value[3])
        result = elo.elo1on1(elo_values[0], elo_values[1], outcome, factor, lambda x:(1/(1+(10**(x/400.0)))))
        print "Result is", result
    else:
        print "Usage:   elo1on1 elo1 elo2 factor"
        print "elo1:    elo value of player 1"
        print "elo2:    elo value of player 2"
        print "outcome: 0 = player 1 lost;  0.5 = draw; 1 = player 1 won"
        print "factor:  k factor (usually depends on players initial Elo rating and game)"
        #:param function: Elo function e.g. chess lambda x:(1/(1+(10**(x/400.0))))


# map arguments to functions
commands = {
    'add'       : add,
    'delete'    : delete,
    'elo1on1'   : elo1on1
}

def default(value):
    if value:
        print "Error: ", value
        print "Command not found"
    else:
        print "Error, no command specified"
        print ""
        print commands.keys()


def parse():
    # omit first argument, i.e. the python file
    cmd_list = sys.argv[1:]
    
    if cmd_list:
        commands.get(cmd_list[0], default)(cmd_list[1:])
    else:
        default([])




