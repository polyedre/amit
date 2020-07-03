#!/usr/bin/env python3

from .jobs import enum_domains_job
from docopt import docopt, DocoptExit

ENUM_USAGE = """Enum command
Usage:
  enum (domains) [<id>]...
  enum (-h | --help)


Options:
  -h --help     Enum this screen.
"""


def interactive_enum(arg, session):
    args = arg.split(" ")
    if "" in args:
        args.remove("")

    try:
        arguments = docopt(ENUM_USAGE, argv=args)
    except (DocoptExit, SystemExit):
        return
    except BaseException as e:
        print(e.__class__)

    enum_elements = {
        "domains": enum_domains,
    }

    for name, function in enum_elements.items():
        if arguments[name]:
            function(arguments, session)


def enum_domains(arguments, session):
    enum_domains_job(arguments["<id>"], session)
