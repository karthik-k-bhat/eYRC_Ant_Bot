# -*- coding: utf-8 -*-
"""
**************************************************************************
*                  IMAGE PROCESSING (e-Yantra 2016)
*                  ================================
*  This software is intended to teach image processing concepts
*
*  MODULE: checkversion
*  Filename: checkversion.py
*  Version: 1.0.0  
*  Date: October 25, 2016
*  
*  Author: e-Yantra Project, Department of Computer Science
*  and Engineering, Indian Institute of Technology Bombay.
*  
*  Software released under Creative Commons CC BY-NC-SA
*
*  For legal information refer to:
*        http://creativecommons.org/licenses/by-nc-sa/4.0/legalcode 
*     
*
*  This software is made available on an “AS IS WHERE IS BASIS”. 
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*  
*  e-Yantra - An MHRD project under National Mission on Education using 
*  ICT(NMEICT)
*
**************************************************************************
"""

import time

print ("==============================================")
result = []
try:
	import platform
	sysver = platform.uname()
	isysver = 1;
	result.append(sysver)
	# print "System version is:", sysver

except ImportError:
    # print "No Information about OS"
    sysver = ""
    result.append(sysver)
    isysver = 0;
    pass
    #sys.exit(0)

try: 
	import platform

	pyver = platform.python_version()
	result.append(pyver[0:3])
	print ("Required Python Version is 3.5.2")
	if (pyver == '3.5.2'):
		print ("Installed Python Version is: ", pyver)
		print ("Python Installation is OK!!")
		print ("==============================================")
	else:
		print ("Installed Python Version is: ", pyver)
		print ("Python Installation is NOT OK .. Please re-install the correct version!!")
		print ("==============================================")
except ImportError:
	print ("Import Error - re-check installation procedure ")
	pyver = ""
	result.append(pyver)
	pass

try:
	import cv2
	opencvver = cv2.__version__
	isopencv = 1;
	result.append(opencvver[0:3])
	print ("Required Opencv version is: 3.4.2")
	if (opencvver == '3.4.2'):
		print ("Installed Opencv Version is: ", opencvver)
		print ("Opencv Installation is OK!!")
		print ("==============================================")
	else:
		print ("Installed Opencv Version is: ", opencvver)
		print ("Opencv Installation is NOT OK .. Please re-install the correct version!!")
		print ("==============================================")
except ImportError:
    print ("Import Error - re-check installation procedure.")
    isopencv = 0;
    result.append(opencvver)
    pass
    #sys.exit(0)

try:
	import numpy
	numpyver = numpy.__version__
	isnumpy = 1
	result.append(numpyver)
	print ("Required Numpy version is: 1.15.2")
	if (numpyver == '1.15.2'):
		print ("Installed Numpy Version is: ", numpyver)
		print ("Numpy Installation is OK!!")
		print ("==============================================")
	else:
		print ("Installed Numpy Version is: ", numpyver)
		print ("Numpy Installation is NOT OK .. Please re-install the correct version!!")
		print ("==============================================")
except ImportError:
	print ("Import Error - re-check installation procedure.")
	isnumpy = 0
	numpyver = ""
	result.append(numpyver)
	pass

try:
	import serial
	serialver = serial.__version__
	isserial = 1
	result.append(serialver)
	print ("Required pySerial version is: 3.4")
	if (serialver == '3.4'):
		print ("Installed pySerial Version is: ", serialver)
		print ("pySerial Installation is OK!!")
		print ("==============================================")
	else:
		print ("Installed pySerial Version is: ", serialver)
		print ("pySerial Installation is NOT OK .. Please re-install the correct version!!")
		print ("==============================================")
except ImportError:
	print ("Import Error - re-check installation procedure.")
	isnumpy = 0
	numpyver = ""
	result.append(numpyver)
	pass
 
if ((isopencv == 0) or (isnumpy == 0)):
	sys.exit(0)
else:
	fo = open("output.csv", "w+")
	fo.write("Python Version"+","+"Numpy Version"+","+"OpenCV Version"+","+"Serial Version"+"\n")
	fo.write(str(pyver)+","+str(numpyver)+","+str(opencvver)+","+str(serialver)+",")
	fo.close()
	pass
