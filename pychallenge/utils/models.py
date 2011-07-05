import copy
from pychallenge.utils.db import db, connection, Query
from pychallenge.utils.fields import Field, Numeric, Text, PK, FK


class Model(object):
    """
    This is the general Model class. All Models inherit from this one
    """
    __query__ = None

    def __init__(self, **kwargs):
        """
        This initializes a new model object.
        :param kwargs: a dictionary with the model fields as index and
        their value
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
                if isinstance(new_field, PK):
                    self.__meta__['pk'] = fname

    def getfield(self, fieldname):
        return self._get_meta_field(fieldname)

    def getdata(self, fieldname):
        return self.getfield(fieldname).value

    def setdata(self, fieldname, value=None):
        return self._set_meta_field(fieldname, value=value)

    @property
    def pk(self):
        """
        :return: None if there is no PK, else the name of the PK-field
        """
        return self.__meta__['pk']

    @classmethod
    def all(cls, **kwargs):
        """
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
                i = 0
                tmp = {}
                while i < len(row):
                    tmp[fields[i]] = row[i]
                    i += 1
                instance = cls(**tmp)
                result.append(copy.copy(instance))
            return result if len(result) > 0 else None

    @classmethod
    def create(cls, dry_run=False):
        fields = {}
        for f, t in cls.__dict__.items():
            if isinstance(t, Field):
                fields[f] = t

        kwargs = {
            'table': cls.__name__.lower(),
            'dry_run': dry_run,
        }
        cls.__query__ = Query(Query.QTYPE_CREATE, fields, **kwargs)
        statement = cls.__query__.run()
        if statement:
            db.execute(statement)

    @classmethod
    def commit(self):
        connection.commit()

    def save(self, commit=True):
        """
        Calling the save methode will store the object in the databse.

        :param commit: If true, each change will direct affect the database
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
        any variable instances refering this object can still access it.

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
        __query__ = Query(Query.QTYPE_DROP, {}, table=cls.__name__.lower())
        ret = __query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)
            connection.commit()

    @classmethod
    def truncate(cls):
        __query__ = Query(Query.QTYPE_TRUNCATE, {}, table=cls.__name__.lower())
        ret = __query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)
            connection.commit()

    @classmethod
    def get(cls, **kwargs):
        """
        :return: returns a sigle instances of the model or None if there is\
                no object matching the pattern If more that one object matches\
                the pattern an exception is raised
        """
        cls.__query__ = cls.__query__.filter(**kwargs).limit(1)
        fields = [f for f, t in cls.__dict__.items() if isinstance(t, Field)]
        fields.sort()

        ret = cls.__query__.run()
        if ret:
            statement, values = ret
            db.execute(statement, values)
            result = []
            for row in db:
                i = 0
                tmp = {}
                while i < len(row):
                    tmp[fields[i]] = row[i]
                    i += 1
                instance = cls(**tmp)
                return instance
        return None

    @classmethod
    def query(cls, dry_run=False):
        """
        :return: list of instances matching the given attributes
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
        cls.__query__ = cls.__query__.filter(**kwargs)
        return cls

    @classmethod
    def filter_or(cls, **kwargs):
        cls.__query__ = cls.__query__.filter_or(**kwargs)
        return cls

    @classmethod
    def join_and(cls):
        cls.__query__ = cls.__query__.join_and()
        return cls

    @classmethod
    def join_or(cls):
        cls.__query__ = cls.__query__.join_or()
        return cls

    @classmethod
    def limit(cls, count, offset=None):
        cls.__query__ = cls.__query__.limit(count, offset)
        return cls

    def _set_meta_field(self, name, value=None, instance=None):
        """
        :param name: This is the name of a field
        :param value: The value that will be assigned to the field
        :param instance: This attribute is used for adding a new field to the
            model
        :type name: String
        :type value: variable
        :type instance: :py:class:`pychallenge.utils.fields.Field`
        """
        assert bool(value) ^ bool(instance)

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
        :return: Returns a readable and unambigious representation of a modal\
                instance
        """
        if self.pk:
            return "<%s pk=%s>" % (self.__meta__['name'],
                self.__meta__['fields'][self.pk].value)
        else:
            return "<%s instance>" % self.__meta__['name']
