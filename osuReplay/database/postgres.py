__author__ = 'Ugrend'
import psycopg2
import psycopg2.extras
from osuReplay.config import Config
from osuReplay.logger import Logger

class Sql:

    def __init__(self, autocommit=True):
        database = Config.get('Database', 'database') or "osu"
        user = Config.get('Database', 'user') or "postgres"
        host = Config.get('Database', 'host') or "localhost"
        password = Config.get('Database', 'password') or ""
        self.conn = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'" %
                                     (database, user, host, password))
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        self.autocommit = autocommit

    def commit(self):
        self.conn.commit()

    def execute_query(self, query, params=None):
        try:
            self.cursor.execute(query, params)
            if self.autocommit:
                self.commit()
            result = [dict(x) for x in self.cursor.fetchall()]
            return result
        except psycopg2.ProgrammingError as e:
            Logger.WARN(str(e))
            return True
        except psycopg2.InternalError:
            self.rollback()
            self.execute_query(query, params)

    def rollback(self):
        self.conn.rollback()

    def close(self):
        try:
            self.conn.close()
        except AttributeError:
            # class hasnt created a db conection
            pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __del__(self):
        self.close()