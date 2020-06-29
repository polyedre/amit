#!/usr/bin/env python3

import cmd
from .database import Service, Machine, Domain, Job
from .constants import GREEN, RED, FAINTED, RESET
from .interactive_show import interactive_show
from .interactive_scan import interactive_scan
from .interactive_add import interactive_add
import logging

logging.basicConfig(level=logging.INFO)


#
# PARSERS
#

# ENUM

# enum_parser = InteractiveArgumentParser(prog="enum", description="Enumerate targets.")
# enum_subparser = enum_parser.add_subparsers(dest="subcommand")

# #      enum domains

# enum_domains_parser = enum_subparser.add_parser("domains")
# enum_domains_parser.add_argument("domains", type=str, nargs="+")

# #      enum website

# enum_machines_parser = enum_subparser.add_parser("machines")
# enum_machines_parser.add_argument("machines", type=str, nargs="+")

# MACHINES


class AmitShell(cmd.Cmd):
    intro = "Welcome to the amit shell.   Type help or ? to list commands.\n"
    prompt = "> "
    data = None

    def __init__(self, session):
        super().__init__()
        self.session = session

    def do_scan(self, arg):
        """Enumerate domains and subdomains related to args"""
        try:
            interactive_scan(arg, self.session)
        except Exception as e:
            print(e)

    def do_show(self, arg):
        """Display informations about machines"""
        s = self.session()
        try:
            interactive_show(arg, s)
        except Exception as e:
            print(e)
        s.close()

    def do_exec(self, arg):
        """Execute a python command. Useful for debug purposes"""
        try:
            print(exec(arg))
        except Exception as e:
            print(e)

    def do_add(self, arg):
        s = self.session()
        try:
            interactive_add(arg, s)
        except Exception as e:
            print(e)
        s.close()

    def do_exit(self, arg):
        """Exit the amit session"""
        print("Bye !")
        exit(0)

    def completedefault(self, arg):
        return list(self.session.jobs)

    def emptyline(self):
        pass  # Override default behaviour

    def postcmd(self, stop, line):
        nb_process = len(
            self.session().query(Job).filter(Job.status == "RUNNING").all()
        )
        self.prompt = f"{nb_process} ⌾ > "
        return False  # Continue interaction


def start_shell(session):
    amit_shell = AmitShell(session)
    amit_shell.cmdloop()


def serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj.__dict__
