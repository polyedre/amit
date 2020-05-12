#!/usr/bin/env python3

import cmd
import threading
import subprocess
from .manager import Domain, Machine, Service
from bs4 import BeautifulSoup
import re


re_ip = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")


class AmitShell(cmd.Cmd):
    intro = "Welcome to the amit shell.   Type help or ? to list commands.\n"
    prompt = "> "
    data = None

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def do_load(self, arg):
        print("Not implemented")

    def do_enum(self, arg):
        domain_targets = []
        for target in arg.split(" "):
            domain_targets.append(target)
        if domain_targets:
            t = threading.Thread(
                target=enum_host,
                name="enum_domain",
                args=[domain_targets, self.manager],
            )
            t.start()
            self.manager.jobs.append(t)

    def do_scan(self, arg):
        ips = set()
        for ip in arg.split(" "):
            if not re_ip.match(ip):
                print(f"ERROR: {ip} is not a valid ip")
            else:
                ips.add(ip)
        if not ips:
            print(f"No ip scanned")
        else:
            t = threading.Thread(
                target=scan_ips, name="ip_scanner", args=[list(ips), self.manager]
            )
            t.start()
            self.manager.jobs.append(t)

    def do_list(self, arg):
        if arg == "targets":
            for target in self.manager.targets:
                print(target)
        if arg == "jobs":
            for job in self.manager.jobs:
                print(f" - {job.name} {'RUNNING' if job.is_alive() else 'DONE'}")
        if arg == "machines":
            for machine in self.manager.machines:
                print(machine)

    def do_exec(self, arg):
        try:
            print(exec(arg))
        except Exception as e:
            print(e)


def execute(args):
    return subprocess.check_output(args.split(" "))


def scan_ips(ips, manager):
    output = execute("nmap {} -oX /tmp/nmap-scan.xml".format(" ".join(ips))).decode()
    with open("/tmp/nmap-scan.xml") as f:
        xml = BeautifulSoup("".join(f.readlines()), features="lxml")
        for host in xml.findAll("host"):
            ip = host.address.get("addr")
            domains = []
            for hostname in xml.findAll("hostname"):
                name = hostname.get("name")
                domain = manager.add_target(name, [ip])
                domains.append(domain)
            services = []
            for port in host.findAll("port"):
                if port.name:
                    s = port.service
                    service = Service(
                        port.get("portid"),
                        s.get("name"),
                        s.get("product"),
                        s.get("version"),
                    )
                    # for script in port.findAll("script"):
                    #     service.scripts.append(
                    #         Script(
                    #             script.get("id"),
                    #             script.get("output"),
                    #             basename=host.hostname + ":" + port.get("portid"),
                    #         )
                    #     )
                    services.append(service)
            manager.add_machine(ip, domains, services)


def enum_host(targets, manager):
    output = execute(
        "sublist3r -n {}".format(" ".join([f"-d {target}" for target in targets]))
    ).decode()
    for line in output.split("\n")[9:-1]:
        if line[:3] != "[-]":
            ip = line
            while not re_ip.match(ip) and ip != "":
                ip = execute(f"dig +short {ip}").decode().strip()
            domain = manager.add_target(line, [ip])
            machine = manager.add_machine(ip, [domain])


def start_shell(manager):
    amit_shell = AmitShell(manager)
    amit_shell.cmdloop()
