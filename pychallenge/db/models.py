# -*- coding: utf-8 -*-
import copy
from pychallenge.db import connection, db
from pychallenge.db.query import Query
from pychallenge.db.fields import Date, Field, Numeric, Text, PK, FK


class Model(object):
    """
    This is the general Model class. All Models inherit from this one.

    To use the object-relational mapping (ORM) first a class has to inherit
    from :py:class:`pychallenge.db.models.Model`. Then, all class
    variables, one adds to the class, are interpreted as columns in the
    database.

    This is an example providing all features::

        >>> from pychallenge.db import models
        >>> class Player(models.Model):
        ...      player_id = models.PK()
        ...      name = models.Text()
        ...      birthday = models.Date()
        ...      games = models.Numeric()
        ...
        >>> Player.create()
        >>> player1 = Player(name="Michael", birthday="1988-03-27", games=10)
        >>> player1.save(commit=False)
        >>> player2 = Player(name="Jessica", birthday="1988-09-14", games=25)
        >>> player2.save()
        >>> Player.query().all()
        [<player pk=1>, <player pk=2>]
        >>> player1.birthday
        '03/27/1988'
        >>> player2.games
        25
        >>> player2.not_available
        Traceback (most recent call last):
        AttributeError: The field not-available does not exists in model player
        >>> player1.games = 11
        >>> player1.save()
        >>> player1.games
        11
        >>> player1.delete()
        >>> Player.query().all()
        [<player pk=2>]
        >>> for i in range(5):
        ...     p=Player(name="player%d"%i)
        ...     p.save(commit=False)
        ...
        >>> Player.commit()
        >>> Player.query().all()
        [<player pk=2>, <player pk=3>, <player pk=4>, <player pk=5>,
        <player pk=6>, <player pk=7>]
        >>> Player.query().filter(player_id__lt=4).filter(player_id__ge=6) \\
        ...     .all()
        ...
        >>> Player.query().filter(player_id__lt=4).filter(player_id__ge=6) \\
        ...     .join_or().all()
        ...
        [<player pk=2>, <player pk=3>, <player pk=6>, <player pk=7>]
        >>> Player.query().truncate()
        >>> Player.query().drop()

    """
    __query__ = None

    def __init__(self, **kwargs):
        """
        This initializes a new model object.

        :param kwargs: a dictionary with the model fields as index and their
            value
        :type kwargs: dictionary
        """
        self.__meta__ = {}
        self.__meta__['fields'] = {}
        self.__meta__['name'] = self.__class__.__name__.lower()
        self.__meta__['pk'] = None
        for fname, ftype in self.__class__.__dict__.iteritems():
            if isinstance(ftype, Field):
                # We need :py:func:`copy.copy` here, since ``ftype`` is the
                # same for each model instance of the same class
                new_field = copy.copy(ftype)
                if kwargs.get(fname, None) != None:
                    new_field.value = kwargs.get(fname, None)
                self._set_meta_field(fname, instance=new_field)
                self.__dict__[fname] = new_field
                if isinstance(new_field, PK):
                    self.__meta__['pk'] = fname

    @property
    def pk(self):
        """
        :return: None if there is no PK, else the name of the PK-field
        """
        return self.__meta__['pk']

    @classmethod
    def all(cls, **kwargs):
        """
        This function returns all objects that match all performed
        (:py:func:`filter`) queries. If there are no results,
        :py:func:`all` returns an empty list.

        :param kwargs: Any type of filter query (see :py:func:`filter`)
        :return: A list of instances or an empty list if there are no matching
        :rtype: list
        """
        cls.__query__ = cls.__query__.filter(**kwargs)
        fields = [f for f, t in cls.__dict__.items() if isinstance(t, Field)]
        fields.sort()

        ret = cls.__query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)
            result = []
            for row in db:
                instance = cls(**row)
                result.append(copy.copy(instance))
            return result if len(result) > 0 else []
        return []

    @classmethod
    def create(cls, dry_run=False):
        """
        This method creates the table in the database.

        :param dry_run: `True` or `False`. If dry_run is `True`, the
            database query is not executed.
        :type dry_run: boolean
        """
        fields = {}
        for f, t in cls.__dict__.items():
            if isinstance(t, Field):
                fields[f] = t

        kwargs = {
            'table': cls.__name__.lower(),
            'dry_run': dry_run,
        }
        cls.__query__ = Query(Query.QTYPE_CREATE, fields, **kwargs)
        ret = cls.__query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)

    @classmethod
    def commit(self):
        """
        This function forces a commit of all data within the current
        connection
        """
        connection.commit()

    def save(self, commit=True):
        """
        Calling the save methode will store the object in the databse.

        :param commit: If `True` (default), each change will direct affect the
            database. If `commit` is `False`
        :type commit: Boolean
        """
        if self.pk and self.__meta__['fields'][self.pk].value:
            __query__ = Query(Query.QTYPE_UPDATE, self.__meta__['fields'],
                            table=self.__meta__['name'],
                            pk=self.pk)
            ret = __query__.run()
            if ret:
                statement, values = ret
                db.execute(statement, values)
                if commit:
                    connection.commit()

        else:
            __query__ = Query(Query.QTYPE_INSERT, self.__meta__['fields'],
                            table=self.__meta__['name'],
                            pk=self.pk)
            ret = __query__.run()
            if ret:
                statement, values = ret
                db.execute(statement, values)
                if commit:
                    connection.commit()
                if self.pk:
                    self.__meta__['fields'][self.pk].value = db.lastrowid

    def delete(self, commit=True):
        """
        Calling this method will remove the object from the database. However,
        any variable that is referring an instance still access it.

        :param commit: If true, each change will direct affect the database
        :type commit: Boolean
        """
        if self.pk and self.__meta__['fields'][self.pk].value:
            __query__ = Query(Query.QTYPE_DELETE, self.__meta__['fields'],
                            table=self.__meta__['name'],
                            pk=self.pk)
            ret = __query__.run()
            if ret:
                statement, values = ret
                db.execute(statement, values)
                if commit:
                    connection.commit()

    @classmethod
    def drop(cls):
        """
        This method drops this table from the database.
        """
        # TODO: dry_run
        __query__ = Query(Query.QTYPE_DROP, {}, table=cls.__name__.lower())
        ret = __query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)
            connection.commit()

    @classmethod
    def truncate(cls):
        """
        This method removes all records in this table from the database.
        """
        # TODO: dry_run
        __query__ = Query(Query.QTYPE_TRUNCATE, {}, table=cls.__name__.lower())
        ret = __query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)
            connection.commit()

    @classmethod
    def get(cls, **kwargs):
        """
        :return: returns a single instances of the model or None if there is
            no object matching the pattern.
        :rtype: either an instance of the current model class or None
        """
        cls.__query__ = cls.__query__.filter(**kwargs).limit(1)

        ret = cls.__query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)
            for row in db:
                instance = cls(**row)
                return instance
        return None

    @classmethod
    def query(cls, dry_run=False):
        """
        This function initializes and constructs the prepared database query
        statement and is used to run functions like :py:func:`all`,
        :py:func:`save`, :py:func:`delete`, :py:func:`create`

        :param dry_run: `True` or `False`. If dry_run is `True`, the
            database query is not executed.
        :type dry_run: boolean
        """
        fields = {}
        for f, t in cls.__dict__.items():
            if isinstance(t, Field):
                fields[f] = t

        kwargs = {
            'table': cls.__name__.lower(),
            'dry_run': dry_run,
        }
        cls.__query__ = Query(Query.QTYPE_SELECT, fields, **kwargs)
        return cls

    @classmethod
    def filter(cls, **kwargs):
        """
        Filter the fields of any select statement to the given fields. See
        :py:func:`pychallenge.db.db.Query.filter` for a description of
        kwargs and return the prepared / filtered query.

        If no :py:func:`join_or` is invoked, all filter statements are
        connected by `AND`.

        *Confer*: :py:func:`filter_or`, :py:func:`join_and`,
        :py:func:`join_or`, :py:func:`pychallenge.db.db.Query.filter`
        """
        cls.__query__ = cls.__query__.filter(**kwargs)
        return cls

    @classmethod
    def filter_or(cls, **kwargs):
        """
        This function does the same :py:func:`filter`, but connects the
        statements by `OR`.

        *Confer*: :py:func:`filter`, :py:func:`join_and`,
        :py:func:`join_or`, :py:func:`pychallenge.db.db.Query.filter`
        """
        cls.__query__ = cls.__query__.filter_or(**kwargs)
        return cls

    @classmethod
    def join_and(cls):
        """
        This forces a connection of the given filter statements by `AND`.

        *Confer*: :py:func:`filter`, :py:func:`filter_or`,
        :py:func:`join_or`, :py:func:`pychallenge.db.db.Query.filter`
        """
        cls.__query__ = cls.__query__.join_and()
        return cls

    @classmethod
    def join_or(cls):
        """
        This forces a connection of the given filter statements by `OR`.

        *Confer*: :py:func:`filter`, :py:func:`filter_or`,
        :py:func:`join_and`, :py:func:`pychallenge.db.db.Query.filter`
        """
        cls.__query__ = cls.__query__.join_or()
        return cls

    @classmethod
    def limit(cls, count, offset=None):
        """
        The limit functions returns only the first (by database) `count`
        rows of the the database.

        :param count: Limit to this number of returned objects.
        :type count: Integer
        :param offset: Setting offset to an positiv Integer ommits the first
            `offset` objects.
        :type offset: positiv Integer
        """
        cls.__query__ = cls.__query__.limit(count, offset)
        return cls

    def _set_meta_field(self, name, **kwargs):
        """
        :param name: This is the name of a field
        :param value: The value that will be assigned to the field
        :param instance: This attribute is used for adding a new field to the
            model
        :type name: String
        :type value: variable
        :type instance: :py:class:`pychallenge.db.fields.Field`
        """
        value = instance = None
        try:
            instance = kwargs.pop('instance')
        except KeyError:
            try:
                value = kwargs.pop('value')
            except KeyError:
                raise AssertionError

        if not (instance or name in self.__meta__['fields']):
            raise AttributeError('Field "%s" does not exists in model "%s"' %
                (name, self.__meta__['name']))
        if instance:
            self.__meta__['fields'][name] = instance
        else:
            self.__meta__['fields'][name].value = value

    def _get_meta_field(self, name):
        """
        :param name: The name of the referred field
        :type name: String
        :return: either the value of field :py:attr:`name` or
            :py:attr:`default` if not defined
        """
        if not name in self.__meta__['fields']:
            raise AttributeError("The field %s does not exists in model %s" %
                (name, self.__meta__['name']))
        return self.__meta__['fields'].get(name)

    def __setattr__(self, name, value):
        """
        Overloaded :py:func:`__setter__` function to set field values

        :param name: The name of the referred field
        :param value: The value that will be stored
        :type name: String
        :type String: variable
        """
        if self.__dict__:
            try:
                self._set_meta_field(name, value=value)
            except AttributeError:
                self.__dict__[name] = value
        else:
            super(Model, self).__setattr__(name, value)

    def __repr__(self):
        """
        :return: Returns a readable and unambiguous representation of a modal\
        instance
        """
        if self.pk:
            return "<%s pk=%s>" % (self.__meta__['name'],
                self.__meta__['fields'][self.pk].value)
        else:
            return "<%s instance>" % self.__meta__['name']
