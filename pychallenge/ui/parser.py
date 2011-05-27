import sys
from pychallenge.algorithms import elo

def default(value):
    if value:
        print "Error: ", value
        print "Command not found"
    else:
        print "Error, no command specified"

def add(value):
    print "executing add with ", value

def delete(value):
    print "executing delete with ", value

def elo1on1(value):
    elo_values = (int(value[0]), int(value[1]))
    outcome = float(value[2])
    factor = float(value[3])
    result = elo.elo1on1(elo_values[0], elo_values[1], outcome, factor, lambda x:(1/(1+(10**(x/400.0)))))
    print "Result is", result

def parse():
    # map arguments to functions
    commands = {
        'add'       : add,
        'delete'    : delete,
        'elo1on1'   : elo1on1
    }
    
    # omit first argument, i.e. the python file
    cmd_list = sys.argv[1:]
    
    if cmd_list:
        commands.get(cmd_list[0], default)(cmd_list[1:])
    else:
        default([])




