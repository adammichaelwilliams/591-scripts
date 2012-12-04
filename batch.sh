#!/bin/sh
    #This file is part of CDNsim.

    #CDNsim is free software; you can redistribute it and/or modify
    #it under the terms of the GNU General Public License as published by
    #the Free Software Foundation; either version 2 of the License, or
    #(at your option) any later version.

    #CDNsim is distributed in the hope that it will be useful,
    #but WITHOUT ANY WARRANTY; without even the implied warranty of
    #MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #GNU General Public License for more details.

    #You should have received a copy of the GNU General Public License
    #along with CDNsim; if not, write to the Free Software
    #Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
####################################################
if [ $# != 1 ]
then
	echo "usage: $0 BOTTLES_DIRECTORY" >> LOG
	exit 1
fi
####################################################
export PATH=$PATH:`pwd`/libs:`pwd`
if [ $? != 0 ]
then
	echo "Failed to set env variables !" >> LOG
	exit 1
fi
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:`pwd`/libs:`pwd`
if [ $? != 0 ]
then
	echo "Failed to set env variables !" >> LOG
	exit 1
fi
####################################################
cd $1
if [ $? != 0 ]
then
	echo "Failed to enter directory $1 !" >> LOG
	exit 1
fi
####################################################
for bottle in *.tgz
do
cp $bottle "$bottle.BACKUP"
tar -xzf $bottle
if [ $? != 0 ]
then
	echo "Failed to extract bottle $bottle !" >> LOG
	exit 1
fi

bottleDir=${bottle%%.tgz}



cd $bottleDir
if [ $? != 0 ]
then
	echo "Failed to cd to directory $bottleDir !" >> LOG
	exit 1
fi

echo "START: " $bottleDir " " `date` >> LOG
	chmod 700 INET
	`pwd`/INET 2> ERRORS 1>STDOUT
if [ $? != 0 ]
then
	echo "FAILED END: " $bottleDir " " `date` >> LOG
else
echo "END: " $bottleDir " " `date` >> LOG
fi

rm -f *.sca *.vec

cd ../
if [ $? != 0 ]
then
	echo "Failed to cd $1 !" >> LOG
	exit 1
fi

#rm -f $bottle
tar cfz ${bottle} $bottleDir
rm -rf $bottleDir
done

echo "BOTTLES EXECUTION DONE!" >> LOG
