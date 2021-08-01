 #!/bin/bash

path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
file="$path/output.txt"

# complete build
start=$(head -n 1 $file | sed -r "s/(\s*),.*$/\1/")
end=$(tail -n 1 $file | sed -r "s/(\s*),.*$/\1/")

time=$(($end - $start))

download_time=0
boot_time=0
rsync_install_time=0
rsync_run_time=0
ansible_install_time=0
ansible_run_time=0

#machines
machines=$(grep -oP "(?<=Bringing machine ').+(?=' up with 'virtualbox' provider...)" $file)

for machine in ${machines} 
do
	# box
	box=$(grep -oP "(?<=$machine: Importing base box ').+(?='...)" $file)

	# downloading box
	if [ -z "$(grep "$machine: Box '$box' could not be found. Attempting to find and install..." $file)" ] ; then
		machine_download_time=0

		boot_start=$(grep "$machine,action,up,start" $file | sed -r "s/(\s*),.*$/\1/")
	elif [ -z "$(grep "$machine: Downloading: " $file)" ] ; then
		machine_download_time=0

		boot_start=$(grep "$machine,action,up,start" $file | sed -r "s/(\s*),.*$/\1/")
	else
		download_start=$(grep "$machine,action,up,start" $file | sed -r "s/(\s*),.*$/\1/")
		download_end=$(grep "$machine: Successfully added box '$box'" $file | sed -r "s/(\s*),.*$/\1/")

		machine_download_time=$(($download_end - $download_start))	

		boot_start=$(grep "$machine: Importing base box '$box'" $file | sed -r "s/(\s*),.*$/\1/")
	fi

	if [ -z "$(grep "$machine: Running provisioner:" $file)" ] ; then
		machine_rsync_install_time=0
		machine_rsync_run_time=0
		machine_ansible_install_time=0
		machine_ansible_run_time=0

		boot_end=$(grep "$machine,action,up,end" $file | sed -r "s/(\s*),.*$/\1/")
	else
		if [ -z "$(grep "$machine: Installing rsync to the VM..." $file)" ] ; then
			machine_rsync_install_time=0
	
			if [ -z "$(grep "$machine: Rsyncing folder:" $file)" ] ; then
				machine_rsync_run_time=0
	
				boot_end=$(grep -m 1 "$machine: Running provisioner:" $file | sed -r "s/(\s*),.*$/\1/")
			else
				boot_end=$(grep "$machine: Rsyncing folder:" $file | sed -r "s/(\s*),.*$/\1/")
	
				#rsync
				rsync_start=$(grep "$machine: Rsyncing folder:" $file | sed -r "s/(\s*),.*$/\1/")
				rsync_end=$(grep -m 1 "$machine: Running provisioner:" $file | sed -r "s/(\s*),.*$/\1/")
	
				machine_rsync_run_time=$(($rsync_end - $rsync_start))
			fi
		else
			boot_end=$(grep "$machine: Installing rsync to the VM..." $file | sed -r "s/(\s*),.*$/\1/")
	
			rsync_install_start=$(grep "$machine: Installing rsync to the VM..." $file | sed -r "s/(\s*),.*$/\1/")
			
			if [ -z "$(grep "$machine: Rsyncing folder:" $file)" ] ; then
				machine_rsync_run_time=0
	
				rsync_install_end=$(grep -m 1 "$machine: Running provisioner:" $file | sed -r "s/(\s*),.*$/\1/")
			else
				rsync_install_end=$(grep "$machine: Rsyncing folder:" $file | sed -r "s/(\s*),.*$/\1/")
	
				#rsync
				rsync_start=$(grep "$machine: Rsyncing folder:" $file | sed -r "s/(\s*),.*$/\1/")
				rsync_end=$(grep -m 1 "$machine: Running provisioner:" $file | sed -r "s/(\s*),.*$/\1/")
	
				machine_rsync_run_time=$(($rsync_end - $rsync_start))
			fi
	
			machine_rsync_install_time=$(($rsync_install_end - $rsync_install_start))
		fi

		# downloading and installing ansible
			if [ -z "$(grep "$machine: Installing Ansible..." $file)" ] ; then
				machine_ansible_install_time=0
	
				ansible_run_start=$(grep -m 1 "$machine: Running provisioner:" $file | sed -r "s/(\s*),.*$/\1/")
			else
				ansible_install_start=$(grep -m 1 "$machine: Running provisioner:" $file | sed -r "s/(\s*),.*$/\1/")
				ansible_install_end=$(grep -m 1 "$machine: Running ansible-playbook..." $file | sed -r "s/(\s*),.*$/\1/")
	
				machine_ansible_install_time=$(($ansible_install_end - $ansible_install_start))
	
				ansible_run_start=$(grep -m 1 "$machine: Running ansible-playbook..." $file | sed -r "s/(\s*),.*$/\1/")
			fi
	
			ansible_run_end=$(grep "$machine,action,up,end" $file | sed -r "s/(\s*),.*$/\1/")
	
		machine_ansible_run_time=$(($ansible_run_end - $ansible_run_start))

	fi
	machine_boot_time=$(($boot_end - $boot_start))

	download_time=$(($download_time+ $machine_download_time))
	boot_time=$(($boot_time+ $machine_boot_time))
	rsync_install_time=$(($rsync_install_time+ $machine_rsync_install_time))
	rsync_run_time=$(($rsync_run_time+ $machine_rsync_run_time))
	ansible_install_time=$(($ansible_install_time+ $machine_ansible_install_time))
	ansible_run_time=$(($ansible_run_time + $machine_ansible_run_time))
done

printf "$time;$download_time;$boot_time;$rsync_install_time;$rsync_run_time;$ansible_install_time;$ansible_run_time\n" >> $path/times.csv









