#!/usr/bin/env python3

import cmd
import threading
import subprocess
from .manager import Service
from bs4 import BeautifulSoup
import re
import logging

logging.basicConfig(level=logging.INFO)

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
        domain_domains = []
        for domain in arg.split(" "):
            domain_domains.append(domain)
        if domain_domains:
            t = threading.Thread(
                domain=enum_host,
                name="enum_domain",
                args=[domain_domains, self.manager],
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
            scan_ips(ips, self.manager)

    def do_machine(self, arg):
        machine = self.manager.get_machine_by_ip(arg)
        if not machine:
            print(f"ERROR: '{arg}' is not a machine")
        else:
            for service in machine.services:
                print(service)
                for info in service.info:
                    print(
                        "\t\t{}\n\t\t{}".format(
                            info, "\n\t\t".join(service.info[info].split("\n"))
                        )
                    )

    def do_list(self, arg):
        if arg == "domains":
            for domain in self.manager.domains:
                print(domain)
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


def start_job(func, manager, args=None):
    t = threading.Thread(target=func, name=f"{func.__name__}({args})", args=args)
    t.start()
    manager.jobs.append(t)


def scan_ips(ips, manager):
    for ip in ips:
        start_job(scan_ip, manager, [ip, manager])


def fast_scan_ip(ip):
    logging.info("Starting fast scan for target %s", ip)
    output = execute(f"nmap {ip}").decode()
    ports = []
    for line in output.split("\n")[5:-3]:
        ports.append(line.split("/")[0])
    return ports


def scan_ip(ip, manager):
    ports = fast_scan_ip(ip)
    if ports:
        logging.info("Starting advanced scan for target %s with ports %s", ip, ports)
        execute(
            f"nmap -A -v -p{','.join(ports)} {ip} -oX /tmp/{ip}nmap-scan.xml"
        ).decode()
        with open(f"/tmp/{ip}nmap-scan.xml") as f:
            xml = BeautifulSoup("".join(f.readlines()), features="lxml")
            for host in xml.findAll("host"):
                ip = host.address.get("addr")
                domains = []
                for hostname in xml.findAll("hostname"):
                    name = hostname.get("name")
                    domain = manager.add_domain(name, [ip])
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
                        for script in port.findAll("script"):
                            service.info[script.get("id")] = script.get("output")
                        services.append(service)
                manager.add_machine(ip, domains, services)
    logging.info("Scan finished for target %s", ip)


def enum_host(domains, manager):
    output = execute(
        "sublist3r -n {}".format(" ".join([f"-d {domain}" for domain in domains]))
    ).decode()
    for line in output.split("\n")[9:-1]:
        if line[:3] != "[-]":
            ip = line
            while not re_ip.match(ip) and ip != "":
                ip = execute(f"dig +short {ip}").decode().strip()
            domain = manager.add_domain(line, [ip])
            manager.add_machine(ip, [domain])


def start_shell(manager):
    amit_shell = AmitShell(manager)
    amit_shell.cmdloop()
