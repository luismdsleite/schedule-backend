import pymysql


class Database:
    """Database connection class."""

    def __init__(self, config):
        self.__host = config.DB_HOST
        self.__username = config.DB_USER
        self.__password = config.DB_PASSWD
        self.__port = int(config.DB_PORT)
        self.__dbname = config.DB_NAME
        self.__connect_timeout = config.CONNECT_TIMEOUT
        self.__conn = None
        self.__open_connection()

    def __del__(self):
        self.close_connection()

    def __open_connection(self):
        """Connect to MySQL Database."""
        try:
            if self.__conn is None:
                self.__conn = pymysql.connect(
                    host=self.__host,
                    port=self.__port,
                    user=self.__username,
                    passwd=self.__password,
                    db=self.__dbname,
                    connect_timeout=self.__connect_timeout
                )
        except pymysql.MySQLError as sqle:
            raise pymysql.MySQLError(
                f'Failed to connect to the database due to: {sqle}')
        except Exception as e:
            raise Exception(f'An exception occured due to: {e}')

    @property
    def db_connection_status(self):
        """Returns the connection status"""
        return True if self.__conn is not None else False

    def close_connection(self):
        """Close the DB connection."""
        try:
            if self.__conn is not None:
                self.__conn.close()
                self.__conn = None
        except Exception as e:
            raise Exception(
                f'Failed to close the database connection due to: {e}')

    def run_query(self, query, get_id=False, args=tuple()):
        """Execute SQL query."""
        try:

            if not query or not isinstance(query, str):
                raise Exception()

            if not self.__conn:
                self.__open_connection()
            with self.__conn.cursor() as cursor:
                cursor.execute(query, args)

                if 'SELECT' in query.upper():
                    # Extract row headers
                    row_headers = [x[0] for x in cursor.description]
                    rv = cursor.fetchall()
                    json_data = []
                    for result in rv:
                        json_data.append(dict(zip(row_headers, result)))
                    result = json_data
                else:
                    self.__conn.commit()
                    if 'INSERT' in query.upper():
                        result = {"id": cursor.lastrowid}
                    else:
                        result = {}
                cursor.close()

                return result
        except pymysql.MySQLError as sqle:
            raise pymysql.MySQLError(f'Failed to execute query due to: {sqle}')
        except Exception as e:
            raise Exception(f'An exception occured due to: {e}')

    def get_connection(self):
        """Returns the connection object."""
        if not self.__conn:
            self.__open_connection()
        return self.__conn
