#!/usr/bin/env python3

from .database import Service, Machine, Domain, Job, User, Group, Note
from .constants import FAINTED, RESET, GREEN, RED
from docopt import docopt, DocoptExit


SHOW_USAGE = """Show command
Usage:
  show [machines|jobs|users|groups|services|domains] [-v | -vv | -vvv] [-m <machine>]... [<id>]...
  show (-h | --help)


Options:
  -h --help     Show this screen.
  -m <machine>  Filter by machine
"""


def interactive_show(arg, session):
    args = arg.split(" ")
    if "" in args:
        args.remove("")

    try:
        arguments = docopt(SHOW_USAGE, argv=args)
    except (DocoptExit, SystemExit):
        return

    show_elements = {
        "machines": show_machines,
        "jobs": show_jobs,
        "users": show_users,
        "groups": show_groups,
        "services": show_services,
        "domains": show_domains,
    }

    for name, function in show_elements.items():
        if arguments[name]:
            return function(arguments, session)

    return show_default(arguments, session)


def show_default(arguments, session):

    machines = session.query(Machine)
    if arguments["-m"]:
        machines = machines.filter(Machine.id.in_(arguments["-m"]))

    for machine in machines.all():
        print("{}{:4d} - {:<15}{}".format(RED, machine.id, machine.ip, RESET))
        if machine.domains:
            print("     - DOMAINS:")
            for domain in machine.domains:
                print("\t{:4d} - {:<50}".format(domain.id, domain.name))
        services = machine.services
        if arguments["-v"] == 0:
            services = [s for s in services if s.status == "open"]
        if services:
            print("     - SERVICES:")
            for service in services:
                print(
                    "\t{:4d} - {:<4d} {:18.18} {:18.18} {:18.18}".format(
                        service.id,
                        service.port or "",
                        service.name or "",
                        service.product or "",
                        service.version or "",
                    )
                )


def show_machines(arguments, session):

    if arguments["<id>"]:
        machines = (
            session.query(Machine).filter(Machine.id.in_(arguments["<id>"])).all()
        )
    else:
        machines = session.query(Machine).all()

    for machine in machines:
        print(
            "{:4d} - {:<15} ({})".format(
                machine.id, machine.ip, ", ".join([d.name for d in machine.domains])
            )
        )


def show_jobs(arguments, session):

    if arguments["<id>"]:
        jobs = (
            session.query(Job)
            .filter(Job.id.in_(arguments["<id>"]), Job.status == "RUNNING")
            .all()
        )
    else:
        jobs = session.query(Job).filter(Job.status == "RUNNING").all()

    for job in jobs:
        print(f"{job.id:4d} - {job.name:30} {job.status}")


def show_users(arguments, session):

    if arguments["<id>"]:
        users = session.query(User).filter(User.id.in_(arguments["<id>"])).all()
    else:
        users = session.query(User).all()

    for user in users:
        print(
            "{:4d} - {:20.20} ({})".format(
                user.id, user.name, ", ".join([g.name for g in user.groups])
            )
        )
        notes = session.query(Note).filter(Note.interest <= arguments["-v"])
        for note in notes:
            print(
                "{}\t{:4d} - {}{}".format(
                    FAINTED, note.id, note.content.replace("\n", "\n\t       "), RESET,
                )
            )


def show_groups(arguments, session):

    if arguments["<id>"]:
        groups = session.query(Group).filter(Group.id.in_(arguments["<id>"])).all()
    else:
        groups = session.query(Group).all()

    for group in groups:
        print(
            "{:4d} - {:20.20} ({})".format(
                group.id, group.name, ", ".join([g.name for g in group.users])
            )
        )


def show_services(arguments, session):

    if arguments["<id>"]:
        services = (
            session.query(Service).filter(Service.id.in_(arguments["<id>"])).all()
        )
    else:
        services = session.query(Service).all()

    for service in services:
        print(
            "{:4d} - {:15} {:<4d} {:18.18} {:18.18} {:18.18}".format(
                service.id,
                service.machine.ip or "",
                service.port or "",
                service.name or "",
                service.product or "",
                service.version or "",
            )
        )
        if arguments["-v"]:
            for service_info in service.info:
                print(
                    "{}\t{}\n\t\t{}{}".format(
                        FAINTED,
                        service_info.name,
                        service_info.content.replace("\n", "\n\t\t"),
                        RESET,
                    )
                )


def show_domains(arguments, session):

    if arguments["<id>"]:
        domains = session.query(Domain).filter(Domain.id.in_(arguments["<id>"])).all()
    else:
        domains = session.query(Domain).all()

    for domain in domains:
        print(
            "{:4d} - {:50} ({})".format(
                domain.id, domain.name, ", ".join([m.ip for m in domain.machines])
            )
        )
