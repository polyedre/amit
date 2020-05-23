#!/usr/bin/env python3

import cmd
import threading
import subprocess
from .manager import Service, ManagerEncoder, re_ip
from bs4 import BeautifulSoup
import logging
import json
import argparse

logging.basicConfig(level=logging.INFO)


class InteractiveArgumentParser(argparse.ArgumentParser):
    def exit(self, status=0, message=None):
        print(message, end="")
        raise ValueError


#
# PARSERS
#

# enum

enum_parser = InteractiveArgumentParser(prog="enum", description="Enumerate targets.")
enum_subparser = enum_parser.add_subparsers(dest="subcommand")
enum_domains_parser = enum_subparser.add_parser("domains")
enum_domains_parser.add_argument("domains", type=str, nargs="+")

enum_hosts_parser = enum_subparser.add_parser("hosts")
enum_hosts_parser.add_argument("hosts", type=str, nargs="+")

# hosts

hosts_parser = InteractiveArgumentParser(prog="hosts", description="Show hosts")
hosts_parser.add_argument("-d", "--domains", action="store_true")
hosts_parser.add_argument("-s", "--services", action="store_true")
hosts_parser.add_argument("targets", type=str, default=None, nargs="*")


class AmitShell(cmd.Cmd):
    intro = "Welcome to the amit shell.   Type help or ? to list commands.\n"
    prompt = "> "
    data = None

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def do_save(self, arg):
        if not arg:
            arg = "amit.json"
        s = json.dumps(self.manager, cls=ManagerEncoder)
        with open(arg, "w") as f:
            f.write(s)
        logging.info("Data saved at '%s'", arg)

    def do_enum(self, arg):
        """Enumerate domains and subdomains related to args"""
        try:
            args = arg.split(" ")
            enum = enum_parser.parse_args(args)
            if enum.subcommand == "domains":
                enum_domains(enum.domains, self.manager)
            elif enum.subcommand == "hosts":
                enum_hosts(enum.hosts, self.manager)
            else:
                print(f"{enum}: no action taken")
        except ValueError:
            pass

    def do_host(self, arg):
        """Display verbose information about a host"""
        host = self.manager.get_host_by_ip(arg)
        if not host:
            print(f"ERROR: '{arg}' is not a host")
        else:
            for service in host.services:
                print(service)
                for info in service.info:
                    print(
                        "\t\t{}\n\t\t{}".format(
                            info, "\n\t\t".join(service.info[info].split("\n"))
                        )
                    )

    def do_hosts(self, arg):
        """Display IPs and services detected"""
        try:
            args = arg.split(" ")
            if "" in args:
                args.remove("")
            hosts_namespace = hosts_parser.parse_args(args)
            targets = (
                self.manager.hosts_from_targets(hosts_namespace.targets)
                if hosts_namespace.targets
                else self.manager.hosts
            )

            for host in targets:
                print(host.ip)
                if hosts_namespace.domains:
                    print("\tdomains")
                    for domain in host.domains:
                        print(f"\t\t{domain.name}")
                if hosts_namespace.services:
                    print("\tservices")
                    for service in host.services:
                        print(f"\t\t{service}")
        except ValueError:
            pass

    def do_domains(self, arg):
        """Display domains and IPs"""
        for domain in self.manager.domains:
            print(domain)

    def do_jobs(self, arg):
        """Display jobs and status"""
        for job in self.manager.jobs:
            print(f" - {job.name} {'RUNNING' if job.is_alive() else 'DONE'}")

    def do_exec(self, arg):
        """Execute a python command. Useful for debug purposes"""
        try:
            print(exec(arg))
        except Exception as e:
            print(e)

    def do_exit(self, arg):
        """Exit the amit session"""
        print("Bye !")
        exit(0)


def execute(args):
    return subprocess.check_output(args.split(" "))


def start_job(func, manager, args=None):
    t = threading.Thread(target=func, name=f"{func.__name__}({args})", args=args)
    t.start()
    manager.jobs.append(t)


def enum_hosts(ips, manager):
    for ip in ips:
        start_job(enum_host, manager, [ip, manager])


def fast_scan_ip(ip):
    logging.info("Starting fast scan for target %s", ip)
    output = execute(f"nmap {ip}").decode()
    ports = []
    for line in output.split("\n"):
        if "tcp" in line:
            ports.append(line.split("/")[0])
    return ports


def enum_host(ip, manager):
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
                manager.add_host(ip, domains, services)
    logging.info("Scan finished for target %s", ip)


def enum_domain(domain, manager):
    logging.info("Starting looking for domain related to %s", domain)
    output = execute(f"sublist3r -n -d {domain}").decode()
    for line in output.split("\n")[9:-1]:
        if line[:3] != "[-]":
            ip = line
            while not re_ip.match(ip) and ip != "":
                ip = execute(f"dig +short {ip}").decode().strip()
            ips = ip.split("\n")
            if "" in ips:
                ips.remove("")
            new_domain = manager.add_domain(line, ips)
            for ip in ips:
                manager.add_host(ip, [new_domain])
    logging.info("Finished looking for domain related to %s", domain)


def enum_domains(domains, manager):
    for domain in domains:
        start_job(enum_domain, manager, [domain, manager])


def start_shell(manager):
    amit_shell = AmitShell(manager)
    amit_shell.cmdloop()


def serialize(obj):
    if isinstance(obj, set):
        return list(obj)
    return obj.__dict__
