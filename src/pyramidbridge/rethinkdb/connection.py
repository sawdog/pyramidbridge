"""rethinkDB connection"""
import rethinkdb as r


class Connection(object):
    """RethinkDB Connection handler"""
    __connection__ = None
    __db__ = None
    __host__ = None
    __port__ = None
    __user__ = None
    __password__ = None
    __session__ = None
    __table__ = None

    def __init__(self,
                 host,
                 port,
                 user,
                 password,
                 db,
                 **kw):
        self.__db__ = db
        self.__host__ = host
        self.__password__ = password
        self.__port__ = port
        self.__user__ = user
        self.__table__ = kw.get('table')
        self._setup_connection(**kw)

    def _setup_connection(self, **kw):
        if self.__connection__ is None:
            self.__connection__ = r.connect(host=self.host,
                                            port=self.port,
                                            user=self.user,
                                            password=self.password,
                                            db=self.db,
                                            **kw)

    @property
    def db(self):
        return self.__db__

    @property
    def host(self):
        return self.__host__

    @property
    def password(self):
        return self.__password__

    @property
    def port(self):
        return self.__port__

    @property
    def session(self):
        """get the connection to the database"""
        if self.__connection__ == None:
            self._setup_connection()

        return self.__connection__

    @property
    def table(self):
        return self.__table__

    @property
    def user(self):
        return self.__user__

    def close(self):
        if self.__session__:
            self.session.close()

    def remove(self):
        """close and remove the connection"""
        self.close()
        self.__connection__ = None

    def commit(self):
        """call run on the db"""
        return

    def open(self):
        """
          close the connection if it is open
          reopen a new connection to the DB"""
        self.session.reconnect()

    @property
    def connect(self):
        """make the connection; create a connection if it does not
          exist.
        """
        self._setup_connection()

    @property
    def created(self):
        return r.now()

    modified = created

    @property
    def model(self):
        """create a model of the record to store in the database
        """
        return self.__model__

    @property
    def r(self):
        return r
