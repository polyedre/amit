#!/usr/bin/env python3

import argparse
from .database import Service, Machine, Domain, Job, User, Group


class InteractiveArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        print(message, end="")


show_parser = InteractiveArgumentParser(prog="show", description="Display elements")
show_subparser = show_parser.add_subparsers(
    title="elements", help="Type of elements to show", prog="element", dest="element"
)

# Machines
machines_parser = show_subparser.add_parser("machines")

# Jobs
jobs_parser = show_subparser.add_parser("jobs")

# Users
users_parser = show_subparser.add_parser("users")
# users_parser.add_argument("-m", "--machine", type=str, nargs="+")

# Groups
groups_parser = show_subparser.add_parser("groups")
# groups_parser.add_argument("-m", "--machine", type=str, nargs="+")

# Services
services_parser = show_subparser.add_parser("services")

# Domains
domain_parser = show_subparser.add_parser("domains")


def interactive_show(arg, session):
    args = arg.split(" ")
    if "" in args:
        args.remove("")

    show_namespace = show_parser.parse_args(args)

    show_elements = {
        "machines": show_machines,
        "jobs": show_jobs,
        "users": show_users,
        "groups": show_groups,
        "services": show_services,
        "domains": show_domains,
    }

    for name, function in show_elements.items():
        if show_namespace.element == name:
            function(show_namespace, session)


def show_machines(namespace, session):
    machines = session.query(Machine).all()
    for machine in machines:
        print(
            "{:4d} - {:<15} ({})".format(
                machine.id, machine.ip, ", ".join([d.name for d in machine.domains])
            )
        )


def show_jobs(namespace, session):
    jobs = session.query(Job).filter(Job.status == "RUNNING").all()
    for job in jobs:
        print(f"{job.id:4d} - {job.name:30} {job.status}")


def show_users(namespace, session):
    users = session.query(User).all()
    for user in users:
        print(user)


def show_groups(namespace, session):
    groups = session.query(Group).all()
    for group in groups:
        print(group)


def show_services(namespace, session):
    services = session.query(Service).all()
    for service in services:
        print(
            "{:4d} - {:15} {:<4d} {:20} {:20} {:20}".format(
                service.id,
                service.machine.ip or "",
                service.port or "",
                service.name or "",
                service.product or "",
                service.version or "",
            )
        )


def show_domains(namespace, session):
    domains = session.query(Domain).all()
    for domain in domains:
        print(
            "{:4d} - {:50} ({})".format(
                domain.id, domain.name, ", ".join([m.ip for m in domain.machines])
            )
        )
