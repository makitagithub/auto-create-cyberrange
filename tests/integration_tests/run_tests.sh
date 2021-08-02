#!/bin/bash

# Integration tests for Cyber Sandbox Creator.
# For a set of topologies defined in given configuration file, see if Creator correctly generates sandbox by  
# building the virtual environment and then testing the virtual network. 


# Generate sandbox from topology definition file with given optional arguments using Cyber Sandbox Creator.
# param file: path to the topology definition yaml file
# param arguments: optional arguments for Cyber Sandbox Creator
create_sandbox()
{
    local file=$1
    IFS="$oIFS"
    local arguments=($2)
    IFS=$'\n'

    local current_path=$(pwd)
    cd $creator_path
    local output=$(python3 create.py ${arguments[@]} $file)
    if [ "$output" != "Sandbox was successfully created." ]; then
        echo "Failed to build virtual machines: error while creating sandbox."
        if [ "$output" != "" ]; then
            echo "Full error is \"$output\"."
        fi
        cd $current_path
        return 1
    fi
    cd $current_path
}


# Build virtual environment from existing sandbox using Vagrant.
# Output is redirected to corresponding file in output directory.
build_machines()
{
    local current_path=$(pwd)
    cd $creator_path/sandbox

    vagrant up --machine-readable > vagrant_output_build.txt 2>&1
    if [ "$?" -ne 0 ]; then
        # Parse the output file to find out which part of build failed and display appropriate output.
        machine=$(grep ",action,up,start" vagrant_output_build.txt | tail -n 1 | sed -r "s/^[0-9]*,(.*),action,up,start$/\1/")

        if [[ ! -z "$machine" ]]; then

            provisioning=$(grep "$machine: Running provisioner:" vagrant_output_build.txt)
            booting=$(grep "$machine: Booting VM..." vagrant_output_build.txt)
            importing_box=$(grep "$machine: Importing base box" vagrant_output_build.txt)
            downloading_box=$(grep "$machine: Downloading:" vagrant_output_build.txt)
    
            if [[ ! -z "$provisioning" ]]; then
                echo "Failed to build machine $machine: error while provisioning machine."
            elif [[ ! -z "$booting" ]]; then
                echo "Failed to build machine $machine: error while booting machine."
            elif [[ ! -z "$importing_box" ]]; then
                echo "Failed to build machine $machine: error while creating machine."
            elif [[ ! -z "$downloading_box" ]]; then
                echo "Failed to build machine $machine: error while downloading Vagrant box."
            else
                echo "Failed to build machine $machine."
            fi    
        else 
            echo "Failed to build virtual machines: error while running vagrant up."
        fi

        if $print_output; then
            echo -e "Full Vagrant output is:\n"

            cat vagrant_output_build.txt | tee -a $outputdir/build_output_$filename_$i.txt
            rm vagrant_output_build.txt
        else
            echo "Full Vagrant output can be found in file $outputdir/build_output_$filename-$i.txt"

            cat vagrant_output_build.txt > $outputdir/build_output_$filename-$i.txt
            rm vagrant_output_build.txt
        fi
    
        cd $current_path
        return 1
    fi

    cat vagrant_output_build.txt >> $outputdir/build_output_$filename-$i.txt
    rm vagrant_output_build.txt
    cd $current_path
}


