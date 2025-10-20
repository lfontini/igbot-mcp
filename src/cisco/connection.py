
import paramiko
from typing import Optional
from infra.config import GeneralConfig
import re
    
class CiscoConnectionRouter:
    """
    Cisco class for handling Cisco devices.
    This class is currently a placeholder and does not implement any functionality.
    """

    @staticmethod
    def _connection(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Create a connection to a cisco device
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        port = GeneralConfig.get_cisco_port()
        username = GeneralConfig.get_cisco_username()
        password = GeneralConfig.get_cisco_password()

 
        try:
            ssh_client.connect(
                hostname=ip,
                port=port,
                username=username,
                password=password
            )
            return ssh_client
        except paramiko.SSHException as e:
            print(f"Failed to connect to Cisco device: {e}")
            return None
        
    @staticmethod
    def get_system_information(type: Optional[str] = ['cpe', 'pop'] , ip: Optional[str] = None):
        """
        Get system information from a Cisco device.
        
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: System information as a string.
        """
        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."

        try:
            stdin, stdout, stderr = connection.exec_command('show version')
            system_info = stdout.read().decode('utf-8')
            return system_info
        except Exception as e:
            return f"Error retrieving system information: {e}"
        finally:
            connection.close()

    @staticmethod
    def clear_counters(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Clear counters on a Cisco device.
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: Result of the clear command.
        """
        connection = CiscoConnectionRouter._connection._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command('clear counters')
            result = stdout.read().decode('utf-8')
            return result
        except Exception as e:
            return f"Error clearing counters: {e}"
            
    @staticmethod
    def get_interfaces(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Get interface information from a Cisco device.
        
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: Interface information as a string.
        """
        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command('show interfaces |  i base|line|Description|rate|address|error')
            interfaces_info = stdout.read().decode('utf-8')
            return interfaces_info
        except Exception as e:
            return f"Error retrieving interface information: {e}"
        finally:
            connection.close() 
    
    @staticmethod
    def get_running_config(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Get the running configuration from a Cisco device.
        
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: Running configuration as a string.
        """
        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command('show running-config')
            running_config = stdout.read().decode('utf-8')
            return running_config
        except Exception as e:
            return f"Error retrieving running configuration: {e}"
        finally:
            connection.close()

    @staticmethod
    def get_arp_table(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Get the ARP table from a Cisco device.
        
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: ARP table as a string.
        """
        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command('show arp')
            arp_table = stdout.read().decode('utf-8')
            return arp_table
        except Exception as e:
            return f"Error retrieving ARP table: {e}"
        finally:
            connection.close()

    @staticmethod
    def get_logs(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Get the logs from a Cisco device.
        
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: Logs as a string.
        """
        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command('show logging')
            logs = stdout.read().decode('utf-8')
            return logs
        except Exception as e:
            return f"Error retrieving logs: {e}"
        finally:
            connection.close()

    @staticmethod
    def get_ip_address(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Get the IP address from a Cisco device.
        
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: IP address as a string.
        """
        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command('show ip interface brief')
            ip_address = stdout.read().decode('utf-8')
            return ip_address
        except Exception as e:
            return f"Error retrieving IP address: {e}"
        finally:
            connection.close()

    @staticmethod
    def get_route_table(type: Optional[str] = ['cpe', 'pop'], ip: Optional[str] = None):
        """
        Get the routing table from a Cisco device.
        
        :param type: Type of device, either 'cpe' or 'pop'.
        :param ip: IP address of the device.
        :return: Routing table as a string.
        """
        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
        try:
            stdin, stdout, stderr = connection.exec_command('show ip route')
            routing_table = stdout.read().decode('utf-8')
            return routing_table
        except Exception as e:
            return f"Error retrieving routing table: {e}"
        finally:
            connection.close()

class CiscoConnectionSwitch:
    """
    Cisco class for handling Cisco switches.
    This class is currently a placeholder and does not implement any functionality.
    """
    @staticmethod
    def _connection(ip: Optional[str] = None):
        """
        Create a connection to a cisco switch
        """
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        port = GeneralConfig.get_cisco_port()
        username = GeneralConfig.get_cisco_username()
        password = GeneralConfig.get_cisco_password()

        try:
            ssh_client.connect(
                hostname=ip,
                port=port,
                username=username,
                password=password
            )
            return ssh_client
        except paramiko.SSHException as e:
            print(f"Failed to connect to Cisco switch: {e}")
            return None
    
    @staticmethod
    def get_system_information(ip: str):
        """
        get all information from a Cisco switch using show version command
        """

        connection = CiscoConnectionRouter._connection(type, ip)
        if not connection:
            return "Connection to Cisco device failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command('show version')
            output = stdout.read().decode('utf-8')
            print(output)
            return output
        except Exception as e:
            return f"Error retrieving system information: {e}"
        finally:
            connection.close()
    
    @staticmethod
    def _get_received_ping(str_ping, manufacturer):
        """
        Extract the number of received packets from the ping output.

        """
        lines = str_ping.splitlines()
        recei = 0
        for line in lines:
            if 'junos' in manufacturer:
                if "transmitted" in line:
                    mtlin = line.split(", ")
                    res = mtlin[1]
                    mtres = res.split()
                    recei = int(mtres[0])
            else:
                if 'Success rate' in line:
                    pattern = r"Success rate is \d+ percent \((\d+)/"
                    match = re.search(pattern, line)
                    if match:
                        recei = int(match.group(1))
                    else:
                        recei = 0
        return recei

    @staticmethod
    def _check_xconnect(connection , interface , output_interface):
        ip_address_match = re.search(r'ip address (\d+\.\d+\.\d+\.\d+)', output_interface)
        check_xc = connection.exec_command(f'show xconnect interface {interface[0]}')
        return check_xc

    @staticmethod
    def _check_ethernet_interface(connection, interface, output_interface):
        """
        Check Ethernet interface and perform ping and traceroute operations.
        """
        ip_address_match = re.search(r'ip address (\d+\.\d+\.\d+\.\d+)', output_interface)
        if ip_address_match:
            ip_address = ip_address_match.group(1)
            ip_parts = ip_address.split('.')
            ip_parts[-1] = str(int(ip_parts[-1]) + 1)
            next_ip = '.'.join(ip_parts)
            ping_output = connection.exec_command(f'ping {next_ip} repeat 5')
            if ping_output:
                recei = CiscoConnectionSwitch._get_received_ping(ping_output, 'cisco')
                if recei > 0:
                    ping_output = connection.exec_command(f'ping {next_ip} size 1472 repeat 1000')
            result = connection.exec_command(f'show ip bgp summary | include  {next_ip}')
            return result
        return ''
    
    @staticmethod
    def check_tunnel_interface(connection, interface, output_interface):
        """
        Check Tunnel interface and perform ping and traceroute operations.
        """
        ip_address = re.search(r'ip address (\d+\.\d+\.\d+\.\d+)', output_interface)
        destination_ip = re.search(r'tunnel destination (\d+\.\d+\.\d+\.\d+)', output_interface)
        source = re.search(r'tunnel source (Loopback\d|GigabitEthernet\d+/\d+/\d+\.\d+|GigabitEthernet\d+/\d+\.\d+|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output_interface)
        if ip_address and destination_ip and source:
            next_ip = ip_address.group(1).rsplit('.', 1)[0] + '.' + str(int(ip_address.group(1).rsplit('.', 1)[-1]) + 1)
            ping_output = connection.exec_command(f'ping {next_ip} repeat 50 source {source.group(1)}')
            traceroute_output = connection.exec_command(f'traceroute {destination_ip.group(1)} source {source.group(1)}')
            return ping_output + traceroute_output
        return ''

    @staticmethod
    def _get_interface_config(connection, interface):
        """
        Get the configuration of a specific interface.
        """
        try:
            stdin, stdout, stderr = connection.exec_command(f'show run int {interface}')
            output_interface = stdout.read().decode('utf-8')
            return output_interface
        except Exception as e:
            return f"Error retrieving interface configuration: {e}"
        
    @staticmethod
    def _detect_type_interface(output_interface):
        """
        Detect the type of interface from the output.
        """
        Detect_type_interface = re.findall(r'interface (Tunnel\d+|GigabitEthernet\d+/\d+/\d+\.\d+|GigabitEthernet\d+/\d+\.\d+|Fa\d+/\d+\.\d+)', output_interface)
        if Detect_type_interface:
            return Detect_type_interface
        return None

    @staticmethod
    def get_interface_status(ip , service): 
        """
        Get the status of interfaces on a Cisco switch.
        
        :param ip: IP address of the device.
        :param service: Service identifier to filter interfaces.
        :return: Interface status as a string.
        """
        connection = CiscoConnectionSwitch._connection(ip=ip)
        if not connection:
            return "Connection to Cisco switch failed."
    
        try:
            stdin, stdout, stderr = connection.exec_command(f'show interface status | include {service}')
            interface_status = stdout.read().decode('utf-8')
            print("interface_status", interface_status)
            interface_pattern = r'(Gi\d+/\d+/\d+\.\d+|Gi\d+/\d+\.\d+|Gi\d+\.\d+|Tu\d+|Fa\d+/\d+\.\d+)'
            interface_matches = re.findall(interface_pattern, interface_status)
            if any(interface_matches):
                for interface in interface_matches:
                    output_interface = CiscoConnectionSwitch._get_interface_config(connection, interface)
                    result += output_interface
                    Detect_type_interface = CiscoConnectionSwitch._detect_type_interface(output_interface)
                    if Detect_type_interface:
                        interface = Detect_type_interface            
                        if 'xconnect' in output_interface:
                            check_xc = CiscoConnectionSwitch._check_xconnect(connection , interface , output_interface)
                            result += check_xc
                        elif 'Ethernet' in output_interface:
                            result += CiscoConnectionSwitch._check_ethernet_interface(connection, interface, output_interface)
                            result += ''
                        elif 'Tunnel' in output_interface:
                            result += CiscoConnectionSwitch.check_tunnel_interface(connection, interface, output_interface)
                            result += ''
                    return interface_status
            else:
                return "No interfaces found matching the service."
        except Exception as e:
            return f"Error retrieving interface status: {e}"
