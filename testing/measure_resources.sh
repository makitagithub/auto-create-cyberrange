#!/bin/bash

create_sandbox()
{
    local file=$1
    IFS="$oIFS"
    local arguments=($2)
    IFS=$'\n'
    python3 create.py ${arguments[@]} $file >/dev/null 2>&1
    
}

build_machines()
{
    local current_path=$(pwd)
    cd $path/../sandbox
    vagrant up --machine-readable > $path/output.txt
    cd $current_path
}

destroy_machines()
{
    local current_path=$(pwd)
    cd $path/../sandbox
    vagrant destroy -f --machine-readable >/dev/null 2>&1
    cd $current_path
}

oIFS="$IFS"
IFS=$'\n'

path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

printf "topology;build time;used memory;commited memory;used disk space;peak cpu usage;avg cpu usage\n" > $path/resources.csv
printf "topology;complete time;downloading boxes;booting machines;installing rsync;running rsync;installing ansible;running ansible\n" > $path/times.csv

config_file=$1

files=($(PYTHONPATH=$path python3 -c "from yaml_config import get_topology_files; get_topology_files('$config_file')"))

for file in "${files[@]}"
do
    filename=$(basename "$file" .yml)

    arguments_strings=($(PYTHONPATH=$path python3 -c "from yaml_config import get_topology_arguments; get_topology_arguments('$config_file', '$file')"))

    if [ "${#arguments_strings[@]}" -eq 0 ]; then
        arguments_strings=(" ")
    fi
    i="1"
    for arguments_string in ${arguments_strings[@]}
    do
        echo "$filename $arguments_string"

        vagrant box remove munikypo/debian-10 >/dev/null 2>&1
        vagrant box remove munikypo/kali-2019.4 >/dev/null 2>&1
        vagrant box remove munikypo/kali-2020.4 >/dev/null 2>&1
        vagrant box remove munikypo/windows-server-2019 >/dev/null 2>&1
    
        for i in {1..2}
        do
            sar -r -o $path/mem 1 >/dev/null 2>&1 &
            mem_pid=$!
    
            $path/disk_usage.sh $path/disk.txt 1 &
            disk_pid=$!
    
            sar -o $path/cpu 1 >/dev/null 2>&1 &
            cpu_pid=$!
    
            if create_sandbox $path/../$file $arguments_string; then
                build_machines
                    
                printf "$filename;" >> $path/times.csv
                printf "$filename;" >> $path/resources.csv
                bash $path/parse_times.sh

                destroy_machines
            fi
    
            kill $mem_pid
            kill $disk_pid
            kill $cpu_pid
    
            start=$(head -n 1 $path/output.txt | sed -r "s/(\s*),.*$/\1/")
            end=$(tail -n 1 $path/output.txt | sed -r "s/(\s*),.*$/\1/")
    
            time=$(($end - $start))
    
            mem_usg_first=$(sar -r -f $path/mem | tail -n +4 | head -n 1 | awk '{ print $5 }')
            mem_usg_max=$mem_usg_first
    
            mem_commit_first=$(sar -r -f $path/mem | tail -n +4 | head -n 1 | awk '{ print $9 }')
            mem_commit_max=$mem_commit_first     
    
            for line in $(sar -r -f $path/mem | tail -n +4 | sed \$d)
            do
                usg=$(echo $line | awk '{ print $5 }')
                if [ $usg -gt $mem_usg_max ]; then
                    mem_usg_max=$usg
                fi
                commit=$(echo $line | awk '{ print $9 }')
                if [ $commit -gt $mem_commit_max ]; then
                    mem_commit_max=$commit
                fi
            done     
    
            mem_usg=$(( ($mem_usg_max-$mem_usg_first) / 1024 ))
            mem_commit=$(( ($mem_commit_max-$mem_commit_first) / 1024 ))
    
            disk_first=$(head -n 1 $path/disk.txt | awk '{ print $3 }')
            disk_max=$disk_first
    
            while IFS= read -r line
            do
                number=$(echo $line | awk '{ print $3 }')
                if [ $number -gt $disk_max ]; then
                    disk_max=$number
                fi
            done < $path/disk.txt
    
            disk=$(( ($disk_max-$disk_first) / 1024 ))
                
            cpu_max=$(sar -f $path/cpu | grep "all" | head -n 1 | awk '{ print (100 - $9)*100 }')
    
            for line in $(sar -f $path/cpu | tail -n +4 | sed \$d)
            do
                number=$(echo $line | awk '{ print (100 - $9)*100 }')
                if [ $number -gt $cpu_max ]; then
                    cpu_max=$number
                fi
            done
    
            cpu_peak=$(awk "BEGIN { print $cpu_max/100 }")
            cpu_avg=$(sar -f $path/cpu | grep "all" | tail -n 1 | awk '{ print (100 - $8) }')
    
            printf "$time;$mem_usg;$mem_commit;$disk;$cpu_peak;$cpu_avg\n" >> $path/resources.csv
    
            rm $path/output.txt
            rm $path/mem
            rm $path/disk.txt
            rm $path/cpu
            i="2"
        done

    done

done