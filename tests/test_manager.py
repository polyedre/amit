#!/usr/bin/env python3

from unittest import TestCase
from amit.manager import Manager, Domain, Machine


class TestManager(TestCase):
    def test_initialise(self):
        """At initilisation, everything should be empty."""
        m = Manager()
        self.assertTrue(len(m.jobs) == 0)
        self.assertTrue(len(m.domains) == 0)
        self.assertTrue(len(m.machines) == 0)

    def test_add_domain(self):
        """Domain can be added properly."""
        m = Manager()
        m.add_domain("domain1.com", ["12.12.12.12"])
        self.assertTrue(len(m.domains) == 1)
        self.assertTrue(Domain("domain1.com") in m.domains)
        m.add_domain("domain2.com", ["12.12.12.12"])
        self.assertTrue(len(m.domains) == 2)
        self.assertTrue(Domain("domain1.com") in m.domains)
        self.assertTrue(Domain("domain2.com") in m.domains)

    def test_add_domain_different_ip(self):
        """When adding a domain that is already in the database, ips must be
        added."""
        m = Manager()
        m.add_domain("domain1.com", ["12.12.12.12"])
        self.assertTrue(len(m.domains) == 1)
        self.assertTrue(Domain("domain1.com") in m.domains)
        m.add_domain("domain1.com", ["12.12.12.13"])
        self.assertTrue(len(m.domains) == 1)
        self.assertTrue(Domain("domain1.com") in m.domains)

        domain = m.get_domain_by_name("domain1.com")
        self.assertTrue(domain.ips == set(["12.12.12.12", "12.12.12.13"]))

    def test_remove_domain(self):
        """Possible to remove a domain."""
        m = Manager()
        m.add_domain("domain1.com", ["12.12.12.12"])
        self.assertTrue(len(m.domains) == 1)
        self.assertTrue(Domain("domain1.com") in m.domains)
        m.remove_domain("domain1.com")
        self.assertTrue(len(m.domains) == 0)
        self.assertFalse(Domain("domain1.com") in m.domains)

    def test_add_machine(self):
        """Machine can be added properly."""
        m = Manager()
        m.add_machine("12.12.12.12", ["domain1.fr"])
        self.assertTrue(len(m.machines) == 1)
        self.assertTrue(Machine("12.12.12.12") in m.machines)
        m.add_machine("12.12.12.13", ["domain1.fr"])
        self.assertTrue(len(m.machines) == 2)
        self.assertTrue(Machine("12.12.12.12") in m.machines)
        self.assertTrue(Machine("12.12.12.13") in m.machines)

    def test_add_machine_different_domains(self):
        """When adding a machine that is already in the database, ips must be
        added."""
        m = Manager()
        m.add_machine("12.12.12.12", ["domain1.fr"])
        self.assertTrue(len(m.machines) == 1)
        self.assertTrue(Machine("12.12.12.12") in m.machines)
        m.add_machine("12.12.12.12", ["domain2.fr"])
        self.assertTrue(len(m.machines) == 1)
        self.assertTrue(Machine("12.12.12.12") in m.machines)

        machine = m.get_machine_by_ip("12.12.12.12")
        self.assertTrue(machine.domains == set(["domain2.fr", "domain1.fr"]))

    def test_remove_machine(self):
        """Possible to remove a machine."""
        m = Manager()
        m.add_machine("12.12.12.12", ["domain1.fr"])
        self.assertTrue(len(m.machines) == 1)
        self.assertTrue(Machine("12.12.12.12") in m.machines)
        m.remove_machine("12.12.12.12")
        self.assertTrue(len(m.machines) == 0)
        self.assertFalse(Machine("12.12.12.12") in m.machines)
