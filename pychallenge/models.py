# -*- coding: utf-8 -*-
from pychallenge.db import models


class Config(models.Model):
    key = models.Text()
    value = models.Text()


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
    date = models.Numeric()
    outcome = models.Numeric()


class Player(models.Model):
    player_id = models.PK()
    firstname = models.Text()
    lastname = models.Text()
    nickname = models.Text()


class Rank_Elo(models.Model):
    id = models.PK()
    player_id = models.FK('Player')
    game_id = models.FK('Game')
    value = models.Numeric(value=1500)


class Rank_Glicko(models.Model):
    id = models.PK()
    player_id = models.FK('Player')
    game_id = models.FK('Game')
    rd = models.Numeric(value=350)
    rating = models.Numeric(value=1500)
    last_match = models.Numeric(value=1)
