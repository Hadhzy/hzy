<p align="center">
<img src="https://raw.githubusercontent.com/Hadhzy/hzy/main/_static/images/logo_buffalo_2.png" alt="" width="70%">
</p>


![OS Linux](https://img.shields.io/badge/OS-Linux-blue)

---
This project is part of the [slodon](https://slodon.io/) ecosystem. It is a python API for the [`libei`](https://gitlab.freedesktop.org/libinput/libei) c library, which allows you to create emulated input.
The project is being developed by the [Hadhzy](https://discord.gg/Qt89JBB2ES) team.

## Installation
- It is really important to note, that `hzy` is only compatible with Linux. This is because it uses the [`snegg`](https://gitlab.freedesktop.org/libinput/snegg) API, which is only available on Linux.


- It is mandatory to have [`libei`](https://gitlab.freedesktop.org/libinput/libei) installed on your system. You can find the installation instructions [here](https://gitlab.freedesktop.org/libinput/snegg/-/blob/master/README.md#installation).

- If you are using one of these distros, you should be able to install libei by only using your package manager:

Get Libei:

- ALT Linux
- Arch Linux,
- Fedora
- FreeBSD

> **Note**: **libei needs to be installed**: It can be installed automatically, in the future!
>
>
```shell
python3 -m pip install hzy
```
---

## Documentation

The full documentation can be viewed [here](https://hadhzy.github.io/hzy/).

---

## Usage

Examples here(TBD)

---
## Dependencies

* <a href="https://gitlab.freedesktop.org/libinput/snegg" target="_blank"><code>snegg</code></a> - the API that `hzy` wraps.
---
## Contributing
`See:` [CONTRIBUTING.md](https://github.com/Hadhzy/hzy/blob/master/CONTRIBUTING.md)
