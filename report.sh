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

if [ $# != 1 ]
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
givenDir='/CDNsim/output/'
for bottle in $(find "/CDNsim/output/" -maxdepth 1 -type d)
do
if [ $bottle != $givenDir ]
then
echo $bottle
echo '<iframe src="'$bottle'/report.html" height="550px" width="1200px" ></iframe>' >> report.html
fi
if [ $? != 0 ]
then
	echo "Failed to extract bottle $bottle !"
	exit 1
fi


if [ $? != 0 ]
then
	echo "ERROR analysing " $bottleDir " " `date`
else
echo "END: " $bottleDir " " `date`
fi

done

echo '</body>
</html>
' >> report.html
