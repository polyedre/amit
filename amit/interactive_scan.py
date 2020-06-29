#!/usr/bin/env python3

import argparse
from .database import Service, Machine, Domain, Job, User, Group
from .jobs import scan_machines_job, scan_domains_job


class InteractiveArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        print(message, end="")


scan_parser = InteractiveArgumentParser(prog="scan", description="Scan elements")
scan_subparser = scan_parser.add_subparsers(
    title="elements", help="Type of elements to scan", prog="element", dest="element"
)

machine_parser = scan_subparser.add_parser("machines", help="scan ports in machines")
machine_parser.add_argument("ids", type=int, nargs="+")

domain_parser = scan_subparser.add_parser("domains", help="scan domain for subdomains")
domain_parser.add_argument("ids", type=int, nargs="+")

service_parser = scan_subparser.add_parser("services", help="scan services")
service_parser.add_argument("ids", type=int, nargs="+")


def interactive_scan(arg, session):
    args = arg.split(" ")
    if "" in args:
        args.remove("")

    scan_namespace = scan_parser.parse_args(args)

    scan_elements = {
        "machines": scan_machines,
        "domains": scan_domains,
        "service": scan_services,
    }

    for name, function in scan_elements.items():
        if scan_namespace.element == name:
            function(scan_namespace, session)


def scan_machines(namespace, session):
    scan_machines_job(namespace.ids, session)


def scan_services(namespace, session):
    print("Not implemented")


def scan_domains(namespace, session):
    scan_domains_job(namespace.ids, session)
