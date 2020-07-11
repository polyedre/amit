#!/usr/bin/env python3

from .interactive import start_shell
from .database import Base, Job
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


def main():
    session = scoped_session(sessionmaker())
    engine = create_engine("sqlite:///amit.sqlite")
    session.configure(bind=engine)
    Base.metadata.create_all(engine)
    try:
        start_shell(session)
    except KeyboardInterrupt:
        session().update(Job).values(status="DONE")
