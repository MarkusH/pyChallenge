import sqlite3
from pychallenge.utils import settings


connection = sqlite3.connect(settings.SETTINGS['DATABASE'])
db = connection.cursor()

class LogicalOperator():

    def __init__(self, query, **kwargs):
        self.expression_list = []
        for k, v in kwargs.iteritems()
            if k.startswith('_and_') or k.startswith('_or_'):
                self.expression_list.append(v)
            else:
                n = query.key_add(k, v)
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

    def __init__(self, qtype, *args, **kwargs):
        """

        """

        self.qtype = qtype
        self.used_keys = {}

        if not kwargs.get('table', None):
            raise AttributeError("Missing table definition")
        self.table = kwargs.pop('table')

    def exec():
        if self.qtype == Query.QTYPE_SELECT:
            return self._select(*args, **kwargs)

        elif self.qtype == Query.QTYPE_INSERT:
            return self._insert(*args, **kwargs)

        elif self.qtype == Query.QTYPE_UPDATE:
            return self._update(*args, **kwargs)

        elif self.qtype == Query.QTYPE_DELETE:
            return self._delete(*args, **kwargs)

        elif self.qtype == Query.QTYPE_CREATE:
            return self._create(*args, **kwargs)

        else:
            raise AttributeError("qtype must be one of QTYPE_SELECT, "
                "QTYPE_INSERT, QTYPE_UPDATE, QTYPE_DELETE, "
                "QTYPE_CREATE")

    def filter(self, **kwargs):
        pass

    def _select(self, *args, **kwargs):
        """

        """
        flds = kwargs.pop('fields', '*')
        self.select_fields = self._get_fields(flds, aggregate=True)


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

    def _get_fields(self, fields, aggregate=False):
        """

        """
        if aggregate:
            flds = []
            for f in fields:
                parts = f.split('__')
                if len(parts) == 1:
                    flds.append(f)
                elif len(parts) == 2:
                    if parts[1] in ['avg', 'count', 'min', 'max']:
                        f_new = parts[1].upper() + '(' + parts[0] + ')'
                        flds.append(f_new)
                    else:
                        raise AttributeError("Aggregate function %s unknown" %
                            parts[1].upper)
                else:
                    raise AttributeError("Unknown field %s" % f)
            return flds

        return fields

    def key_used(self, name):
        return name in self.used_keys

    def key_add(self, name, value = None)
        n = name
        i = 1
        while n in self.used_keys.keys():
            n = "%s_%d" %(name, i)
            i = i +1
        self.used_keys[n] = value
        return n
