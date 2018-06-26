# coding: utf-8
import socket, os, sys, hashlib, json, time, zipfile

# Importando métodos da classe gerar_arquivo_backup
from GeraArquivoBackup import getFileSeparator, getNameFile, createZipFile, getDefaultPath, checkPath

# Porta default do FileBackup
server_port = 23000

connection_log = "{0}{1}{2}".format("log", getFileSeparator(), "connection.log")
history_log = "{0}{1}{2}".format("log", getFileSeparator(), "connection_history.log")

'''
	Este BackupServer.py estará em execução em cada host
	cliente em que o servidor irá realizar o backup.
'''
def main():
	# Inicializando o connection_socket como nulo.
	connection_socket = None

	try:
		checkPath("log")
		checkPath("backup")
		createZipFile("files")
		# Gera a senha de conexão
		key_connect = hashlib.md5("123456".encode("utf-8").strip()).hexdigest()

		# Obtém a conexão com o servidor de backup, caso contrário recebe None.
		connection_socket = get_connection()

		# Verificando se a conexão foi estabelecida.
		if (connection_socket):
			try:
				# recebendo a chave de conexão do cliente.
				key_server = connection_socket.recv(1024).decode("utf-8")

				# Gravando a informação sobre a conexão no histórico.
				history_data = "\n[{0} - {1}]: {2}".format(get_data(), get_hora(), "Conexão estabelecida com sucesso!")
				gera_log(history_log, history_data)

				#print ("Senha do Server: " + keyServer)

				# Verificando a chave do servidor de backup
				if (key_connect == key_server):
					if (os.path.exists("{0}{1}{2}{3}".format("backup",getFileSeparator(), getNameFile(), ".zip"))):
						# Enviando mensagem de acesso autorizado para o servidor de backup.
						connection_socket.send(bytes("Conectado!".encode("utf-8").strip()))

						# Obtendo propriedades do host e dos arquivos
						dados = get_property()

						# Transformando o dicionário para um objeto json para ser enviado ao servidor de backup.
						json_dados = json.dumps(dados)

						# Enviando os dados do host e do arquivo para o servidor de backup.
						send_property(connection_socket, json_dados)

						# Enviando o arquivo zip para o servidor de backup
						send_file(connection_socket)

						if(checkPath("log")):
							logData = "\n[{0} - {1} - {2}:{3}]\n\t{4}".format(get_data(), get_hora(), dados["ip"], dados["porta"], '\n\t'.join(get_zip_files()))

							# Gera o arquivo de relatório.
							gera_log(connection_log, logData)
					else:
						print("Não foi encontrado arquivo de backup.")

				# Finalizando a conexão
				connection_socket.close()

				# Gravando no log de conexões.
				history_data = "\n[{0} - {1}]: {2}".format(get_data(), get_hora(), "Conexão finalizada!")
				gera_log(history_log, history_data)



			except (socket.herror, socket.gaierror, socket.error):
				history_data = "\n[{0} - {1}]: {2}".format(get_data(), get_hora(), "Ocorreu um erro no estabelecimento da conexão.")
				if(checkPath("log")):
					gera_log(history_log, history_data)
			except (socket.timeout):
				history_data = "\n[{0} - {1}]: {2}".format(get_data(), get_hora(), "O tempo limite para estabelecimento de conexão foi atingido.")
				if(checkPath("log")):
					gera_log(history_log, history_data)


	except (KeyboardInterrupt, SystemExit):
		# verificando se há conexão estabelecida pra fechar.
		if(connection_socket != None):
			connection_socket.close()

'''
	Estabelece uma conexão com o google-open-dns
	para obter o ip do host.
'''
def get_ip_address():
	# Definindo socket IPv4 UDP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	#conectando ao google-open-dns na HTTP(80)
    s.connect(("8.8.8.8", 80))

	# retornando o ip do host
    return s.getsockname()[0]

