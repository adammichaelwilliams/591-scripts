# Use: ./script/run.sh {{bottleName}} {{optionsFile}}

#!/bin/sh

echo "bottleName: " $1
echo "optionsFile: " $2
echo "inputGenFile: " $3

# Create inputGen files
./script/inputGen.sh $3
DIR=~/CDNsim/output/
BOTTLEDIR=~/CDNsim/output/$1/

if [ ! -d "$DIR" ]; then
    mkdir ~/CDNsim/output
fi
if [ ! -d "$BOTTLEDIR" ]; then
    mkdir ~/CDNsim/output/$1
fi

# Run bottle creation
python ~/CDNsim/script/CDNsim_cmd.py $1 $2

echo "yeah"

# Create traffic profile graph
#python /CDNsim/inputStats.py -i /CDNsim/591repo/InputGen/
#cp /CDNsim/graph.png /CDNsim/output/$1/

# Copy input files and batch script to bottle's output directory
cp ~/CDNsim/script/options ~/CDNsim/output/$1/
cp ~/CDNsim/591repo/InputGen/input.in ~/CDNsim/output/$1/
cp ~/CDNsim/591repo/InputGen/traffic.in ~/CDNsim/output/$1/
cp ~/CDNsim/591repo/InputGen/traffic.stats ~/CDNsim/output/$1/
cp ~/CDNsim/591repo/InputGen/website.in ~/CDNsim/output/$1/
cp ~/CDNsim/591repo/InputGen/placement.in ~/CDNsim/output/$1/
cp ~/CDNsim/script/batch.sh ~/CDNsim/output/$1/

# Run CDNsim on bottle
cd ~/CDNsim/output/$1
./batch.sh ./
#~/CDNsim/script/batch.sh ~/CDNsim/output/$1/

cd ~/CDNsim

# Create report.html and stats for given bottle sim
#~/CDNsim/script/stats.sh ./output/$1 ~/CDNsim/script/stats.py ~/CDNsim/script/util.py