# Get list of all host and router machines in virtual network from topology definition file and test that they
# can all reach www.muni.cz and each other, and check the routing.
test_machines()
{
    local current_path=$(pwd)
    cd $creator_path/sandbox

    # Get list of host machines.
    hosts=($(PYTHONPATH=$path python3 -c "from yaml_topology import get_hosts; get_hosts('$creator_path/$file')"))
    # Get list of router machines.
    routers=($(PYTHONPATH=$path python3 -c "from yaml_topology import get_routers; get_routers('$creator_path/$file')"))  

    # check network settings on host machines.
    for host in "${hosts[@]}"
    do 
        vagrant ssh $host -c 'cmd /c ver' > /dev/null 2>&1
        if [ $? -ne 0 ]; then
            # Check that machine has access to the internet.
            vagrant ssh $host -c "ping -c 1 www.muni.cz" > /dev/null 2>&1
            if [ "$?" -ne 0 ]; then
                echo "Test failed: $host can't reach www.muni.cz."
                cd $current_path
                return 1
            fi

            # Check that machine can reach all other host machines.
            for target in "${hosts[@]}"
            do
                if [ "$host" != "$target" ]; then
                    vagrant ssh $host -c "ping -c 1 $target" > /dev/null 2>&1
                    if [ "$?" -ne 0 ]; then
                        echo "Test failed: $host can't reach $target."
                        cd $current_path
                        return 1
                    fi
                fi
            done

            if [ "${#routers[@]}" -ne 0 ]; then
                # Check that machine can reach all router machines.
                for target in "${routers[@]}"
                do
                    vagrant ssh $host -c "ping -c 1 $target" > /dev/null 2>&1
                    if [ "$?" -ne 0 ]; then
                        echo "Test failed: $host can't reach $target."
                        cd $current_path
                        return 1
                    fi
                done

                # Check that route from host goes through the correct router.        
                network=$(PYTHONPATH=$path python3 -c "from yaml_topology import get_network_for_host; get_network_for_host('$creator_path/$file', '$host')")
                router=$(PYTHONPATH=$path python3 -c "from yaml_topology import get_router_for_network; get_router_for_network('$creator_path/$file', '$network')")
        
                output=$(vagrant ssh $host -c "traceroute $router | head -n 2 | tail -n 1 | grep '$router'" 2> /dev/null | tr -d '\r')
                if [ -z "$output" ]; then
                    echo "Test failed: $host does not route through $router."
                    cd $current_path
                    return 1
                fi

                # Check if network contains border router.
                if [[ $arguments_string == *"border_router"* ]]; then
                    # Check that machine can reach border router.
                    vagrant ssh $host -c "ping -c 1 br" > /dev/null 2>&1
                    if [ "$?" -ne 0 ]; then
                        echo "Test failed: $host can't reach border router."
                        cd $current_path
                        return 1
                    fi

                    # Check that route from host goes through the border router.
                    output=$(vagrant ssh $host -c "traceroute www.muni.com | grep 'br'" 2> /dev/null | tr -d '\r')
                    if [ -z "$output" ]; then
                        echo "Test failed: $host does not route through border router."
                        cd $current_path
                        return 1
                    fi
                fi
            fi
        else
            # Check that machine has access to the internet.
            output=$(vagrant powershell $host -c "ping -c 1 www.muni.cz" 2>&1 | tr -d '\r' | grep "output code 0")
            if [ -z "$output" ]; then
                echo "Test failed: $host can't reach www.muni.cz."
                cd $current_path
                return 1
            fi

            # Check that machine can reach all other host machines.
            for target in "${hosts[@]}"
            do
                if [ "$host" != "$target" ]; then
                    ip=$(PYTHONPATH=$path python3 -c "from yaml_topology import get_ip_for_host; get_ip_for_host('$creator_path/$file', '$target')")
                    vagrant ssh $host -c "ping -c 1 $ip" > /dev/null 2>&1
                    if [ "$?" -ne 0 ]; then
                        echo "Test failed: $host can't reach $target."
                        cd $current_path
                        return 1
                    fi
                fi
            done

            if [ "${#routers[@]}" -ne 0 ]; then
                # Check that machine can reach all router machines.
                for target in "${routers[@]}"
                do
                    ip=$(PYTHONPATH=$path python3 -c "from yaml_topology import get_ip_for_host; get_ip_for_host('$creator_path/$file', '$target')")
                    output=$(vagrant powershell $host -c "ping -c 1 www.muni.cz" 2>&1 | tr -d '\r' | grep "output code 0")
                    if [ -z "$output" ]; then
                        echo "Test failed: $host can't reach $target."
                        cd $current_path
                        return 1
                    fi
                done
            fi
        fi
    done

    # Check network settings on router machines.
    for router in "${routers[@]}"
    do 
        # Check that machine can reach all other router machines.
        for target in "${routers[@]}"
        do
            if [ "$router" != "$target" ]; then
                vagrant ssh $router -c "ping -c 1 $target" > /dev/null 2>&1
                if [ "$?" -ne 0 ]; then
                    echo "Test failed: $router can't reach $target."
                    cd $current_path
                    return 1
                fi
            fi
        done

        # Check that machine can reach all host machines.
        for target in "${hosts[@]}"
        do
            vagrant ssh $router -c "ping -c 1 $target" > /dev/null 2>&1
            if [ "$?" -ne 0 ]; then
                echo "Test failed: $router can't reach $target."
                cd $current_path
                return 1
            fi
        done

        # Check if network contains border router.
        if [[ $arguments_string == *"border_router"* ]]; then
            # Check that machine can reach border router.
            vagrant ssh $router -c "ping -c 1 br" > /dev/null 2>&1
            if [ "$?" -ne 0 ]; then
                echo "Test failed: $router can't reach border router."
                cd $current_path
                return 1
            fi

            # Check that route from host goes through the border router.
            output=$(vagrant ssh $router -c "traceroute www.muni.com | grep 'br'" 2> /dev/null | tr -d '\r')
            if [ -z "$output" ]; then
                echo "Test failed: $router does not route through border router."
                cd $current_path
                return 1
            fi
        fi
    done

    cd $current_path
}

