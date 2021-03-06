# coding: utf-8

import sys, zipfile, os, time

def main():
	checkPath("log")
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

	checkPath("backup")

	connection_log = "{0}{1}{2}".format("log", getFileSeparator(), "connection.log")

	logData = "\n[{0} - {1}]: {2}".format(get_data(), get_hora(), "Inicio da criação do aquivo zip.")

	# Gera o arquivo de relatório.
	gera_log(connection_log, logData)

	zf = zipfile.ZipFile("{0}{1}{2}{3}".format("backup", getFileSeparator(), nameFile, ".zip"), "w")
	for dirname, subdirs, files in os.walk("{0}".format(path)):
		zf.write(dirname)
		for filename in files:
			zf.write(os.path.join(dirname, filename))

	zf.close()

	logData = "\n[{0} - {1}]: {2}".format(get_data(), get_hora(), "Finalização da criação do aquivo zip.")

	# Gera o arquivo de relatório.
	gera_log(connection_log, logData)

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

		connection_log = "{0}{1}{2}".format("log", getFileSeparator(), "connection.log")
		logData = "\n[{0} - {1}]: Criação do diretorio: {2}".format(get_data(), get_hora(), path)
		gera_log(connection_log, logData)

	return True


def gera_log(arquivo, mensagem):
	connection_log = open(arquivo,"a+")

	connection_log.write(mensagem)

'''
	Obtém a data do sistema (dd/mm/aaaa)
'''
def get_data():
	return time.strftime("%d/%m/%Y")

'''
	Obtém a hora do sistema (hh:mm:ss)
'''
def get_hora():
	return time.strftime("%H:%M:%S")

if __name__ == "__main__":
	main()
