# -*- coding: utf-8 -*-
from datetime import datetime


class Field():
    """
    Base field class for all fields
    """

    def __init__(self, value=None):
        """
        :param value: the field value
        :type value: variable
        """
        self.value = value

    def clean(self, value):
        """
        :param value: clean `value`
        :type value: variable
        :return: cleans up the value and returns the cleaned data
        """
        return value

    def get_value(self):
        """
        value stores the field value
        :return: returns the value of that field
        """
        return self._value

    def set_value(self, value):
        """
        :param value: this is the setter function for the value
        :type value: variable
        """
        self._value = self.clean(value)

    value = property(get_value, set_value)

    def __repr__(self):
        """
        :return: This returns a string formatted field-object
        """
        return '<%s "%s">' % (
            str(self.__class__.__name__),
            (self.value))


class Numeric(Field):
    """
    This field class matches the SQLite field type "NUMERIC"
    """
    def clean(self, value):
        """
        :param value: clean `value`
        :type value: variable
        :return: cleans up the value and returns the cleaned data
        """
        try:
            return float(value)
        except ValueError:
            return None


class Text(Field):
    """
    This field class matches the SQLite field type "TEXT"
    """
    pass


class PK(Field):
    """
    This field class matches the SQLite field type "INTEGER PRIMARY KEY"
    """
    def clean(self, value):
        """
        :param value: clean `value`
        :type value: variable
        :return: cleans up the value and returns the cleaned data
        """
        try:
            return int(value)
        except ValueError:
            return None


class FK(Numeric):
    """
    This field class matches the SQLite field type "NUMERIC" and will be used
    for foreign key validation.
    """

    def __init__(self, ref_table, ref_field, value=0):
        """
        :param ref_table: defines the foreign table
        :param ref_field: defines the lookup field for the foreign table
        :param value: the field value
        :type ref_table: String
        :type ref_field: String
        :type value: Integer
        """
        self.ref_table = ref_table
        self.ref_field = ref_field
        self.value = self.clean(value)

    def clean(self, value):
        """
        :param value: clean `value`
        :type value: variable
        :return: cleans up the value and returns the cleaned data
        """
        try:
            return int(value)
        except ValueError:
            return None

    @property
    def related(self):
        """
        """
        module = __import__("pychallenge.models", fromlist=['pychallenge'])
        ref_class = module.__dict__.get(self.ref_table)

        return ref_class.query().get(**{self.ref_field: self.value})


class Date(Text):
    """
    This field class matches the SQLite field type "DATE"
    """
    def clean(self, value):
        """
        :param value: clean `value`
        :type value: variable
        :return: cleans up the value and returns the cleaned data
        """
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            return None
