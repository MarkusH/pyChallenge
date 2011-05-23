import copy
from pychallenge.utils.db import db, connection
from pychallenge.utils.fields import Field, Numeric, Text, PK, FK

class Model(object):
    """
    This is the general Model class. All Models inherit from this one
    """

    id = PK()

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
        for fname, ftype in self.__class__.__dict__.items():
            if isinstance(ftype, Field):
                # We need :py:func:`copy.copy` here, since ``ftype`` is the
                # same for each model instance of the same class
                new_field = copy.copy(ftype)
                new_field.value = kwargs.get(fname, None)
                self._set_meta_field(fname, new_field)
                if isinstance(new_field, PK):
                    self.__meta__['pk'] = fname

    def pk(self):
        """
        :return: None if there is no PK, else the name of the PK-field
        """
        return self.__meta__['pk']

    def save(self, commit=True):
        """
        :param commit: If true, each change will direct affect the database
        :type commit: Boolean
        """
        if self.pk() and self.__meta__['fields'][self.pk()].value:
            cmd = "UPDATE %(_tablename)s SET " % {
                '_tablename': self.__meta__['name']
            }
            cmd += ", ". join("%s = :%s" % (f, f)
                for f in self.__meta__['fields'].keys() if
                    self.__meta__['pk'] != f)
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
                '_tablename': self.__meta__['name'], 'fl':fl, 'fl2':fl2}
        values = {}
        for f, t in self.__meta__['fields'].items():
            values[f] = t.value
        db.execute(cmd, values)
        if commit:
            connection.commit()
        self.__meta__['fields'][self.pk()].set_value(db.lastrowid)

    def _set_meta_field(self, name, value):
        """
        :param name: This is the name of a field
        :param value: The value that will be assigned to the field
        :type name: String
        :type value: variable
        """
        self.__meta__['fields'][name] = value

    def _get_meta_field(self, name, default=None):
        """
        :param name: The name of the referred field
        :param default: A default value that will be returned if the field
            does not exists
        :type name: String
        :type default: variable
        :return: either the value of field :py:attr:`name` or
            :py:attr:`default` if not defined
        """
        return self.__meta__['fields'].get(name, default)

    def __setattr__(self, name, value):
        """
        Overloaded :py:func:`__setter__` function to set field values

        :param name: The name of the referred field
        :param value: The value that will be stored
        :type name: String
        :type String: variable
        """
        if self.__dict__:
            if name in self.__meta__['fields']:
                self.__meta__['fields'][name].value = value
            else:
                self.__dict__[name] = value
        else:
            super(Model, self).__setattr__(name, value)
