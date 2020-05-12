#!/usr/bin/env python3


class Service:
    def __init__(self, port, name, product, version):
        self.port = port
        self.name = name
        self.product = product
        self.version = version
        self.scripts = []

    def __str__(self):
        text = (
            f"{BOLD}{self.port:6}{self.name:15} {self.product} {self.version}{RESET}\n"
        )
        for script in self.scripts:
            text += str(script)
        return text
