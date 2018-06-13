# coding: utf-8
import socket, os, sys, hashlib, json, time
from GeraArquivoBackup import getFileSeparator, getNameFile, createZipFile, getDefaultPath, checkPath

serverPort = 23000

def main():
	connectionSocket = None

	if(checkPath("log")):
		connectionLog = open("{0}{1}{2}".format("logs", getFileSeparator(), "connection.log"))

	try:
		# Gera key
		keyConnect = hashlib.md5("123456".encode("utf-8").strip()).hexdigest()
		print ("Senha de Conexão: " + keyConnect)

		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serverSocket.bind(("",serverPort))
		serverSocket.listen(1)

		print("Servidor aguardando conexão!")

		connectionSocket, addr = serverSocket.accept()
		keyServer = connectionSocket.recv(1024).decode("utf-8")
		print ("Senha do Server: " + keyServer)

		if (keyConnect == keyServer):
			connectionSocket.send(bytes("Conectado!".encode("utf-8").strip()))

			# Abrindo arquivo para obter o checksum md5
			arquivo = open("{0}{1}{2}{3}".format("backup",getFileSeparator(), getNameFile(), ".zip"), "rb")

			# Obtendo hash md5 do conteudo do arquivo
			checksum_md5 = hashlib.md5(arquivo.read()).hexdigest()

			# Fechando o arquivo
			arquivo.close()

			dados = {
				"ip" : "{0}".format(get_ip_address()),
				"porta": serverPort,
				"host_name": "linux20",
				"name_file": "{0}".format(getNameFile()),
				"checksum_md5": checksum_md5,
				"date": time.strftime("%d-%m-%Y"),
				"hour": time.strftime("%H-%M-%S")
			}

			json_dados = json.dumps(dados)
			print(json_dados)
			connectionSocket.send(bytes(json_dados.encode().strip()))

			connectionSocket.recv(1024).decode("utf-8")
			# Abrindo arquivo para enviar
			arquivo = open("backup{0}{1}{2}".format(getFileSeparator(), getNameFile(), ".zip"), "rb")

			# Lendo os primeiros bytes do arquivo
			l = arquivo.read(1024)
			while(l):
				connectionSocket.send(bytes(l))
				l = arquivo.read(1024)

			# Fechando o arquivo
			arquivo.close()

		# Finalizando a conexão
		connectionSocket.close()
	except (KeyboardInterrupt, SystemExit):
		if(connectionSocket != None):
			connectionSocket.close()

def get_ip_address():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    return s.getsockname()[0]

if __name__ == "__main__":
	main()
