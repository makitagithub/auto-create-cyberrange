# Cyber Sandbox Creator

Cyber Sandbox Creator is a tool that can generate portable input files for building lightweight virtual environments using Vagrant and Ansible from a simple YAML definition of topology. The combination of these three tools makes it possible to build virtual machines connected with virtual networks even on a desktop computer.

![usage](doc/sandbox_creator_general.svg "Usage")

---

**Note: This is just a quick guide how to install and generate files with Cyber Sandbox Creator. For full description of how to prepare the host device to run the generated environments and how to build the virtual machines, check our [wiki page](https://gitlab.ics.muni.cz/muni-kypo-csc/cyber-sandbox-creator/-/wikis/home).**

**The latest stable release is available in [Releases](https://gitlab.ics.muni.cz/muni-kypo-csc/cyber-sandbox-creator/-/releases).**

## Installation

### Linux (Ubuntu/Debian)

1. Install git using the command `$ sudo apt-get install git`.
2. Clone the project with `$ git clone https://gitlab.ics.muni.cz/cs4eu/sandbox-creator.git` to an arbitrary directory.
3. Navigate to the project directory (`$ cd cyber-sandbox-creator`).
4. Install pip using `$ sudo apt-get install python3-pip`.
5. Install setuptools with `$ pip3 install setuptools`.
6. Install dependencies with the command `$ pip3 install -r requirements.txt`.

### Windows 10

1. Install [Python 3](https://www.python.org/downloads/windows/). At the beginning of the installation mark the "Add Python to PATH" option.
2. Install [git](https://git-scm.com/downloads).
3. Clone the project with `git clone https://gitlab.ics.muni.cz/cs4eu/sandbox-creator.git` to an arbitrary folder.
4. Navigate to the project folder (`cd cyber-sandbox-creator`).
5. Install Python dependencies using the command `python -m pip install -r requirements.txt`.

## Usage

### Linux (Ubuntu/Debian)

1. After the installation, simply run the command `$ python3 create.py topology.yml` to generate intermediate definition files.
2. Navigate to the newly created directory `sandbox` and run `$ vagrant up` to build the virtual environment.
3. The built environment can be deleted using the command `$ vagrant destroy -f`.

### Windows 10

1. Generate files using the command `python create.py --ansible_local topology.yml`.
2. Navigate to the newly created directory `sandbox` and run `vagrant up` to build the virtual environment.
3. The built environment can be deleted using the command `vagrant destroy -f`.

## License

This project is licensed under the [MIT License](LICENSE).

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




