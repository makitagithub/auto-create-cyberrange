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
    local output=$(python3 create.py ${arguments[@]} $file)
    if [ "$output" != "Sandbox was successfully created." ]; then
        return 1
    fi
}


# Build virtual environment from existing sandbox using Vagrant.
# Output is redirected to corresponding file in output directory.
build_machines()
{
    cd sandbox
    vagrant up > ../$outputdir/vagrant_output_processing.txt
    if [ "$?" -ne 0 ]; then
        cd ..
        return 1
    fi
    cat ../$outputdir/vagrant_output_processing.txt >> ../$outputdir/vagrant_output_$filename.txt
    rm ../$outputdir/vagrant_output_processing.txt
    echo $'\n' >> ../$outputdir/vagrant_output_$filename.txt
    cd ..
}


# Get list of all machines in virtual network from topology definition file and test that they all
# have access to the internet and that they all see each other.
# Output is redirected to corresponding file in output directory.
test_machines()
{
    local machines=($(python3 -c "from testing.yaml_topology import get_hosts, get_routers; get_hosts('$file'); get_routers('$file')"))
    cd sandbox
    for machine in "${machines[@]}"
    do
        echo "$machine" >> ../$outputdir/test_output_processing.txt
        vagrant ssh $machine -c "ping -c 5 www.muni.cz" >> ../$outputdir/test_output_processing.txt
        if [ "$?" -ne 0 ]; then
            cd ..
            return 1
        fi
        echo $'\n' >> ../$outputdir/test_output_processing.txt

        for target in "${machines[@]}"
        do
            if [ "$machine" != $target ]; then
                vagrant ssh $machine -c "ping -c 5 $target" >> ../$outputdir/test_output_processing.txt
                if [ "$?" -ne 0 ]; then
                    cd ..
                    return 1
                fi
                echo $'\n' >> ../$outputdir/test_output_processing.txt
            fi
        done
        echo $'\n' >> ../$outputdir/test_output_processing.txt
    done

    cat ../$outputdir/test_output_processing.txt >> ../$outputdir/test_output_$filename.txt
    rm ../$outputdir/test_output_processing.txt
    echo $'\n\n' >> ../$outputdir/test_output_$filename.txt
    
    cd ..
}

# Destroy existing virtual environment using Vagrant.
# Output is redirected to corresponding file in output directory.
destroy_machines()
{
    cd sandbox
    vagrant destroy -f > ../$outputdir/vagrant_output_processing.txt
    if [ "$?" -eq 1 ]; then
        cd ..
        return 1
    fi
    cat ../$outputdir/vagrant_output_processing.txt >> ../$outputdir/vagrant_output_$filename.txt
    rm ../$outputdir/vagrant_output_processing.txt
    echo $'\n\n' >> ../$outputdir/vagrant_output_$filename.txt
    cd ..
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

    local boxname=$(python3 -c "from testing.yaml_topology import get_box_name; get_box_name('$box')")

    newfile="./tmp_topologies/${filename}_$boxname.yml"
    
    python3 -c "from testing.yaml_topology import change_boxes; change_boxes('$file', '$newfile', '$box')"

    echo "$newfile"
}


# Get path to configuration file from command line arguments or use default value.
if [ "$#" -eq 0 ]; then
    config_file="config.yml"
elif [ "$#" -eq 1 ]; then
    config_file="$1"
else 
    echo "usage: ./test_topologies.sh [config_file]"
    echo "    config_file: configuration file [default: config.yml]"
    echo "error: too many arguments"
fi

# Check if given configuration file exists.
if [ ! -e $config_file ]; then
    echo "configuration file not found"
    exit 1
fi

# Check if configuration file is a yaml.
if [[ $config_file != *.yml && $config_file != *.yaml ]]; then
    echo "configuration file has a wrong format"
    exit 1
fi

oIFS="$IFS"
IFS=$'\n'

# Get a list of paths to topology definition files from configuration file.
files=($(python3 -c "from testing.yaml_config import get_topology_files; get_topology_files('$config_file')"))
if [ "${#files[@]}" -eq 0 ]; then
    echo "configuration file: no topologies were defined"
fi

# Get path to output directory from configuration file.
outputdir=$(python3 -c "from testing.yaml_config import get_output_dir; get_output_dir('$config_file')")

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
    arguments_strings=($(python3 -c "from testing.yaml_config import get_topology_arguments; get_topology_arguments('$config_file', '$file')"))
    if [ "${#arguments_strings[@]}" -eq 0 ]; then
        arguments_strings=(" ")
    fi

    # Get list of OS images to be tried in current topology's host machines.
    boxes=($(python3 -c "from testing.yaml_config import get_topology_boxes; get_topology_boxes('$config_file', '$file')"))
    boxes=("${boxes[@]}")

    for box in ${boxes[@]}
    do 
        if [ "$box" = "no-box" ]; then
            newfile=$file
        else
            newfile=$(change_boxes "$file" "$box")
        fi

        filename=$(basename "$newfile" .yml)

        for arguments_string in ${arguments_strings[@]}
        do
            # Try to generate sandbox and write result to terminal.
            if create_sandbox $newfile $arguments_string; then
                echo "$filename: sandbox succesfully created"
            else
                echo "$filename: sandbox creation failed"
                failed=true
                continue
                # If generating sandbox failed, skip building and testing machines.
            fi

            # Try to build and test machines from sandbox and write results to terminal.
            # If either fails the output from failed part is also written to terminal.
            if build_machines; then 
                echo "$filename: vagrant succesfully built machines"

                if test_machines; then
                    echo "$filename: test were ok"
                else
                    echo "$filename: one of the tests failed"
                    cat $outputdir/test_output_processing.txt | tee -a $outputdir/test_output_$filename.txt
                    rm $outputdir/test_output_processing.txt
                    failed=true
                fi
            else
                echo "$filename: vagrant failed to build one of the machines"
                cat $outputdir/vagrant_output_processing.txt | tee -a $outputdir/vagrant_output_$filename.txt
                rm $outputdir/vagrant_output_processing.txt
                failed=true
            fi  

            # Try to destroy virtual environment and write result to terminal.
            # Should not fail unless something unexpected happens, in that case it might be necessary to destroy remaining machines manually.
            if destroy_machines; then
                echo "$filename: vagrant succesfully destroyed machines"
            else
                echo "$filename: vagrant failed to destroy machines"
                cat $outputdir/vagrant_output_processing.txt | tee -a $outputdir/vagrant_output_$filename.txt
                rm $outputdir/vagrant_output_processing.txt
                failed=true
            fi
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

# If any of the topologies failed to build correctly, exit with error.
if $failed; then
    exit 1
else
    exit 0
fi