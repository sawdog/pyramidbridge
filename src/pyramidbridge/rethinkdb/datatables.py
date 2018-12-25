"""Base API View"""
import rethinkdb as r
#from sqlalchemy import and_
#from sqlalchemy.exc import (IntegrityError,
#                            ProgrammingError,
#                            StatementError)
#
from pyramidbridge.views import API as Base
from pyramidbridge.yamlcfg import yamlcfg
from pyramidbridge.utils import setup_logger

from .adapter import rethinkDBAdapter

from .models import Binstore

HOST = yamlcfg.rethinkdb.host
PORT = yamlcfg.rethinkdb.port
USER = yamlcfg.rethinkdb.user
PASSWORD = yamlcfg.rethinkdb.password


BINSTORE_TABLEDATA = {
    'column_definitions': {},
    'model': Binstore,
    'db': 'binstore',
    'table': 'files',
    'default_sort': 'created',
}
[BINSTORE_TABLEDATA['column_definitions'].update({i[0]: i[1]})
 for i in enumerate(
    [{'title': 'ID', 'colattr': 'id', 'visible': False,
                            'global_search': False},
                           {'title': 'Title', 'colattr': 'title',
                            'global_search': True},
                           {'title': 'Filename', 'colattr': 'filename',
                            'global_search': True},
                           {'title': 'File', 'colattr': 'data',
                            'global_search': False, 'visible': False},
                           {'title': 'Created', 'colattr': 'created',
                            'global_search': False},
                           {'title': 'Modified', 'colattr': 'modified',
                            'global_search': False},
                           {'title': 'User ID', 'colattr': 'appuserid',
                            'global_search': True},
     ])
 ]

log = setup_logger()


class BaseUploadFileAdapter(rethinkDBAdapter):
        """
            Generic base adapter class; override _methods as necessary in sub
            classes.

            add
            :param record: tuple
            :return: status

            _failed_model_
            :param record: tuple
            :return: failed_model obj for storing in db table

            _model_
            :param record: tuple
            :return: model obj for storing in db table

            parse_records
            :param records: sequence of tuples

            add_records
            :param records: sequence of tuples


          Default behaviour is the file is stored in a binary store, with just
           a filename, title, name, created, modified, userid and blob

        """
        __db__ = None
        __failed_model__ = None
        __model__ = None
        __pcm_config__ = None
        __tabledata__ = None
        __table__ = None
        __customerid__ = None
        _connection_ = None
        _error_ = None
        _error_list_ = None
        _fileid_ = None
        _filename_ = None
        _record_ = None
        _default_sort_ = _listing_view_order_by = None
        _failed = None
        _failed_records = None
        _programid_ = None
        _success = None
        _total = None

        def __init__(self, request, fileid, filename, **kw):
            self._error_list_ = []
            self._filename_ = filename
            self._fileid_ = fileid
            self._failed = 0
            self._success = 0
            self._total = 0
            super(BaseUploadFileAdapter, self).__init__(request)

        def _model_(self, records):
            """
            Base implementation is not defined; a subclass to store the file
            uploaded in the correct location is required.

            :return: model obj

            """
            # model = self.__model__(record)
            # return model
            raise NotImplementedError

        def _setup_connection(self):
            """Handle setting up the session within the adapter for consistent
               use; all subclasses must implement this.
            """
            raise NotImplementedError

        def _add_record_(self, record):
            """How the db record is added can be abstracted here."""
            try:
                self.connection.add(self._model_(record))
                status = 0
            except Exception:
                self.connection.rollback()
                self._error_ = str(Exception)
                status = 1
                log.error(self._error_)

            return dict(code=status, error=self._error_)

        @property
        def customerid(self):
            return self.__customerid__

        def format_value(self, fmtrs, value, from_date_fmt=None):
            """

            :param fmt: String: name of the formatter to apply to the value,
                        from the possible functions in shawowutils.formatters
            :param value: String: value which is applied to the frmttrs
            :param from_fmt: String: Optional value used in date formatting
                             used to be able to parse the date from a string.
            :return: String: Formatted value
            """
            if from_date_fmt is None:
                return format_value(fmtrs, value)
            else:
                return format_value(fmtrs, value, from_date_fmt)

        def lookup_pcm_config(self):
            """return the pcm configuration if the process is associated with
               a program.
            """
            if self.programid:
                session = self.dataops_utils_connection
                query = session.query(PCM)\
                    .filter(and_(PCM.programid == self.programid,
                                 PCM.customerid == self.customerid)
                            )
                return query.one_or_none()

        def add(self, record):
            """Add the record to the database"""
            self._add_record_(record)

        @property
        def connection(self):
            """Return the connection; create a connection if it does not
               exist.
            """
            return self._setup_connection()

        @property
        def dataops_utils_connection(self):
            return self.request.unity

        @property
        def created(self):
            return r.now()

        modified = created

        @property
        def failed(self):
            """count of total failed records handled"""
            return self._failed

        @failed.setter
        def failed(self, value):
            """set value of failed record count"""
            self._failed = value

        @property
        def fileid(self):
            return self._fileid_

        def getrows(self, sheet, cols):
            """
            Iterate through the rows in the sheet.
            create a list of headers
            compare the headers from the sheet to passed in cols - and
            return mapping value to replace with table column name
            """
            self.__headers__ = headers = [c.value for c in sheet.rows[0] if c.value]
            for row in sheet.rows[1:]:
                d = dict(zip(headers, [c.value for c in row]))
                yield dict((k2, d[k1]) for k1, k2 in cols)

        @property
        def model(self):
            """create a model of the record to store in the database
            """
            return self.__model__

        def parse_records(self, file):
            """Default parser for records is .xlxs files; handle the parsing
               of the uploaded file. The default parser is for xlxs files
               This will yield the record, used for creating a database
               entry

               yeild record

               TODO: Add content-type sniffer so we can parse records smartly.

            """
            wb = load_workbook(filename=file)
            sheet = wb.active
            # headers = [c.value for c in sheet.rows[0] if c.value]
            # can't slice a generator; so need to start at row 2
            for row in sheet.iter_rows(min_row=2):
                record = [i.value for i in row]
                yield record

        @property
        def pcm(self):
            if self.__pcm_config__ is None:
                self.__pcm_config__ = self.lookup_pcm_config()

            return self.__pcm_config__

        @property
        def programid(self):
            return self._programid_

        @property
        def record(self):
            return self._record_

        @property
        def session(self):
            return self._setup_connection()

        @property
        def success(self):
            """"count of total successful records handled"""
            return self._success

        @success.setter
        def success(self, value):
            """"set value of total successful record count"""
            self._success = value

        @property
        def total(self):
            """count total records handled"""
            return self._total

        @total.setter
        def total(self, value):
            """"set value of total record count"""
            self._total = value

        @property
        def status(self):
            return self._status_


