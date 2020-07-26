#!/usr/bin/env python3

from unittest import TestCase
from amit.database import (
    add_machine,
    add_domain,
    add_service,
    Machine,
    Service,
    Domain,
    Job,
)
from amit.database import Base
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker, scoped_session


class TestDatabase(TestCase):
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
        self.s.query(Machine).all()
        self.s.query(Service).all()
        self.s.query(Domain).all()
        self.s.query(Job).all()

    def test_add_domain(self):
        """Domain can be added properly."""

        # Adding a domain
        d = add_domain(self.s, "domain1.com")
        res = self.s.query(Domain).filter(Domain.name == d.name).first()
        self.assertEqual(d.id, res.id)
        self.s.commit()

        # Adding an already existing domain
        d = add_domain(self.s, "domain1.com")
        res = self.s.query(Domain).filter(Domain.name == d.name).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.s.commit()

        # Adding a domain with an ip
        machine = add_machine(self.s, "12.12.12.12")
        add_domain(self.s, "domain1.com", machines=[machine])
        res = self.s.query(Domain).filter(Domain.name == d.name).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.assertTrue(machine in res[0].machines)
        self.assertEqual(res[0].machines[0].id, machine.id)

        res = self.s.query(Machine).filter(Machine.id == machine.id).first()
        self.assertEqual(res, machine)

        # Adding a domain with another ip
        machine = add_machine(self.s, "12.12.12.13")
        add_domain(self.s, "domain1.com", machines=[machine])
        res = self.s.query(Domain).filter(Domain.name == d.name).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.assertEqual(len(res[0].machines), 2)

        res = self.s.query(Machine).filter(Machine.id == machine.id).first()
        self.assertEqual(res, machine)

    def test_add_machine(self):
        """Machine can be added properly."""

        # Adding a machine
        d = add_machine(self.s, "12.12.12.12")
        res = self.s.query(Machine).filter(Machine.ip == d.ip).first()
        self.assertEqual(d.id, res.id)

        # Adding an already existing machine
        d = add_machine(self.s, "12.12.12.12")
        res = self.s.query(Machine).filter(Machine.ip == d.ip).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)

        # Adding a machine with a domain
        domain = add_domain(self.s, "domain1.com")
        d = add_machine(self.s, "12.12.12.12", domains=[domain])
        res = self.s.query(Machine).filter(Machine.ip == d.ip).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.assertTrue(domain in res[0].domains)
        self.assertEqual(res[0].domains[0].id, domain.id)

        res = self.s.query(Domain).filter(Domain.id == domain.id).first()
        self.assertEqual(res, domain)

        # Adding a machine with another domain
        domain = add_domain(self.s, "domain2.com")
        d = add_machine(self.s, "12.12.12.12", domains=[domain])
        res = self.s.query(Machine).filter(Machine.ip == d.ip).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.assertEqual(len(res[0].domains), 2)

        res = self.s.query(Domain).filter(Domain.id == domain.id).first()
        self.assertEqual(res, domain)

    def test_add_service(self):
        """Service can be added properly."""

        # Adding a service
        machine = add_machine(self.s, "12.12.12.12")
        s = add_service(self.s, 80, "http", machine, product="apache", version="2.3.4")
        res = (
            self.s.query(Service)
            .join(Machine)
            .filter(Service.port == s.port, Machine.id == machine.id)
            .first()
        )
        self.assertEqual(res.port, 80)
        self.assertEqual(res.name, "http")

        # Adding an already existing service
        s = add_service(self.s, 80, "http", machine)
        res = (
            self.s.query(Service)
            .join(Machine)
            .filter(and_(Service.port == s.port, Machine.id == machine.id))
            .all()
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(s.id, res[0].id)

        # Adding an identical service with another machine
        machine = add_machine(self.s, "12.12.12.13")
        s2 = add_service(self.s, 80, "http", machine, product="apache", version="2.3.4")
        res = (
            self.s.query(Service)
            .join(Machine)
            .filter(Service.port == s2.port, Machine.id == machine.id)
            .first()
        )
        self.assertEqual(res.port, 80)
        self.assertEqual(res.name, "http")
        self.assertNotEqual(s2.id, s.id)
