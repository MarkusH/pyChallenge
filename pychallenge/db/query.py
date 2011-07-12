# -*- coding: utf-8 -*-
from pychallenge.conf import settings
from pychallenge.db import fields


class KeyTable():

    def __init__(self):
        self.keys = {}

    def __repr__(self):
        return str(self.keys)

    def used(self, name):
        return name in self.keys.keys()

    def add(self, name, value=None):
        n = name
        i = 1
        while n in self.keys.keys():
            n = "%s_%d" % (name, i)
            i = i + 1
        self.keys[n] = value
        return n

    def get(self):
        return self.keys

    def __iter__(self):
        self.index = 0
        self.length = len(self.keys.keys())
        return self

    def __len__(self):
        return len(self.keys)

    def __next__(self):
        if self.index < self.length:
            value = self.keys.items[self.index]
            self.index += 1
            return value
        raise StopIteration


class Query():
    """
    http://www.sqlite.org/lang_select.html
    """

    QTYPE_SELECT = 1
    QTYPE_INSERT = 2
    QTYPE_UPDATE = 3
    QTYPE_DELETE = 4
    QTYPE_CREATE = 5
    QTYPE_TRUNCATE = 6
    QTYPE_DROP = 7

    AGGREGATE = ['avg', 'count', 'min', 'max']

    def __init__(self, qtype, modelfields, **kwargs):
        """

        """

        self.qtype = qtype
        self.modelfield_names = modelfields.keys()
        self.modelfields = modelfields
        self.key_table = KeyTable()
        self.dry_run = kwargs.get('dry_run', False)
        self.filter_fields = []
        self.select_fields = []
        self.limit_expression = ""

        if not kwargs.get('table', None):
            raise AttributeError("Missing table definition")
        self.table = kwargs.pop('table')

        if self.qtype == Query.QTYPE_SELECT:
            self._select(**kwargs)

        elif self.qtype == Query.QTYPE_INSERT:
            pass

        elif self.qtype == Query.QTYPE_UPDATE:
            self._update(**kwargs)

        elif self.qtype == Query.QTYPE_DELETE:
            self._delete(**kwargs)

        elif self.qtype == Query.QTYPE_CREATE:
            pass

        elif self.qtype == Query.QTYPE_TRUNCATE:
            pass

        elif self.qtype == Query.QTYPE_DROP:
            pass

        else:
            raise AttributeError("qtype must be one of QTYPE_SELECT, "
                "QTYPE_INSERT, QTYPE_UPDATE, QTYPE_DELETE, "
                "QTYPE_CREATE", "QTYPE_TRUNCATE", "QTYPE_DROP")

    def run(self):
        """
        Call this method to build the actual query.
        """

        def match(x):
            """
            Helper function to create update statement - check for NOT
            :py:func:`pychallenge.db.models.Model.pk`

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

        if self.qtype == Query.QTYPE_SELECT:
            statement = "SELECT %(_fields)s FROM %(_table)s"
            replace = {
                '_fields': ", ".join(self.select_fields),
                '_table': self.table,
            }
            if self.filter_fields:
                self.join_and()
                statement += " WHERE %(_filter)s"
                replace['_filter'] = self.filter_fields[0]

            statement += self.limit_expression

        elif self.qtype == Query.QTYPE_INSERT:
            statement = "INSERT INTO %(_table)s (%(_fs)s) VALUES (%(_vs)s)"
            ff = {}
            for k, f in self.modelfields.iteritems():
                if isinstance(f, fields.PK):
                    continue
                ff[k] = ":%s" % k
                self.key_table.add(name=k, value=f.value)

            replace = {
                '_table': self.table,
                '_fs': ", ".join(ff.keys()),
                '_vs': ", ".join(ff.values())}

        elif self.qtype == Query.QTYPE_UPDATE:
            statement = "UPDATE %(_table)s SET %(_fields)s WHERE %(_pk)s"
            ff = {}
            for k, f in self.modelfields.iteritems():
                ff["%s__eq" % k] = f.value

            replace = {
                '_table': self.table,
                '_pk': "%s = :%s__eq" % (self.pk, self.pk),
                '_fields': ", ".join(self._get_filter_fields(**ff))}

        elif self.qtype == Query.QTYPE_DELETE:
            statement = "DELETE FROM %(_table)s WHERE %(_pk)s"
            replace = {
                '_table': self.table,
                '_pk': "%s = :%s" % (self.pk, self.pk)}
            self.key_table.add(self.pk, self.modelfields[self.pk].value)

        elif self.qtype == Query.QTYPE_CREATE:
            statement = "CREATE TABLE `%(_table)s` (%(_fields)s);"
            flds = []
            for f, i in self.modelfields.iteritems():
                if isinstance(i, fields.Numeric):
                    flds.append("`%s` NUMERIC" % f)
                elif isinstance(i, fields.Text):
                    flds.append("`%s` TEXT" % f)
                elif isinstance(i, fields.PK):
                    flds.append("`%s` INTEGER PRIMARY KEY" % f)
            replace = {
                '_table': self.table,
                '_fields': ", ".join(flds),
            }

        elif self.qtype == Query.QTYPE_TRUNCATE:
            statement = "DELETE FROM %(_table)s"
            replace = {'_table': self.table}

        elif self.qtype == Query.QTYPE_DROP:
            statement = "DROP TABLE %(_table)s"
            replace = {'_table': self.table}

        if self.dry_run:
            print statement % replace
            if settings.SETTINGS['DEBUG']:
                if self.key_table:
                    print self.key_table
            return None
        elif settings.SETTINGS['DEBUG']:
            print statement % replace
            if self.key_table:
                print self.key_table
        return (statement % replace, self.key_table.get())

    def filter(self, **kwargs):
        """
        Use `filer` for specifying the `WHERE`-clause of the SQL statement.
        All statements are combined by `AND`.

        :param kwargs: use the model fields as parameter names and assign
            them a value. Additionally you may append `__lt`, `__le`, `__eq`,
            `__ge`, `__gt` to the fieldname for `<`, `<=`, `=`, `>=`, `>`.
            Use `__in` and `__nin` and assign either a `list` or a `tuple` for
            `IN` or `NOT IN`.
        """
        ff = self._get_filter_fields(**kwargs)
        if ff:
            tmp = "(" + " AND ".join(ff) + ")"
            self.filter_fields.append(tmp)
        return self

    def filter_or(self, **kwargs):
        """
        See :py:func:`pychallenge.db.db.Query.filter`.
        The only difference is the combination `OR`.
        """
        ff = self._get_filter_fields(**kwargs)
        if ff:
            tmp = "(" + " OR ".join(ff) + ")"
            self.filter_fields.append(tmp)
        return self

    def join_and(self):
        """
        use this function to concat filter expressions with *AND*
        """
        if len(self.filter_fields) > 1:
            tmp = "(" + " AND ".join(self.filter_fields) + ")"
            self.filter_fields = [tmp]
        return self

    def join_or(self):
        """
        use this function to concat filter expressions with *OR*
        """
        if len(self.filter_fields) > 1:
            tmp = "(" + " OR ".join(self.filter_fields) + ")"
            self.filter_fields = [tmp]
        return self

    def limit(self, count, offset=None):
        if offset:
            self.limit_expression = " LIMIT %d, %d" % (count, offset)
        else:
            self.limit_expression = " LIMIT %d" % count
        return self

    def _select(self, **kwargs):
        """

        """
        self.select_fields += self._get_select_fields(self.modelfield_names,
             aggregate=True)
        # unique `self.select_fields`
        tmp = {}
        for e in self.select_fields:
            tmp[e] = 1
        self.select_fields = tmp.keys()
        self.select_fields.sort()

    def _update(self, **kwargs):
        """

        """
        if 'pk' in kwargs.keys():
            self.pk = kwargs.pop('pk')
        else:
            raise AttributeError("Updating a model needs an existing PK!")

    def _delete(self, **kwargs):
        """

        """
        if 'pk' in kwargs.keys():
            self.pk = kwargs.pop('pk')
        else:
            raise AttributeError("Updating a model needs an existing PK!")

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
            'nin': 'NOT IN'}
        flds = []
        # iterate over all given filter fields
        for f, v in kwargs.iteritems():

            # split the filter comparison
            parts = f.split('__')

            # if no comparison is specified act as __eq
            if len(parts) == 1 and parts[0] in self.modelfield_names:
                n = self.key_table.add(name=f, value=v)
                flds.append(build(parts[0], n, op['eq']))

            # there is a concrete comparison
            elif len(parts) == 2 and parts[0] in self.modelfield_names:

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
                if len(parts) == 1 and parts[0] in self.modelfield_names:
                    flds.append(f)

                # build the aggregation sql string for the agg. function
                elif len(parts) == 2 and parts[0] in self.modelfield_names:
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
        # fields are allowed (along to self.modelfield_names)
        else:
            for f in fields:
                if f in self.modelfield_names:
                    flds.append(f)
                else:
                    raise AttributeError("Unknown field %s" % f)
        return flds
