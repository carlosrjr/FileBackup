# coding: utf-8

import sys, zipfile, os

def main():
	try:
		path = "files"
		checkPath(path)
	except IOError:
		path = getDefaultPath()

	createZipFile(path)

def getDefaultPath():
	if sys.platform == "linux" or sys.platform == "linux2":
		path = os.environ['HOME']
	elif sys.platform == "win32":
		path = os.environ['USERPROFILE']

	path += "{0}{1}{2}".format(path , getFileSeparator(), "files")

	checkPath(path)

	return path

def createZipFile(path):
	nameFile = getNameFile()

	zf = zipfile.ZipFile("{0}{1}{2}{3}".format("backup", getFileSeparator(), nameFile, ".zip"), "w")
	for dirname, subdirs, files in os.walk("{0}".format(path)):
		zf.write(dirname)
		for filename in files:
			zf.write(os.path.join(dirname, filename))

	zf.close()

def getNameFile():
	return os.environ['USERNAME']

def getFileSeparator():
	if sys.platform == "linux" or sys.platform == "linux2":
		fileSeparator = "/"
	elif sys.platform == "win32":
		fileSeparator = "\\"

	return fileSeparator

def checkPath(path):
	if(not os.path.isdir(path)):
		os.system("mkdir {0}".format(path))

if __name__ == "__main__":
	main()
