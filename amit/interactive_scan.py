#!/usr/bin/env python3

from .jobs import scan_machines_job, scan_domains_job, scan_service_job
from docopt import docopt, DocoptExit

SCAN_USAGE = """Scan command
Usage:
  scan (machines|jobs|users|groups|services|domains) [-v | -vv | -vvv] [<id>]...
  scan (-h | --help)


Options:
  -h --help     Scan this screen.
"""


def interactive_scan(arg, session):
    args = arg.split(" ")
    if "" in args:
        args.remove("")

    try:
        arguments = docopt(SCAN_USAGE, argv=args)
    except (DocoptExit, SystemExit):
        return
    except BaseException as e:
        print(e.__class__)

    scan_elements = {
        "machines": scan_machines,
        "domains": scan_domains,
        "services": scan_services,
    }

    for name, function in scan_elements.items():
        if arguments[name]:
            function(arguments, session)


def scan_machines(arguments, session):
    scan_machines_job(arguments["<id>"], session)


def scan_services(arguments, session):
    scan_service_job(arguments["<id>"], session)


def scan_domains(arguments, session):
    scan_domains_job(arguments["<id>"], session)
