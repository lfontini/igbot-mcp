
import paramiko
import time

def ssh_command(hostname, username, password, command, manufacture, timeout=120):
    """
    Executa um comando SSH em um dispositivo remoto.

    Parâmetros:
        hostname (str): O IP ou hostname do dispositivo remoto.
        username (str): O usuário SSH.
        password (str): A senha SSH.
        command (str): O comando a ser executado.
        manufacture (str): O fabricante do dispositivo (para tratamento específico).
        timeout (int, opcional): Timeout em segundos. Padrão é 120.

    Retorna:
        str: A saída do comando ou mensagem de erro.
    """
    try:
        print(hostname, username, password, command, manufacture)
        print("Entering ssh_command", manufacture)
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(hostname=hostname, username=username, password=password , look_for_keys=False ,  allow_agent=False)    
        except Exception as e:
            print(f"Error connect:{e}")
            return None
        
        if manufacture.lower() == "accedian":
            # Tratamento especial para dispositivos Accedian: abre shell interativo
            print("Accedian device detected")
            shell = ssh.invoke_shell()
            time.sleep(2)  # Aguarda inicialização do shell
            shell.recv(1000)  # Limpa o buffer inicial
            shell.send(command + '')  # Envia o comando
            
            output_lines = []
            start_time = time.time()
            while time.time() - start_time < timeout:
                if shell.recv_ready():
                    output = shell.recv(65000).decode("utf-8", errors='ignore')
                    output_lines.append(output)
                    if command in output:
                        break
            time.sleep(1)
            output = ''.join(output_lines)
            print("Output:", output)
            shell.close()
            return output
        # Executa o comando normalmente
        print(f"Executing command: {command}")
        stdin, stdout, stderr = ssh.exec_command(command + '', timeout=timeout, get_pty=True)
        # output_lines = []
        # for line in iter(stdout.readline, ""):
        #     print("line-------------------------------" , line)
        #     output_lines.append(line)
        # output = ''.join(output_lines)
        ssh.close()
        output = stdout.read().decode()
        stdout.channel.settimeout(5)  
        error = stderr.read().decode()
        if error:
            return f"Error: {error}"
        return output
    except Exception as e:
        print(e)
        return None

def ssh_ping(hostname, username, password, command, max_wait_time=120, key="packet-loss"):
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=hostname, username=username, password=password , look_for_keys=False ,  allow_agent=False)


        stdin, stdout, stderr = ssh.exec_command(command)
        channel = stdout.channel
        output_lines = []
        
        # Lê a saída enquanto o comando não termina
        while not channel.exit_status_ready():
            if channel.recv_ready():
                output_lines.append(channel.recv(65000).decode('utf-8', errors='ignore'))
        while channel.recv_ready():
            output_lines.append(channel.recv(65000).decode('utf-8', errors='ignore'))
        

        full_output = "".join(output_lines)
        lines = full_output.splitlines()

        # Filtra a última linha com o resultado do ping (depende do vendor)
        for line in reversed(lines):
            print("---->", line)
            if key in line:
                result = line.strip()
                break
        else:
            result = None
        
        ssh.close()
        return result  

def ping(credencials, hostname, target_ip, manufacture, count=10, interval=1):
    """
    Trata o procedimento de ping e retorna a saída.
    """
    if manufacture.lower() == 'mikrotik':
        user = credencials["user_pop_mikrotik"]
        password = credencials["password_pop_mikrotik"]
        try:
            command = f'/ping {target_ip} count={count} interval={interval}'
            return ssh_ping(hostname, user, password, command)
        except:
            command = f'/ping {target_ip} count=100 interval=0.05'
            return ssh_ping(hostname, user, password, command, key="packet-loss")    
        
    elif manufacture.lower() == 'cisco':
        user = credencials["user_pop_ldap"]
        password = credencials["password_ldap"]
        command = f'ping {target_ip} repeat {count}'
        return ssh_ping(hostname, user, password, command, key="Success rate is")
    
    elif manufacture.lower() == 'juniper':
        user = credencials["user_pop_ldap"]
        password = credencials["password_ldap"]
        command = f'ping {target_ip} count {count} rapid'
        return ssh_ping(hostname, user, password, command, key="loss")
    else:
        print( "Manufacturer not supported")
        return None


