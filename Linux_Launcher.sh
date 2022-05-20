#!/bin/bash
read -p "Campaign Name : " campaign_name
read -p "Grid Size : " grid_size
count=$(find Monster_Database -maxdepth 1 -type f|wc -l)
python3 Battle.py $campaign_name $count $grid_size "windowed"
