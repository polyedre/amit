[![Issues][issues-shield]][issues-url]
[![GPL License][license-shield]][license-url]
![Python application](https://github.com/polyedre/amit/workflows/Python%20application/badge.svg)

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/polyedre/amit">
    <img src="images/logo.svg" alt="Logo" width="128" height="128">
  </a>

  <h3 align="center">AMIT</h3>

  <p align="center">
    Centralise all your enumerations !
    <!-- <br /> -->
    <!-- <a href="https://github.com/polyedre/amit"><strong>Explore the docs »</strong></a> -->
    <!-- <br /> -->
    <br />
    <!-- <a href="https://github.com/polyedre/amit">View Demo</a> -->
    <a href="https://github.com/polyedre/amit/issues">Report Bug</a>
    ·
    <a href="https://github.com/polyedre/amit/issues">Request Feature</a>
  </p>
</p>

## Table of Contents

- [About the Project](#about-the-project)
  - [Tools used](#tools-used)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
- [Help](#help)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://github.com/polyedre/amit)

Amit is a tool that group other tools into a unique view. Informations collected are organized and stored into a database.

### Tools used

Amit uses some performant tools to fetch information about the targets.

- [Nmap](https://nmap.org/)
- [ldapsearch](https://linux.die.net/man/1/ldapsearch)
- [rpcclient](https://www.samba.org/samba/docs/current/man-html/rpcclient.1.html)

## Getting Started

Just install it as a python module.

```sh
pip install amit
```

## Usage

Just run amit !

```sh
amit
```

1. Add machines

Here we add 2 machines defined by their IP or domain.

```sh
> add 10.10.10.10 example.com
```

2. Scan machines

The 2 machines have id 1 and 2.

```sh
> scan machines 1 2
```

3. Show job status

```sh
> show jobs
```

4. Show services found

```sh
> show services
```

5. Scan services

```sh
> scan services <id> <id>...
```

6. Show informations found for services

```sh
> show services <id> -vvv
```

## Help

You can inspect the list of available commands using the `help` command.
For each command, you can view its usage using the `-h` flag.

## Roadmap

See the [open issues](https://github.com/polyedre/amit/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->

## License

Distributed under the GPL-3.0 License. See `LICENSE` for more information.

<!-- MARKDOWN LINKS & IMAGES -->

[issues-shield]: https://img.shields.io/github/issues/polyedre/amit.svg
[issues-url]: https://github.com/polyedre/amit/issue
[license-shield]: https://img.shields.io/github/license/polyedre/amit.svg
[license-url]: https://github.com/polyedre/amit/blob/master/LICENSE.txt
[product-screenshot]: images/screenshot.png
