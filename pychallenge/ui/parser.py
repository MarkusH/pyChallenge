# -*- coding: utf-8 -*-
import sys
import argparse
import pychallenge
from pychallenge.algorithms import elo, glicko
from pychallenge.models import Match1on1, Player, Rank_Elo, Rank_Glicko, Config
from pychallenge.ui import utils
import csv
import os
import math


def add_result(args):
    """
    Adds a result row to the result table.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    if args.player1 is args.player2:
        print "A player can not play against himself."
        return
    print "Adding a result for %s" % args.game
    print "\tPlayer 1:", args.player1
    print "\tPlayer 2:", args.player2
    print "\tOutcome: ", utils.outcomes[args.outcome]
    print "\tDate: ", args.date

    player1 = utils.add_player(args.player1, commit=False)
    player2 = utils.add_player(args.player2, commit=False)

    pid1 = player1.player_id.value
    pid2 = player2.player_id.value

    dbRow = Match1on1(player1=pid1, player2=pid2, outcome=args.outcome,
        date=args.date)
    dbRow.save(commit=True)

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
        csvfile, reader, hasHeader = utils.get_csv(args.file)
        line = 0

        for row in reader:
            if line != 0 or (line == 0 and not hasHeader):
                entry = Config(key=row[0], value=row[1])
                entry.save(commit=False)

            line = line + 1
        Config.commit()
        csvfile.close()
        print "Imported", line - 1, "config entries."
    except csv.Error:
        print "Error importing %s in line %d" % (args.file, line)
    except IOError:
        print "No such file: %s" % args.file


def import_results(args):
    """
    Imports the match data of a csv file into the result table.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    print "Importing results from", args.file

    try:
        csvfile, reader, hasHeader = utils.get_csv(args.file)
        line = 0

        if hasHeader:
            print "\tFirst line of csv file is ignored. It seems to be a " \
                  "header row.\n"

        # nickname --> player
        players = {}

        for row in reader:
            if line != 0 or (line == 0 and not hasHeader):
                if row[1] is row[2]:
                    continue

                player1 = players.get(row[1], None)
                player2 = players.get(row[2], None)
                if player1 is None:
                    player1, created = utils.add_player(row[1], commit=False)
                    players[player1.nickname.value] = player1
                if player2 is None:
                    player2, created = utils.add_player(row[2], commit=False)
                    players[player2.nickname.value] = player2

                dbRow = Match1on1(player1=player1.player_id.value,
                    player2=player2.player_id.value, outcome=row[3],
                    date=row[0])
                dbRow.save(commit=False)

            if line % 100 == 0:
                sys.stdout.write("\r" + "Imported %d entries..." % line)
                sys.stdout.flush()
            line = line + 1

        Rank_Elo.commit()
        Rank_Glicko.commit()
        Match1on1.commit()
        csvfile.close()
        print "\rImported %d entries." % (line - (1 if hasHeader else 0))
    except csv.Error:
        print "Error importing %s in line %d" % (args.file, line)
    except IOError:
        print "No such file: %s" % args.file


