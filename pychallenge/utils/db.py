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

"""
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
"""

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
        # unique `self.select_fields`
        tmp = {}
        for e in self.select_fields:
            tmp[e] = 1
        self.select_fields = tmp.keys()
        
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

        def lbuild(f, id, op):
            return '%s %s (:%s)' % (f, op, id)

        op = {
            'lt': '<',
            'le': '<=',
            'eq': '=',
            'ge': '>=',
            'gt': '>',
        }

        lop = {
            'in': 'IN',
            'nin': 'NOT IN'
        }
        flds = []
        # iterate over all given filter fields
        for f, v in kwargs.iteritems():

            # split the filter comparison
            parts = f.split('__')

            # if no comparison is specified act as __eq
            if len(parts) == 1 and parts[0] in self.modelfields:
                n = self.key_table.add(name=f, value=v)
                flds.append(build(parts[0], n, op['eq']))

            # there is a concrete comparison
            elif len(parts) == 2 and parts[0] in self.modelfields:

                # it's a simple comparision operator
                if parts[1] in op.keys():
                    n = self.key_table.add(name=f, value=v)
                    flds.append(build(parts[0], n, op[parts[1]]))

                # comparision on lists
                elif parts[1] in lop.keys():
                    assert isinstance(v, (tuple, list))
                    n = self.key_table.add(name=f, value=v)
                    flds.append(lbuild(parts[0], n, lop[parts[1]]))

                # this comparision operator is unknown
                else:
                    raise AttributeError("Operator %s unknown" %
                        parts[1].upper)

            # stupid user :-)  --  field does not exists
            else:
                raise AttributeError("Unknown field %s" % f)
        return flds


    def _get_select_fields(self, fields, aggregate=False, **kwargs):
        """

        """
        # if we accept aggregation functions MIN, MAX, AVG, COUNT ...
        if aggregate:
            flds = []

            # iterate over the list of all given fields
            for f in fields:

                # split the agg. function if it exists
                parts = f.split('__')

                # we have no agg. function -> directly add the field
                if len(parts) == 1 and parts[0] in self.modelfields:
                    flds.append(f)

                # build the aggregation sql string for the agg. function
                elif len(parts) == 2 and parts[0] in self.modelfields:
                    if parts[1] in Query.AGGREGATE:
                        f_n = parts[1].upper() + '(' + parts[0] + ') AS ' + f
                        flds.append(f_n)
                    else:
                        raise AttributeError("Aggregate function %s unknown" %
                            parts[1].upper)

                # unknown field
                else:
                    raise AttributeError("Unknown field %s" % f)

        # we don't accept an aggregation function. Just check that all given
        # fields are allowed (along to self.modelfields)
        else:
            for f in fields:
                if f in self.modelfields:
                    flds.append(f)
                else:
                    raise AttributeError("Unknown field %s" % f)
        return flds
