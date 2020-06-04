#!/usr/bin/env python3

import cmd
from .database import Service, Machine, Domain, Job
from .jobs import enum_machines, enum_domains
import logging
import argparse

logging.basicConfig(level=logging.INFO)


class InteractiveArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        print(message, end="")
        raise ValueError


#
# PARSERS
#

# enum

enum_parser = InteractiveArgumentParser(prog="enum", description="Enumerate targets.")
enum_subparser = enum_parser.add_subparsers(dest="subcommand")
enum_domains_parser = enum_subparser.add_parser("domains")
enum_domains_parser.add_argument("domains", type=str, nargs="+")

enum_machines_parser = enum_subparser.add_parser("machines")
enum_machines_parser.add_argument("machines", type=str, nargs="+")

# machines

machines_parser = InteractiveArgumentParser(
    prog="machines", description="Show machines"
)
machines_parser.add_argument("-d", "--domains", action="store_true")
machines_parser.add_argument("-s", "--services", action="store_true")
machines_parser.add_argument("-S", "--services-verbose", action="store_true")
machines_parser.add_argument("targets", type=str, default=None, nargs="*")


class AmitShell(cmd.Cmd):
    intro = "Welcome to the amit shell.   Type help or ? to list commands.\n"
    prompt = "> "
    data = None

    def __init__(self, session):
        super().__init__()
        self.session = session

    def do_enum(self, arg):
        """Enumerate domains and subdomains related to args"""
        try:
            args = arg.split(" ")
            enum = enum_parser.parse_args(args)
            if enum.subcommand == "domains":
                enum_domains(enum.domains, self.session)
            elif enum.subcommand == "machines":
                enum_machines(enum.machines, self.session)
            else:
                print(f"{enum}: no action taken")
        except ValueError:
            pass

    def do_machine(self, arg):
        """Display informations about machines"""
        s = self.session()
        try:
            args = arg.split(" ")
            if "" in args:
                args.remove("")
            machines_namespace = machines_parser.parse_args(args)
            if machines_namespace.targets:
                # FIXME: machine target filter
                targets = (
                    self.session.query(Machine)
                    .filter(Machine.ip in machines_namespace.targets)
                    .all()
                )
                print(targets)
            else:
                targets = self.session.query(Machine).all()

            for machine in targets:
                print(machine.ip)
                if machines_namespace.domains:
                    print("  domains")
                    for domain in machine.domains:
                        print(f"    {domain.name}")
                if machines_namespace.services or machines_namespace.services_verbose:
                    print("  services")
                    for service in sorted(
                        list(machine.services),
                        key=lambda x: Service.__getattribute__(x, "port"),
                    ):
                        print(f"    {service.port}")
        except ValueError:
            pass
        s.close()

    def do_save(self, arg):
        self.session.commit()

    def do_domains(self, arg):
        """Display domains and IPs"""
        for domain in self.session.query(Domain).all():
            print(f"{domain.name:30.30s} {''.join([m.ip for m in domain.ips]):<30s}")

    def do_jobs(self, arg):
        """Display jobs and status"""
        for job in self.session.query(Job).all():
            print(f" - {job.name} {job.status}")

    def do_exec(self, arg):
        """Execute a python command. Useful for debug purposes"""
        try:
            print(exec(arg))
        except Exception as e:
            print(e)

    def do_exit(self, arg):
        """Exit the amit session"""
        print("Bye !")
        exit(0)

    def completedefault(self, arg):
        return list(self.session.jobs)


def start_shell(session):
    amit_shell = AmitShell(session)
    amit_shell.cmdloop()


def serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj.__dict__