'''
	Cria um socket server TCP que ficará aguardado a conexão com
	o servidor de backup. Retorna a conexão se for bem sucedidaself.
	caso contrário, irá gerar uma exceção.
'''
def get_connection():
	try:
		# definindo o socket IPv4 TCP
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

		# Realizando o bind na porta default 23000
		server_socket.bind(("",server_port))

		# Definindo o número de conexões que o socket estará escutando.
		server_socket.listen(1)

		print("Servidor aguardando conexão!")

		# Aguardando a conexão com o servidor de backup
		connection_socket, addr = server_socket.accept()

		# Retorna a conexão caso tenha sido bem sucedida.
		return connection_socket

	except (socket.error, socket.herror, socket.gaierror, socket.timeout):
		return None

# Gera o checksum_md5 do conteudo arquivo zip.
def get_zip_md5():
	# Abrindo arquivo para obter o checksum md5
	arquivo = open("{0}{1}{2}{3}".format("backup",getFileSeparator(), getNameFile(), ".zip"), "rb")

	# Obtendo hash md5 do conteudo do arquivo
	checksum_md5 = hashlib.md5(arquivo.read()).hexdigest()

	# Fechando o arquivo
	arquivo.close()

	# retornando o checksum_md5 do conteudo arquivo zip
	return checksum_md5

'''
	Obtém as propriedades do host e do arquivo zip para realizar
	a verificação do arquivo no servidor.
'''
def get_property():
	# Armazenando em um dicionário os dados.
	dados = {
		"ip" : "{0}".format(get_ip_address()), # ip do host
		"porta": server_port, # porta de conexão
		"name_file": "{0}".format(getNameFile()), # nome do arquivo
		"checksum_md5": get_zip_md5(), # checksum_md5 do arquivo zip.
		"date": time.strftime("%d-%m-%Y"), # data de envio
		"hour": time.strftime("%H-%M-%S") # hora de envio
	}

	# Retornando dicionário com os dados.
	return dados


def gera_log(arquivo, mensagem):
	connection_log = open(arquivo,"a+")

	connection_log.write(mensagem)

'''
	Envia json com com as propriedades do host e do arquivo.
	Recebe uma mensagem de confirmação do cliente.
'''
def send_property(connection_socket, json_dados):
	# Enviando json com as propriedades do host e do arquivo.
	connection_socket.send(bytes(json_dados.encode("utf-8").strip()))

	# Recebendo mensagem de confirmação do recebindo do json
	connection_socket.recv(1024).decode("utf-8")

'''cliente
	Envia o arquivo para o cliente
'''
def send_file(connection_socket):
	try:
		# Abrindo arquivo para enviar
		arquivo = open("backup{0}{1}{2}".format(getFileSeparator(), getNameFile(), ".zip"), "rb")

		# Lendo os primeiros bytes do arquivo
		l = arquivo.read(1024)

		# Continua enviando equanto houver dados do arquivo para ser lido e enviado.
		while(l):
			connection_socket.send(bytes(l))
			l = arquivo.read(1024)

		# Fechando o arquivo
		arquivo.close()

	except (ConnectionResetError):
		gera_log(connection_log,"Erro no envio do(s) arquivo(s). Conexão reiniciada pelo cliente.")
		connection_socket.close()
	except (ConnectionAbortedError):
		gera_log(connection_log,"Erro no envio do(s) arquivo(s). Conexão abortada pelo cliente.")
		connection_socket.close()
	except (ConnectionRefusedError):
		gera_log(connection_log,"Erro no envio do(s) arquivo(s). Conexão recusada pelo cliente.")
		connection_socket.close()

'''
	Obtém a lista de arquivos do arquivo zip.
'''
def get_zip_files():
	# Obtém o arquivo zip.
	zf = zipfile.ZipFile("backup{0}{1}{2}".format(getFileSeparator(), getNameFile(), ".zip"))

	# Obtém lista de arquivos do zip.
	arquivos_list = zf.namelist()

	# Retorna lista de arquivos do arquivo zip.
	return arquivos_list

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
