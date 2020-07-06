#!/usr/bin/env python3

from threading import Thread
import re
from .database import (
    Machine,
    Domain,
    Job,
    User,
    Group,
    Note,
    Service,
    add_user,
    add_group,
    add_machine,
    add_domain,
    add_service,
)
from .config import LDAP_UNINTERESTING_FIELDS, LDAP_POTENTIAL_USERNAME_FIELDS
from bs4 import BeautifulSoup
import subprocess
import logging

# logging.basicConfig(level=logging.CRITICAL)
logging.basicConfig(level=logging.INFO)


def service_scan(id, session):
    s = session()
    service = s.query(Service).filter(Service.id == id).first()
    j = Job(name=f"service_scan({service.port}, {service.name}, {service.machine.ip})")
    s.add(j)
    s.commit()

    # Run scans
    ldap_scan(service, session)
    smb_scan(service, session)
    j.status = "DONE"
    s.commit()


def smb_scan(service, session):
    if service.port == 445:
        nmap(service.machine, session, options=f"--script smb-vuln* -p {service.port}")


def ldap_scan(service, session):

    if service.name == "ldap":
        base_dn = None  # Ldap base dn

        res = execute(
            f"ldapsearch -x -h {service.machine.ip} -p {service.port} -s base"
        )

        service.notes.append(
            Note(
                title="Detecting base ldap domain (ldapsearch)",
                content=res,
                interest=3,
            )
        )

        if "ldap_sasl_bind" not in res:

            lines = res.split("\n")
            for line in lines:
                if line.startswith("defaultNamingContext") or line.startswith(
                    "rootDomainNamingContext"
                ):
                    base_dn = line.split(": ")[1]

            if base_dn:
                res = execute(
                    f"ldapsearch -x -h {service.machine.ip} -p {service.port} -b {base_dn}"
                )

                service.notes.append(
                    Note(
                        title="Searching the whole ldap domain (ldapsearch)",
                        content=res,
                        interest=3,
                    )
                )

                ldap_parse_users_and_groups(res, service, session)
            else:
                logging.info("could not retreive ldap base dn")
    else:
        logging.debug("service on {service.machine.ip}:{service.port} is not ldap")


def ldap_parse_users_and_groups(search_results, service, session):
    for _ in range(2):  # We do the parsing 2 times to get right links
        for dn in search_results.split("\n\n"):
            if ldap_is_user(dn):
                ldap_parse_user(dn, service, session)
            if ldap_is_group(dn):
                ldap_parse_group(dn, service, session)


def ldap_is_user(dn):
    return "objectClass: user" in dn or "objectClass: person" in dn


def ldap_is_group(dn):
    return "objectClass: group" in dn


def ldap_parse_user(dn, service, session):
    name = None
    notes = [Note(title="Ldap Dump", content=dn, interest=2)]

    interesting_fields = ""
    potential_usernames = ""

    for line in dn.split("\n"):
        if line and not line[0] == "#":
            field = line.split(":")[0]
            if field == "cn":
                name = line.split(": ")[1]
            elif field in LDAP_POTENTIAL_USERNAME_FIELDS:
                potential_usernames += line + "\n"
            elif field not in LDAP_UNINTERESTING_FIELDS:
                interesting_fields += line + "\n"

    if interesting_fields:
        notes.append(
            Note(
                title="Interesting fields (ldapsearch)",
                content=interesting_fields.strip(),
                interest=1,
            )
        )
    if potential_usernames:
        notes.append(
            Note(
                title="Potential usernames (ldapsearch)",
                content=potential_usernames.strip(),
                interest=1,
            )
        )

    add_user(session, name, service, notes=notes)


def ldap_parse_group(dn, service, session):
    name = None
    users = []
    notes = [Note(title="Ldap Dump", content=dn, interest=2)]

    interesting_fields = ""

    for line in dn.split("\n"):
        if line and not line[0] == "#":
            field = line.split(":")[0]
            if field == "cn":
                name = line.split(": ")[1]
            elif field == "member":
                u = add_user(session, name=ldap_address_get_first(line.split(": ")[1]))
                users.append(u)
            elif field not in LDAP_UNINTERESTING_FIELDS:
                interesting_fields += line + "\n"

    if interesting_fields:
        notes.append(
            Note(
                title="Interesting fields (ldapsearch)",
                content=interesting_fields.strip(),
                interest=1,
            )
        )
    add_group(session, name, service, users, notes=notes)


def ldap_address_get_first(address):
    return address.split(",")[0].split("=")[1]


def port_scan(id, session):
    machine = session.query(Machine).filter(Machine.id == id).first()
    s = session()
    j = Job(name=f"port_scan({machine.ip})")
    s.add(j)
    s.commit()
    nmap(machine, s, options="-Pn")

    ports = [s.port for s in machine.services]
    if ports:
        nmap(machine, s, options=f"-Pn -A -v -p{','.join([str(p) for p in ports])}")
    else:
        logging.warning("port_scan: no port found for target '%s'", machine.ip)
    j.status = "DONE"
    s.commit()
    s.close()


