# coding: utf-8

import socket, hashlib, time, threading, json

'''
	Obtém todos os backups de todos os hosts cadastrados.

	Autores
	Maiki Neves Ferreira
	Carlos Roberto Barbosa Júnior
	Paulo Cirino Júnior

	version 0.1
'''
def main():
	# Obtem lista de endereços ip dos hosts que participaram do backup
	arquivo_ips = open("arquivo_ips.txt", "r")
	lista_ips = arquivo_ips.read().split("\n");
	arquivo_ips.close()

	gerenciaConexoes(lista_ips)

def gerenciaConexoes(lista_ips):
	threads = []
	last_thread = 0;
	wait_thread = 0;

	for lista in lista_ips:
		dados = lista.split(";")
		print(dados)
		thread = threading.Thread(target=backupDados, args=(dados[0], dados[1].replace("\r", ""), 0,))
		threads.append(thread)

	while(last_thread < len(threads)):
		size = (len(threads)-last_thread) if (len(threads)-last_thread) <= 2 else 2

		for count in range(size):
			threads[last_thread].start()
			last_thread += 1

		for count in range(size):
			threads[wait_thread].join(2)
			wait_thread += 1

'''
	Obtém a conexão com host e tenta realizar o backup do arquivo
	a partir de um endereço ip que está na lista de ips e usando
	a porta default definida 21000.
'''
def backupDados(ip, password, attempt):
	print("ip: {0}    password: {1}    attempt: {2}".format(ip, password, attempt))
	try:
		clientSocket = getTCPConnection(ip, 23000) # Tenta estabelecer uma conexão com um host

		clientSocket.send(bytes(password.encode().strip()))

		ok = clientSocket.recv(1024).decode("utf-8")
		if(ok == "Conectado!"):
			getFile(clientSocket) # Tenta realizar backup do arquivo
		else:
			print("Senha incorreta!")

		clientSocket.close()

	except socket.timeout:
		reconnect("O tempo de conexão excedeu o limite.", attempt, ip, password)
	except socket.error:
		reconnect("Problema ao tentar estabelecer conexão. Verifique se o host está conectado à rede.", attempt, ip, password)
	except socket.herror:
		reconnect("Há um problema com o endereço do host.", attempt, ip, password)
	except socket.gaierror:
		reconnect("Erro ao conectar.", attempt, ip, password)

'''
	Estabelece uma conexão TCP com um host
'''
def getTCPConnection(ip, port):
	serverName = ip # ip do servidor
	serverPort = port # porta do servidor

	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Estabelecendo conexão TCP
	clientSocket.connect((serverName,serverPort)) # Conectando ao servidor

	return clientSocket

'''
	Rotina para realizar o download dos dados backup
'''
def getFile(clientSocket):
	nomeDispositivo, data, checksum_md5_servidor, dados = getFileProperty(clientSocket) # Recebe o nome do arquivo do servidor

	fileName = "{0}:{1}".format(nomeDispositivo, data)


	f = open("{0}.zip".format(fileName), "wb") # Gerando arquivo que será recebido no diretorio

	rec = clientSocket.recv(1024) # recebe primeira parte do arquivo
	while(rec): # Enquanto rec não é null, o arquivo é gravado no diretório
		#print("{0}: recebendo...".format(nomeDispositivo))
		f.write(rec); # Escrevendo os dados no arquivo
		rec = clientSocket.recv(1024) # recebendo a proxima parte do arquivo

	f.close() # Fechando o arquivo

	f = open("{0}.zip".format(fileName), "rb") # Abrindo o arquivo em modo leitura para obter o checksum md5 do conteudo
	checksum_md5_cliente = hashlib.md5(f.read()).hexdigest() # Gera checksum md5 do arquivo de backup obtido.
	f.close() # Fechando o arquivo

'''
	Recebe nome do computador e a data que o arquivo foi gerado
	para ser gravado no diretório de backup
'''
def getFileProperty(clientSocket):
	json_dados = clientSocket.recv(1024).decode("utf-8")

	clientSocket.send(bytes("ok".encode("utf-8")))

	dados = json.loads(json_dados)

	nomeDispositivo = dados["host_name"]
	data = dados["date"]
	checksum_md5 = dados["checksum_md5"]

	return nomeDispositivo, data, checksum_md5, dados

def checkPath(path):
	if(not os.path.isdir(path)):
		os.system("mkdir {0}".format(path))

def reconnect(message, attempt, ip, password):
	print("{0}\n".format(message))
	if(attempt < 2):
		backupDados(ip, password, attempt+1)

if __name__ == "__main__":
	main()
