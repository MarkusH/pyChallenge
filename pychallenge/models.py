from pychallenge.utils import models


class Algorithm(models.Model):
    algorithm_id = models.PK()
    name = models.Text()
    description = models.Text()
    algorithm_type_id = models.FK('Algorithm_Type')

class Match1on1(models.Model):
    match_id = models.PK()
    game_id = models.FK('.....')
    player1 = models.FK('Player')
    player2 = models.FK('Player')
    date = models.Text()
    outcome = models.Numeric()

class Player(models.Model):
    player_id = models.PK()
    firstname = models.Text()
    lastname = models.Text()
    nickname = models.Text()

class RankElo(models.Model):
    player_id = models.FK('Player')
    game_id = models.FK('Game')
    value = models.Numeric(value=1500)
