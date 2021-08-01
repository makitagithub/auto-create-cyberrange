#!/bin/bash

file=$1
i=$2

while true; do
    df /home | grep "/home" >> $file
    sleep $i
done


