#!/usr/bin/env python3

from threading import Thread
import re
from .manager import Service
from bs4 import BeautifulSoup
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
re_ip = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")


class Job:
    def __init__(self, manager, register=True):
        self.state = "READY"
        self.manager = manager
        if register:
            self.manager.add_job(self)

    def start(self):
        self.state = "RUNNING"
        return self.run()

    def run(self):
        pass

    def finish(self):
        self.state = "DONE"
        logging.debug("%s finished", self.__repr__())

    def stop(self):
        self.state = "STOPPED"

    def __str__(self):
        return f"{self.__repr__()} {self.state}"


class PotentiallyAsyncJob(Job):
    def __init__(self, manager, is_async=False, register=True):
        super().__init__(manager, register)
        self.is_async = is_async

    def run(self):
        logging.debug(
            f"Started Job {self.__repr__()} {'with' if self.is_async else 'without'} a thread"
        )
        if self.is_async:
            t = Thread(target=self.do)
            t.start()
            return None
        else:
            return self.do()


class ExecJob(PotentiallyAsyncJob):
    def __init__(self, command, manager, is_async=False, register=True):
        super().__init__(manager, is_async, register)
        self.command = command

    def do(self):
        output = subprocess.check_output(self.command.split(" ")).decode()
        res = self.parse(output)
        self.finish()
        return res

    def parse(self, output):
        pass


class NmapJob(ExecJob):
    def __init__(self, target, manager, options="", is_async=True, register=True):
        self.target = target
        if options:
            command = f"nmap {options} {self.target} -oX /tmp/{self.target}-nmap.xml"
        else:
            command = f"nmap {self.target} -oX /tmp/{self.target}-nmap.xml"
        logging.debug(command)
        super().__init__(
            command=command, manager=manager, is_async=is_async, register=register
        )

    def parse(self, output):
        f = open(f"/tmp/{self.target}-nmap.xml")
        xml = BeautifulSoup("".join(f.readlines()), features="lxml")
        for host in xml.findAll("host"):
            ip = host.address.get("addr")
            domains = []
            for hostname in xml.findAll("hostname"):
                name = hostname.get("name")
                domain = self.manager.add_domain(name, [ip])
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
            scanned_host = self.manager.add_host(ip, domains, services)
        f.close()
        return scanned_host


class EnumHostJob(PotentiallyAsyncJob):
    def __init__(self, target, manager):
        super().__init__(manager, is_async=True)
        self.target = target

    def do(self):
        ips, domain_names = analyse_target(self.target)
        domains = []
        for domain_name in domain_names:
            domain = self.manager.add_domain(domain_name, ips)
            domains.append(domain)
        for ip in ips:
            self.manager.add_host(ip, domains)

        host = NmapJob(
            self.target, self.manager, is_async=False, register=False
        ).start()
        ports = [s.port for s in host.services]
        if ports:
            logging.info(
                "Starting advanced scan for target %s with ports %s", self.target, ports
            )
            NmapJob(
                self.target,
                self.manager,
                options=f"-A -v -p{','.join([str(p) for p in ports])}",
                is_async=False,
                register=False,
            ).start()

        self.finish()

    def __repr__(self):
        return f"EnumHost({self.target})"


class Sublist3rJob(ExecJob):
    def __init__(self, target, manager, is_async=True, register=True):
        self.target = target
        command = f"sublist3r -n -d {self.target}"
        logging.debug(command)
        super().__init__(
            command=command, manager=manager, is_async=is_async, register=register
        )

    def parse(self, output):
        for line in output.split("\n")[9:-1]:
            if line[:3] != "[-]":
                target = line
                ips, domain_names = analyse_target(target)
                domains = []
                for domain_name in domain_names:
                    domain = self.manager.add_domain(domain_name, ips)
                    domains.append(domain)
                for ip in ips:
                    self.manager.add_host(ip, domains)

    def __repr__(self):
        return f"Sublit3rJob({self.target})"


class EnumDomainJob(PotentiallyAsyncJob):
    def __init__(self, target, manager):
        super().__init__(manager, is_async=True)
        self.target = target

    def do(self):
        ips, domain_names = analyse_target(self.target)
        domains = []
        for domain_name in domain_names:
            domain = self.manager.add_domain(domain_name, ips)
            domains.append(domain)
        for ip in ips:
            self.manager.add_host(ip, domains)

        Sublist3rJob(self.target, self.manager, is_async=False, register=False).start()

        self.finish()

    def __repr__(self):
        return f"EnumDomain({self.target})"


def execute(command):
    return subprocess.check_output(command.split(" "))


def analyse_target(target):
    ips = []
    domain_names = []

    if re_ip.match(target):
        ips.append(target)
    else:
        domain_names.append(target)

    while True:
        target = execute(f"dig +short {target}").decode().strip()
        if not target:
            break
        if re_ip.match(target):
            ips.append(target)
            break
        else:
            domain_names.append(target)
    return ips, domain_names


def enum_hosts(targets, manager):
    for target in targets:
        EnumHostJob(target, manager).start()


def enum_domains(targets, manager):
    for target in targets:
        EnumDomainJob(target, manager).start()


# def enum_domain(domain, manager):
