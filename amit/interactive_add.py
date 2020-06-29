#!/usr/bin/env python3

import argparse
from .database import add_machine, add_domain
from .jobs import analyse_target


class InteractiveArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        print(message, end="")


def interactive_add(arg, session):
    args = arg.split(" ")

    for arg in args:
        analyse_target(arg, session)