def update(args):
    def update_elo():
        sys.stdout.write("Query matches...")
        matches = Match1on1.query().all()
        sys.stdout.write("\rBeginning to update %d matches" % len(matches))
        print ""

        # constants
        conf = utils.get_config(args)
        k = conf["elo.chess.k"]
        func = conf["elo.chess.function"]

        # Query all ratings and store it in a dictionary. This is done to store
        # the newest rating data in memory. We do not have to commit.
        ratings = Rank_Elo.query().all()
        rdict = {}
        for r in ratings:
            rdict[r.player_id.value] = r

        updates = 0
        for match in matches:
            rating1 = rdict[match.player1.value]
            rating2 = rdict[match.player2.value]

            result = elo.elo1on1(rating1.value.value, rating2.value.value,
                match.outcome.value, k, func)
            rating1.value = result[0]
            rating2.value = result[1]

            updates = updates + 1
            if updates % 50 == 0:
                sys.stdout.write("\r" + "Updated %d matches..." % updates)
                sys.stdout.flush()

        # update table
        for r in ratings:
            r.save(commit=False)
        Rank_Elo.commit()
        print "\rUpdated", updates, "matches."

    def update_glicko():
        sys.stdout.write("Query matches...")
        matches = Match1on1.query().all()
        sys.stdout.write("\rBeginning to update %d matches" % len(matches))
        print ""

        # Query all ratings and store it in a dictionary. This is done to store
        # the newest rating data in memory. We do not have to commit.
        ratings = Rank_Glicko.query().all()
        rdict = {}
        for r in ratings:
            rdict[r.player_id.value] = r

        # sort matches by date
        matches = sorted(matches, key=lambda x: x.date.value)
        mDict = {}

        for match in matches:
            if match.date.value in mDict:
                mDict[match.date.value].append(match)
            else:
                mDict[match.date.value] = [match]

        # for each rating period...
        for period, pMatches in mDict.iteritems():
            # players in current period --> (RD, rating)
            pDict = {}
            for match in pMatches:
                for player in [match.player1.value, match.player2.value]:
                    if player not in pDict:
                        pDict[player] = (rdict[player].rd.value,
                            rdict[player].rating.value)
                        # glicko.chess.c
                        curRD = glicko.getCurrentRD(pDict[player][0], 15.8,
                            period - rdict[player].last_match.value)
                        curRating = rdict[player].rating.value
                        # search all matches the player participated, in period
                        ratingList = []
                        RDList = []
                        outcomeList = []
                        for m in pMatches:
                            # player is player1 of match
                            if m.player1.value == player:
                                if m.player2.value in pDict:
                                    ratingList.append(
                                        pDict[m.player2.value][1])
                                    RDList.append(pDict[m.player2.value][0])
                                else:
                                    ratingList.append(
                                        rdict[m.player2.value].rating.value)
                                    RDList.append(
                                        rdict[m.player2.value].rd.value)
                                outcomeList.append(m.outcome.value)
                            # player player2 of match
                            if m.player2.value == player:
                                if m.player1.value in pDict:
                                    ratingList.append(
                                        pDict[m.player1.value][1])
                                    RDList.append(pDict[m.player1.value][0])
                                else:
                                    ratingList.append(
                                        rdict[m.player1.value].rating.value)
                                    RDList.append(
                                        rdict[m.player1.value].rd.value)
                                outcomeList.append(1.0 - m.outcome.value)

                        # calculate new rating
                        newRating = glicko.newRating(curRD, curRating,
                            ratingList, RDList, outcomeList)
                        newRD = glicko.newRD(curRD, newRating, ratingList,
                            RDList)

                        rdict[player].rd.value = newRD
                        rdict[player].rating.value = newRating
                        rdict[player].last_match.value = period
                        rdict[player].save(commit=False)

            Rank_Glicko.commit()
            stage = period % 4
            if stage == 0:
                sys.stdout.write("\r| ")
            elif stage == 1:
                sys.stdout.write("\r/ ")
            elif stage == 2:
                sys.stdout.write("\r--")
            else:
                sys.stdout.write("\r\\ ")
            sys.stdout.flush()
        print "\rDone."
    """
    Updates the ratings for all players.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    update_funcs = {'elo': update_elo, 'glicko': update_glicko}

    print "Updating the ratings for all players in %s using %s" % (args.game,
        args.algorithm)
    update_funcs[args.algorithm]()


def match(args):
    def match_elo(rating):
        ratings = Rank_Elo.query().all()
        best = None
        deviation = 99999999
        for r in ratings:
            if (best is None or abs(r.value.value - rating.value.value) <
                deviation) and r.player_id.value != rating.player_id.value:
                best = r
                deviation = abs(r.value.value - rating.value.value)
        return best

    def match_glicko(rating):
        print "Not implemented yet"
        return None

    """
    Finds the best opponent for a given player.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    match_funcs = {'elo': match_elo, 'glicko': match_glicko}

    rating = utils.get_rating(args)
    if rating is None:
        print "Player %s is not known." % args.player
        return

    print "Looking for the best opponent for player %s..." % args.player

    opponent = match_funcs[args.algorithm](rating)

    if opponent is None:
        print "No opponent found."
        return

    print "Best opponent for player %s with rating %d is:" % (args.player,
        rating.value.value)
    other = Player.query().get(player_id=opponent.player_id.value)
    print "\tPlayer %s with rating %d." % (other.nickname.value,
        opponent.value.value)


