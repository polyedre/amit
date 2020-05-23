#!/usr/bin/env python3

import cmd
from .manager import Service, ManagerEncoder
from .jobs import enum_hosts, enum_domains
import logging
import json
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

enum_hosts_parser = enum_subparser.add_parser("hosts")
enum_hosts_parser.add_argument("hosts", type=str, nargs="+")

# hosts

hosts_parser = InteractiveArgumentParser(prog="hosts", description="Show hosts")
hosts_parser.add_argument("-d", "--domains", action="store_true")
hosts_parser.add_argument("-s", "--services", action="store_true")
hosts_parser.add_argument("-S", "--services-verbose", action="store_true")
hosts_parser.add_argument("targets", type=str, default=None, nargs="*")


class AmitShell(cmd.Cmd):
    intro = "Welcome to the amit shell.   Type help or ? to list commands.\n"
    prompt = "> "
    data = None

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def do_save(self, arg):
        if not arg:
            arg = "amit.json"
        s = json.dumps(self.manager, cls=ManagerEncoder)
        with open(arg, "w") as f:
            f.write(s)
        logging.info("Data saved at '%s'", arg)

    def do_enum(self, arg):
        """Enumerate domains and subdomains related to args"""
        try:
            args = arg.split(" ")
            enum = enum_parser.parse_args(args)
            if enum.subcommand == "domains":
                enum_domains(enum.domains, self.manager)
            elif enum.subcommand == "hosts":
                enum_hosts(enum.hosts, self.manager)
            else:
                print(f"{enum}: no action taken")
        except ValueError:
            pass

    def do_host(self, arg):
        """Display verbose information about a host"""
        host = self.manager.get_host_by_ip(arg)
        if not host:
            print(f"ERROR: '{arg}' is not a host")
        else:
            for service in host.services:
                print(service)
                for info in service.info:
                    print(
                        "    {}\n    {}".format(
                            info, "\n    ".join(service.info[info].split("\n"))
                        )
                    )

    def do_hosts(self, arg):
        """Display informations about hosts"""
        try:
            args = arg.split(" ")
            if "" in args:
                args.remove("")
            hosts_namespace = hosts_parser.parse_args(args)
            targets = (
                self.manager.hosts_from_targets(hosts_namespace.targets)
                if hosts_namespace.targets
                else self.manager.hosts
            )

            for host in targets:
                print(host.ip)
                if hosts_namespace.domains:
                    print("  domains")
                    for domain in host.domains:
                        print(f"    {domain.name}")
                if hosts_namespace.services or hosts_namespace.services_verbose:
                    print("  services")
                    for service in sorted(
                        list(host.services),
                        key=lambda x: Service.__getattribute__(x, "port"),
                    ):
                        print(f"    {service}")
                        if hosts_namespace.services_verbose:
                            for key, value in service.info.items():
                                print(f"      {key}:")
                                print(
                                    "        {}".format(
                                        value.replace("\n", "\n        ")
                                    )
                                )
        except ValueError:
            pass

    def do_domains(self, arg):
        """Display domains and IPs"""
        for domain in self.manager.domains:
            print(domain)

    def do_jobs(self, arg):
        """Display jobs and status"""
        for job in self.manager.jobs:
            print(f" - {job}")

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
        return list(self.manager.jobs)


def start_shell(manager):
    amit_shell = AmitShell(manager)
    amit_shell.cmdloop()


def serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj.__dict__
