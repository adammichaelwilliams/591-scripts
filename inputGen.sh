# Use: ./run.sh {{bottleName}} {{optionsFile}}

#!/bin/sh

#echo "inputGenFile:	 " $1

cp /CDNsim/$1 /CDNsim/591repo/InputGen/

cd /CDNsim/591repo/InputGen/
./inputGen < input.in
cd /CDNsim/