def rating(args):
    """
    Queries the rating of a given player.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    player = utils.get_rating(args)

    if player is None:
        print "The rating for player %s in %s using %s is not known." % (
            args.player, args.game, args.algorithm)
    else:
        if args.algorithm == "elo":
            print "The rating for player %s in %s using %s is %d." % (
                args.player, args.game, args.algorithm, player.value.value)
        else:
            print "The rating for player %s in %s using %s is %d " \
                "with rating deviation %d" % (args.player, args.game,
                args.algorithm, player.rating.value, player.rd.value)


def predict(args):
    """
    Reads match constellations from an input file and writes the
    results to a specified output file.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    if os.path.abspath(args.ifile) == os.path.abspath(args.ofile):
        print "You tried to overwrite your input with your output file."
        print "Aborted."
        return

    if args.algorithm == "glicko":
        print "Not implemented yet"
        return

    try:
        modes = {True: "incremental", False: "non-incremental"}
        print "Predicting the matches in %s mode" % modes[args.incremental]
        print "Open %s and write into %s..." % (args.ifile, args.ofile)
        csvfile, reader, hasHeader = utils.get_csv(args.ifile)
        ofile = open(args.ofile, 'w')
        line = 0

        if hasHeader:
            print "\tFirst line of csv file is ignored. It seems to be a " \
                  "header row.\n"

        # constants
        conf = utils.get_config(args)
        k = conf["elo.chess.k"]
        func = conf["elo.chess.function"]

        # Query all ratings and store it in a dictionary. This is done for
        # faster access and on-the-fly calculation of new elo values
        ratings = Rank_Elo.query().all()
        rdict = {}
        for r in ratings:
            player = Player.query().get(player_id=r.player_id.value)
            rdict[player.nickname.value] = r

        for row in reader:
            if line != 0 or (line == 0 and not hasHeader):
                ratings = (rdict.get(row[1], None), rdict.get(row[2], None))
                if ratings[0] is None or ratings[1] is None:
                    continue
                value1 = ratings[0].value.value
                value2 = ratings[1].value.value

                if (value1 > value2):
                    outcome = 1
                elif (value1 < value2):
                    outcome = 0
                else:
                    outcome = 0.5

                if args.incremental:
                    result = elo.elo1on1(value1, value2, outcome, k, func)
                    ratings[0].value = result[0]
                    ratings[1].value = result[1]

                ofile.write("%s,%s,%s,%s\n" % (row[0], row[1], row[2],
                    str(outcome)))
            elif line == 0 and hasHeader:
                ofile.write('"%s","%s","%s","Statistically most possible ' \
                            'outcome"\n' % (row[0], row[1], row[2]))
            if line % 13 == 0:
                sys.stdout.write("\rWrote %d entries to the out file" % line)
                sys.stdout.flush()
            line = line + 1
        print "\rWrote %d entries to the out file" % (
            line - (1 if hasHeader else 0))
        csvfile.close()
        ofile.close()

    except csv.Error:
        print "Error importing %s in line %d" % (args.ifile, line)
    except IOError:
        print "One file is missing. Either %s or %s" % (args.ifile, args.ofile)


def compare(args):
    def compare_elo(ratings):
        value1 = ratings[0].value.value
        value2 = ratings[1].value.value
        if value1 != value2:
            winning_player = args.player1 if value1 > value2 else args.player2
            print "\tPlayer %s will (probably) win." % winning_player
            print "\tRank player %s: %d" % (args.player1, value1)
            print "\tRank player %s: %d" % (args.player2, value2)
            print "\tPlayer %s is %d points better." % (winning_player,
                abs(value1 - value2))
        else:
            print "Both players have the same elo rank (%d)" % value1

    def compare_glicko(ratings):
        exp = glicko.expectation(ratings[0].rating.value, ratings[1].rating.value, ratings[1].rd.value)
        print "The result is %f.\n" % exp
        if 0.45 <= exp <= 0.55:
            print "They will probably draw."
        elif exp > 0.55:
            print "Player %s will (probably) win." % args.player1
        else:
            print "Player %s will (probably) win." % args.player2

    """
    Compares the rating of two given players.

    :param args: A list with arguments from the argument parser
    :type args: namespace
    """

    if args.player1 is args.player2:
        print "You cannot compare player %s with himself" % args.player1
        return

    print "Comparing the rating of two players in %s with %s:" % (args.game,
        args.algorithm)

    ratings = utils.get_rating(args)
    if ratings is None:
        print "Both players are not known!"
        return

    if (ratings[0] == None):
        print "Player with nickname %s not known." % args.player1
        return
    if (ratings[1] == None):
        print "Player with nickname %s not known." % args.player2
        return

    compare_funcs = {'elo': compare_elo, 'glicko': compare_glicko}
    compare_funcs[args.algorithm](ratings)


