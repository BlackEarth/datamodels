from importlib import import_module
from .model import Model
from .util import nameify, classproperty


class SQLMixin:
    """
    Give SQL abilities (import and query-building) to a data Model,
    in conjunction with the sql-query library
    """
    SQL_DIALECT = None

    @classproperty
    def RELATION(cls):
        return nameify(cls.__name__).lower() + 's'

    @classproperty
    def PRIMARY_KEY(cls):
        """default primary key is a list with the first field name."""
        return list(cls.__dataclass_fields__.keys())[0:1]

    PK = PRIMARY_KEY

    def nopk(self, empty=False):
        """data that are not part of the PRIMARY_KEY"""
        return {k: v for k, v in self.items(empty=empty) if k not in self.PK}

    def pk(self):
        """data in the PRIMARY_KEY"""
        return {k: v for k, v in self.items() if k in self.PK}

    def sql(self,
            query=None,
            fields=None,
            relation=None,
            keys=None,
            updates=None,
            dialect=None,
            empty=True):
        SQL = import_module('sqlquery.sql').SQL
        query = query or []
        fields = fields or list(self.keys(empty=empty))
        relation = relation or self.RELATION
        keys = keys or [key for key in fields if key in self.PK]
        updates = updates or [key for key in fields if key not in self.PK]
        dialect = dialect or self.SQL_DIALECT
        return SQL(
            query=query or [],
            fields=fields,
            relation=relation,
            keys=keys,
            updates=updates,
            dialect=dialect)

