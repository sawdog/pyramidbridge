"""rethinkDB adapter

   The adpaters implement common functionality across databases for use within
   the platform. This is loosely pased on sqlalchemy ORM db implementations.

"""
import rethinkdb as r

from pyramidbridge.yamlcfg import yamlcfg
from pyramidbridge.utils import setup_logger

logger = setup_logger()

HOST = yamlcfg.rethinkdb.host
PORT = yamlcfg.rethinkdb.port
USER = yamlcfg.rethinkdb.user
PASSWORD = yamlcfg.rethinkdb.password
DB = yamlcfg.rethinkdb.smartthings.db

from .connection import Connection


class rethinkDBAdapter(object):
    """
       todo derive from a abse adapter which has all the interfaces defined.
    """
    __connection__ = None
    default_pageLength = 50
    pageLength = None
    start = None
    table = None

    def __init__(self, table, **kw):
        self.pageLength = kw.get('pageLength')
        self.start = kw.get('start')
        self.table = table
        self.query = r.table(table)
        self._set_pagination()
        # setup and necessary ordering
        self._set_sort_expressions()
        self._setup_order_by()

    def _setup_base_query(self, table=None):
        """Todo move to service; adapter"""
        if table is None:
            table = self.table

        self.query = r.table(table)

    def _setup_connection(self):
        """Todo establish the connection
        """
        self.__connection__ = Connection(HOST, PORT, USER, PASSWORD, DB)

    def _set_pagination(self):
        """if there are any pagination settings, add to the query"""
        pagelength = self.pageLength
        if pagelength is None:
            pagelength = self.default_pageLength

        query = self.query
        if self.pageLength == -1:
            # limit = self.cardinality_filtered
            # the above is what should be implemented - but until then...
            pagelength = self.pageLength

        query = query.limit(pagelength)

        start = self.start
        if start is not None:
            query = query.skip(start)

        self.query = query

    def _set_sort_expressions(self):
        pass

    def _setup_order_by(self):
        pass

    def add(self, item):
        """Add model to the db
           todo make models.....
        """
        table = item.get('table')
        self._setup_base_query(table)
        return self.query.insert(item).run(self.connection.session)

    @property
    def connection(self):
        """Todo: return the connection if it exists, create one or raise Error
            The view should just get the service/adapter - and all logic for
            managing that sould be encapsulated there.
        """
        if self.__connection__ is None:
            self._setup_connection()

        return self.__connection__

    def items(self):
        """get items from the table"""
        return self.query.run(self.connection.session)