def create_player(args):
    """
    Creates a new player (as specified in args)
    :param args: A list with arguments from the argument parser
    :type args: namespace
    """
    player, created = utils.add_player(args.nickname, args.firstname,
        args.lastname, True)
    if created is True:
        print "The player is now known in the database:"
        print "ID: %d;\tfirst name: %s;\tlast name: %s;\tnickname: %s" % (
            player.player_id.value, args.firstname, args.lastname,
            args.nickname)
    else:
        print "The player with nickname %s already exists." % args.nickname


def best_worst(args, best):
    def best_worst_elo():
        ranks = Rank_Elo.query().all()
        ranks = sorted(ranks, key=lambda x: x.value.value, reverse=best)

        # the table to print out
        table = [['Rank', 'Rating', 'Nick', 'Firstname', 'Lastname', 'ID']]
        #print "Rank\tRating\tNick\tForename\tSurname\tid"

        for i in range(min(args.amount, len(ranks))):
            player = Player().query().get(player_id=ranks[i].player_id.value)
            #print "%d\t%d\t%s\t%s,\t%s\t%s" % (i + 1, ranks[i].value.value,
            #    player.nickname.value, player.firstname.value,
            #    player.lastname.value, player.player_id.value)
            table.append([i + 1, ranks[i].value.value,
                player.nickname.value, player.firstname.value,
                player.lastname.value, player.player_id.value])
        utils.print_table(table)

    def best_worst_glicko():
        ranks = Rank_Glicko.query().all()
        ranks = sorted(ranks, key=lambda x: x.rating.value - (x.rd.value), reverse=best)

        table = [['Rank', 'Rating', 'RD', 'Nick', 'Firstname', 'Lastname', 'ID']]
        #print "Rank\tRating\tRD\tNick\tForename\tSurname\tid"

        for i in range(min(args.amount, len(ranks))):
            player = Player().query().get(player_id=ranks[i].player_id.value)
            #print "%d\t%d\t%d\t%s\t%s,\t%s\t%s" % (i + 1, ranks[i].rating.value,
            #    ranks[i].rd.value, player.nickname.value, player.firstname.value,
            #    player.lastname.value, player.player_id.value)
            table.append([i + 1, int(ranks[i].rating.value),
                int(ranks[i].rd.value), player.nickname.value, player.firstname.value,
                player.lastname.value, player.player_id.value])
        utils.print_table(table)
    """
    Queries the n best or worst players of a given pair of game and algorithm.
    """

    best_worst_funcs = {'elo': best_worst_elo, 'glicko': best_worst_glicko}

    print "The %s %d players in %s with %s:" % (("Top" if best else "Worst"),
        args.amount, args.game, args.algorithm)

    best_worst_funcs[args.algorithm]()


def clear(args):
    def clear_elo():
        ranks = Rank_Elo.query().all()
        for rank in ranks:
            rank.value = 1500
            rank.save(commit=False)
        Rank_Elo.commit()

    def clear_glicko():
        ranks = Rank_Glicko.query().all()
        for rank in ranks:
            rank.rd = 350
            rank.rating = 350
            rank.last_match = 0
            rank.save(commit=False)
        Rank_Glicko.commit()

    """
    Clears ranks or matches or both.
    """

    if not args.ranks and not args.matches:
        print "You have to specify either --ranks or --matches, or both."
        return

    # (ranks, matches) --> output string
    output = {(True, True): 'ranks and matches', (True, False): 'ranks',
        (False, True): 'matches', (False, False): ''}
    print "Clearing %s..." % output[args.ranks, args.matches]

    # clear ranks
    if args.ranks:
        clear_funcs = {'elo': clear_elo, 'glicko': clear_glicko}
        clear_funcs[args.algorithm]()

    # clear matches
    if args.matches:
        Match1on1.query().truncate()


