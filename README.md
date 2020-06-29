# Amit

Amit is an enumeration framework to help pentesters.
All the scans are done in threads. And the results can be visualized using `list domains` and `list machines` commands.

![Python application](https://github.com/polyedre/amit/workflows/Python%20application/badge.svg)

## Usage

Example session

```
$ amit
Welcome to the amit shell.   Type help or ? to list commands.

> add example.com 9.9.9.9
0 ⌾ > show machines
   1 93.184.216.34   (example.com)
   2 9.9.9.9         ()
0 ⌾ > show domains
   1 - example.com                                        (93.184.216.34)
0 ⌾ > scan machines 1 2
0 ⌾ > show jobs
port_scan(93.184.216.34)       RUNNING
port_scan(9.9.9.9)             RUNNING
2 ⌾ > show services
   1 - 93.184.216.34   80   http                 Edgecast CDN httpd
   2 - 93.184.216.34   443  http                 Edgecast CDN httpd
   3 - 93.184.216.34   1119 bnetgame
   4 - 93.184.216.34   1935 rtmp
   5 - 9.9.9.9         53   domain
   6 - 9.9.9.9         443  https
   7 - 9.9.9.9         8443 https-alt
```

## Installation

Just install it as a python module.

```sh
pip install amit
```
