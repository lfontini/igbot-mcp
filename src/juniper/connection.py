from  infra.config import GeneralConfig
import re
import ipaddress
from netmiko import ConnectHandler

class JuniperConnection:
    """
    This class is used to manage the connection to Juniper devices.
    """

    @staticmethod
    def _connection(ip: str):
        """
        Create a Netmiko connection to a Juniper device.
        :param ip: IP address of the device.
        :return: Netmiko SSH connection object or None if failed.
        """
        

        port = GeneralConfig.get_junos_port()
        username = GeneralConfig.get_junos_username()
        password = GeneralConfig.get_junos_password()


        device = {
            'device_type': 'juniper_junos',
            'host': ip,
            'username': username,
            'password': password,
            'port': port
        }

        try:
            connection = ConnectHandler(**device)
            return connection
        except Exception as e:
            print(f"Failed to connect to Juniper device at {ip}: {e}")
            return None
        

    @staticmethod
    def get_system_information(ip: str):
        """
        Get system information from a Juniper device using Netmiko.
        :param ip: IP address of the device.
        :return: System information as a string.
        """
        connection = JuniperConnection._connection(ip)
        if not connection:
            return "Connection to Juniper device failed."
        
        try:
            system_info = connection.send_command_timing('show version | match Model', strip_prompt=False, strip_command=False)
            connection.disconnect()
            return system_info
        except Exception as e:
            return f"Error retrieving system information: {e}"
        
    
    @staticmethod
    def _get_version(connection):
        """
        Get the Junos version from the device.
        :param connection: Netmiko connection object.
        :return: Junos version as a string.
        """
        version = connection.send_command_timing('show version', strip_prompt=False, strip_command=False)
        lines = version.splitlines()
        for line in lines:
            if "Model" in line:
                return line.split(":")[1].strip()
        return "Unknown Version"



    @staticmethod
    def _get_received_ping(str_ping):
        """
        Get the number of received packets from a ping command output.
        :param str_ping: The output string from the ping command.
        :return: The number of received packets as an integer.
        """
        pattern = r'(\d+) packets received'
        match = re.search(pattern, str_ping)
        if match:
            return int(match.group(1))
        return 0
    
    @staticmethod
    def test_model_ex4300(connection, service):
        """
        Check if the Juniper device is an EX4300 model.
        :param connection: Netmiko connection object.
        :return: True if the device is an EX4300, False otherwise.
        """

        outputconfig = connection.send_command_timing(f' show configuration | match {service} | display set ', strip_prompt=False, strip_command=False)  
        result = ""
        result += outputconfig
        patter_vlan = r'unit (\d+)'
        vlan_raw = re.search(patter_vlan, outputconfig)
        if vlan_raw:
            vlan = vlan_raw[0].strip("unit").strip()
            result += connection.send_command_timing(f'show ethernet-switching table | match {vlan}', strip_prompt=False, strip_command=False)
        return result

    @staticmethod
    def _is_l2circuit_service(service, config):
        """
        Check if the service is an L2 circuit service.
        :param service: The service name to check.
        :return: True if the service is an L2 circuit, False otherwise.
        """
        patternL2circuit = r'l2circuit neighbor\s+(\d+\.\d+\.\d+\.\d+)' 

        match = re.findall(patternL2circuit, config)
        if match:
            return match
        else:
            return None
        
    @staticmethod
    def _check_l2circuit(connection, service):
        """
        Check if the service is present in the L2 circuit configuration.
        :param connection: Netmiko connection object.
        :param service: The service name to check.
        :return: True if the service is present in the L2 circuit configuration, False otherwise.
        """

        result = connection.send_command_timing(f'show l2circuit connections neighbor {service} summary', strip_prompt=False, strip_command=False)
        if "No L2 circuit connections" in result:
            return f"Service {service} not found in L2 circuit configuration."
        else:
            return result

    @staticmethod
    def _is_irb_service(service, config):
        """
        Check if the service is an IRB service.
        :param service: The service name to check.
        :return: True if the service is an IRB, False otherwise.
        """
        pattern_irb = r'irb unit (\d+)'
        match = re.findall(pattern_irb, config)
        if match:
            return match
        else:
            return None
        

    @staticmethod
    def _is_vpls_service(service, config):
        """
        Check if the service is a VPLS service.
        :param service: The service name to check.
        :return: True if the service is a VPLS, False otherwise.
        """
        pattern_vpls = r'vpls (\d+)'
        match = re.findall(pattern_vpls, config)
        if match:
            return match
        else:
            return None
    
    @staticmethod
    def _check_irb(connection, service):
        """
        Check if the service is present in the IRB configuration.
        :param connection: Netmiko connection object.
        :param service: The service name to check.
        :return: True if the service is present in the IRB configuration, False otherwise.
        """
        patter_ip = r'address (\d+\.\d+\.\d+\.\d+)'
        result = connection.send_command_timing(f'show configuration interfaces irb | match {service}', strip_prompt=False, strip_command=False)
        ip_irb = re.findall(patter_ip, result)
        if ip_irb:
            ip_irb_mais = ipaddress.IPv4Address(ip_irb[0]) + 1
            ping = connection.send_command_timing(f'ping {ip_irb_mais} rapid count 5 do-not-fragment', strip_prompt=False, strip_command=False)
            recei = JuniperConnection._get_received_ping(ping)
            if recei > 0:
                ping += connection.send_command_timing(f'ping {ip_irb_mais} rapid count 1000 size 1472', strip_prompt=False, strip_command=False)
            result += ping
            return result
        else:
            return f"Service {service} not found in IRB configuration."



    @staticmethod
    def _is_bgp_service(service, config):
        """
        Check if the service is a BGP service.
        :param service: The service name to check.
        :return: True if the service is a BGP, False otherwise.
        """
        pattern_bgp = r'neighbor\s+(\d+\.\d+\.\d+\.\d+)'
        match = re.findall(pattern_bgp, config)
        if match:
            return match
        else:
            return None


    @staticmethod
    def _check_bgp_summary(connection , service):
        """
        Check if the service is present in the BGP summary.
        :param service: The service name to check.
        :return: True if the service is present in the BGP summary, False otherwise.
        """
        
        result = connection.send_command_timing(f'show bgp summary | match {service}', strip_prompt=False, strip_command=False)
        
    @staticmethod
    def is_vlan_service(service, config):
        """
        Check if the service is a VLAN service.
        :param service: The service name to check.
        :return: True if the service is a VLAN, False otherwise.
        """
        pattern_vlan = r'unit (\d+)'
        match = re.findall(pattern_vlan, config)
        if match:
            return match
        else:
            return None

    @staticmethod
    def check_vlan(connection, vlan_id):
        """
        Check if the service is present in the VLAN configuration.
        :param connection: Netmiko connection object.
        :param service: The service name to check.
        :return: True if the service is present in the VLAN configuration, False otherwise.
        """
        result = " -------------- Result show bridge mac-table vlan-id ---------------\n"
        result += connection.send_command_timing(f'show bridge mac-table vlan-id {vlan_id}', strip_prompt=False, strip_command=False)
        if result:
            return result
        else:
            return None
    
    @staticmethod
    def _get_vpls_status(connection, service):
        """
        Get the status of a VPLS instance.
        :param connection: Netmiko connection object.
        :param instance: The VPLS instance to check.
        :return: The status of the VPLS instance as a string.
        """
        result = connection.send_command_timing(f'show vpls connections instance VPLS_{service} | last 13', strip_prompt=False, strip_command=False)
        if "No VPLS connections" in result:
            return f"VPLS instance {service} not found."
        else:
            return result

    @staticmethod
    def get_junos_troubleshooting(ip, service):
        """
        Get the interfaces associated with a specific service on a Juniper device.
        :param connection: Netmiko connection object.
        :param service: The service name to search for.
        :return: A string containing the interfaces and their configurations.
        """
        connection = JuniperConnection._connection(ip)
        version = JuniperConnection._get_version(connection)
        if connection is None:
            return "Connection to Juniper device failed."
        result = ""
        result += connection.send_command_timing(f'show interface descr | match {service}', strip_prompt=False, strip_command=False) 
        
        

        if 'ex4300' in version:
            result += JuniperConnection.test_model_ex4300(connection, service)
            
        else:
            result += " -------------- Result show config  ----------------\n"
            outputconfig = connection.send_command_timing(f'show configuration | match {service} | display set' , strip_prompt=False, strip_command=False)
            result += outputconfig

            bgp_neighbor = JuniperConnection._is_bgp_service(service, outputconfig)
            if bgp_neighbor:
                result += " -------------- Result bgp found ---------------\n"
                neighbor = bgp_neighbor[0]
                result += connection.send_command_timing(f'show bgp summary | match {neighbor}', strip_prompt=False, strip_command=False)
            irb = JuniperConnection._is_irb_service(service, outputconfig)
            if irb:
                result += " -------------- Result irb found ---------------\n"
                result += JuniperConnection._check_irb(connection, service)
            l2_circuit = JuniperConnection._is_l2circuit_service(service, outputconfig)

            if l2_circuit:
                ip_matches_l2 = l2_circuit[0]
                result += " -------------- Result l2_circuit found ---------------\n"
                result += JuniperConnection._check_l2circuit(connection, ip_matches_l2)

            vpls = JuniperConnection._is_vpls_service(service, outputconfig)
            if vpls:
                result += " -------------- Result vpls found ---------------\n"
                result += JuniperConnection._get_vpls_status(connection, service)

            vlan = JuniperConnection.is_vlan_service(service, outputconfig)
            if vlan:
                result += " -------------- Result vlan found ---------------\n"
                vlan = vlan[0].strip("unit").strip()
                result += JuniperConnection.check_vlan(connection, vlan)

        return result
            
            
         
           
 