def history(args):

    if args.player1 == args.player2:
        print "Player1 and Player2 are equal. Use 'history <player>'."
        return

    # store all players in a dict (player_id --> player) and get player1/2
    players = Player.query().all()
    pdict = {}
    for player in players:
        pdict[player.player_id.value] = player
        if player.nickname.value == args.player1:
            player1 = player
        if player.nickname.value == args.player2:
            player2 = player

    if args.player2 is None:
        print "Searching for the history of %s\n" % args.player1

        # the table to print out
        table = [['Opponent', 'Outcome', 'Date']]

        # get all matches with player 1
        matches = Match1on1.query().filter(
            player1=player1.player_id.value).filter(
            player2=player1.player_id.value).join_or().all()

        won = 0
        lost = 0
        draw = 0

        # iterate over all matches
        for match in matches:
            # check who the opponent is and who actually won
            opponent = match.player1.value
            if match.outcome.value == 0.5:
                outcome = "Draw"
                draw += 1
            if opponent == player1.player_id.value:
                opponent = match.player2.value
                if match.outcome.value == 1:
                    outcome = "Won"
                    won += 1
                elif match.outcome.value == 0:
                    lost += 1
                    outcome = "Lost"
            else:
                if match.outcome.value == 1:
                    outcome = "Lost"
                    lost += 1
                elif match.outcome.value == 0:
                    outcome = "Won"
                    won += 1

            table.append([pdict[opponent].nickname.value, outcome,
                match.date.value])

        # finally print the table
        utils.print_table(table)
        print "\nStatistics:"
        print "Won:  %d\nLost: %d\nDraw: %d" % (won, lost, draw)

    else:
        #TODO modify this when IN (...) works
        print "Searching for the history of %s and %s\n" % (args.player1,
            args.player2)

        # the table to print out
        table = [['Winner', 'Date']]

        # get all matches with player 1
        matches1 = Match1on1.query().filter(
            player1=player1.player_id.value).filter(
            player2=player1.player_id.value).join_or().all()

        # get all matches with player 2
        matches2 = Match1on1.query().filter(
            player1=player2.player_id.value).filter(
            player2=player2.player_id.value).join_or().all()

        statistics = {args.player1: 0, args.player2: 0, 'Draw': 0}

        # Find the intersection of the two list. Other methods do not work
        # because the 'in' operator does not seem to work with instances
        matches = [x for x in matches1 if
            [y for y in matches2 if y.match_id.value == x.match_id.value]]

        for match in matches:
            if match.outcome.value == 0:
                nickname = pdict[match.player2.value].nickname.value
                table.append([nickname, match.date.value])
                statistics[nickname] += 1
            elif match.outcome.value == 1:
                nickname = pdict[match.player2.value].nickname.value
                table.append([nickname, match.date.value])
                statistics[nickname] += 1
            else:
                table.append(['Draw', match.date.value])
                statistics['Draw'] += 1

        # finally print the table
        utils.print_table(table)

        print "\nStatistics for %s:" % args.player1
        print "Won:  %d\nLost: %d\nDraw: %d" % (statistics[args.player1],
            len(matches) - statistics[args.player1] - statistics["Draw"],
            statistics["Draw"])

        print "\nStatistics for %s:" % args.player2
        print "Won:  %d\nLost: %d\nDraw: %d" % (statistics[args.player2],
            len(matches) - statistics[args.player2] - statistics["Draw"],
            statistics["Draw"])


