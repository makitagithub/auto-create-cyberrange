#!/bin/bash

# Integration tests for Cyber Sandbox Creator.

# Set constants
TEST_PATH="$(readlink -e "$(dirname "${BASH_SOURCE[0]}")")"
CSC_PATH="$(readlink -e "${TEST_PATH}/../..")"
CREATOR_PATH="${CSC_PATH}/sandboxcreator/scripts/create.py"
MANAGER_PATH="${CSC_PATH}/sandboxcreator/scripts/manage.py"
TEMP_TOPOLOGY_PATH="$(readlink -f "${PWD}/tmp_topologies")"

# Generate an intermediate definition from a topology definition file with
# given optional arguments using Cyber Sandbox Creator.
# param file: path to the topology definition yaml file
# param arguments: optional arguments for Cyber Sandbox Creator
create_sandbox()
{
    local file=$1
    IFS="$oIFS"
    local arguments=( "$2" )
    IFS=$'\n'

	echo '└── Generating intermediate definition...'
    PYTHONPATH=$CSC_PATH python3 "$CREATOR_PATH" "-o=${TEMP_TOPOLOGY_PATH}/sandbox" "$file" 1> /dev/null || { echo 'Error while creating intermediate definition.'; exit 1; }
}


# Build virtual environment from existing sandbox using Vagrant.
# Output is redirected to corresponding file in output directory.
build_machines()
{
	echo '└── Building the sandbox...'
    PYTHONPATH=$CSC_PATH python3 "$MANAGER_PATH" 'build' '-v' "-d=${TEMP_TOPOLOGY_PATH}/sandbox" > vagrant_output_build.txt 2>&1
    if [ "$?" -ne 0 ]; then
        # Parse the output file to find out which part of build failed and display appropriate output.
        machine=$(grep ",action,up,start" vagrant_output_build.txt | tail -n 1 | sed -r "s/^[0-9]*,(.*),action,up,start$/\1/")

        if [ -n "$machine" ]; then

            provisioning=$(grep "$machine: Running provisioner:" vagrant_output_build.txt)
            booting=$(grep "$machine: Booting VM..." vagrant_output_build.txt)
            importing_box=$(grep "$machine: Importing base box" vagrant_output_build.txt)
            downloading_box=$(grep "$machine: Downloading:" vagrant_output_build.txt)

            if [ -n "$provisioning" ]; then
                echo "Failed to build machine $machine: error while provisioning machine."
            elif [ -n "$booting" ]; then
                echo "Failed to build machine $machine: error while booting machine."
            elif [ -n "$importing_box" ]; then
                echo "Failed to build machine $machine: error while creating machine."
            elif [ -n "$downloading_box" ]; then
                echo "Failed to build machine $machine: error while downloading Vagrant box."
            else
                echo "Failed to build machine $machine."
            fi
        else
            echo "Failed to build virtual machines: error while running vagrant up."
        fi

        if $print_output; then
            echo -e "Full Vagrant output is:\n"
            cat vagrant_output_build.txt | tee -a "$outputdir/build_output_${filename}_$i.txt"
            rm vagrant_output_build.txt
        else
            echo "Full Vagrant output can be found in file $outputdir/build_output_$filename-$i.txt"

            cat vagrant_output_build.txt > "$outputdir/build_output_$filename-$i.txt"
            rm vagrant_output_build.txt
        fi

        return 1

    fi

    cat vagrant_output_build.txt >> "${outputdir}/build_output_${filename}-${i}.txt"
    rm vagrant_output_build.txt
}


