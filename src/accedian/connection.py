import netmiko
from infra.config import AccedianConfig

class AccedianConnection:
    """
    Accedian connection class for managing connections to Accedian devices.
    """

    @staticmethod
    def _connection(ip: str):
        """
        Create a Netmiko connection to an Accedian device.
        :param ip: IP address of the device.
        :return: Netmiko SSH connection object or None if failed.
        """
        port = AccedianConfig.get_accedian_port()
        username = AccedianConfig.get_accedian_username()
        password = AccedianConfig.get_accedian_password()
        device = {
            'device_type': 'autodetect',  # Ajuste conforme necessário para Accedian
            'host': ip,
            'username': username,
            'password': password,
            'port': port

        }
        try:
            print(f"Connecting to Accedian device at {ip}:{port} with username {username}")
            connection = netmiko.ConnectHandler(**device)
            return connection
        except Exception as e:
            print(f"Failed to connect to Accedian device at {ip}: {e}")
            return None

    @staticmethod
    def get_system_information(ip: str):
        """
        Get system information from an Accedian device using Netmiko.
        :param ip: IP address of the device.
        :return: System information as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        try:
            system_info = connection.send_command_timing('board show uptime', strip_prompt=False, strip_command=False)
            print(f"System information for {ip}:\n{system_info}")
            connection.disconnect()
            return system_info
        except Exception as e:
            return f"Error retrieving system information: {e}"

    @staticmethod
    def get_logs(ip: str):
        """
        Get logs from an Accedian device using Netmiko.
        :param ip: IP address of the device.
        :return: Logs as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        try:
            logs = connection.send_command_timing('syslog show log', strip_prompt=False, strip_command=False)
    
            connection.disconnect()
            return logs
        except Exception as e:
            return f"Error retrieving logs: {e}"


    @staticmethod
    def get_mac_learning_results(ip: str, port: str):
        """
        Get MAC learning results from an Accedian device using Netmiko.
        :param ip: IP address of the device.
        :param port: Port to start MAC learning on.
        :return: MAC learning results as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        try:
            connection.send_command_timing('mac-learning stop', strip_prompt=False, strip_command=False)
            connection.send_command_timing('mac-learning start port Client', strip_prompt=False, strip_command=False)
            results_client = connection.send_command_timing('mac-learning show results', strip_prompt=False, strip_command=False)
            connection.send_command_timing('mac-learning stop', strip_prompt=False, strip_command=False)
            connection.send_command_timing('mac-learning start port Network', strip_prompt=False, strip_command=False)
            results_network = connection.send_command_timing('mac-learning show results', strip_prompt=False, strip_command=False)
            connection.send_command_timing('mac-learning stop', strip_prompt=False, strip_command=False)
            final_results = connection.send_command_timing('mac-learning show results', strip_prompt=False, strip_command=False)
            connection.disconnect()
            results = f"Client Results:\n{results_client}\nNetwork Results:\n{results_network}\nFinal Results:\n{final_results}"
            return results
        except Exception as e:
            return f"Error retrieving MAC learning results: {e}"
        

    @staticmethod
    def get_port_statistics(ip: str):
        """
        Get port statistics from an Accedian device using Netmiko.
        :param ip: IP address of the device.
        :return: Port statistics as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        try:
            port_stats = connection.send_command_timing('port show statistics', strip_prompt=False, strip_command=False)
            connection.disconnect()
            return port_stats
        except Exception as e:
            return f"Error retrieving port statistics: {e}"
        

