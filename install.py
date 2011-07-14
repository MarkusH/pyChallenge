#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pychallenge.models import Config, Match1on1, Player, Rank_Elo, Rank_Glicko

if __name__ == "__main__":
    Config.create()
    Match1on1.create()
    Player.create()
    Rank_Elo.create()
    Rank_Glicko.create()
