# Cyber Sandbox Creator

Cyber Sandbox Creator is a tool that can generate portable definition files and build virtual environments using VirtualBox, Vagrant, and Ansible from a simple YAML definition of topology. The combination of these tools makes it possible to create virtual machines connected with virtual networks with minimal effort, even on a desktop computer.

![usage](doc/sandbox_creator_general.svg "Usage")

---

**Note: This is just a quick guide how to install and generate files with Cyber Sandbox Creator. For full description of how to prepare the host device to run the generated environments and how to build the virtual machines, check our [wiki page](https://gitlab.ics.muni.cz/muni-kypo-csc/cyber-sandbox-creator/-/wikis/home).**

**The latest stable release is available in [Releases](https://gitlab.ics.muni.cz/muni-kypo-csc/cyber-sandbox-creator/-/releases).**

## Installation

### Linux (Ubuntu/Debian)

1. Install pip using `$ sudo apt-get install python3-pip`.
2. Install setuptools with `$ pip3 install setuptools`.
3. Install Kypo Topology Definition `$ pip3 install kypo-topology-definition --extra-index-url https://gitlab.ics.muni.cz/api/v4/projects/2358/packages/pypi/simple`.
4. Install Cyber Sandbox Creator with `$ pip3 install sandboxcreator`.

### Windows 10

1. Install [Python 3](https://www.python.org/downloads/windows/). At the beginning of the installation mark the "Add Python to PATH" option.
3. Install Kypo Topology Definition `$ pip install kypo-topology-definition --extra-index-url https://gitlab.ics.muni.cz/api/v4/projects/2358/packages/pypi/simple`.
4. Install Cyber Sandbox Creator with `$ pip install sandboxcreator`.

## Usage

### Linux (Ubuntu/Debian) and Windows 10

1. After the installation, simply run the command `$ create-sandbox <topology_definition>` to generate intermediate definition files.
2. Navigate to the newly created directory `sandbox` (next to the topology definition) and run `$ manage-sandbox build` to build the virtual environment.
3. The built environment can be deleted using the command `$ manage-sandbox destroy`.

## License

This project is licensed under the [MIT License](LICENSE).

## How to cite

If you use or build upon Cyber Sandbox Creator, we would appreciate it if you link to this GitLab repository. If you can, please also use the BibTeX entry below to cite the original work.
Jan Vykopal, Pavel Čeleda, Pavel Seda, Valdemar Švábenský, and Daniel Tovarňák.\
*Scalable Learning Environments for Teaching Cybersecurity Hands-on [in press].*\
In Proceedings of the 51st IEEE Frontiers in Education Conference (FIE' 2021).
```
@inproceedings{Vykopal2021Scalable,
    author    = {Vykopal, Jan and Čeleda, Pavel and Seda, Pavel and Švábenský, Valdemar and Tovarňák, Daniel},
    title     = {{Scalable Learning Environments for Teaching Cybersecurity Hands-on [in press]}},
    booktitle = {Proceedings of the 51st IEEE Frontiers in Education Conference},
    series    = {FIE '21},
    location  = {Lincoln, Nebraska, USA},
    publisher = {IEEE},
    address   = {New York, NY, USA},
    month     = {10},
    year      = {2020},
    pages     = {1--9},
    numpages  = {9},
}
```

## Credits

**[Cybersecurity Laboratory](https://kypo.fi.muni.cz)**\
**Faculty of Informatics**\
**Masaryk University**

**Project lead**: Jan Vykopal

**Lead developer**: Attila Farkas

**Developer**: Jana Ziková

**Contributors**:

- Valdemar Švábenský - user testing
- Daniel Tovarňák (KYPO Cyber Range Platform) - technical advisor
- Kamil Andoniadis (KYPO Cyber Range Platform)

**Student contributors:**  all students who use the tool for their thesis projects or training

### Acknowledgements

<table>
  <tr>
    <td>![EU](doc/EU.jpg "EU emblem")</td>
    <td>
This software and accompanying documentation is part of a [project](https://cybersec4europe.eu) that has received funding from the European Union’s Horizon 2020 research and innovation programme under grant agreement No. 830929.
</td>
  </tr>
  <tr>
      <td>![TACR](doc/TACR.png "TACR logo")</td>
      <td>This software was developed with the support of the Technology Agency of the Czech Republic (TA ČR) from the National Centres of Competence programme (project identification TN01000077 – [National Centre of Competence in Cybersecurity](https://nc3.cz/)). 
      </td>
  </tr>
 </table>




