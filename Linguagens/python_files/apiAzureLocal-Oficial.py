from json import loads
from time import sleep
from tokenize import String
from urllib3 import PoolManager
import datetime
from datetime import datetime
import psutil
import mysql.connector
import time 
import os
from mysql.connector import errorcode
import pyodbc
import textwrap

# def Conexao():
#     #variaveis de conexao
#     driver ='{ODBC Driver 18 for SQL Server}'
#     server_name = 'greeneye'
#     database_name = 'greeneye'
#     server = '{server_name}.database.windows.net,1433'.format(server_name=server_name)
#     username = 'GreeneyeADM'
#     password = 'Greeneye123@'
#     # definindo banco url 
#     connection_string = textwrap.dedent('''
#     Driver={driver};
#     Server={server};
#     Database={database};
#     Uid={username};
#     Pwd={password};
#     Encrypt=yes;
#     TrustedServerCertificate=no;
#     Connection Timeout=10;
#     '''.format(
#         driver=driver,
#         server=server,
#         database=database_name,
#         username=username,
#         password=password
#     )) 

#     cnxn:pyodbc.Connection = pyodbc.connect(connection_string) 

#     global crsr
#     crsr = cnxn.cursor()
#     print("Conectado ao banco de dados:")


try:
        cnxn = pyodbc.connect(driver='{ODBC Driver 18 for SQL Server}', host='greeneye.database.windows.net',
                        database='greeneye', user='GreeneyeADM', password='Greeneye123@')
        print("Conectei no banco! (Azure)")
        db_connection = mysql.connector.connect(
                host='localhost', user='root', password='Lucas0708', database='greeneye')
        print("Conectei no banco! (Local)")
except mysql.connector.Error as error:
        if error.errno == errorcode.ER_BAD_DB_ERROR:
                print("Não encontrei o banco")
        elif error.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Credenciais erradas")
        else:
                print(error)

while (True):

        #Captura do sistema operacional da máquina, utilizando a própria psutil 
        # sistemaoperacional = psutil.disk_partitions()[0][2] 
        if(os.name == 'nt'):
            sistemaoperacional = 'NTFS'
        elif(os.name == 'posix'):
            sistemaoperacional = 'EXT4'
        else:
            sistemaoperacional = 'Sistema não Identificado.'


        # Processador
        processador = psutil.cpu_count()
        porcentagem_cpu = psutil.cpu_percent()


        # Disco
        if(sistemaoperacional == 'NTFS'):
            discoTotal =(psutil.disk_usage("C:\\")[0] / 10**9)
        elif(sistemaoperacional == 'EXT4' or sistemaoperacional == 'EXT3'):
            discoTotal =(psutil.disk_usage("/")[0] / 10**9)
        
        if(sistemaoperacional == 'NTFS' or sistemaoperacional == 'Windows'):
            discoUso = (psutil.disk_usage("C:\\")[1] / 10**9)
        elif(sistemaoperacional == 'EXT4' or sistemaoperacional == 'EXT3' or sistemaoperacional == 'Linux'):
            discoUso = (psutil.disk_usage("/")[1] / 10**9)

        if(sistemaoperacional == 'NTFS' or sistemaoperacional == 'Windows'):
            discoLivre = (psutil.disk_usage("C:\\")[2] / 10**9)
        elif(sistemaoperacional == 'EXT4' or sistemaoperacional == 'EXT3' or sistemaoperacional == 'Linux'):
            discoLivre = (psutil.disk_usage("/")[2] / 10**9)

        if(sistemaoperacional == 'NTFS'):
            disk = psutil.disk_usage('C:\\')
        elif(sistemaoperacional == 'EXT4' or sistemaoperacional == 'EXT3'):
            disk = psutil.disk_usage('/')

        diskPercent = disk.percent

        # Ram
        ramTotal = (psutil.virtual_memory() [0] / 10**9)
        ramUso =  (psutil.virtual_memory() [3] / 10**9)
        ramUso2 = ramUso * 1.15
        ramUso3 = ramUso2 * 1.05
        ram = (psutil.virtual_memory())
        ramPercent = ram.percent

        #Temperatura
        def conversor(valor):
            return float(valor[0:4].replace(",", '.'))
        
        def leitura(db_connection):
            cursorLocal = db_connection.cursor()
            cursorAzure = cnxn.cursor()

            # row = cursor.fetchone()
            # Equip = int(''.join(map(str, row)))

        with PoolManager() as pool:
                while True:
                    for i in range(3):
                        i = i + 1
                        a = i - 1         
                        response = pool.request('GET', 'http://localhost:8085/data.json')
                        data = loads(response.data.decode('utf-8'))

                        #OPEN HARDWARE MONITOR
                        temp_min = conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][4]['Min'])
                        temp_value = conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][4]['Value'])
                        temp_max = conversor(data['Children'][0]['Children'][1]['Children'][1]['Children'][4]['Max'])

                        # print("Temperatura minima:", temp_min)
                        # print("Temperatura média:", temp_value)
                        # print("Temperatura maxima:", temp_max)

                        #CURSOR
                        cursorLocal = db_connection.cursor()
                        cursorLocal2 = db_connection.cursor()
                        cursorAzure = cnxn.cursor()
                        cursorAzure2 = cnxn.cursor()
                        

                        #AZURE
                        fkMaquina = 50000
                        sql = f"INSERT INTO Leitura (fkMaquina, sistemaOperacional, cpuMedia, qtdProcessador, ramTotal, ramUso,  ramUsoPercent, discoTotal, discoUso, discoLivre, discoPercent, dataHora) VALUES ({fkMaquina},'{sistemaoperacional}', {porcentagem_cpu}, {processador}, {ramTotal}, {ramUso},{ram.percent},{discoTotal},{discoUso},{discoLivre},{disk.percent},(CURRENT_TIMESTAMP))" 
                        cursorAzure.execute(sql)
                        
                        #TEMPERATURA AZURE
                        sqltemp = (f"INSERT INTO Temperatura (tempMin, tempValor, tempMax, data_agr, hora_agr ) VALUES (?,?,?,?,?)")
                        data = datetime.now().strftime('%Y-%m-%d')
                        hora = datetime.now().strftime('%H:%M:%S')
                        values = (temp_min, temp_value, temp_max, data, hora)
                        cursorAzure2.execute(sqltemp, values)

                        #LOCAL
                        fkMaquina = 50000
                        sql = f"INSERT INTO Leitura (fkMaquina, sistemaOperacional, cpuMedia, qtdProcessador, ramTotal, ramUso,  ramUsoPercent, discoTotal, discoUso, discoLivre, discoPercent, dataHora) VALUES ({fkMaquina},'{sistemaoperacional}', {porcentagem_cpu}, {processador}, {ramTotal}, {ramUso},{ram.percent},{discoTotal},{discoUso},{discoLivre},{disk.percent},(CURRENT_TIMESTAMP))"
                        cursorLocal.execute(sql)

                        #TEMPERATURA LOCAL
                        sqltemp = (f"INSERT INTO Temperatura (tempMin, tempValor, tempMax, data_agr, hora_agr ) VALUES (%s,%s,%s,%s,%s)")
                        data = datetime.now().strftime('%Y-%m-%d')
                        hora = datetime.now().strftime('%H:%M:%S')
                        values = (temp_min, temp_value, temp_max, data, hora)
                        cursorLocal2.execute(sqltemp, values) 

                        print("\n")
                        print(cursorAzure.rowcount, "Inserindo no banco (Azure).")
                        cnxn.commit()

                        print(cursorLocal.rowcount, "Inserindo no banco (Local).")
                        db_connection.commit()
                        time.sleep(1)