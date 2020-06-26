#!/usr/bin/env python3

from sqlalchemy import Column, String, Integer, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()


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

    def __repr__(self):
        return f"{self.ip}"


class Domain(Base):
    __tablename__ = "domain"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    machines = relationship("Machine", secondary="domain_machine_link")

    def __repr__(self):
        return f"{self.name}"


class DomainMachineLink(Base):
    __tablename__ = "domain_machine_link"
    domain_id = Column(Integer, ForeignKey("machine.id"), primary_key=True)
    machine_id = Column(Integer, ForeignKey("domain.id"), primary_key=True)


class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True)
    port = Column(Integer)
    name = Column(String)
    product = Column(String)
    version = Column(String)
    machine_id = Column(Integer, ForeignKey("machine.id"))
    machine = relationship("Machine", backref=backref("services", uselist=True))

    def oneline(self):
        return f"{self.port:5d} {self.name:15.15s} {self.product if self.product else 'None':15.15s} {self.version if self.version else 'None'}"

    def __repr__(self):
        return f"Service(port={self.port}, name={self.name}, product={self.product}) on {self.machine.ip}"


class ServiceInfo(Base):
    __tablename__ = "service_info"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    content = Column(String)
    source = Column(String)
    confidence = Column(Integer)
    service_id = Column(Integer, ForeignKey("service.id"))
    service = relationship("Service", backref=backref("info", uselist=True))

    def desc(self):
        return f"{self.name} (from source: {self.source})\n{self.content}"


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    groups = relationship("Group", secondary="user_group_link")

    service_id = Column(Integer, ForeignKey("service.id"))
    service = relationship("Service", backref=backref("users", uselist=True))

    notes = relationship("Note", secondary="user_note_link")

    def __repr__(self):
        text = f"User(name={self.name}"
        if self.groups:
            text += f", groups={[g.name for g in self.groups]}"
        return text + ")"


class Group(Base):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    users = relationship("User", secondary="user_group_link")

    service_id = Column(Integer, ForeignKey("service.id"))
    service = relationship("Service", backref=backref("groups", uselist=True))

    notes = relationship("Note", secondary="group_note_link")

    def __repr__(self):
        text = f"Group(name={self.name}"
        if self.users:
            text += f", users={[u.name for u in self.users]}"
        return text + ")"


class Note(Base):
    __tablename__ = "note"
    id = Column(Integer, primary_key=True)
    content = Column(String)

    def __repr__(self):
        return self.content


class UserGroupLink(Base):
    __tablename__ = "user_group_link"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    group_id = Column(Integer, ForeignKey("group.id"), primary_key=True)


class UserNoteLink(Base):
    __tablename__ = "user_note_link"
    user_id = Column(Integer, ForeignKey("user.id"), primary_key=True)
    note_id = Column(Integer, ForeignKey("note.id"), primary_key=True)


class GroupNoteLink(Base):
    __tablename__ = "group_note_link"
    group_id = Column(Integer, ForeignKey("group.id"), primary_key=True)
    note_id = Column(Integer, ForeignKey("note.id"), primary_key=True)


def add_machine(session, ip, domains=[]):
    m = session.query(Machine).filter(Machine.ip == ip).first()
    if m:
        for d in domains:
            if d not in m.domains:
                m.domains.append(d)
    else:
        m = Machine(ip=ip, domains=domains)
        session.add(m)
    return m


def add_domain(session, name, machines=[]):
    d = session.query(Domain).filter(Domain.name == name).first()
    if d:
        for m in machines:
            if m not in d.machines:
                d.machines.append(m)
    else:
        d = Domain(name=name, machines=machines)
        session.add(d)
    return d


def add_service(session, port, name, machine, product=None, version=None):
    s = (
        session.query(Service)
        .join(Machine)
        .filter(Machine.ip == machine.ip, Service.port == port)
        .first()
    )
    if s:
        s.name = name
        if product:
            s.product = product
        if version:
            s.version = version
    else:
        s = Service(
            port=port, name=name, product=product, version=version, machine=machine
        )
        session.add(s)
    return s


def add_serviceinfo(session, name, content, service, source="Unknown", confidence=100):
    s = ServiceInfo(
        name=name,
        content=content,
        source=source,
        confidence=confidence,
        service=service,
    )
    session.add(s)
    return s


def add_user(session, name, service=None, notes=[]):
    if service:
        u = (
            session.query(User)
            .join(Service)
            .join(Machine)
            .filter(User.name == name, Machine.ip == service.machine.ip)
            .first()
        )
    else:
        u = session.query(User).filter(User.name == name).first()
    if u:
        u.name = name
        if service:
            u.service = service
        for note in notes:
            u.notes.append(note)
    else:
        u = User(name=name, service=service, notes=notes)
        session.add(u)
    return u


def add_group(session, name, service=None, users=[], notes=[]):
    if service:
        g = (
            session.query(Group)
            .join(Service)
            .join(Machine)
            .filter(
                Service.port == service.port,
                Machine.ip == service.machine.ip,
                Group.name == name,
            )
            .first()
        )
    else:
        g = session.query(Group).filter(Group.name == name).first()
    if g:
        g.name = name
        if g.users:
            ids = [u.id for u in g.users]
            for u in users:
                if u.id not in ids:
                    g.users.append(u)
        else:
            g.users = users
        for note in notes:
            g.notes.append(note)
    else:
        g = Group(name=name, service=service, users=[], notes=notes)
        session.add(g)
    return g


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
