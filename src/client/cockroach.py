import os
from typing import Any, Callable, Optional

import sqlalchemy
from sqlalchemy.orm import Session, sessionmaker


class CockroachDBClient:
    ENV_URL = "COCKROACH_DB_URL"

    def __init__(self, url: Optional[str] = None):
        # self.url = url or os.environ[self.ENV_URL]
        self.db_name = os.environ["DB_NAME"]
        self.db_user = os.environ["DB_USER"]
        self.db_pass = os.environ["DB_PASS"]
        self.unix_socket_path = os.environ["UNIX_SOCKET_PATH"]
        self.engine = sqlalchemy.create_engine(
            sqlalchemy.engine.url.URL.create(
                drivername="postgresql+pg8000",
                username=self.db_user,
                password=self.db_pass,
                database=self.db_name,
                query={"unix_sock": f"{self.unix_socket_path}/.s.PGSQL.5432"},
            )
        )

    def get_session_maker(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def query(self, fn: Callable[[Session, ...], Any], **kwargs):
        # Instead of using run_transaction, directly execute the provided function
        session = self.get_session_maker()()
        try:
            result = fn(session, **kwargs)
            session.commit()
            return result
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
