from infra.config import DatacomConfig
import paramiko
from netmiko import ConnectHandler
import re


class DatacomConnection:    
    @staticmethod
    def connect_datacom(ip):
        """
        Attempts to connect to a Datacom device using Netmiko. If it fails, tries Paramiko.
        Returns (connection, type), where type is 'netmiko' or 'paramiko'.
        """

        port = DatacomConfig.get_datacom_port()
        username = DatacomConfig.get_datacom_username()
        password = DatacomConfig.get_datacom_password()
        device = {
            'device_type': 'autodetect',
            'host': ip,
            'username': username,
            'password': password,
            'port': port
        }
        try:
            connection = ConnectHandler(**device)
            return connection, 'netmiko'
        except Exception:
            try:
                ssh_client = paramiko.SSHClient()
                ssh_client.load_system_host_keys()
                ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh_client.connect(hostname=ip, port=port, username=username, password=password)
                return ssh_client, 'paramiko'
            except Exception:
                return None, None

    
    @staticmethod
    def identify_datacom_version(connection, conn_type):
        """
        Identifies the Datacom device model/version by sending a sequence of commands.
        Returns (model, output) where model is a string and output is the command result.
        The first valid response is used to identify the model.
        """
        try:
            commands = ['show version', 'show platform', 'show system']
            last_valid_output = ''
            for command in commands:
                if conn_type == 'netmiko':
                    output = connection.send_command(command, strip_prompt=False, strip_command=False)
                else:
                    stdin, stdout, stderr = connection.exec_command(command)
                    output = stdout.read().decode('utf-8')
                # Check if output is valid (not empty, no error/syntax)
                if output and not any(err in output.lower() for err in ['invalid input', 'syntax error', 'unknown command']):
                    last_valid_output = output
                    for model in ['DM2301', 'DM4050', 'DM4100', 'DM4170', 'DM4370']:
                        if model in output:
                            return model, output
            # If no model found but a valid response exists
            if last_valid_output:
                return 'Unknown', last_valid_output
            return 'Unknown', output
        except Exception as e:
            return 'Unknown', str(e)

    
    @staticmethod
    def test_dm4050(connection, conn_type, service):
        """
        Runs troubleshooting commands for DM4050 model.
        Returns the output as a string.
        """
        output = ""
        if conn_type == 'netmiko':
            output += connection.send_command_timing('show system uptime', strip_prompt=False, strip_command=False)
            cmd = connection.send_command_timing(f'show vlan brief | include {service}', strip_prompt=False, strip_command=False)
        else:
            stdin, stdout, stderr = connection.exec_command('show system uptime')
            output += stdout.read().decode('utf-8')
            stdin, stdout, stderr = connection.exec_command(f'show vlan brief | include {service}')
            cmd = stdout.read().decode('utf-8')
        output += cmd
        # Adicione mais comandos conforme necessário
        return output


    @staticmethod
    def test_dm2301(connection, conn_type, service):
        """
        Runs troubleshooting commands for DM2301 model.
        Returns the output as a string.
        """
        output = ""
        if conn_type == 'netmiko':
            output += connection.send_command_timing(f'show vlan name {service}', strip_prompt=False, strip_command=False)
            # TO DO 
            # GET ALL INTERFACES  
            # GET THE CONFIGURATION OF THEM 
            # GET STATUS OF THEM 
            # GET MAC ADDRESS LEARNING RESULT
            
        else:
            stdin, stdout, stderr = connection.exec_command(f'show vlan name {service}')
            output += stdout.read().decode('utf-8')
        # Adicione mais comandos conforme necessário
        return output
    

    @staticmethod
    def _extract_vlan_from_output(output, service_name):
        """
        Extracts the VLAN number from switch output for the given service name.
        Returns the VLAN number as a string, or None if not found.
        """
        pattern = rf"^(\d+)\s+{re.escape(service_name)}"
        for line in output.splitlines():
            match = re.match(pattern, line.strip())
            if match:
                return match.group(1)
        return None

    @staticmethod
    def get_interface_status(connection, conn_type, service_id):
        """
        Runs troubleshooting commands to get interface status.
        Returns the output as a string.
        """
         
        pass
    

    @staticmethod
    def get_mac_learning_results(connection, conn_type, service_id):
        """
        Runs troubleshooting commands to get MAC learning results.
        Returns the output as a string.
        """

        pass
    
    @staticmethod
    def get_interface_configuration(connection, conn_type, interface_name, model_type):
        """
        Runs troubleshooting commands to get interface configuration.
        Returns the output as a string.
        """
      
        pass
        
    @staticmethod
    def test_dm4100(connection, conn_type, service):
        """
        Runs troubleshooting commands for DM4100 model.
        Returns the output as a string.
        """
        output = ""
        if conn_type == 'netmiko':
            output += connection.send_command_timing(f'show vlan name {service}', strip_prompt=False, strip_command=False)
            interface_matches =re.findall(r'(?<=Eth)\d+\/\d+', output)
            portchannel = re.findall(r'(?<=Port-Channel)\d+', output)
            if portchannel:
                for port in portchannel:
                    output += connection.send_command_timing(f' show interfaces status Port-Channel {port} | include Name|admin|status', strip_prompt=False, strip_command=False)
            for interface in interface_matches:
                output += connection.send_command_timing(f' show interfaces status Eth {interface} | include Name|admin|status', strip_prompt=False, strip_command=False) 
            for interface in interface_matches:
                output += connection.send_command_timing(f' show interfaces counters Eth {interface}', strip_prompt=False, strip_command=False) 
            vlan_match = re.search(r'VLAN:\s+(\d+)', output)
            if vlan_match:
                vlan_number = vlan_match.group(1)
                # user admin authorized to run this command      
                output += connection.send_command_timing(f' clear mac-address-table vlan {vlan_number} unicast', strip_prompt=False, strip_command=False)
                #time.sleep(6)
                output += connection.send_command_timing(f' show mac-address-table vlan {vlan_number}', strip_prompt=False, strip_command=False)
        else:
            stdin, stdout, stderr = connection.exec_command(f'show vlan name {service}')
            output += stdout.read().decode('utf-8')
        return output
 
    @staticmethod
    def test_dm4170(connection, conn_type, service):
        """
        Runs troubleshooting commands for DM4170 model.
        Returns the output as a string.
        """
        print("connection type: ", conn_type)
        output = ""
        if conn_type == 'netmiko':
            output += connection.send_command('show system uptime', strip_prompt=False, strip_command=False, expect_string="#") 
            output += connection.send_command(f' show vlan | include {service}', strip_prompt=False, strip_command=False, expect_string="#")
            vlan = DatacomConnection._extract_vlan_from_output(output, service)
            if vlan:
                cmd = connection.send_command(f'show vlan membership {vlan}', strip_prompt=False, strip_command=False, expect_string="#")
                output += cmd
                interface_pattern = r'((?:gigabit-ethernet|ten-gigabit-ethernet)-\d+/\d+/\d+)'
                interface_matches = re.findall(interface_pattern, cmd)
                if interface_matches:
                    res = [sub.replace("ethernet-", "ethernet ") for sub in interface_matches]
                    for interface in res:
                            output += connection.send_command(f'show interface {interface}', strip_prompt=False, strip_command=False, expect_string="#") 
                            output += connection.send_command(f' show interface {interface} statistics | include Errors', strip_prompt=False, strip_command=False, expect_string="#") 
                output += connection.send_command(f' show mac-address-table vlan {vlan}', strip_prompt=False, strip_command=False, expect_string="#")
            
        else:
            stdin, stdout, stderr = connection.exec_command(f'show system uptime')
            output += stdout.read().decode('utf-8')
            stdin, stdout, stderr = connection.exec_command(f'show vlan | include {service}')
            output += stdout.read().decode('utf-8')
            interface_pattern = r'(gigabit-ethernet-Gi\d+/\d+/\d+|Gi\s+\d+/\d+(?:,\d+)?|lag-\d+)'
            pattern = rf"^(\d+)\s+{re.escape(service)}"
            for line in output.splitlines():
                match = re.match(pattern, line)
            if match:
                return f"Service {service} found in output: {match.group(1)}"
            connection.close()

        return output

 
    @staticmethod
    def test_dm4370(connection, conn_type, service):
        """
        Runs troubleshooting commands for DM4370 model.
        Returns the output as a string.
        """
        output = "Not implemented yet for DM4370 model."
        return output

    @staticmethod
    def troubleshooting_datacom(hostname, service):
        """
        Main troubleshooting entry point for Datacom devices.
        Attempts connection, identifies model, and runs model-specific troubleshooting.
        Returns the output as a string.
        """
        connection, conn_type = DatacomConnection.connect_datacom(hostname)
        if not connection:
            return f"Could not connect to Datacom device {hostname} using Netmiko or Paramiko."
        model, version_output = DatacomConnection.identify_datacom_version(connection, conn_type)

        if model == 'DM4050':
            result = DatacomConnection.test_dm4050(connection, conn_type, service)
        elif model == 'DM2301':
            result = DatacomConnection.test_dm2301(connection, conn_type, service)
        elif model == 'DM4100':
            result = DatacomConnection.test_dm4100(connection, conn_type, service)

        elif model == 'DM4170':
            result = DatacomConnection.test_dm4170(connection, conn_type, service)
        elif model == 'DM4370':
            result = DatacomConnection.test_dm4370(connection, conn_type, service)
        else:
            result = f"Unrecognized model. Output:\n{version_output}"
        if conn_type == 'netmiko':
            connection.disconnect()
        else:
            connection.close()
        return result

