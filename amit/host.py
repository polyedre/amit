#!/usr/bin/env python3


class Host:
    def __init__(self, ip, hostname, services=[]):
        self.hostname = hostname
        self.ip = ip
        self.services = services

    def add_service(self, service):
        self.services.append(service)

    def __str__(self):
        text = f"{BOLD}{self.hostname} : {self.ip}{RESET}\n"
        text += "\n".join([str(s) for s in self.services])
        return text


# Domain
#   Machine
# Machine (IP)
#   Domains
#   Service (PORT)
