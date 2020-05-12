#!/usr/bin/env python3

from .interactive import start_shell
from .manager import Manager


def main():
    manager = Manager()
    start_shell(manager)
