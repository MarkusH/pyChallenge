import copy
from pychallenge.utils.db import db, connection
from pychallenge.utils.fields import Field, Numeric, Text, PK, FK


class Model(object):
    """
    This is the general Model class. All Models inherit from this one
    """

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
        for fname, ftype in self.__class__.__dict__.items():
            if isinstance(ftype, Field):
                # We need :py:func:`copy.copy` here, since ``ftype`` is the
                # same for each model instance of the same class
                new_field = copy.copy(ftype)
                new_field.value = kwargs.get(fname, None)
                self._set_meta_field(fname, instance=new_field)
                if isinstance(new_field, PK):
                    self.__meta__['pk'] = fname

    @property
    def pk(self):
        """
        :return: None if there is no PK, else the name of the PK-field
        """
        return self.__meta__['pk']

    def save(self, commit=True):
        """
        Calling the save methode will store the object in the databse.

        :param commit: If true, each change will direct affect the database
        :type commit: Boolean
        """
        if self.pk and self.__meta__['fields'][self.pk].value:
            cmd = "UPDATE %s SET " % self.__meta__['name']

            def match(x):
                """
                Helper function to create update statement - check for NOT
                :py:func:`pychallenge.utils.models.Model.pk`

                :param x: fieldname
                :type x: String
                :return: True if `x` is not the models pk
                """
                return self.pk != x

            def format(x):
                """
                Helper function to create update statement - format the sql
                assignments

                :param x: fieldname
                :type x: String
                :return: Returns a formatted string for the given fieldname
                """
                return "%s = :%s" % (x, x)

            cmd += ", ".join(map(format, filter(match,
                                    self.__meta__['fields'].keys())))
            """
            The following line builds the assignment part of the SQL
            statement::

                a = :a, b = :b, c = :c, ....

            When calling :py:func:`pychallenge.utils.models.db.execute()` make
            sure to name the keys of the dictionary regarding the fieldname
            """

            cmd += " WHERE %s = :%s" % (self.__meta__['pk'],
                self.__meta__['pk'])
        else:
            flist = []
            flist2 = []
            for f in self.__meta__['fields']:
                flist.append(f)
                flist2.append(":%s" % f)
            fl = ", ".join(flist)
            fl2 = ", ".join(flist2)
            cmd = "INSERT INTO %(_tablename)s (%(fl)s) VALUES (%(fl2)s)" % {
                '_tablename': self.__meta__['name'], 'fl': fl, 'fl2': fl2}
        values = {}
        for f, t in self.__meta__['fields'].items():
            values[f] = t.value
        db.execute(cmd, values)
        if commit:
            connection.commit()
        self.__meta__['fields'][self.pk].set_value(db.lastrowid)

    def delete(self, commit=True):
        """
        Calling this method will remove the object from the database. However,
        any variable instances refering this object can still access it.

        :param commit: If true, each change will direct affect the database
        :type commit: Boolean
        """
        if self.pk and self.__meta__['fields'][self.pk].value:
            cmd = "DELETE FROM %(_tablename)s WHERE %(_pk)s = :%(_pk)s" % {
                '_tablename': self.__meta__['name'],
                '_pk': self.pk,
            }
            db.execute(cmd, {self.pk: self.__meta__['fields'][self.pk].value})
            if commit:
                connection.commit()

    @classmethod
    def query(cls, **kwargs):
        """
        :return: list of instances matching the given attributes
        """
        fields = [f for f, t in cls.__dict__.items() if isinstance(t, Field)]

        exists = lambda x: x in fields

        matching = [x for x in kwargs.keys() if exists(x)]

        cmd = "SELECT %(_fieldlist)s FROM %(_tablename)s" % {
            '_fieldlist': ", ".join(fields),
            '_tablename': cls.__name__.lower(),
        }
        if len(matching) > 0:
            cmd += " WHERE "
            cmd += " and ". join("%s = :%s" % (f, f) for f in matching)
        values = {}
        for f in matching:
            values[f] = kwargs.get(f)
        db.execute(cmd, values)
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
    def get(cls, **kwargs):
        """
        :return: returns a sigle instances of the model or None if there is\
                no object matching the pattern If more that one object matches\
                the pattern an exception is raised
        """
        q = cls.query(**kwargs)
        if q:
            if len(q) > 1:
                raise Exception("More than 1 (%d) objects for %s returned." %
                    (len(q), cls.__name__))
            else:
                return q[0]
        else:
            return None

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
        return "<%s pk=%s>" % (self.__meta__['name'],
            self.__meta__['fields'][self.pk].value)
