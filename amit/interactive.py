#!/usr/bin/env python3

import cmd
import threading
import subprocess


class AmitShell(cmd.Cmd):
    intro = "Welcome to the amit shell.   Type help or ? to list commands.\n"
    prompt = "> "
    data = None

    def __init__(self, domains):
        super().__init__()
        self.data = domains

    def do_load(self, arg):
        print("Not implemented")

    def do_enum(self, arg):
        domain_targets = []
        for target in arg.split(" "):
            domain_targets.append(target)
        if domain_targets:
            threading.Thread(
                target=enum_host, name="enum_domain", args=domain_targets
            ).start()


def show_hosts(data):
    # TODO: implement
    print(data)


def execute(args):
    return subprocess.check_output(args.split(" "))


def enum_host(*targets):
    output = execute(
        "sublist3r -n {}".format(" ".join([f"-d {target}" for target in targets]))
    ).decode()
    for line in output.split("\n")[8:]:
        if line[:3] != "[-]":
            print(line)


def start_shell():
    amit_shell = AmitShell([])
    amit_shell.cmdloop()
