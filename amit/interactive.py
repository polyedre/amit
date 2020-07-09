#!/usr/bin/env python3

import cmd
from .database import Job
from .interactive_show import interactive_show
from .interactive_scan import interactive_scan
from .interactive_enum import interactive_enum
from .interactive_add import interactive_add
from .interactive_report import interactive_report
import logging

logging.basicConfig(level=logging.INFO)


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
            print("ERROR: ", e)

    def do_show(self, arg):
        """Display informations about machines"""
        s = self.session()
        try:
            interactive_show(arg, s)
        except Exception as e:
            print(e)
        s.close()

    def do_report(self, arg):
        """Build reports about informations present in database"""
        s = self.session()
        try:
            interactive_report(arg, s)
        except Exception as e:
            print(e)
        s.close()

    def do_enum(self, arg):
        """Display informations about machines"""
        try:
            interactive_enum(arg, self.session)
        except Exception as e:
            print(e)

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