class RDBMSAdapter(BaseUploadFileAdapter):
    """Default storage of the adapter is an RDBMS"""
    __failed_model__ = None
    __model__ = None
    __tabledata__ = None
    __connection__ = None
    _error_ = None
    _fileid_ = None
    _filename_ = None
    _record_ = None
    _default_sort_ = _listing_view_order_by = None

    def __init__(self, request, fileid, filename, **kw):
        super(RDBMSAdapter, self).__init__(request, fileid, filename, **kw)

    def _setup_base_query_(self):
        pass

    def _setup_connection(self):
        """the RDBMS uses the unity session as its connection"""
        if self.__connection__ is None:
            self.__connection__ = self.request.unity

        return self.__connection__

    def _add_record(self, record=None):
        """Add the record to the db"""
        if record:
            self._record_ = record

        obj = self._model_(self.record)
        self.connection.add(obj)
        try:
            self.connection.commit()
            status = 0
        except (StatementError, ProgrammingError, IntegrityError,
                TypeError) as e:
            self._error_ = str(e)
            self.connection.rollback()
            self._failed_record()
            status = 1
            log.error(self._error_)
        return dict(code=status, error=self._error_)

    def _failed_record(self):
        """TODO set up to call function to get the **kw
           to pass into the Model's __init__
        """
        obj = self._failed_model_(self.record)

        try:
            self.connection.add(obj)
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            log.error(str(e))

    def add(self, record):
        return self._add_record(record)

    def add_records(self, records):
        """add bulk records"""
        failed_list = []
        failed = 0
        success = 0
        total = 0
        for record in records:
            total += 1
            # add records
            status = self.add(record)
            if status.get('code') == 0:
                success += 1
            else:
                failed += 1
                record = [json_dump_helper(i) for i in record]
                self._error_list_.append(status.get('error', ''))
                failed_list.append(record)

        self.failed = failed
        self.success = success
        self.total = total
        self._failed_records = failed_list

    def _failed_model_(self, record):
        """
           create the failed model if adding fails
        """
        return self.__failed_model__(record)


