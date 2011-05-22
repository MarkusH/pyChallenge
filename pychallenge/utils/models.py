from pychallenge.utils.db import db, connection


class Field():
   
    def __init__(self, value=None, **kwargs):
        self.set_value(value)

    def get_value(self):
        """
        :return: returns the value of that field
        """
        return self.value

    def clean(self, value):
        """
        :param value: clean `value`
        :return: cleans up the value and returns the cleaned data
        """
        return value

    def set_value(self, value):
        """
        :param value: this is the setter function for the value
        """
        self.value = self.clean(value)

class Numeric(Field):
    pass

class Text(Field):
    pass

class PK(Field):
    pass

class FK(Numeric):

    def __init__(self, ref_table, value=None):
        self.ref_table = ref_table
        self.value = self.clean(value)

class Model(object):

    id = PK()

    __meta__ = {
        'fields': {},
        'name': "",
        'pk': None
    }

    def __init__(self, **kwargs):
        """
        This initializes a new model object.
        :param **kwargs: a dictionary with the model fields as index
        """
        self.__meta__['fields'] = {}
        self.__meta__['name'] = self.__class__.__name__.lower()
        for f, t in self.__class__.__dict__.items():
            if isinstance(t, Field):
                if f in kwargs:
                    t.set_value(kwargs.get(f))
                self.__meta__['fields'][f] = t
                if isinstance(t, PK):
                    self.__meta__['pk'] = f

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
        if self.pk() and self.__meta__['fields'][self.pk()].get_value():
            cmd = "UPDATE %(_tablename)s SET " % {
                '_tablename': self.__meta__['name']
            }
            cmd += ", ". join("%s = :%s" % (f, f)
                for f in self.__meta__['fields'].keys() if
                    self.__meta__['pk'] != f)
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
            values[f] = t.get_value()
        db.execute(cmd, values)
        if commit:
            connection.commit()
        self.__meta__['fields'][self.pk()].set_value(db.lastrowid)