# Destroy existing virtual environment using Vagrant.
# Output is redirected to corresponding file in output directory.
destroy_machines()
{
    local current_path=$(pwd)
    cd $creator_path/sandbox
    vagrant destroy -f > vagrant_output_destroy.txt 2>&1
    if [ "$?" -eq 1 ]; then
        echo "Failed to destroy machines."

        if $print_output; then
            echo -e "Full Vagrant output is:\n"

            cat vagrant_output_destroy.txt
            rm vagrant_output_destroy.txt
        else
            echo "Vagrant output can be found in file $outputdir/destroy_output_$filename-$i.txt"
            
            cat vagrant_output_destroy.txt >> $outputdir/destroy_output_$filename-$i.txt
            rm vagrant_output_destroy.txt
        fi

        cd $current_path
        return 1
    fi
    
    rm vagrant_output_destroy.txt
    cd $current_path
}

# Open topology definition file and change all host OS images to given value creating a new definition file.
# param file: path to the topology definition yaml file
# param box: vagrant box to be used in host machines, needs to be available either locally or on vagrant cloud and work with VirtualBox as provider
# Return path to new topology definition file in temporary directory.
change_boxes()
{
    local file=$1
    local box=$2
    local filename=$(basename "$file" .yml)

    local box_name=$(PYTHONPATH=$path python3 -c "from yaml_topology import get_box_name; get_box_name('$path/box_names_mapping.yml', '$box')")
    local box_memory=$(PYTHONPATH=$path python3 -c "from yaml_topology import get_box_memory; get_box_memory('$path/box_memory_mapping.yml', '$box')")

    newfile="$creator_path/tmp_topologies/${filename}_$box_name.yml"
    
    PYTHONPATH=$path python3 -c "from yaml_topology import change_boxes; change_boxes('$file', '$newfile', '$box', '$box_memory')"

    echo "$newfile"
}

# Get absolute path to the script.
path="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
creator_path=$(dirname $path)

config_file=""
print_output=false

# Read command-line arguments given while starting the script and save values to variables.
while [ "$1" != "" ]; do
    case $1 in
        -c | --config )         shift
                                config_file="$1"
                                ;;
        -p | --print_output )   print_output=true
                                ;;
        -h | --help )           echo "Usage: ./run_tests.sh [-c|--config CONFIG_FILE] [-p|--print_output]"
                                echo "    CONFIG_FILE: configuration file [default: $path/config.yml]"
                                ;;
        * )                     echo "Failed to parse arguments: unknown argument $1"
                                exit 1
                                ;;
    esac
    shift
done

