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

    def __init__(self, ref_table, value=0):
        """
        :param ref_table: defines the foreign table
        :type ref_table: String
        """
        self.ref_table = ref_table
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


    def related(self):
        """
        """
        __import__(self.rev_table, fromlist=['pychallenge', 'utils', 'fields'])
        const = self.ref_table()
        return const


class Date(Field):
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
