.. _database:

Database
========

This page describes the full database design. All table fields that are mentioned in this document are prefixed with the tablename followed by an underscore `_` except those fields that act as a foreign key. Their fieldname is fully defined and is the full name of the foreign primary key field.

.. _database-config:

config
------
:param key: String (keys for unique constants and config values e.g. glicko2.tau.chess or elo.function.chess)
:param value: String

:param UNIQUE: key


.. _database-match1on1:

match1on1
---------
:param participant_id1: Integer :ref:`database-player`
:param participant_id2: Integer :ref:`database-player`
:param date: Date
:param outcome: Float


.. _database-player:

player
------
:param id: Integer
:param firstname: Text
:param lastname: Text
:param nickname: Text

:param PRIMARY: id
:param UNIQUE: nickname


Algorithm specific databases
============================

The following tables are algorithm specific tables and 

.. _database-rank_elo:

rank_elo
--------
:param player_id: Integer :ref:`database-player`
:param value: Integer

:param UNIQUE: (player_id, game_id)
:param KEY: game_id


.. _databse-rank_glicko:

rank_glicko
-----------
:param player_id: Integer :ref:`database-player`
:param RD: Float
:param rating: Float
:param last_match: Date

:param UNIQUE: (player_id, game_id)


For future releases
===================

.. _database-rank_glicko2:

rank_glicko2
------------
:param player_id: Integer :ref:`database-player`
:param mu: Float
:param phi: Float
:param sigma: Float
:param last_match: Date

:param UNIQUE: (player_id, game_id)


.. _database-rank_trueskill:

rank_trueskill
--------------
:param player_id: Integer :ref:`database-player`
:param mu: Float
:param sigma: Float

:param UNIQUE: (player_id, game_id)
:param KEY: game_id