# Get list of all host and router machines in virtual network from topology definition file and test that they
# can all reach www.muni.cz and each other, and check the routing.
test_machines()
{
	echo '└── Initializing tests...'
    local current_path
    current_path=$(pwd)
    cd "${TEMP_TOPOLOGY_PATH}/sandbox" || { echo "Could not find the intermediate definition"; cleanup_and_exit 1; }

    # Get list of host machines.
    mapfile -t hosts < <(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_hosts; get_hosts('$TEST_PATH/$file')")
    # Get list of router machines.
    mapfile -t routers < <(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_routers; get_routers('$TEST_PATH/$file')")

    # check network settings on host machines.
    for host in "${hosts[@]}"
    do

        if ! vagrant ssh "$host" -c 'cmd /c ver' > /dev/null 2>&1; then
            # Check that machine has access to the internet.
            vagrant ssh "$host" -c "ping -c 1 www.muni.cz" > /dev/null 2>&1 && echo "    └── '$host' has Internet access." || { echo "Test failed: $host can't reach www.muni.cz."; cd "$current_path"; return 1; }

            # Check that machine can reach all other host machines.
            for target in "${hosts[@]}"
            do
                if [ "$host" != "$target" ]; then
                    vagrant ssh "$host" -c "ping -c 1 $target" > /dev/null 2>&1 && echo "    └── '$host' can access '$target'." || { echo "Test failed: $host can't reach $target."; cd "$current_path"; return 1; }
                fi
            done

            if [ "${#routers[@]}" -ne 0 ]; then
                # Check that machine can reach all router machines.
                for target in "${routers[@]}"
                do
                    vagrant ssh "$host" -c "ping -c 1 $target" > /dev/null 2>&1 && echo "    └── '$host' can access '$target'." || { echo "Test failed: $host can't reach $target."; cd "$current_path"; return 1; }
                done

                # Check that route from host goes through the correct router.
                network=$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_network_for_host; get_network_for_host('$TEST_PATH/$file', '$host')")
                router=$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_router_for_network; get_router_for_network('$TEST_PATH/$file', '$network')")

                output=$(vagrant ssh "$host" -c "traceroute $router | head -n 2 | tail -n 1 | grep '$router'" 2> /dev/null | tr -d '\r')
                if [ -n "$output" ]; then
                	echo "    └── '$host routes through $router'"
                else
                	echo "Test failed: $host does not route through $router."
                	cd "$current_path"
                	return 1
                fi
            fi
        else
            # Check that machine has access to the internet.
            output=$(vagrant powershell "$host" -c "ping -c 1 www.muni.cz" 2>&1 | tr -d '\r' | grep "output code 0")
            if [ -n "$output" ]; then
            	echo "    └── '$host' has Internet access."
            else
            	echo "Test failed: $host can't reach www.muni.cz."
            	cd "$current_path"
            	return 1
			fi

            # Check that machine can reach all other host machines.
            for target in "${hosts[@]}"
            do
                if [ "$host" != "$target" ]; then
                    ip=$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_ip_for_host; get_ip_for_host('$TEST_PATH/$file', '$target')")
                    vagrant ssh "$host" -c "ping -c 1 $ip" > /dev/null 2>&1 && echo "    └── '$host' can access '$target'." || { echo "Test failed: $host can't reach $target."; cd "$current_path"; return 1; }
                fi
            done

            if [ "${#routers[@]}" -ne 0 ]; then
                # Check that machine can reach all router machines.
                for target in "${routers[@]}"
                do
                    ip=$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_ip_for_host; get_ip_for_host('$TEST_PATH/$file', '$target')")
                    output=$(vagrant powershell "$host" -c "ping -c 1 www.muni.cz" 2>&1 | tr -d '\r' | grep "output code 0")
                    if [ -n "$output" ]; then
                    	echo "    └── '$host' can access '$target'."
                    else
                    	echo "Test failed: $host can't reach $target."
                    	cd "$current_path"
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
                vagrant ssh "$router" -c "ping -c 1 $target" > /dev/null 2>&1 && echo "    └── '$router' can access '$target'." || { echo "Test failed: $router can't reach $target."; cd "$current_path"; return 1; }
            fi
        done

        # Check that machine can reach all host machines.
        for target in "${hosts[@]}"
        do
            vagrant ssh "$router" -c "ping -c 1 $target" > /dev/null 2>&1 && echo "    └── '$router' can access '$target'." || { echo "Test failed: $router can't reach $target."; cd "$current_path"; return 1; }
        done
    done

    cd "$current_path" || return 1
}

# Destroy existing virtual environment using Vagrant.
# Output is redirected to corresponding file in output directory.
destroy_machines()
{
	echo '└── Destroying sandbox...'
    PYTHONPATH=$CSC_PATH python3 "$MANAGER_PATH" 'destroy' '-v' "-d=$TEMP_TOPOLOGY_PATH/sandbox" > vagrant_output_destroy.txt 2>&1
    if [ "$?" -eq 1 ]; then
        echo "Failed to destroy machines."

        if $print_output; then
            echo -e "Full Vagrant output is:\n"

            cat vagrant_output_destroy.txt
            rm vagrant_output_destroy.txt
        else
            echo "Vagrant output can be found in file $outputdir/destroy_output_$filename-$i.txt"

            cat vagrant_output_destroy.txt >> "${outputdir}/destroy_output_${filename}-${i}.txt"
            rm vagrant_output_destroy.txt
        fi

        return 1
    fi

    rm vagrant_output_destroy.txt
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

    local box_name=$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_box_name; get_box_name('$TEST_PATH/box_names_mapping.yml', '$box')")
    local box_memory=$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import get_box_memory; get_box_memory('$TEST_PATH/box_memory_mapping.yml', '$box')")

    newfile="${TEMP_TOPOLOGY_PATH}/${filename}_${box_name}.yml"

    PYTHONPATH=$TEST_PATH python3 -c "from yaml_topology import change_boxes; change_boxes('$file', '$newfile', '$box', '$box_memory')"

    echo "$newfile"
}

cleanup_and_exit()
{
	local exitcode=$1
	[ -d "$TEMP_TOPOLOGY_PATH" ] && rm -r "$TEMP_TOPOLOGY_PATH"
	exit "$exitcode"
}



# Read command-line arguments given while starting the script and save values to variables.
config_file=''
print_output=false
while [ "$1" != '' ]; do
    case $1 in
        -c | --config )         shift
                                config_file="$1"
                                ;;
        -p | --print_output )   print_output=true
                                ;;
        -h | --help )           echo "Usage: ./run_tests.sh [-c|--config CONFIG_FILE] [-p|--print_output]"
                                echo "    CONFIG_FILE: configuration file [default: ${TEST_PATH}/config.yml]"
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
    config_file="${TEST_PATH}/config.yml"
