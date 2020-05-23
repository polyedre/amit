#!/usr/bin/env python3

from unittest import TestCase
from amit.manager import Manager, Domain, Host


class TestManager(TestCase):
    def test_initialise(self):
        """At initilisation, everything should be empty."""
        m = Manager()
        self.assertTrue(len(m.jobs) == 0)
        self.assertTrue(len(m.domains) == 0)
        self.assertTrue(len(m.hosts) == 0)

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

    def test_add_host(self):
        """Host can be added properly."""
        m = Manager()
        m.add_host("12.12.12.12", ["domain1.fr"])
        self.assertTrue(len(m.hosts) == 1)
        self.assertTrue(Host("12.12.12.12") in m.hosts)
        m.add_host("12.12.12.13", ["domain1.fr"])
        self.assertTrue(len(m.hosts) == 2)
        self.assertTrue(Host("12.12.12.12") in m.hosts)
        self.assertTrue(Host("12.12.12.13") in m.hosts)

    def test_add_host_different_domains(self):
        """When adding a host that is already in the database, ips must be
        added."""
        m = Manager()
        m.add_host("12.12.12.12", ["domain1.fr"])
        self.assertTrue(len(m.hosts) == 1)
        self.assertTrue(Host("12.12.12.12") in m.hosts)
        m.add_host("12.12.12.12", ["domain2.fr"])
        self.assertTrue(len(m.hosts) == 1)
        self.assertTrue(Host("12.12.12.12") in m.hosts)

        host = m.get_host_by_ip("12.12.12.12")
        self.assertTrue(host.domains == set(["domain2.fr", "domain1.fr"]))

    def test_remove_host(self):
        """Possible to remove a host."""
        m = Manager()
        m.add_host("12.12.12.12", ["domain1.fr"])
        self.assertTrue(len(m.hosts) == 1)
        self.assertTrue(Host("12.12.12.12") in m.hosts)
        m.remove_host("12.12.12.12")
        self.assertTrue(len(m.hosts) == 0)
        self.assertFalse(Host("12.12.12.12") in m.hosts)

    def test_hosts_from_targets(self):
        """Get hosts from targets name."""
        m = Manager()
        m.add_host("12.12.12.12", [Domain("domain1.fr")])
        m.add_host("12.12.12.13", [Domain("domain2.fr")])
        m.add_host("12.12.12.14", [Domain("domain1.fr")])
        m.add_host("12.12.12.15", [Domain("domain1.fr")])
        m.add_host("12.12.12.16", [Domain("domain3.fr")])
        hosts_1 = m.hosts_from_targets(["12.12.12.12"])
        self.assertEqual(hosts_1, [Host("12.12.12.12")], "One host found")
        hosts_2 = m.hosts_from_targets(["domain1.fr"])
        self.assertEqual(
            set(hosts_2),
            set([Host("12.12.12.12"), Host("12.12.12.15"), Host("12.12.12.14"),]),
            "Host from domain",
        )
        hosts_3 = m.hosts_from_targets(["domain3.fr", "12.12.12.16"])
        self.assertEqual(
            set(hosts_3), set([Host("12.12.12.16")]), "Multiple targets but one host",
        )
        hosts_4 = m.hosts_from_targets(["domain4.fr", "12.12.12.17"])
        self.assertEqual(
            set(hosts_4), set(), "No target found",
        )
