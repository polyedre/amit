# Amit

Amit is an enumeration framework to help pentesters.
All the scans are done in threads. And the results can be visualized using `list targets` and `list machines` commands.

## Usage

Example session

```sh
$ amit
Welcome to the amit shell.   Type help or ? to list commands.

> enum example.com
> scan 192.168.1.8
> list targets
10588.example.com
1270011721.example.com                             1270011721.example.com
ajloy1.01.example.com
13.example.com
113751.example.com
boris.klimenko.01.example.com
ilya2.androsov.029.example.com
69.48.135.122.example.com                          69.48.135.122.example.com
stas4.andrianov.14.example.com
112621.example.com
12165.example.com
> list machines
93.184.216.34
69.48.135.127
69.48.135.102
69.48.135.125
192.168.1.8
    14000 scotty-ft       None None
    443   https           None None
    515   printer         None None
    21    ftp             None None
    631   ipp             None None
    23    telnet          None None
    7627  soap-http       None None
    80    http            None None
    9100  jetdirect       None None
    280   http-mgmt       None None
> list jobs
 - enum_domain DONE
 - ip_scanner DONE
>
```

## Installation

Just install it as a python module.

```sh
pip install amit
```
