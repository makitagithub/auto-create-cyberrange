# Ubuntu 22.04 networking

CSC selects its bundled `csc_netplan` role when the guest reports Ubuntu 22.04.
Other guests continue to use the existing external `interface` role. This change
does not modernize that legacy role or establish support for other Ubuntu releases.

## How it works

- Vagrant first configures the exercise IP addresses. Ansible maps those addresses
  to the actual Ethernet interface names; missing addresses fail before changes.
- CSC writes static exercise addresses and routes to `/etc/netplan/60-csc.yaml`.
  Existing cloud-init and Vagrant YAML files are preserved.
- Exactly one additional Ethernet interface must exist: Vagrant's NAT management
  interface. Its DHCP address is preserved.
- A standalone host and a router retain DHCP-provided management routes.
  A host behind a topology router uses its first exercise interface's router as
  its IPv4 default gateway. Management DHCP route installation is disabled.
  Matching IPv4/IPv6 DHCP overrides satisfy the networkd backend's requirements.
- Router-to-router routes use the existing CSC WAN and routing model.
- A candidate is staged with existing `/etc/netplan` files and checked with
  `netplan generate --root-dir` before installation. Invalid candidates leave
  the active file unchanged. `netplan apply` runs only if the CSC file changes.
- Check mode validates the candidate, then removes its temporary staging files;
  it never installs or applies the candidate.

The role assumes the normal Vagrant Ubuntu 22.04 layout (networkd, one NAT NIC,
and exercise Ethernet NICs whose Netplan IDs are their interface names).
Custom Netplan configurations in `/run/netplan` or `/lib/netplan`, extra NICs,
bridges, and NetworkManager guests are not covered by this implementation.
The legacy router forwarding/SNAT tasks are unchanged. IPv6 exercise routing is
outside the current CSC IPv4 routing model.

## Use the modified source

Activate the Python environment used for CSC. Use an editable installation, or
run from the checkout explicitly:

```bash
PYTHONPATH="$PWD" python -m sandboxcreator.scripts.create /absolute/topology.yml -o /absolute/new-sandbox
```

Do not assume an older installed `create-sandbox` uses the checkout.
Generation replaces `preconfig`; preserve any manual changes before regenerating.
The bundled Netplan role is copied on every generation, so this fix does not rely
on editing generated files.

## Tests

Unit tests include routed hosts, router static routes, legacy variables, all
shipped topology samples, and regeneration of the bundled role:

```bash
python -m unittest discover -s tests/unit_tests -v
```

To exercise two Ubuntu routers and two Ubuntu hosts, generate into a new directory:

```bash
PYTHONPATH="$PWD" python -m sandboxcreator.scripts.create \
  "$PWD/tests/integration_tests/topology_ubuntu2204.yml" -o /absolute/new-sandbox
cd /absolute/new-sandbox
vagrant up
```

This creates four VMs (1 GiB RAM and one vCPU each); it is not a read-only test.
It downloads missing boxes/packages. The fixture uses 10.77.20.0/24 and
10.77.30.0/24 plus CSC's default WAN, so run it in isolation from other sandboxes
using those internal networks.

Run the verification script from the repository:

```bash
bash tests/integration_tests/verify_ubuntu2204.sh /absolute/new-sandbox
```

Repeat `vagrant provision` to check idempotence. Reboot with
`vagrant reload --no-provision`, then repeat verification to check persistence.
VM cleanup is intentionally not automatic.

## 20-VM nested virtualization test (2026-11-11)

The 20-VM fixture is `tests/integration_tests/topology_ubuntu2204_20vm.yml`: two
routers (1024 MiB each), eighteen hosts (768 MiB each), one vCPU per VM.
Generate with `create-sandbox topology.yml -a -o /absolute/new-sandbox` to use
host-installed Ansible. All 20 VMs booted and completed Ansible provisioning.
All 18 hosts reached their local router; representative cross-network pings
succeeded in both directions with zero packet loss.

This VMware/VirtualBox test required a test-only Vagrant provider override:
`vb.customize ["modifyvm", :id, "--paravirtprovider", "none"]`. One guest also
needed a reset after a kernel boot fault. These are boot-environment issues
observed before Ansible, not proof that default nested virtualization is stable.
Host Ansible 2.10 also required `PYTHONNOUSERSITE=1 vagrant provision` to avoid
a user-installed Jinja2 incompatibility; no dependency versions were changed.
The tested Vagrantfile and initial failure logs are retained with the evidence.

No fixed VM-count cap was found in CSC's generation/build code. CPU and memory
checks warn on shortages rather than enforcing a numeric VM limit. This run
confirms 20 VMs in this environment; it does not establish a maximum.
