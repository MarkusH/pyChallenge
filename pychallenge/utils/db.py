import sqlite3
from pychallenge.utils import settings


connection = sqlite3.connect(settings.SETTINGS['DATABASE'])
db = connection.cursor()

class KeyTable():
    
    def __init__(self):
        self.keys = {}

    def __repr__(self):
        return str(self.keys)

    def used(self, name):
        return name in self.keys.keys()

    def add(self, name, value = None):
        n = name
        i = 1
        while n in self.keys.keys():
            n = "%s_%d" %(name, i)
            i = i +1
        self.keys[n] = value
        return n

    def __iter__(self):
        self.index = 0
        self.length = len(self.keys.keys())
        return self

    def __next__(self):
        if self.index < self.length:
            value = self.keys.items[self.index]
            self.index += 1
            return value
        raise StopIteration


class LogicalOperator():

    def __init__(self, **kwargs):
        self.key_table = KeyTable()

        self.expression_list = []
        for k, v in kwargs.iteritems():
            if k.startswith('_and_') or k.startswith('_or_'):
                self.expression_list.append(str(v))
            else:
                n = self.key_table.add(k, v)
                self.expression_list.append('%s = :%s' % (n, n))


class And(LogicalOperator):

    def __repr__(self):
        return " (" + " AND ".join(self.expression_list) + ") "


class Or(LogicalOperator):

    def __repr__(self):
        return " (" + " OR ".join(self.expression_list) + ") "


class Query():

    QTYPE_SELECT = 1
    QTYPE_INSERT = 2
    QTYPE_UPDATE = 3
    QTYPE_DELETE = 4
    QTYPE_CREATE = 5

    AGGREGATE = ['avg', 'count', 'min', 'max']

    def __init__(self, qtype, modelfields, *args, **kwargs):
        """

        """

        self.qtype = qtype
        self.modelfields = modelfields
        self.modelfields.append('*')
        self.key_table = KeyTable()
        self.filter_fields = []
        self.select_fields = []

        if not kwargs.get('table', None):
            raise AttributeError("Missing table definition")
        self.table = kwargs.pop('table')
        if self.qtype == Query.QTYPE_SELECT:
            self._select(*args, **kwargs)

        elif self.qtype == Query.QTYPE_INSERT:
            self._insert(*args, **kwargs)

        elif self.qtype == Query.QTYPE_UPDATE:
            self._update(*args, **kwargs)

        elif self.qtype == Query.QTYPE_DELETE:
            self._delete(*args, **kwargs)

        elif self.qtype == Query.QTYPE_CREATE:
            self._create(*args, **kwargs)

        else:
            raise AttributeError("qtype must be one of QTYPE_SELECT, "
                "QTYPE_INSERT, QTYPE_UPDATE, QTYPE_DELETE, "
                "QTYPE_CREATE")


    def run(self, dry_run=True):
        if dry_run:
            print self.__dict__
            return


    def filter(self, **kwargs):
        """
        """
        self.filter_fields += self._get_filter_fields(**kwargs)
        print self.filter_fields
        return self


    def _select(self, *args, **kwargs):
        """

        """
        flds = kwargs.pop('fields', '*')
        self.select_fields += self._get_select_fields(flds, aggregate=True)
        print self.select_fields


    def _insert(self, *args, **kwargs):
        """

        """
        pass

    def _update(self, *args, **kwargs):
        """

        """
        pass

    def _delete(self, *args, **kwargs):
        """

        """
        pass

    def _create(self, *args, **kwargs):
        """

        """
        pass

    def _get_filter_fields(self, **kwargs):
        def build(f, id, op):
            return '%s %s :%s' % (f, op, id)

        op = {
            'lt': '<',
            'le': '<=',
            'eq': '=',
            'ge': '>=',
            'gt': '>',
        }
        flds = []
        for f, v in kwargs.iteritems():
            parts = f.split('__')
            if len(parts) == 1 and parts[0] in self.modelfields:
                n = self.key_table.add(name=f, value=v)
                flds.append(build(f, n, op['eq']))
            elif len(parts) == 2 and parts[0] in self.modelfields:
                if parts[1] in op.keys():
                    n = self.key_table.add(name=f, value=v)
                    flds.append(build(f, n, op[parts[1]]))
                else:
                    raise AttributeError("Operator %s unknown" %
                        parts[1].upper)
            else:
                raise AttributeError("Unknown field %s" % f)
        return flds


    def _get_select_fields(self, fields, aggregate=False, compare=False, **kwargs):
        """

        """
        if aggregate:
            flds = []
            for f in fields:
                parts = f.split('__')
                if len(parts) == 1 and parts[0] in self.modelfields:
                    flds.append(f)
                elif len(parts) == 2 and parts[0] in self.modelfields:
                    if parts[1] in Query.AGGREGATE:
                        f_n = parts[1].upper() + '(' + parts[0] + ') AS ' + f
                        flds.append(f_n)
                    else:
                        raise AttributeError("Aggregate function %s unknown" %
                            parts[1].upper)
                else:
                    raise AttributeError("Unknown field %s" % f)
        else:
            for f in fields:
                if f in self.modelfields:
                    flds.append(f)
                else:
                    raise AttributeError("Unknown field %s" % f)
        return flds
