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
    ips = relationship("Machine", secondary="domain_machine_link")

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

    def __repr__(self):
        return f"Service(port={self.port}, name={self.name}, product={self.product}) on {self.machine.ip}"


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
