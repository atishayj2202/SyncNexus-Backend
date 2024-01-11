import os
from typing import Any, Callable, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy_cockroachdb import run_transaction


class CockroachDBClient:
    ENV_URL = "COCKROACH_DB_URL"

    def __init__(self, url: Optional[str] = None):
        self.url = url or os.environ[self.ENV_URL]
        self.engine = create_engine(self.url, max_overflow=100, pool_size=10)

    def get_session_maker(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def query(self, fn: Callable[[Session, ...], Any], **kwargs):
        return run_transaction(self.get_session_maker(), lambda s: fn(s, **kwargs))
