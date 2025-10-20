import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

class NetboxConfig:
    NETBOX_HOST = os.getenv('NETBOX_HOST', None)
    NETBOX_TOKEN = os.getenv('NETBOX_TOKEN', None)

    @classmethod
    def get_netbox_url(cls):
        return cls.NETBOX_HOST

    @classmethod
    def get_netbox_token(cls):
        return cls.NETBOX_TOKEN
    

 
class IsToolsConfig:
    IS_TOOLS_HOST = os.getenv('IS_TOOLS_HOST', None)
    @classmethod
    def get_is_tools_url(cls):
        if cls.IS_TOOLS_HOST is None:
            raise ValueError("IS_TOOLS_HOST environment variable is not set.")
        return cls.IS_TOOLS_HOST


class QuickbaseConfig:
    QUICKBASE_API_TOKEN = os.getenv('QUICKBASE_API_TOKEN', None)
    QUICKBASE_HOSTNAME = os.getenv('QUICKBASE_HOSTNAME', None)
    @classmethod
    def get_quickbase_api_token(cls):
        return cls.QUICKBASE_API_TOKEN
    
    @classmethod
    def get_quickbase_hostname(cls):
        return cls.QUICKBASE_HOSTNAME
    

class MikrotikConfig:
    MIKROTIK_PORT = int(os.getenv('MIKROTIK_PORT', 22))   
    MIKROTIK_USERNAME_CPE = os.getenv('MIKROTIK_USERNAME_CPE', None)
    MIKROTIK_PASSWORD_CPE = os.getenv('MIKROTIK_PASSWORD_CPE', None)
    MIKROTIK_USERNAME_POP = os.getenv('MIKROTIK_USERNAME_POP', None)
    MIKROTIK_PASSWORD_POP = os.getenv('MIKROTIK_PASSWORD_POP', None)

    @classmethod
    def get_mikrotik_port(cls):
        return cls.MIKROTIK_PORT

    @classmethod
    def get_mikrotik_username(cls):
        return cls.MIKROTIK_USERNAME_CPE
    
    @classmethod
    def get_mikrotik_password(cls):
        return cls.MIKROTIK_PASSWORD_CPE
    
    @classmethod
    def get_mikrotik_pop(cls):
        return cls.MIKROTIK_USERNAME_POP
    
    @classmethod
    def get_mikrotik_pop_password(cls):
        return cls.MIKROTIK_PASSWORD_POP
    

class GeneralConfig:
    """General configuration class to retrieve Cisco connection details from environment variables.
    This class provides methods to get the Cisco port, username, and password.
    It uses environment variables to allow for flexible configuration without hardcoding sensitive information.
    """

    CISCO_PORT = int(os.getenv('CISCO_PORT', 22))  # Default to port 22 if not set
    CISCO_USERNAME = os.getenv('CISCO_USERNAME_CPE', None)
    CISCO_PASSWORD = os.getenv('CISCO_PASSWORD_CPE', None)

    JUNOS_PORT = int(os.getenv('JUNOS_PORT', 22))  # Default to port 22 if not set
    JUNOS_USERNAME = os.getenv('JUNOS_USERNAME', None)
    JUNOS_PASSWORD = os.getenv('JUNOS_PASSWORD', None)

    @classmethod
    def get_cisco_port(cls):
        return cls.CISCO_PORT

    @classmethod
    def get_cisco_username(cls):
        return cls.CISCO_USERNAME

    @classmethod
    def get_cisco_password(cls):
        return cls.CISCO_PASSWORD
    
    @classmethod
    def get_junos_port(cls):
        return cls.JUNOS_PORT
    
    @classmethod
    def get_junos_username(cls):    
        return cls.JUNOS_USERNAME
    
    @classmethod
    def get_junos_password(cls):    
        return cls.JUNOS_PASSWORD
    


    
class AccedianConfig:
    ACCEDIAN_PORT = int(os.getenv('ACCEDIAN_PORT', 22))  # Default to port 22 if not set
    ACCEDIAN_USERNAME = os.getenv('ACCEDIAN_USERNAME', None)
    ACCEDIAN_PASSWORD = os.getenv('ACCEDIAN_PASSWORD', None)

    @classmethod
    def get_accedian_port(cls):
        return cls.ACCEDIAN_PORT

    @classmethod
    def get_accedian_username(cls):
        return cls.ACCEDIAN_USERNAME

    @classmethod
    def get_accedian_password(cls):
        return cls.ACCEDIAN_PASSWORD


class DatacomConfig:
    DATACOM_PORT = int(os.getenv('DATACOM_PORT', 22))  # Default to port 22 if not set
    DATACOM_USERNAME = os.getenv('DATACOM_USERNAME', None)
    DATACOM_PASSWORD = os.getenv('DATACOM_PASSWORD', None)

    @classmethod
    def get_datacom_port(cls):
        return cls.DATACOM_PORT

    @classmethod
    def get_datacom_username(cls):
        return cls.DATACOM_USERNAME

    @classmethod
    def get_datacom_password(cls):
        return cls.DATACOM_PASSWORD
    

class VersaConfig:
    VERSA_URL = os.getenv('VERSA_URL', None) 
    VERSA_USERNAME = os.getenv('VERSA_USERNAME', None)
    VERSA_PASSWORD = os.getenv('VERSA_PASSWORD', None)

    @classmethod
    def get_url(cls):
        return cls.VERSA_URL

    @classmethod
    def get_versa_username(cls):
        return cls.VERSA_USERNAME

    @classmethod
    def get_versa_password(cls):
        return cls.VERSA_PASSWORD
    

class ZabbixConfig:
    ZABBIX_URL = os.getenv('ZABBIX_URL', None)
    ZABBIX_USER = os.getenv('ZABBIX_USER', None)
    ZABBIX_PASSWORD = os.getenv('ZABBIX_PASSWORD', None)

    @classmethod
    def get_zabbix_url(cls):
        return cls.ZABBIX_URL
    @classmethod
    def get_zabbix_user(cls):
        return cls.ZABBIX_USER
    @classmethod
    def get_zabbix_password(cls):
        return cls.ZABBIX_PASSWORD
    
    