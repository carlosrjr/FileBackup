# coding: utf-8

import socket, hashlib, time, threading, json, enum, os

'''
	Obtém todos os backups de todos os hosts cadastrados.

	Este arquivo executará em um determinado período para
	coletar os arquivos de backup em cada cliente registrado.

	Autores
	Maiki Neves Ferreira
	Carlos Roberto Barbosa Júnior
	Paulo Cirino Júnior

	version 0.1
'''
def main():
	# Verificando diretórios
	checkPath("logs");

	# Obtém o conteudo do arquivo de endereços ip dos hosts que participarão do backup.
	file_ip = open("file_ip.txt", "r")

	# Obtém a lista de ips hosts.
	list_ip = file_ip.read().split("\n");

	# Fechando arquivo de ips.
	file_ip.close()

	# Inicia o gerenciamento de conexões.
	ConnectionsManager(list_ip)

'''
	Gerencia os conexões com os clientes realizando a conexão
	com os clientes do backup.
	É gerado para cada cliente uma thread, mas executarão apenas
	o número de conexões definido no enum Connection.NUMBER_THREAD por
	vez.
'''
def ConnectionsManager(list_ip):
	threads = [] # Array com as threads dos usuários
	last_thread = 0; # Útima Thread que foi executada.
	wait_thread = 0; # Número da Thread esperando.

	# Verificando se a lista de hosts não está vazia.
	if(len(list_ip) > 0):
		for lista in list_ip:
			if(lista != ''):
				dados = lista.split(";")
				print(dados)
				if(len(dados) == 2):
					# Inicializando as Threads.
					thread = threading.Thread(target=backupDados, args=(dados[0], dados[1].replace("\r", ""), 0,))

					# Adicionando a nova Thread na lista de Threads.
					threads.append(thread)

	# Verificando qual foi a última thread executada. Caso já tenha executado todas, finaliza a execução.
	while(last_thread < len(threads)):
		size = (len(threads)-last_thread) if (len(threads)-last_thread) < Connection.NUMBER_THREAD.value else Connection.NUMBER_THREAD.value

		for count in range(size):
			threads[last_thread].start()
			last_thread += 1

		for count in range(size):
			threads[wait_thread].join()
			wait_thread += 1

def backupDados(ip, password, attempt):
	try:
		# Resgistrando log
		gravar_log(logs.CONNECTION_LOG.value, "IP: {0} Porta: {1} Tentativa: {2}".format(ip, Connection.PORT.value, attempt))

		# Tentando estabelecer conexão.
		clientSocket = get_tpc_Connection(ip, Connection.PORT.value) # Tenta estabelecer uma conexão com um host

		# Enviando senha de conexão
		clientSocket.send(bytes(password.encode().strip()))

		# recebendo mensagem de confirmação da conexão
		ok = clientSocket.recv(1024).decode("utf-8")

		# Verficiando se a conexão foi aceita.
		if(ok == "Conectado!"):
			getFile(clientSocket) # Tenta realizar backup do arquivo
		else:
			print("Senha incorreta!")

		clientSocket.close()

	except socket.timeout:
		reconnect("O tempo de conexão excedeu o limite", attempt, ip, password)
	except socket.error:
		reconnect("Problema ao tentar estabelecer conexão. Verifique se o host está conectado à rede", attempt, ip, password)
	except socket.herror:
		reconnect("Há um problema com o endereço do host", attempt, ip, password)
	except socket.gaierror:
		reconnect("Erro ao conectar", attempt, ip, password)

'''
	Estabelece uma conexão TCP com um host
'''
def get_tpc_Connection(ip, port):
	serverName = ip # ip do servidor
	serverPort = port # porta do servidor

	# Definindo socket IPv4 TCP
	clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Estabelecendo conexão TCP

	# Tentando realizar a conexão com o host na porta default definida no enum Connection.PORT
	clientSocket.connect((serverName,serverPort)) # Conectando ao servidor

	return clientSocket

'''
	Rotina para realizar o download dos dados backup
'''
def getFile(clientSocket):
	# Obténdo dados do host e do arquivo
	nomeDispositivo, ip, data, checksum_md5_servidor, dados = getFileProperty(clientSocket) # Recebe o nome do arquivo do servidor

	# Definindo nome do arquivo
	fileName = "{0}:{1}".format(ip, data)

	f = open("{0}.zip".format(fileName), "wb") # Gerando arquivo que será recebido no diretorio

	rec = clientSocket.recv(1024) # recebe primeira parte do arquivo
	while(rec): # Enquanto rec não é null, o arquivo é gravado no diretório
		f.write(rec); # Escrevendo os dados no arquivo
		rec = clientSocket.recv(1024) # recebendo a proxima parte do arquivo

	f.close() # Fechando o arquivo

	f = open("{0}.zip".format(fileName), "rb") # Abrindo o arquivo em modo leitura para obter o checksum md5 do conteudo
	checksum_md5_cliente = hashlib.md5(f.read()).hexdigest() # Gera checksum md5 do arquivo de backup obtido.
	f.close() # Fechando o arquivo

'''
	Recebe nome do computador e a data que o arquivo foi gerado
	para ser gravado no diretório de backup.
'''
def getFileProperty(clientSocket):
	# Recebendo o json com os dados do host e do arquivo.
	json_dados = clientSocket.recv(1024).decode("utf-8")

	# Enviando uma mensagem de confirmação de recebindo dos dados.
	clientSocket.send(bytes("ok".encode("utf-8")))

	# Fazendo parse de json para um dicionário.
	dados = json.loads(json_dados)

	nomeDispositivo = dados["host_name"]
	data = dados["date"]
	checksum_md5 = dados["checksum_md5"]
	ip = dados["ip"]

	return nomeDispositivo, ip, data, checksum_md5, dados

'''
	Verificando se diretório existe. Caso não exista, tenta criar.
'''
def checkPath(path):
	if(not os.path.isdir(path)):
		os.system("mkdir {0}".format(path))

'''
	Tenta reconectar com o host caso tenha algum problema.
	O número máximo de reconexão permitida é de Connection.RECONNECT.
'''
def reconnect(message, attempt, ip, password):
	gravar_log(logs.CONNECTION_LOG.value, "{0}: {1}".format(ip, message))
	if(attempt < Connection.RECONNECT.value):
		backupDados(ip, password, attempt+1)

'''
	Registra em log uma mensagem.
'''
def gravar_log(arquivo, mensagem):
	file_log = open(arquivo, "a+")

	file_log.write("[{0} {1}]: {2}.\n".format(get_data(), get_hora(), mensagem))

'''
	Obtém a data do sistema.
'''
def get_data():
	return time.strftime("%d-%m-%Y")

'''
	Obtém a hora do sistema.
'''
def get_hora():
	return time.strftime("%H-%M-%S")

'''
	Enum definido para armazenar dados sobre a conexão.
'''
class Connection(enum.Enum):
	NUMBER_THREAD = 2
	RECONNECT = 2
	PORT = 23000

class logs(enum.Enum):
	CONNECTION_LOG = "logs/connection.log"

if __name__ == "__main__":
	main()
