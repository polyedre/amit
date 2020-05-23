# Amit

Amit is an enumeration framework to help pentesters.
All the scans are done in threads. And the results can be visualized using `list domains` and `list machines` commands.

![Python application](https://github.com/polyedre/amit/workflows/Python%20application/badge.svg)

## Usage

Example session

```sh
$ amit
Welcome to the amit shell.   Type help or ? to list commands.

> enum domains example.com
> enum hosts 192.168.1.8
> jobs
 - EnumDomain(example.com) RUNNING
 - EnumHost(192.168.1.8) RUNNING
```

And when jobs are finished :

```sh
> jobs
 - EnumDomain(example.com) DONE
 - EnumHost(192.168.1.8) DONE
> hosts -h
usage: hosts [-h] [-d] [-s] [-S] [targets [targets ...]]

Show hosts

positional arguments:
  targets

optional arguments:
  -h, --help            show this help message and exit
  -d, --domains
  -s, --services
  -S, --services-verbose
> hosts -d
93.184.216.34
  domains
    www.example.com
    example.com
192.168.1.8
  domains
> hosts -s 192.168.1.8
192.168.1.8
  services
    21    ftp             None, HP JetDirect ftpd None
    23    telnet          None, HP JetDirect telnetd None
    80    http            None, HP-ChaiSOE None, 1.0
    280   http-mgmt       None, HP-ChaiSOE None, 1.0
    443   https           None None
    515   printer         None None
    631   ipp             None, HP-ChaiSOE None, 1.0
    7627  soap-http       None, HP-ChaiSOE None, 1.0
    9100  jetdirect       None None
    14000 scotty-ft       None None
```

## Installation

Just install it as a python module.

```sh
pip install amit
```
