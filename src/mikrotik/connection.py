from typing import Optional, Literal
import paramiko
from infra.config import MikrotikConfig
from infra.logger.service_log import Logger
from typing import Optional
import re
import time
CPE_USER = MikrotikConfig.get_mikrotik_username()
CPE_PASSWORD = MikrotikConfig.get_mikrotik_password()
POP_USER = MikrotikConfig.get_mikrotik_pop()
POP_PASSWORD = MikrotikConfig.get_mikrotik_pop_password()

logger = Logger.get_logger("mikrotik")


class MikrotikConnection:
    @staticmethod
    def _connect(
        conn_type: Literal["cpe", "pop"],
        ip: str,
        timeout: int = 10
    ) -> paramiko.SSHClient:
        """
        Connect to Mikrotik RouterOS using SSH.

        Args:
            conn_type (str): Connection type, either 'cpe' or 'pop'.
            ip (str): IP address of the Mikrotik device.
            timeout (int): Timeout in seconds for the connection.

        Returns:
            paramiko.SSHClient: An SSH client connected to the Mikrotik device.

        Raises:
            ValueError: If conn_type is invalid or ip is not provided.
            ConnectionError: If connection to the Mikrotik device fails.
        """

        if not ip:
            logger.error("IP address must be provided for Mikrotik connection.")
            raise ValueError("IP address must be provided.")

        # Escolhe credenciais dependendo do tipo
        if conn_type == "cpe":
            username = MikrotikConfig.get_mikrotik_username()
            if username is None:
                logger.error("MIKROTIK_USERNAME_CPE environment variable is not set.")
                raise ValueError("MIKROTIK_USERNAME_CPE environment variable is not set.")
            password = MikrotikConfig.get_mikrotik_password()
            if password is None:
                logger.error("MIKROTIK_PASSWORD_CPE environment variable is not set.")
                raise ValueError("MIKROTIK_PASSWORD_CPE environment variable is not set.")
        elif conn_type == "pop":
            username = MikrotikConfig.get_mikrotik_pop()
            if username is None:
                logger.error("MIKROTIK_USERNAME_POP environment variable is not set.")
                raise ValueError("MIKROTIK_USERNAME_POP environment variable is not set.")
            password = MikrotikConfig.get_mikrotik_pop_password()
            if password is None:
                logger.error("MIKROTIK_PASSWORD_POP environment variable is not set.")
                raise ValueError("MIKROTIK_PASSWORD_POP environment variable is not set.")
        else:
            logger.error(f"Invalid connection type: {conn_type}. Must be 'cpe' or 'pop'.")
            raise ValueError(f"Invalid connection type: {conn_type}. Must be 'cpe' or 'pop'.")

        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())



        try:

            ssh_client.connect(
                hostname=ip,
                port=MikrotikConfig.get_mikrotik_port(),
                username=username,
                password=password,
                timeout=timeout,
                look_for_keys=False,
                allow_agent=False
            )
        except Exception as e:
            logger.error(f"Failed to connect to Mikrotik device {ip}: {e}")
            raise ConnectionError(f"Failed to connect to Mikrotik device {ip}: {e}")

        if ssh_client.get_transport() is None or not ssh_client.get_transport().is_active():
            logger.error(f"SSH transport is not active after connection attempt to {ip}.")
            raise ConnectionError("SSH transport is not active after connection attempt.")

        return ssh_client

    @staticmethod
    def run_command(client, command):
        stdout = client.exec_command("/n")
        stdin, stdout, stderr = client.exec_command(command)
        time.sleep(3)
        result = None
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if output.strip():
            result = f"{command}"
            result += output
        else:
            result = f"error: {error}"
        return result

    @staticmethod
    def get_system_resource(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None) -> str:
        """
        Get system resource information from the Mikrotik device.
        
        Returns:
            str: The output of the system resource command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        stdin, stdout, stderr = ssh_client.exec_command("/system resource print")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        ssh_client.close()
        if error:
            return f"Error: {error}"
        
        return output.strip() if output else "No system resource information found."

    @staticmethod
    def get_allinterface_status(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None) -> str:
        """
        Get the status of interfaces on the Mikrotik device.
        
        Returns:
            str: The output of the interface status command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        stdin, stdout, stderr = ssh_client.exec_command("/interface print")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        ssh_client.close()
        
        if error:
            logger.error(f"Error fetching interface status: {error}")
            return f"Error: {error}"
        
        return output.strip() if output else "No interfaces found."
        
    @staticmethod
    def get_eoip_interfaces(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None, service: Optional[str] = None) -> str:
        """
        Get the EoIP interfaces on the Mikrotik device.
        
        Returns:
            str: The output of the EoIP interfaces command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        if type == 'cpe':
            logger.info("Fetching EoIP interfaces for CPE")
            stdin, stdout, stderr = ssh_client.exec_command("/interface eoip print")
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            ssh_client.close()
        
        elif type == 'pop':
            logger.info(f"Fetching EoIP interfaces for POP with service {service}")
            stdin, stdout, stderr = ssh_client.exec_command(f'/interface eoip print where name~"{service}"')
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            local_address = re.search(r'local-address=(\d+\.\d+\.\d+\.\d+)', output)
            local_address = local_address.group(1) if local_address else None 
            remote_address = re.search(r'remote-address=(\d+\.\d+\.\d+\.\d+)', output)
            remote_address = remote_address.group(1) if remote_address else None
            if remote_address != None and local_address != None:
                output += f"\nLocal Address: {local_address}\nRemote Address: {remote_address}"
                ping = MikrotikConnection.extented_ping(ip, type , local_address, remote_address, count=5, interval=1, size=1472)
                small_ping = MikrotikConnection.IsPingSucess(ping)
                logger.info(f"Ping result: {ping}")
                if small_ping == True:
                    logger.info(f"Ping to remote address {remote_address} with 5 repetitions performed cleanly.")
                    output += "ping to remote address with 5 repetions performed clean: " + remote_address + "\n"
                    output += ping
                    ping_extented = MikrotikConnection.extented_ping(ip, type , local_address, remote_address, count=1000, interval=0.1,size=1400)
                    logger.info(f"Extended ping result: {ping_extented}")
                    output += "extended ping to eoip remote address\n"
                    output += "Extended ping not performed well\n" if ping_extented == False else "Extended ping performed well\n"
                    output += ping_extented
                elif small_ping == False:
                    logger.warning(f"Ping to remote address {remote_address} with 5 repetitions performed with errors.")
                    output += "ping to remote address with 5 repetions performed with errors: " + remote_address + "\n"
                    traceroute = MikrotikConnection.run_command(ssh_client, f'/tool traceroute {remote_address} src-address={local_address} max-hops=10 duration=2 timeout=2')
                    output += traceroute
                return output
            ssh_client.close()
        if error:
            logger.error(f"Error fetching EoIP interfaces: {error}")
            return f"Error: {error}"
        
        return output.strip() if output else "No EoIP interfaces found."
    
    @staticmethod
    def get_l2tp_interfaces(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None, service: Optional[str] = None) -> str:
        """
        Get the L2TP interfaces on the Mikrotik device.
        Returns:
            str: The output of the L2TP interfaces command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        if type == 'cpe':
            logger.info("Fetching L2TP interfaces for CPE")
            stdin, stdout, stderr = ssh_client.exec_command("/interface l2tp print")
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
        elif type == 'pop':
            logger.info(f"Fetching L2TP interfaces for POP with service {service}")
            stdin, stdout, stderr = ssh_client.exec_command(f'interface l2tp-server print where name~"{service}"')
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            client_address = re.search(r'(\d+\.\d+\.\d+\.\d+)', output)
            client_address = client_address.group(1) if client_address else None
            if client_address != None:
                cmd = f'/ping {client_address} count=5 do-not-fragment'
                ping = MikrotikConnection.run_command(ssh_client, cmd)
                output += "ping to cpe client address: " + client_address + "\n"
                output += ping
        ssh_client.close()
        if error:
            logger.error(f"Error fetching L2TP interfaces: {error}")
            return f"Error: {error}"
        return output.strip() if output else "No L2TP interfaces found."
    
    @staticmethod
    def get_gre_interfaces(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None, service: Optional[str] = None) -> str:
        """
        Get the GRE interfaces on the Mikrotik device.
        
        Returns:
            str: The output of the GRE interfaces command.
        """
        if type == 'cpe':
            logger.info("Fetching GRE interfaces for CPE")
            ssh_client = MikrotikConnection._connect(type , ip )
            stdin, stdout, stderr = ssh_client.exec_command("/interface gre print")
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            ssh_client.close()
        elif type == 'pop':
            logger.info(f"Fetching GRE interfaces for POP with service {service}")
            ssh_client = MikrotikConnection._connect(type , ip )
            stdin, stdout, stderr = ssh_client.exec_command(f'/interface gre print where name~"{service}"')
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            logger.info(f"GRE interfaces output: {output}")
            local_address = re.search(r'local-address=(\d+\.\d+\.\d+\.\d+)', output)
            logger.info(f"Local address: {local_address}")
            local_address = local_address.group(1) if local_address else None
            remote_address = re.search(r'remote-address=(\d+\.\d+\.\d+\.\d+)', output)
            logger.info(f"Remote address: {remote_address}")
            remote_address = remote_address.group(1) if remote_address else None
            if remote_address != None and local_address != None:
                ping = MikrotikConnection.extented_ping(ip, type , local_address, remote_address, count=5, interval=1, size=1472)
                ping_small = MikrotikConnection.IsPingSucess(ping)
                logger.info(f"Ping result: {ping}")
                if ping_small:
                    logger.info(f"Ping to remote address {remote_address} with 5 repetitions performed cleanly.")
                    output += "ping to gre remote address with 5 repetions performed clean: " + remote_address + "\n"
                    output += ping
                    ping_extended = MikrotikConnection.extented_ping(ip, type , local_address, remote_address, count=1000, interval=0.1, size=1472)
                    logger.info(f"Extended ping result: {ping_extended}")
                    output += "extended ping to gre remote address\n"
                    output += "Extended ping not performed well\n" if ping_extended == False else "Extended ping performed well\n"
                    output += ping_extended

                else:
                    logger.warning(f"Ping to remote address {remote_address} with 5 repetitions performed with errors.")
                    output += "ping to gre remote address with 5 repetions performed with errors: " + remote_address + "\n"
                    output += ping
                    traceroute = MikrotikConnection.run_command(ssh_client, f'/tool traceroute {remote_address} src-address={local_address} max-hops=10 duration=2 timeout=2')
                    logger.info(f"Traceroute result: {traceroute}")
                    output += traceroute
            ssh_client.close()
        if error:
            logger.error(f"Error fetching GRE interfaces: {error}")
            return f"Error: {error}"
        
        return output.strip() if output else "No GRE interfaces found."
    
    @staticmethod
    def get_customer_interface_status(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None) -> str:
        """
        Get the status of customer interfaces on the Mikrotik device.
        
        Returns:
            str: The output of the customer interface status command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        stdin, stdout, stderr = ssh_client.exec_command('/interface print where comments="Customer Port"')
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        ssh_client.close()
        
        if error:
            logger.error(f"Error fetching customer interface status: {error}")
            return f"Error: {error}"
        
        return output.strip() if output else "No customer interfaces found."
    
    @staticmethod
    def get_external_macs_bridge_learned(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None, service: Optional[str] = None) -> str:
        """
        Get the external MAC addresses from customer interfaces on the Mikrotik device.
        
        Returns:
            str: The output of the command to get external MAC addresses.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        if type == 'cpe':
            stdin, stdout, stderr = ssh_client.exec_command('interface bridge host print terse where dynamic=yes local=no')
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            logger.info(f"External MACs learned CPE: {output}")
            return output.strip() if output else "No external MACs found."
        elif type == 'pop':
            stdin, stdout, stderr = ssh_client.exec_command(f'/interface bridge host print terse where bridge~"{service}" dynamic=yes local=no')
            output = stdout.read().decode('utf-8')
            logger.info(f"External MACs learned POP: {output}")
            error = stderr.read().decode('utf-8')
            return output.strip() if output else "No external MACs found."
        ssh_client.close()
        if error:
            logger.error(f"Error fetching external MACs: {error}")
            return f"Error: {error}"
        
        

    @staticmethod
    def get_traffic_statistics(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None) -> str:
        """
        Get traffic statistics for WAN and Customer interfaces.
        
        Args:
            connection (paramiko.SSHClient): An established SSH connection to the Mikrotik device.
        
        Returns:
            str: The output of the traffic statistics commands.
        """
        results = ""
        
        # Comandos para Exibir resultado
        ssh_client = MikrotikConnection._connect(type , ip )
        
        stdin, stdout, stderr = ssh_client.exec_command(f'/interface monitor-traffic [find comment~"WAN"] once')
        wan_output = stdout.read().decode('utf-8')
        wan_error = stderr.read().decode('utf-8')
        logger.info(f"WAN Traffic Statistics: {wan_output}")
        if wan_error:
            results += f"Error in WAN traffic statistics: {wan_error}\n"
        else:
            results += f"WAN Traffic Statistics:\n{wan_output.strip()}\n"
        
        
        stdin, stdout, stderr = ssh_client.exec_command(f'/interface monitor-traffic [find comment~"Customer"] once')
        customer_output = stdout.read().decode('utf-8')
        customer_error = stderr.read().decode('utf-8')  
        logger.info(f"Customer Traffic Statistics: {customer_output}")
        if customer_error:
            logger.error(f"Error in Customer traffic statistics: {customer_error}")
            results += f"Error in Customer traffic statistics: {customer_error}\n"
        else:
            results += f"Customer Traffic Statistics:\n{customer_output.strip()}\n"
        ssh_client.close()
        return results
    

    @staticmethod
    def get_ip_address(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None) -> str:
        """
        Get the IP address of the Mikrotik device.
        
        Returns:
            str: The output of the IP address command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        stdin, stdout, stderr = ssh_client.exec_command("/ip address print")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        ssh_client.close()
        
        if error:
            logger.error(f"Error fetching IP addresses: {error}")
            return f"Error: {error}"
        
        return output.strip() if output else "No IP addresses found." 
    
    @staticmethod
    def get_firewall_filter(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None) -> str:
        """
        Get the firewall filter rules on the Mikrotik device.
        
        Returns:
            str: The output of the firewall filter command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        stdin, stdout, stderr = ssh_client.exec_command("/ip firewall filter print")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        logger.info(f"Firewall Filter Rules: {output}")
        ssh_client.close()
        
        if error:
            logger.error(f"Error fetching firewall filter rules: {error}")
            return f"Error: {error}"
        
        return output.strip() if output else "No firewall filter rules found."
    
    @staticmethod
    def get_running_config(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None) -> str:
        """
        Get the running configuration of the Mikrotik device.
        
        Returns:
            str: The output of the running configuration command.
        """
        ssh_client = MikrotikConnection._connect(type , ip )
        stdin, stdout, stderr = ssh_client.exec_command("/export")
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        logger.info(f"Running Configuration: {output}")
        ssh_client.close()
        
        if error:
            logger.error(f"Error fetching running configuration: {error}")
            return f"Error: {error}"
        
        return output.strip() if output else "No running configuration found."
    

    @staticmethod
    def IsPingSucess(output: str):
        """
        Processa a saída do ping para verificar se o procedimento foi bem-sucedido.
        """
        for line in output.splitlines():
            if 'sent=' in line and 'received=' in line and 'packet-loss=' in line:
                parts = line.split()
                ping_stats = {}
                for part in parts:
                    if '=' in part:
                        key, value = part.split('=')
                        ping_stats[key] = value
                
                print("resultado do packet loss:", ping_stats['packet-loss'])
                
                # Limite de 2% de perda de pacote
                packet_loss = int(ping_stats['packet-loss'].strip("%"))
                if packet_loss == 0 or packet_loss < 2:
                    return True
                elif 0 < packet_loss < 100:
                    return f"Packet loss: {ping_stats['packet-loss']}"
                else:
                    return False
                




    @staticmethod
    def extented_ping(ip, type , src , dst, count=10, interval=0.1, size=1472) -> str:
        """
        Perform an extended ping to the specified destination IP address from the source IP address.
        Args:
            ip (str): The IP address of the Mikrotik device.
            type (str): The type of connection ('cpe' or 'pop').
            src (str): The source IP address to use for the ping.
            dst (str): The destination IP address to ping.
            count (int): The number of ping requests to send. Default is 10.
            interval (int): The interval between ping requests in seconds. Default is 1.
            size (int): The size of the ping packets in bytes. Default is 1472.
        Returns:
            str: The output of the ping command, including packet loss statistics.
        """
        command = f'/ping {dst} src-address={src} count={count} size={size} interval={interval}'
        ssh_client = MikrotikConnection._connect(type , ip)
        stdin, stdout, stderr = ssh_client.exec_command(command)
        logger.info(f"Executing command: {command}")
        channel = stdout.channel
        output_lines = []

        # keep reading until the command completes
        while not channel.exit_status_ready():
            if channel.recv_ready():
                output_lines.append(channel.recv(65000).decode('utf-8', errors='ignore'))
        while channel.recv_ready():
            output_lines.append(channel.recv(65000).decode('utf-8', errors='ignore'))
        full_output = "".join(output_lines)
        lines = full_output.splitlines()
    
        # Filter out lines that do not contain ping statistics
        for line in reversed(lines):
            print("---->", line)
            if "packet-loss" in line:
                result = line.strip()
                break
            else:
                result = None
        logger.info(f"Ping output: {full_output}")
        ssh_client.close()
        return result  