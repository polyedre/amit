#!/usr/bin/env python3

from .database import Service, Machine, Domain, Job, User, Group, Note
from docopt import docopt, DocoptExit

REPORT_USAGE = """Report command
Usage:
  report (users) [<id>]...
  report (-h | --help)


Options:
  -h --help     Report this screen.
"""


def interactive_report(arg, session):
    args = arg.split(" ")
    if "" in args:
        args.remove("")

    try:
        arguments = docopt(REPORT_USAGE, argv=args)
    except (DocoptExit, SystemExit):
        return
    except BaseException as e:
        print(e.__class__)

    report_elements = {
        "users": report_users,
    }

    for name, function in report_elements.items():
        if arguments[name]:
            function(arguments, session)


def report_users(arguments, session):

    if arguments["<id>"]:
        users = session.query(User).filter(User.id.in_(arguments["<id>"])).all()
    else:
        users = session.query(User).all()

    usernames = set()
    for user in users:
        for note in user.notes:
            if note.title == "Potential usernames (ldapsearch)":
                for line in note.content.split("\n"):
                    if ":" in line:
                        usernames.add(line.split(": ")[1])

    with open("users.txt", "w") as f:
        f.write("\n".join(usernames))
