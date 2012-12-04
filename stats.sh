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

if [ $# != 3 ]
then
	echo "usage: $0 BOTTLES_DIRECTORY /ABSOLUTE/PATH_TO/stats.py /ABSOLUTE/PATH_TO/util.py"
	exit 1
fi

cd $1
if [ $? != 0 ]
then
	echo "Failed to enter directory $1 !"
	exit 1
fi

echo '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=windows-1252" />
<title>STATISTICS REPORT - ' > report.html
echo `date` >> report.html
echo ' ' >> report.html
echo $1 >> report.html
echo '</title>
</head>

<body>' >> report.html

for bottle in *.tgz
do
tar -xzf $bottle
if [ $? != 0 ]
then
	echo "Failed to extract bottle $bottle !"
	exit 1
fi

bottleDir=${bottle%%.tgz}



cd $bottleDir
if [ $? != 0 ]
then
	echo "Failed to cd to directory $bottleDir !"
	exit 1
fi

echo "analysing " $bottleDir " " `date`
echo '<p>Bottle: <strong>' $bottleDir '</strong> </p><p>' >> ../report.html


statsGenerator=$2
python $statsGenerator -l ./stats/stats -o ./dataset/objects >> ../report.html
utilGenerator=$3
python $utilGenerator -s ./STDOUT -i -1 >> ../report.html
echo '</p>'  >> ../report.html

	echo '<hr>' >> ../report.html

cp ./graph.png ../graph.png
cp ./reqComplete.csv ../reqComplete.csv


if [ $? != 0 ]
then
	echo "ERROR analysing " $bottleDir " " `date`
else
echo "END: " $bottleDir " " `date`
fi

rm -f *.sca *.vec

cd ../
if [ $? != 0 ]
then
	echo "Failed to cd $1 !"
	exit 1
fi

filename='input.in'
echo "<h1>inputGen input.in file</h1>" >> report.html
while read p; do
	echo "$p<br>" >> report.html
done < $filename

filename='options'
echo "<h1>CDNsim options file</h1>" >> report.html
while read p; do
	echo "$p<br>" >> report.html
done < $filename


rm -f $bottle
tar cfz $bottle $bottleDir
rm -rf $bottleDir
done
echo '</body>
</html>
' >> report.html
