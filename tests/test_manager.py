#!/usr/bin/env python3

from unittest import TestCase
from amit.database import (
    add_machine,
    add_domain,
    add_service,
    add_serviceinfo,
    Machine,
    Service,
    Domain,
    Job,
    ServiceInfo,
)
from amit.database import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


class TestManager(TestCase):
    def setUp(self):
        session = scoped_session(sessionmaker())
        engine = create_engine("sqlite:///tests/amit.sqlite")
        session.configure(bind=engine)
        Base.metadata.create_all(engine, checkfirst=True)
        self.s = session()

    def test_initialise(self):
        """At initilisation, everything should be empty."""
        self.s.query(Machine).all()
        self.s.query(Service).all()
        self.s.query(Domain).all()
        self.s.query(Job).all()
        self.s.query(ServiceInfo).all()

    def test_add_domain(self):
        """Domain can be added properly."""

        # Adding a domain
        d = add_domain(self.s, "domain1.com")
        res = self.s.query(Domain).filter(Domain.name == d.name).first()
        self.assertEqual(d.id, res.id)

        # Adding an already existing domain
        d = add_domain(self.s, "domain1.com")
        res = self.s.query(Domain).filter(Domain.name == d.name).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)

        # Adding a domain with an ip
        machine = Machine(ip="12.12.12.12")
        add_domain(self.s, "domain1.com", machines=[machine])
        res = self.s.query(Domain).filter(Domain.name == d.name).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.assertEqual(len(res[0].machines), 1)
        self.assertEqual(res[0].machines[0].id, machine.id)

        res = self.s.query(Machine).filter(Machine.id == machine.id).first()
        self.assertEqual(res, machine)

        # Adding a domain with another ip
        machine = Machine(ip="12.12.12.13")
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
        domain = Domain(name="domain1.com")
        d = add_machine(self.s, "12.12.12.12", domains=[domain])
        res = self.s.query(Machine).filter(Machine.ip == d.ip).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.assertEqual(len(res[0].domains), 1)
        self.assertEqual(res[0].domains[0].id, domain.id)

        res = self.s.query(Domain).filter(Domain.id == domain.id).first()
        self.assertEqual(res, domain)

        # Adding a machine with another domain
        domain = Domain(name="domain2.com")
        d = add_machine(self.s, "12.12.12.12", domains=[domain])
        res = self.s.query(Machine).filter(Machine.ip == d.ip).all()
        self.assertEqual(len(res), 1)
        self.assertEqual(d.id, res[0].id)
        self.assertEqual(len(res[0].domains), 2)

        res = self.s.query(Domain).filter(Domain.id == domain.id).first()
        self.assertEqual(res, domain)
