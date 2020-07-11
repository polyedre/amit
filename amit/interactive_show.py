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
                    "\t{:4d} - {:<5d} {:18.18} {:18} {:18}".format(
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

    jobs = session.query(Job)
    if arguments["<id>"]:
        jobs = jobs.filter(Job.id.in_(arguments["<id>"]))
    if arguments["-v"] == 0:
        jobs = jobs.filter(Job.status == "RUNNING")

    for job in jobs.all():
        print(f"{job.id:4d} - {job.name:30} {job.status}")


def show_users(arguments, session):

    if arguments["<id>"]:
        users = session.query(User).filter(User.id.in_(arguments["<id>"])).all()
    else:
        users = session.query(User).all()

    for user in users:
        if arguments["-v"] == 0:
            print(
                "{:4d} - {:20.20} '{}'".format(
                    user.id, user.name, ", ".join([g.name for g in user.groups])
                )
            )
        else:
            print("{:4d} - {:20.20}".format(user.id, user.name,))
            if user.groups:
                print(
                    "\tgroups: \n\t\t{}".format(
                        "\n\t\t".join([g.name for g in user.groups])
                    )
                )
            if user.credentials:
                print(
                    "\tcreds: \n\t\t{}".format(
                        "\n\t\t".join(
                            [
                                f"'{c.username or ''}' {c.password or ''}"
                                for c in user.credentials
                            ]
                        )
                    )
                )
            show_notes(user.notes, arguments["-v"])


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
        show_notes(group.notes, arguments["-v"])


def show_services(arguments, session):

    services = session.query(Service)
    if arguments["<id>"]:
        services = services.filter(Service.id.in_(arguments["<id>"]))
    if arguments["-v"] == 0:
        services = services.filter(Service.status == "open")
    if arguments["-m"]:
        services = services.filter(Service.machine_id.in_(arguments["-m"]))

    for service in services.all():
        print(
            "{:4d} - {:15} {:<5d} {:17.17} {:17} {:17}".format(
                service.id,
                service.machine.ip or "",
                service.port or "",
                service.name or "",
                service.product or "",
                service.version or "",
            )
        )
        show_notes(service.notes, arguments["-v"])


def show_domains(arguments, session):

    domains = session.query(Domain)
    if arguments["<id>"]:
        domains = domains.filter(Domain.id.in_(arguments["<id>"]))

    for domain in domains.all():
        print(
            "{:4d} - {:50} ({})".format(
                domain.id, domain.name, ", ".join([m.ip for m in domain.machines])
            )
        )
        show_notes(domain.notes, arguments["-v"])


def show_notes(notes, verbosity):
    for note in notes:
        if note.interest <= verbosity:
            print(
                "\t{}{}\n\t\t{}{}".format(
                    FAINTED, note.title, note.content.replace("\n", "\n\t\t"), RESET
                )
            )
