.. _database:

Database
========

This page describes the full database design. All table fields that are mentioned in this document are prefixed with the tablename followed by an underscore `_` except those fields that act as a foreign key. Their fieldname is fully defined and is the full name of the foreign primary key field.


.. _database-algorithm:

algorithm
---------
:param id: Integer
:param name: Text
:param description: Text
:param algorithm_type_id: Integer :ref:`database-algorithm_type`

:param PRIMARY: id
:param UNIQUE: name
:param KEY: algorithm_type_id


.. _database-algorithm_type:

algorithm_type
--------------

:param id: Integer
:param type: Text
:param description: Text

:param PRIMARY: id
:param KEY: type


.. _database-game:

game
----

:param id: Integer
:param name: Text
:param description: Text
:param algorithm_type_id: Integer :ref:`database-algorithm_type`

:param PRIMARY: id
:param UNIQUE: name
:param KEY: algorithm_type_id


.. _database-match:

match
-----
:param id: Integer
:param game_id: Integer :ref:`database-game`
:param participants_id: Integer :ref:`database-participant`

:param PRIMARY: id


.. _database-membership:

membership
----------

:param player_id: Integer :ref:`database-player`
:param team_id: Integer :ref:`database-team`

:param UNIQUE: (player_id, team_id)
:param KEY: team_id


.. _database-participant:

participant
-----------

:param id: Integer
:param object_id: Interger Either refers to :ref:`database-player` or :ref:`database-team` depending of `is_team`.
:param is_team: Boolean
:param ranking: Integer

:param PRIMARY: id


.. _database-player:

player
------

:param id: Integer
:param firstname: Text
:param lastname: Text
:param nickname: Text

:param PRIMARY: id
:param UNIQUE: nickname


.. _database-team:

team
----

:param id: Integer
:param name: Text (Null)
:param static: Boolean

:param PRIMARY: id
:param UNIQUE: name
:param KEY: static


Algorithm specific databases
============================

The following tables are algorithm specific tables and 

.. _database-rank_elo:

rank_elo
--------

:param player_id: Integer :ref:`database-player`
:param value: Integer
:param game_id: Integer :ref:`database-game`

:param UNIQUE: (player_id, game_id)
:param KEY: game_id


.. _database-rank_trueskill:

rank_trueskill
--------------

:param player_id: Integer :ref:`database-player`
:param mu: Float
:param sigma: Float
:param game_id: Integer :ref:`database-game`

:param UNIQUE: (player_id, game_id)
:param KEY: game_id
