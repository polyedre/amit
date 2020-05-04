#!/usr/bin/env bash
# Config file for the amit hacking wrapper
# Copyright (C) 2020 Lucas Henry

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# Wordlist used in enumeration
DIR_WORDLIST=~/.ZAP/fuzzers/dirbuster/directory-list-1.0.txt

# Directory were files are served
SERVE_DIR=uploads

# Package manager to use to install ressources
# Supported: pacman
PACKAGE_MANAGER=pacman

# Location of your installed amit directory
AMIT_DIR=~/code/amit

# Command to start a new terminal and run a command in it
TERM_EXT_RUN="termite -e"