elif [[ ! "$config_file" = /* && ! "$config_file" = ~* ]]; then
    config_file=$(pwd)/$config_file
fi

# Check if given configuration file exists.
if [ ! -e "$config_file" ]; then
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
files=( "$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_config import get_topology_files; get_topology_files('$config_file')")" )
if [ "${#files[@]}" -eq 0 ]; then
    echo "Failed to process configuration file: no topologies were found."
fi

# Get path to output directory from configuration file.
outputdir="$(PYTHONPATH=$TEST_PATH python3 -c "from yaml_config import get_output_dir; get_output_dir('$config_file')")"
if [[ ! "$outputdir" = /* && ! "$outputdir" = ~* ]]; then
    outputdir=$(pwd)/$outputdir
fi

# Create output directory or delete all contents if it already exists.
if [ -d "$outputdir" ]; then
    rm -rf "${outputdir:?}/"*
else
    mkdir -p "$outputdir"
fi

# Create directory for temporary topology files.
mkdir -p "$TEMP_TOPOLOGY_PATH"

# Flag indicating if any of the tested topologies failed to build correctly.
failed=false

for file in ${files[@]}
do
    # Get list of optional arguments for creating sandbox from configuration file.
    mapfile -t arguments_strings < <(PYTHONPATH=$TEST_PATH python3 -c "import yaml_config; yaml_config.get_topology_arguments('$config_file', '${file}')")
    if [ "${#arguments_strings[@]}" -eq 0 ]; then
        arguments_strings=(" ")
    fi

    # Get list of OS images to be tried in current topology's host machines.
    mapfile -t boxes < <(PYTHONPATH=$TEST_PATH python3 -c "from yaml_config import get_topology_boxes; get_topology_boxes('$config_file', '$file')")
    boxes=("${boxes[@]}")

    for box in "${boxes[@]}"
    do
        if [ "$box" = "no-box" ]; then
            newfile=$file
        else
            newfile=$(change_boxes "$TEST_PATH/$file" "$box")
        fi

        filename=$(basename "$newfile" .yml)

        i=1
        for arguments_string in "${arguments_strings[@]}"
        do
            echo "Testing topology $filename with arguments [$arguments_string]."

            # Try to generate sandbox.
            create_sandbox "$newfile" "$arguments_string" && echo '└── Intermediate definition was successfully generated.' || { echo 'Stopping tests.'; cleanup_and_exit 1; }

            # Try to build and test machines from sandbox.
            # If either fails the output from failed part is also written to terminal.
            if build_machines; then
                echo '└── All machines have been built and provisioned.'

                test_machines && echo '└── All tests have been successful.' || { echo 'Stopping tests.'; failed=true; }
            else
                echo 'Stopping tests.'
                failed=true
            fi

            # Try to destroy virtual environment.
            # Should not fail unless something unexpected happens, in that case it might be necessary to destroy remaining machines manually.
            destroy_machines && echo "└── All machines of the sandbox have been destroyed." || { echo 'Stopping tests.'; failed=true; }

            # If building or testing the virtual environment failed, exit with error.
            if $failed; then
                cleanup_and_exit 1
            fi

            i=$(( i+1 ))
            printf '\n'
        done

        # Remove temporary topology file if it exists.
        [ "$newfile" != "$file" ] && rm "$newfile"
    done
done

cleanup_and_exit 0