def parse(arguments=None):

    """
    Parses the command-line arguments either passed in the parameter
    arguments, or if None, from the standard input.
    """

    parser = argparse.ArgumentParser(prog='pyChallenge')
    parser.add_argument('-g', '--game', help='The game for the following ' \
        'command. The default value is "chess".')
    parser.add_argument('-a', '--algorithm', help='The algorithm for the ' \
        'following command. The default value is "elo"')
    parser.add_argument('-v', '--version', action='version',
        version="%s version: %s" % ("%(prog)s", pychallenge.get_version()),
        help='Print out the version of pyChallenge and exit')
    subparsers = parser.add_subparsers(help='sub-command help')

    # import config
    p_config = subparsers.add_parser('import-config',
        help='Update the config table with a given config file in csv format.')
    p_config.add_argument('file', help='The (csv) config file to import')
    p_config.set_defaults(func=import_config)

    # import results
    p_import = subparsers.add_parser('import-results',
        help='Import data to the result table from a csv file. This only ' \
             'adds the matches but does not compute any ratings.')
    p_import.add_argument('file', help='The file to import')
    p_import.set_defaults(func=import_results)

    # add result
    p_add_result = subparsers.add_parser('add-result',
        help='Add a result to the result table. This only adds the matches ' \
             'but does not compute any ratings.')
    p_add_result.add_argument('player1', help='Nickname of player 1')
    p_add_result.add_argument('player2', help='Nickname of player 2')
    p_add_result.add_argument('outcome', type=float, help='Outcome of the ' \
        'game: 0 = player 1 lost; 0.5 = draw; 1 = player 1 won')
    p_add_result.add_argument('date', type=int, help='The date of the game')
    p_add_result.set_defaults(func=add_result)

    # update
    p_update = subparsers.add_parser('update',
        help='Update the rating values for all players in the given game ' \
             'for the specified algorithm.')
    p_update.set_defaults(func=update)

    # match
    p_match = subparsers.add_parser('match',
        help='Find the best opponent for the given player in the specified ' \
             'game with the selected algorithm.')
    p_match.add_argument('player', help='Nickname of the player')
    p_match.set_defaults(func=match)

    # get value
    p_value = subparsers.add_parser('rating', help='Query the rating of the ' \
        'given player in the specified game using the selected algorithm.')
    p_value.add_argument('player', help='Nickname of the player')
    p_value.set_defaults(func=rating)

    # best
    p_best = subparsers.add_parser('best',
        help='Query the best player(s) in the given game and algorithm.')
    p_best.add_argument('amount', nargs='?', type=int, default=1,
        help='The number of players to query. "10" for Top 10')
    p_best.set_defaults(func=lambda x: best_worst(x, True))

    # worst
    p_worst = subparsers.add_parser('worst',
        help='Query the worst player(s) in the given game and algorithm.')
    p_worst.add_argument('amount', nargs='?', type=int, default=1,
        help='The number of player to query. "10" for Worst 10')
    p_worst.set_defaults(func=lambda x: best_worst(x, False))

    # predict
    p_predict = subparsers.add_parser('predict',
        help='Predict the matches listed in a csv file and write the ' \
             'predicted results to another csv file.')
    p_predict.add_argument('ifile', help='The file to import')
    p_predict.add_argument('ofile', help='The output file')
    p_predict.add_argument('-i', '--incremental', action="store_true",
        help='If specified, updates the ratings after each match on-the-fly.' \
        ' This does not set any values in the database. If not specified, ' \
        'uses the current ratings for each listed game.')
    p_predict.set_defaults(func=predict)

    # compare two players
    p_compare = subparsers.add_parser('compare',
        help='Compare two players in the specified game with the given ' \
             'algorithm and predict who will win.')
    p_compare.add_argument('player1', help='Nickname of player 1')
    p_compare.add_argument('player2', help='Nickname of player 2')
    p_compare.set_defaults(func=compare)

    # create new player
    p_create_player = subparsers.add_parser('create-player',
        help='Creates a new player in the database and initializes his ' \
              'rating with the default values.')
    p_create_player.add_argument('nickname',
        help='Nickname for the new player')
    p_create_player.add_argument('firstname', type=unicode,
        help='First name of the new player')
    p_create_player.add_argument('lastname', type=unicode,
        help='Last name of the new player')
    p_create_player.set_defaults(func=create_player)

    # clear
    p_clear = subparsers.add_parser('clear',
        help='Clears ratings and/or matches. See --ranks and --matches.')
    p_clear.add_argument('-r', '--ranks', action='store_true',
        help='Clear the ranks and set the default values for all players')
    p_clear.add_argument('-m', '--matches', action='store_true',
        help='Clear all matches')
    p_clear.set_defaults(func=clear)

    # history
    p_history = subparsers.add_parser('history',
        help='Shows the history of the given player(s)')
    p_history.add_argument('player1', help='Nickname of player 1')
    p_history.add_argument('player2', nargs='?', default=None,
        help='Nickname of player 2')
    p_history.set_defaults(func=history)

    if arguments is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arguments)

    if (not utils.prepare_args(args)):
        return

    print ""
    args.func(args)
    print ""