class RethinkDBAdapter(rethinkDBAdapter):
    """Base RethinkDB file adapter for handling uploads"""
    __connection__ = None
    __db__ = BINSTORE_TABLEDATA['db']
    __failed_model__ = None
    __headers__ = None
    __model__ = None
    __tabledata__ = BINSTORE_TABLEDATA
    __table__ = BINSTORE_TABLEDATA['table']
    _error_ = None
    _fileid_ = None
    _filename_ = None
    _record_ = None
    _default_sort_ = BINSTORE_TABLEDATA['default_sort']
    _listing_view_order_by = order_by = BINSTORE_TABLEDATA['default_sort']

    def __init__(self, request, fileid, filename, **kw):
        super(RethinkDBAdapter, self).__init__(request, fileid, filename, **kw)
        self.__connection__ = self._setup_connection()
        self.__customerid__ = kw.get('customerid')

    def _set_sort_expressions(self):
        """Construct the query: sorting.
        rethinkDB sorting is different and without writing an SQLAlchemy
        integration - we'll just map the behavior here. Eventually this will be
        a wrapper around rethinkDB within dataTables

        In rethink column is a string; not an object as it is in SQLAlchemy
        so the direction gets applied as asc('column_name')

        coumpound ordering is simply: order_by('foo', desc('bar')..)

        """
        def set_column_sort_dir(column, direction):
            """since we are applying direction as a function, it's just a
               getattr and then pass the column name string to that function.
            """
            if direction in ('asc', 'desc'):
                column = getattr(r, direction)(column)
            else:
                raise ValueError(
                    'Invalid order direction: {}'.format(direction))
            return column

        apply_default = True
        sort_expressions = []

        # when sorting via the DataTable happens, we lose the initial
        # default sort order; we still want that applied - so when being
        # called after an initial load, grab the order from the view and set
        # it also.
        sort_column = self.column_definitions[self.default_sort_column]
        default_colname = sort_column and sort_column['colattr']

        for n in self.tableparams.get('order', []):
            column_index = int(n.get('column'))
            col = self.column_definitions[column_index]
            direction = n.get('dir', self.default_sort_dir)
            sortcol = col.get('sortattr')
            if sortcol:
                colname = sortcol
            else:
                colname = col.get('colattr')

            if colname == default_colname:
                apply_default = False

            column = colname

            column = set_column_sort_dir(column, direction)

            # XXX not sure how rethinkDB handles nulls explicitly;
            # by default in sorting compound values (e.g. fields with differemt
            # Types - rethink will sort on their Type name first letter:
            # Array, Boolean, .. None, String, etc. This is very unexpected
            # sorting when multiple types in a field.
            if col.get('nulls_order'):
                if col.get('nulls_order') == 'nullsfirst':
                    column = column.nullsfirst()
                elif col.get('nulls_order') == 'nullslast':
                    column = column.nullslast()
                else:
                    raise ValueError(
                        'Invalid order direction: %s'.format(direction))

            sort_expressions.append(column)
        if apply_default:
            default_column = default_colname
            default_direction = self.default_sort_dir
            default_column = set_column_sort_dir(default_column,
                                                 default_direction)
            sort_expressions.append(default_column)

        self.sort_expressions = sort_expressions

    def _model_(self, **record):
        """
        Default implementation is to store the file uploaded in the binstore
        :param record: list
        :return: model obj

        """
        obj = self.__model__(**record)
        return obj


    def _setup_filters(self):
        pass

    @property
    def cardinality(self):
        if self._cardinality_ is None:
            try:
                self._cardinality_ = self.query.count().run(self.conn)
            except (KeyError, TypeError):
                return 0

        return self._cardinality_

    @property
    def cardinality_filtered(self):
        """XXX not working currently.
           TODO: implement cardinality when filtering

        """
        return self.cardinality

    @property
    def conn(self):
        """return the actual rethinkdb.connection returned from::
           rethinkdb.connect(...)

        """
        return self.__connection__.session

    def datatable_response(self):
        """ build response data set for the
            json / ajax interface for a DataTable
        """
        # execute results query
        results = self.render_results()

        # DataTables expected response.attr format
        data = {'data': results.get('data'),
                'draw': self.draw,
                'recordsTotal': self.cardinality,
                'recordsFiltered': self.cardinality_filtered,
                'displayLength': self.pagelength,
                'displayStart': self.displaystart,
                'success': 'success',
                }
        return data

    @property
    def db(self):
        return self.__db__

    @property
    def model_headers(self):
        """
        Generate the string of headers for passing into named tuple - which
        is then used to pass in dict to populate the object
        :return: String e.g 'uid,customerid,name,created,modified'
        """
        return ','.join(self.__headers__)

    @property
    def session(self):
        return r

    @property
    def table(self):
        return self.__table__


class BinstoreFileStoreAdapter(RethinkDBAdapter):
    """Adapter to just store the upload in database as a binary
    """

    def add_records(self, records):
        total = 0
        record_list = []
        for i in records:
            total += 1
            record_list.append(self.transform(i))
        self.__records__ = record_list
        session = self.session
        try:
            self.success = total
            session.table(self.table).insert(
                self.__records__
            ).run(self.conn)
        except total:
            self.failed = total

        finally:
            self.connection.close()

    def parse_records(self, file):
        """Just return the file..."""
        yield file

    def transform(self, data):
        """for now, just return data"""

        trans = {'title': self._filename_,
                'filename': self._filename_,
                'file':r.binary(data.read()),
                'created': self.created,
                'modified': self.modified,
                'appuserid': self.request.user.uid}

        return trans

