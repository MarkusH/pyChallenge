#!/usr/bin/env python

from pychallenge.utils.db import db

if __name__ == "__main__":
    db.executescript("""
        CREATE TABLE `algorithm` (
            `algorithm_id` INTEGER PRIMARY KEY,
            `name` TEXT,
            `description` TEXT,
            `algorithm_type_id` NUMERIC
        );
        CREATE TABLE `algorithm_type` (
            `algorithm_type_id` INTEGER PRIMARY KEY,
            `type` TEXT,
            `description` TEXT
        );
        CREATE TABLE `game` (
            `game_id` INTEGER PRIMARY KEY,
            `name` TEXT,
            `description` TEXT,
            `algorithm_type_id` NUMERIC
        );
        CREATE TABLE `match` (
            `match_id` INTEGER PRIMARY KEY,
            `game_id` NUMERIC,
            `participant_id` NUMERIC
        );
        CREATE TABLE `membership` (
            `player_id` NUMERIC,
            `team_id` NUMERIC
        );
        CREATE TABLE `participant` (
            `participant_id` INTEGER PRIMARY KEY,
            `object_id` NUMERIC,
            `is_team` NUMERIC,
            `ranking` NUMERIC
        );
        CREATE TABLE `player` (
            `player_id` INTEGER PRIMARY KEY,
            `firstname` TEXT,
            `lastname` TEXT,
            `nickname` TEXT
        );
        CREATE TABLE `team` (
            `team_id` INTEGER PRIMARY KEY,
            `name` TEXT,
            `static` NUMERIC
        );
        CREATE TABLE `match1on1` (
            `match_id` INTEGER PRIMARY KEY,
            `game_id` NUMERIC,
            `player1` NUMERIC,
            `player2` NUMERIC,
            `date` NUMERIC,
            `outcome` NUMERIC
        );
        CREATE TABLE `rank_elo` (
            `id` INTEGER PRIMARY KEY,
            `player_id` NUMERIC,
            `game_id` NUMERIC,
            `value` NUMERIC
        );
        CREATE TABLE `config` (
            `key` TEXT,
            `value` TEXT
        );
        CREATE TABLE `rank_glicko` (
            `id` INTEGER PRIMARY KEY,
            `player_id` NUMERIC,
            `game_id` NUMERIC,
            `rd` NUMERIC,
            `rating` NUMERIC,
            `last_match` NUMERIC
        );
        """)