# Check if path to configuration file was set by a command-line argument. If not use the default value.
# If the path passes as command-line argument was relative, append it to the path to current directory to get absolute path.
if [ -z "$config_file" ]; then
    config_file="$path/config.yml"
elif [[ ! "$config_file" = /* && ! "$config_file" = ~* ]]; then
    config_file=$(pwd)/$config_file
fi 

# Check if given configuration file exists.
if [ ! -e $config_file ]; then
    echo "Failed to process configuration file: file $config_file not found."
    exit 1
fi

# Check if configuration file is a yaml.
if [[ $config_file != *.yml && $config_file != *.yaml ]]; then
    echo "Failed to process configuration file: file $config_file has wrong format."
    exit 1
fi

oIFS="$IFS"
IFS=$'\n'

# Get a list of paths to topology definition files from configuration file.
files=($(PYTHONPATH=$path python3 -c "from yaml_config import get_topology_files; get_topology_files('$config_file')"))
if [ "${#files[@]}" -eq 0 ]; then
    echo "Failed to process configuration file: no topologies were found."
fi

# Get path to output directory from configuration file.
outputdir=$(PYTHONPATH=$path python3 -c "from yaml_config import get_output_dir; get_output_dir('$config_file')")
if [[ ! "$outputdir" = /* && ! "$outputdir" = ~* ]]; then
    outputdir=$(pwd)/$outputdir
fi 

# Create output directory or delete all contents if it already exists.
if [ -d "$outputdir" ]; then
    rm -rf "$outputdir/"*
else
    mkdir -p "$outputdir"
fi

# Create directory for temporary topology files.
mkdir -p "./tmp_topologies"

# Flag indicating if any of the tested topologies failed to build correctly.
failed=false

for file in ${files[@]}
do
    # Get list of optional arguments for creating sandbox from configuration file.
    arguments_strings=($(PYTHONPATH=$path python3 -c "from yaml_config import get_topology_arguments; get_topology_arguments('$config_file', '$file')"))
    if [ "${#arguments_strings[@]}" -eq 0 ]; then
        arguments_strings=(" ")
    fi

    # Get list of OS images to be tried in current topology's host machines.
    boxes=($(PYTHONPATH=$path python3 -c "from yaml_config import get_topology_boxes; get_topology_boxes('$config_file', '$file')"))
    boxes=("${boxes[@]}")

    for box in ${boxes[@]}
    do 
        if [ "$box" = "no-box" ]; then
            newfile=$file
        else
            newfile=$(change_boxes "$creator_path/$file" "$box")
        fi

        filename=$(basename "$newfile" .yml)

        i=1
        for arguments_string in ${arguments_strings[@]}
        do
            echo "Starting test for topology $filename and execution arguments [$arguments_string]."

            # Try to generate sandbox.
            if create_sandbox $newfile $arguments_string; then
                echo "Sandbox was succesfully created."
            else
                echo "Stopping tests."
                exit 1
                # If generating sandbox failed, exit with error.
            fi

            # Try to build and test machines from sandbox.
            # If either fails the output from failed part is also written to terminal.
            if build_machines; then 
                echo "All machines have been built and provisioned." 

                if test_machines; then
                    echo "All tests have been succesfull."
                else
                    echo "Stopping tests."
                    failed=true   
                fi
            else
                echo "Stopping tests."
                failed=true                
            fi  

            # Try to destroy virtual environment.
            # Should not fail unless something unexpected happens, in that case it might be necessary to destroy remaining machines manually.
            if destroy_machines; then
                echo "All machines have been destroyed."
            else
                echo "Stopping tests."
                failed=true
            fi

            # If building or testing the virtual environment failed, exit with error.
            if $failed; then
                exit 1
            fi

            i=$(( $i+1 ))
        done

        # Remove temporary topology file if it exists.
        if [ "$newfile" != "$file" ]; then
            rm "$newfile"
        fi
    done
    
done

# Remove directory for temporary topology files.
if [ -d "./tmp_topologies" ]; then
    rm -r "./tmp_topologies"
fi
