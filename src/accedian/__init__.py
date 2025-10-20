import paramiko 
from infra.config import AccedianConfig

class AccedianConnection:
    """
    Accedian connection class for managing connections to Accedian devices.
    """

    @staticmethod
    def _connection(ip: str):
        """
        Create a connection to an Accedian device.
        
        :param ip: IP address of the device.
        :param username: Username for SSH authentication.
        :param password: Password for SSH authentication.
        :param port: Port number for SSH connection (default is 22).
        :return: An SSH client connected to the device.
        """

        port = AccedianConfig.get_accedian_port()
        username = AccedianConfig.get_accedian_username()
        password = AccedianConfig.get_accedian_password()

        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(hostname=ip, port=port, username=username, password=password)
            return ssh_client
        except paramiko.SSHException as e:
            print(f"Failed to connect to Accedian device at {ip}: {e}")
            return None

    @staticmethod
    def get_system_information(ip: str):
        """
        Get system information from an Accedian device.
        
        :param ip: IP address of the device.
        :return: System information as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        try:
            stdin, stdout, stderr = connection.exec_command('board show uptime')
            system_info = stdout.read().decode('utf-8')
            return system_info
        
        except Exception as e:
            return f"Error retrieving system information: {e}"

    @staticmethod
    def get_logs(ip: str):
        """
        Get logs from an Accedian device.
        
        :param ip: IP address of the device.
        :return: Logs as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        
        try:
            stdin, stdout, stderr = connection.exec_command('syslog show log')
            logs = stdout.read().decode('utf-8')
            return logs
        except Exception as e:
            return f"Error retrieving logs: {e}"


    @staticmethod
    def get_mac_learning_results(ip: str, port: str):
        """
        Get MAC learning results from an Accedian device.
        
        :param ip: IP address of the device.
        :param port: Port to start MAC learning on.
        :return: MAC learning results as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        
        try:
            connection.exec_command(f'mac-learning stop')
            connection.exec_command(f'mac-learning start port Client')
            stdin, stdout, stderr = connection.exec_command('mac-learning show results')
            connection.exec_command(f'mac-learning stop')
            connection.exec_command(f'mac-learning start port Network')
            stdin, stdout, stderr = connection.exec_command('mac-learning show results')
            connection.exec_command(f'mac-learning stop')
            stdin, stdout, stderr = connection.exec_command('mac-learning show results')
            results = stdout.read().decode('utf-8')
            return results
        except Exception as e:
            return f"Error retrieving MAC learning results: {e}"
        

    @staticmethod
    def get_port_statistics(ip: str):
        """
        Get port statistics from an Accedian device.
        :param ip: IP address of the device.
        :return: Port statistics as a string.
        """
        connection = AccedianConnection._connection(ip)
        if not connection:
            return "Connection to Accedian device failed."
        
        try:
            stdin, stdout, stderr = connection.exec_command('port show statistics')
            port_stats = stdout.read().decode('utf-8')
            return port_stats
        except Exception as e:
            return f"Error retrieving port statistics: {e}"
        


