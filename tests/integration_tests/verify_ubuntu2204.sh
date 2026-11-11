#!/usr/bin/env bash
# Read-only checks for topology_ubuntu2204.yml; does not create/destroy VMs.
set -euo pipefail
cd "${1:?Usage: bash verify_ubuntu2204.sh ABSOLUTE_SANDBOX_DIRECTORY}"
for machine in server-router home-router server home; do
    vagrant ssh "$machine" -c 'set -eu; test "$(lsb_release -rs)" = 22.04; sudo test -f /etc/netplan/60-csc.yaml; systemctl is-active --quiet systemd-networkd' </dev/null
done
vagrant ssh server-router -c "set -eu; ip -4 route | grep -F '10.77.30.0/24 via 100.100.100.2'; test \"\$(sysctl -n net.ipv4.ip_forward)\" = 1" </dev/null
vagrant ssh home-router -c "set -eu; ip -4 route | grep -F '10.77.20.0/24 via 100.100.100.1'; test \"\$(sysctl -n net.ipv4.ip_forward)\" = 1" </dev/null
vagrant ssh server -c "set -eu; ip -4 route show default | grep -F 'default via 10.77.20.1'; if ip -4 route show default | grep -F 'via 10.0.2.2'; then exit 1; fi; ping -c 3 -W 3 10.77.30.5" </dev/null
vagrant ssh home -c "set -eu; ip -4 route show default | grep -F 'default via 10.77.30.1'; if ip -4 route show default | grep -F 'via 10.0.2.2'; then exit 1; fi; ping -c 3 -W 3 10.77.20.5" </dev/null
echo 'PASS: Ubuntu 22.04 addresses, routed defaults, forwarding and cross-router connectivity'
