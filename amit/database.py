#!/usr/bin/env python3

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import case
from sqlalchemy.orm import relationship, backref, sessionmaker
import logging

Base = declarative_base()
# logging.basicConfig(level=logging.DEBUG)

# Objects


class Job(Base):
    __tablename__ = "job"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    status = Column(String, default="RUNNING")


class Machine(Base):
    __tablename__ = "machine"
    id = Column(Integer, primary_key=True)
    ip = Column(String, unique=True)
    domains = relationship("Domain", secondary="domain_machine_link")

    def _merge(self, machine):
        if machine:
            self.merge(machine.domains)

    def merge(self, domains):
        for domain in domains:
            if domain in self.domains:
                self_domain = self.domains[self.domains.index(domain)]
                if self_domain != domain:
                    self_domain._merge(domain)
            else:
                self.domains.append(domain)

    def __repr__(self):
        return f"{self.ip}"


class Domain(Base):
    __tablename__ = "domain"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    machines = relationship("Machine", secondary="domain_machine_link")
    notes = relationship("Note", secondary="domain_note_link")

    def _merge(self, domain):
        self.merge(domain.machines, domain.notes)

    def merge(self, machines, notes):

        for machine in machines:
            if machine in self.machines:
                self_machine = self.machines[self.machines.index(machine)]
                if self_machine != machine:
                    self_machine._merge(machine)
            else:
                self.machines.append(machine)

        titles = [n.title for n in self.notes]
        for n in notes:
            if n.title not in titles:
                self.notes.append(n)

    def __repr__(self):
        return f"{self.name}"


class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True)
    port = Column(Integer)
    name = Column(String)
    product = Column(String)
    version = Column(String)
    machine_id = Column(Integer, ForeignKey("machine.id"))
    machine = relationship("Machine", backref=backref("services", uselist=True))
    status = Column(String)
    notes = relationship("Note", secondary="service_note_link")

    __mapper_args__ = {
        "polymorphic_on": case([(name == "http", "http")], else_="service"),
        "polymorphic_identity": "service",
    }

    def _merge(self, service):
        self.merge(
            service.name,
            service.product,
            service.version,
            service.status,
            service.notes,
        )

    def merge(self, name, product, version, status, notes):

        # Choose to take last
        if name:
            self.name = name

        if product:
            self.product = product

        if version:
            self.version = version

        if status:
            self.status = status

        titles = [n.title for n in self.notes]
        for n in notes:
            if n.title not in titles:
                print(f"note {n.title} not in {titles}")
                self.notes.append(n)
            else:
                print(f"note {n.title} in {titles}")

    def oneline(self):
        return f"{self.port:5d} {self.name:15.15s} {self.product if self.product else 'None':15.15s} {self.version if self.version else 'None'}"

    def __repr__(self):
        return f"Service(port={self.port}, name={self.name}, product={self.product}) on {self.machine.ip}"


class HTTPService(Service):
    url = Column(String)

    __mapper_args__ = {"polymorphic_identity": "http"}


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    groups = relationship("Group", secondary="user_group_link")
    notes = relationship("Note", secondary="user_note_link")
    smb_rid = Column(String)

    machine_id = Column(Integer, ForeignKey("machine.id"))
    machine = relationship("Machine", backref=backref("users", uselist=True))

    def _merge(self, user):
        self.merge(user.machine, user.notes, user.credentials)

    def merge(self, machine=None, notes=[], credentials=[], groups=[]):
        if not self.machine and machine:
            self.machine = machine
        else:
            self.machine._merge(machine)

        # TODO: use note.merge
        titles = [n.title for n in self.notes]
        for n in notes:
            if n.title not in titles:
                self.notes.append(n)

        for c in credentials:
            if c in self.credentials:
                self.credentials[self.credentials.index(c)]._merge(c)
            else:
                self.credentials.append(c)

        for group in groups:
            if group in self.groups:
                self_group = self.groups[self.groups.index(group)]
                if self_group != group and self_group:
                    self_group._merge(group)
            else:
                self.groups.append(group)

    def __eq__(self, other):
        return set([other.name] + [c.username for c in other.credentials]).intersection(
            [self.name] + [c.username for c in self.credentials]
        )

    def __repr__(self):
        return f"User({self.name}, groups: ({[g.name for g in self.groups]}), creds: ({[c.username for c in self.credentials]})"


class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User", secondary="user_group_link")
    notes = relationship("Note", secondary="group_note_link")
    smb_rid = Column(String)

    machine_id = Column(Integer, ForeignKey("machine.id"))
    machine = relationship("Machine", backref=backref("groups", uselist=True))

    def _merge(self, group):
        if group:
            self.merge(group.machine, group.users, group.notes)

    def merge(self, machine=None, users=[], notes=[]):

        if not self.machine:
            self.machine = machine
        else:
            self.machine._merge(machine)

        for user in users:
            if user in self.users:
                self_user = self.users[self.users.index(user)]
                if self_user != user and self_user:
                    self_user._merge(user)
            else:
                self.users.append(user)

        # TODO: use note.merge
        titles = [n.title for n in self.notes]
        for n in notes:
            if n.title not in titles:
                self.notes.append(n)

    def __repr__(self):
        return f"Group({self.name}, users=[{', '.join([u.name for u in self.users])}])"

    def __eq__(self, other):
        return self.name == other.name


