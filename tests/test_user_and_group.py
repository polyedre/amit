#!/usr/bin/env python3

from unittest import TestCase
from amit.database import add_user, add_group, User, Group
from amit.database import Base
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session


class TestUserAndGroup(TestCase):
    def setUp(self):
        session = scoped_session(sessionmaker())
        engine = create_engine("sqlite:///tests/amit.sqlite")
        session.configure(bind=engine)
        Base.metadata.create_all(engine, checkfirst=True)
        self.s = session()

    def tearDown(self):
        self.s.commit()

    def test_initialise(self):
        """At initilisation, everything should be empty."""
        self.s.query(User).all()
        self.s.query(Group).all()

    def test_add_user(self):
        """Domain can be added properly."""
        u = add_user(self.s, name="Sally Morgan")
        res = self.s.query(User).filter(User.name == u.name).first()
        self.assertEqual(u.id, res.id)
        self.s.commit()

        u.email = "smorgan@MEGABANK.LOCAL"

        u2 = add_user(self.s, name="Ray O'Leary", pseudo="roleary")
        res = self.s.query(User).filter(User.name == u2.name).first()
        self.assertEqual(u2.id, res.id)
        self.s.commit()

    def test_add_group(self):
        # Adding an already existing domain
        g = add_group(self.s, name="New York")
        res = self.s.query(User).filter(Group.name == g.name).first()
        self.assertEqual(g.id, res.id)
        self.s.commit()

        smorgan = User(name="Sally Morgan", pseudo="smorgan")
        g.users.append(smorgan)
