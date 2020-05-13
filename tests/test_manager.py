#!/usr/bin/env python3

from unittest import TestCase
from amit.manager import Manager, Domain, Machine


class TestManager(TestCase):
    def test_initialise(self):
        """At initilisation, everything should be empty."""
        m = Manager()
        self.assertTrue(len(m.jobs) == 0)
        self.assertTrue(len(m.targets) == 0)
        self.assertTrue(len(m.machines) == 0)

    def test_add_target(self):
        """Target can be added properly."""
        m = Manager()
        m.add_target("domain1.com", ["12.12.12.12"])
        self.assertTrue(len(m.targets) == 1)
        self.assertTrue(Domain("domain1.com") in m.targets)
        m.add_target("domain2.com", ["12.12.12.12"])
        self.assertTrue(len(m.targets) == 2)
        self.assertTrue(Domain("domain1.com") in m.targets)
        self.assertTrue(Domain("domain2.com") in m.targets)

    def test_add_target_different_ip(self):
        """When adding a target that is already in the database, ips must be
        added."""
        m = Manager()
        m.add_target("domain1.com", ["12.12.12.12"])
        self.assertTrue(len(m.targets) == 1)
        self.assertTrue(Domain("domain1.com") in m.targets)
        m.add_target("domain1.com", ["12.12.12.13"])
        self.assertTrue(len(m.targets) == 1)
        self.assertTrue(Domain("domain1.com") in m.targets)

        domain = m.get_target_by_name("domain1.com")
        self.assertTrue(domain.ips == set(["12.12.12.12", "12.12.12.13"]))

    def test_remove_target(self):
        """Possible to remove a target."""
        m = Manager()
        m.add_target("domain1.com", ["12.12.12.12"])
        self.assertTrue(len(m.targets) == 1)
        self.assertTrue(Domain("domain1.com") in m.targets)
        m.remove_target("domain1.com")
        self.assertTrue(len(m.targets) == 0)
        self.assertFalse(Domain("domain1.com") in m.targets)

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