class Note(Base):
    __tablename__ = "note"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
    interest = Column(Integer, default="1")

    def __repr__(self):
        return self.content


class Credential(Base):
    __tablename__ = "credential"
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    confidence = Column(Integer)

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", backref=backref("credentials", uselist=True))

    services = relationship("Service", secondary="service_credential_link")

    def merge(self, confidence, user, services, username, password):
        if self.confidence:
            self.confidence = max(confidence, self.confidence)
        else:
            self.confidence = confidence

        # TODO: add new credential if user does not match
        if not self.user:
            self.user = user

        if not self.username:
            self.username = username

        if not self.password:
            self.password = password

        for service in services:
            if service in self.services:
                self.services[self.services.index(service)]._merge(service)
            else:
                self.services.append(service)

    def _merge(self, credential):
        return self.merge(
            credential.confidence,
            credential.user,
            credential.services,
            credential.username,
            credential.password,
        )

    def __eq__(self, other):
        return self.username == other.username and (
            self.password == None or self.password == other.password
        )


# Links


class DomainMachineLink(Base):
    __tablename__ = "domain_machine_link"
    domain_id = Column(Integer, ForeignKey("machine.id"), primary_key=True)
    machine_id = Column(Integer, ForeignKey("domain.id"), primary_key=True)


class UserGroupLink(Base):
    __tablename__ = "user_group_link"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("group.id"), primary_key=True)


class DomainNoteLink(Base):
    __tablename__ = "domain_note_link"
    domain_id = Column(Integer, ForeignKey("domain.id"), primary_key=True)
    note_id = Column(Integer, ForeignKey("note.id"), primary_key=True)


class UserNoteLink(Base):
    __tablename__ = "user_note_link"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    note_id = Column(Integer, ForeignKey("note.id"), primary_key=True)


class GroupNoteLink(Base):
    __tablename__ = "group_note_link"
    group_id = Column(Integer, ForeignKey("group.id"), primary_key=True)
    note_id = Column(Integer, ForeignKey("note.id"), primary_key=True)


class ServiceNoteLink(Base):
    __tablename__ = "service_note_link"
    service_id = Column(Integer, ForeignKey("service.id"), primary_key=True)
    note_id = Column(Integer, ForeignKey("note.id"), primary_key=True)


class ServiceCredentialLink(Base):
    __tablename__ = "service_credential_link"
    service_id = Column(Integer, ForeignKey("service.id"), primary_key=True)
    credential_id = Column(Integer, ForeignKey("credential.id"), primary_key=True)


# API


def add_machine(session, ip, domains=[]):
    m = session.query(Machine).filter(Machine.ip == ip).first()
    if m:
        m.merge(domains)
    else:
        m = Machine(ip=ip, domains=domains)
        session.add(m)
    return m


def add_domain(session, name, machines=[], notes=[]):
    d = session.query(Domain).filter(Domain.name == name).first()
    if d:
        d.merge(machines, notes)
    else:
        d = Domain(name=name, machines=machines)
        session.add(d)
    return d


def add_service(
    session, port, name, machine, product=None, version=None, status=None, notes=[]
):
    s = (
        session.query(Service)
        .join(Machine)
        .filter(Machine.ip == machine.ip, Service.port == port)
        .first()
    )
    if s:
        s.merge(name, product, version, status, notes)
    else:
        s = Service(
            port=port,
            name=name,
            product=product,
            version=version,
            machine=machine,
            status=status,
        )
        session.add(s)
    return s


def add_user(session, name, machine=None, notes=[], credentials=[]):
    # Here we do not add notes or machine, else it is added in database
    new_u = User(name=name)
    logging.debug("Adding user %s", new_u)
    users = session.query(User).all()

    for u in users:
        if set([u.name] + [c.username for c in u.credentials]).intersection(
            [name] + [c.username for c in credentials]
        ):
            logging.debug("User is the same as %s", u)
            u.merge(machine, notes, credentials)
            return u

    logging.debug("User not found in %s", users)
    new_u.merge(machine, notes, credentials)
    session.add(new_u)
    return new_u


def add_group(session, name, machine=None, users=[], notes=[]):
    # Here we do not add notes or machine, else it is added in database
    new_g = Group(name=name)
    logging.debug("Adding group %s", new_g)
    groups = session.query(Group).all()

    for g in groups:
        if new_g == g:
            logging.debug("Group is the same as %s", g)
            g.merge(machine, users, notes)
            return g

    logging.debug("Group not found in %s", groups)
    new_g.merge(machine, users, notes)
    session.add(new_g)
    return new_g


if __name__ == "__main__":
    session = sessionmaker()
    engine = create_engine("sqlite:///amit.sqlite")
    session.configure(bind=engine)
    Base.metadata.create_all(engine)

    s = session()

    s.add_all([Machine(ip="127.0.0.1"), Machine(ip="8.8.8.8")])

    m = s.query(Machine).filter(Machine.ip == "127.0.0.1").one()
    m.domains.append(Domain(name="localhost"))

    print(s.query(Domain).all())