def nmap(machine, session, options=""):
    logging.debug("started nmap on target %s with options '%s'", machine.ip, options)
    if options:
        execute(f"nmap {options} {machine.ip} -oX /tmp/{machine.ip}-nmap.xml")
    else:
        execute(f"nmap {machine.ip} -oX /tmp/{machine.ip}-nmap.xml")
    logging.debug("finished nmap on target %s with options '%s'", machine.ip, options)
    ports = []
    with open(f"/tmp/{machine.ip}-nmap.xml") as f:
        xml = BeautifulSoup("".join(f.readlines()), features="lxml")
        for xml_machine in xml.findAll("host"):
            ip = xml_machine.address.get("addr")
            m = add_machine(session, ip)
            for hostname in xml.findAll("hostname"):
                name = hostname.get("name")
                add_domain(session, name, machines=[m])
            for port in xml_machine.findAll("port"):
                if port.name:
                    xml_service = port.service
                    xml_state = port.state
                    ports.append(port.get("portid"))
                    s = add_service(
                        session,
                        port=port.get("portid"),
                        name=xml_service.get("name"),
                        machine=m,
                        product=xml_service.get("product"),
                        version=xml_service.get("version"),
                        status=xml_state.get("state"),
                    )
                    for script in port.findAll("script"):
                        s.notes.append(
                            Note(
                                title=script.get("id") + " (nmap)",
                                content=script.get("output").strip(),
                                interest="2",
                            )
                        )
    session.commit()
    return ports


def scan_domain(id, session):
    s = session()
    domain = s.query(Domain).filter(Domain.id == id).first()
    j = Job(name=f"scan_domain({domain.name})")
    s.add(j)
    s.commit()

    # Nameservers
    nameservers = execute(f"dig {domain.name} NS +short").strip()
    if nameservers:
        for nameserver in nameservers.split("\n"):
            analyse_target(nameserver, session)

        domain.notes.append(Note(title="Nameservers", content=nameservers))

    # Zone transfert
    for nameserver in nameservers.split("\n"):
        res = execute(f"dig axfr @{nameserver} {domain.name}")
        if not "Transfer failed." in res:
            domain.notes.append(Note(title="Zone transfer", content=res, interest=0))

    # MX
    mailservers = execute(f"dig {domain.name} MX +short").strip()
    if mailservers:
        for mailserver in mailservers.split("\n"):
            analyse_target(mailserver, session)

        domain.notes.append(Note(title="Mail servers", content=mailservers))

    # TXT
    txtentries = execute(f"dig {domain.name} TXT +short").strip()
    if txtentries:
        domain.notes.append(Note(title="Text entries", content=txtentries))

    whois = execute(f"whois {domain.name}")
    domain.notes.append(Note(title="Whois", content=whois, interest=2))

    j.status = "DONE"
    s.commit()


def sublist3r(id, session):
    s = session()
    domain = s.query(Domain).filter(Domain.id == id).first()
    j = Job(name=f"sublist3r({domain.name})")
    s.add(j)
    s.commit()

    # Execution
    logging.debug("started sublist3r for target %s", domain.name)
    output = execute(f"sublist3r -n -d {domain.name}")
    logging.debug("finished sublist3r for target %s", domain.name)

    # Parsing
    for line in output.split("\n")[9:-1]:
        if line[:3] != "[-]":
            analyse_target(line, session)
    j.status = "DONE"
    s.commit()


def analyse_target(target, session):
    m = None
    if is_ip(target):
        m = session.query(Machine).filter(Machine.ip == target).one_or_none()
        if not m:
            m = Machine(ip=target)
            session.add(m)
    else:
        if target[-1] == ".":
            domains = [target[:-1]]
        else:
            domains = [target]

        while True:
            target = execute(f"dig +short {target}").strip().split("\n")[0]
            if not target:
                for domain_name in domains:
                    add_domain(session, domain_name)
                break
            if is_ip(target):
                m = session.query(Machine).filter(Machine.ip == target).one_or_none()

                # create new domain entry for domain name not in database
                domain_instances = []
                for domain_name in domains:
                    d = (
                        session.query(Domain)
                        .filter(Domain.name == domain_name)
                        .one_or_none()
                    )
                    if not d:
                        d = Domain(name=domain_name)
                    domain_instances.append(d)

                # No machine for these domains, adding a new one
                if not m:
                    m = Machine(ip=target, domains=domain_instances)
                    session.add(m)
                else:
                    names = [domain.name for domain in m.domains]
                    for domain in domain_instances:
                        if domain.name not in names:
                            m.domains.append(domain)
                break
            else:
                if target[-1] == ".":
                    domains.append(target[:-1])
                else:
                    domains.append(target)
    session.commit()
    return m


def execute(command, shell=False):
    if shell:
        return subprocess.check_output(command, shell=shell).decode()
    else:
        return subprocess.check_output(command.split(" ")).decode()


def is_ip(target):
    re_ip = re.compile("\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}")
    return re_ip.match(target)


def scan_machines_job(machine_ids, session):
    for id in machine_ids:
        Thread(target=port_scan, args=(id, session)).start()


def enum_domains_job(domains_ids, session):
    for id in domains_ids:
        Thread(target=sublist3r, args=(id, session)).start()


def scan_domains_job(domains_ids, session):
    for id in domains_ids:
        Thread(target=scan_domain, args=(id, session)).start()


def scan_service_job(services_ids, session):
    for id in services_ids:
        Thread(target=service_scan, args=(id, session)).start()


# def enum_domain(domain, session):