def IsPingSucess(output, manufacture):
    """
    Processa a saída do ping para verificar se o procedimento foi bem-sucedido.
    """
    if manufacture.lower() == 'mikrotik':
        for line in output.split(''):
            if 'sent=' in line and 'received=' in line and 'packet-loss=' in line:
                parts = line.split()
                ping_stats = {}
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=')
                        ping_stats[key] = value
                
                print("resultado do paclet loss" , int(ping_stats['packet-loss'].strip("%")))
                # Limite de 2% de perda de pacote
                if int(ping_stats['packet-loss'].strip("%")) == 0 or int(ping_stats['packet-loss'].strip("%")) < 2:
                    return True
                elif int(ping_stats['packet-loss'].strip("%")) > 0 and int(ping_stats['packet-loss'].strip("%")) < 100:
                    return f"Packet loss: {ping_stats['packet-loss']}"
                else:
                    return False
    elif manufacture.lower() == 'cisco':
        for line in output.split(''):
            if 'Success rate is' in line:
                parts = line.split()
                for part in parts:
                    if "/" in part:
                        received, sent = part.replace("(", "").replace(")", "").replace(",", "").split('/')
                        if sent == received:
                            return True
                        elif received == '0':
                            return False
                        else:
                            return f"Packet loss"
    elif manufacture.lower() == 'juniper':
        print(output)
        for line in output.splitlines():
            if 'packet loss' in line:
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        packet_loss = int(part.strip('%'))
                        if packet_loss == 0:
                            return True
                        elif packet_loss > 0 and packet_loss < 100:
                            return f"Packet loss: {packet_loss}%"
                        else:
                            return False
                return False
    return False







            

            # Obtém informações do dispositivo
            connectedto, primary_ip, cpe_manufacture = GetDeviceInfo(service)
            result["result_pop"] = connectedto
            result["result_ping_ip_cpe"] = primary_ip
            if connectedto and primary_ip:
                print("connectedto            ", connectedto)
                hostname = f'{connectedto}.eq.ignetworks.com'
                print(hostname)
                connectedto_manufacture = GetConnectedtoinfo(connectedto)
                if connectedto_manufacture:
                    # Executa o ping inicial
                    output = ping(credencials, hostname, primary_ip.split('/')[0], connectedto_manufacture, count=10, interval=2)
                    if output is not None:
                        ping_sucess = IsPingSucess(output, connectedto_manufacture)
                        print("result", ping_sucess)
                        result["result_pop"] = connectedto
                        result["result_ping_ip_cpe"] = primary_ip
                        # Se o ping inicial for bem-sucedido, executa o ping extendido
                        if ping_sucess:
                            print("entrou aqui")
                            result["responsibility"] = "not-vendor"
                            result["status"] = "up" if ping_sucess == True else "down"
                            result["result_ping_10"]["ping_output"] = output
                            output = ping(credencials, hostname, primary_ip.split('/')[0], connectedto_manufacture, count=1000, interval=0.05)
                            print("resultado ping extendido", output)
                            if output:
                                ping_sucess = IsPingSucess(output, connectedto_manufacture)
                                print("extendido", ping_sucess)
                                result["status"] = "clean" if ping_sucess == True else "packet_loss"
                                result["result_ping_1000"]["ping_output"] = output
                            else:
                                result["result_ping_1000"] = None
                            if result["status"] == "clean" and result["status"] is not None:
                                result["responsibility"] = "customer"
                                result["reason"] = "ping to cpe with 1000 repetions performed clean"
                                result["issue_type"] = "unknown"
                            else:
                                result["responsibility"] = "vendor"
                                result["reason"] = "ping to cpe with 1000 repetions not performed clean it might be a degradation"
                            # Verifica a interface do CPE
                            output_cpe = Access_cpe(credencials, primary_ip.split('/')[0], manufacture=cpe_manufacture)
                            result["customer_interface"] = "customer interface up" if output_cpe == True else "cpe unreachable or interface not localized"
                            result["issue_type"] = define_issuetype(result["status"])
                            return result
                        else:
                            result["responsibility"] = "vendor"
                            result["status"] = "down"
                            result["result_ping_10"]["ping_output"] = output
                            result["result_ping_1000"] =  None
                            result["reason"] = "ping to cpe failed"
                            result["issue_type"] = define_issuetype(result["status"])
                            return result   
                    else:
                        result["responsibility"] = "unknown"
                        result["result_ping_10"]["ping_output"] = output
                        result["result_ping_1000"]["status"] =  None
                        result["reason"] = "ping could not be performed, output is none"
                        result["issue_type"] = define_issuetype(result["status"])
                        return result    
                else:
                    print(f"Unable to get the manufacture of the device connectedto: {connectedto} primary ip: {primary_ip}")
                    result["status"] = "unknown"
                    result["reason"] = f"Unable to get the manufacture of the device connectedto: {connectedto} primary ip: {primary_ip}"
                    result["result_ping_10"] =  {"ping_output": [output]}
                    result["result_ping_1000"] = {}
                    result["issue_type"] = define_issuetype(result["status"])
                    return result
            else:
                print(f"Unable to ping the device vars connectedto: {connectedto} primary ip: {primary_ip}")
                result["reason"] = f"Unable to ping the device vars connectedto: {connectedto} primary ip: {primary_ip}"
                result["result_ping_10"]  =  {}
                result["result_ping_1000"]  =  {}
                return result

        except Exception as e:
            result["reason"] = str(e)
            print(f"Erro inesperado durante a execução: {e}")
            return result