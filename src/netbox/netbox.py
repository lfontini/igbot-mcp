from infra.config import NetboxConfig
from typing import Optional
import pynetbox

HOST = NetboxConfig.get_netbox_url()
TOKEN = NetboxConfig.get_netbox_token()

class Netbox:
    @staticmethod
    def connect():
        """
        Connect to the NetBox API using the provided host and token.
        
        :return: A pynetbox API instance.
        """
        return pynetbox.api(HOST,TOKEN)

    @staticmethod
    def get_management_ip(device_name: str) -> Optional[str]:
        """
        Retrieve the management IP address of a device from NetBox.
        
        :param device_name: The name of the device to query.
        :return: The management IP address as a string, or None if not found.
        """
        
        nb = Netbox.connect()
        try:
            device = nb.dcim.devices.get(name=device_name)
            if device and device.primary_ip:
                return device.primary_ip.address.split('/')[0]  # Return only the IP part
            return None
        except Exception as e:
            print(f"Error retrieving management IP for {device_name}: {e}")
            return None
    
    @staticmethod
    def get_devices_by_site(site_name: str) -> Optional[list]:
        """
        Retrieve a list of devices associated with a specific site from NetBox.
        
        :param site_name: The name of the site to query.
        :return: A list of device names, or None if not found.
        """
        
        nb = Netbox.connect()
        devices = nb.dcim.devices.filter(q=site_name)
        device_list = []
        for device in devices:
            print(f"Device: {device.name}, Site: {device.site.name}")
            device_list.append(device.name)
        return device_list if device_list else None
        
    



    @staticmethod
    def get_manufacturer(device_name: str) -> Optional[str]:
        """
        Retrieve the manufacturer of a device from NetBox.
        
        :param device_name: The name of the device to query.
        :return: The manufacturer name as a string, or None if not found.
        """
        
        nb = Netbox.connect()
        try:
            device = nb.dcim.devices.get(name=device_name)
            if device and device.device_type and device.device_type.manufacturer:
                return device.device_type.manufacturer.name
            return None
        except Exception as e:
            print(f"Error retrieving manufacturer for {device_name}: {e}")
            return None
        

    @staticmethod
    def get_device_type(device_name: str) -> Optional[str]:
        """
        Retrieve the device type of a device from NetBox.
        
        :param device_name: The name of the device to query.
        :return: The device type as a string, or None if not found.
        """
        
        nb = Netbox.connect()
        try:
            device = nb.dcim.devices.get(name=device_name)
            if device and device.device_type:
                return device.device_type.model
            return None
        except Exception as e:
            print(f"Error retrieving device type for {device_name}: {e}")
            return None
    
    @staticmethod
    def get_connected_to(device_name: str) -> Optional[str]:
        """
        retrive connected to field from NetBox.
        :param device_name: The name of the device to query.
        :return: The device type as a string, or None if not found.
        """
        
        nb = Netbox.connect()
        try:
            device = nb.dcim.devices.get(name=device_name)
            if device:
                connected_to = device.custom_fields.get('ConnectedTo', None)    
                if connected_to:
                    if 'display' in connected_to:
                        return connected_to.get('display', None)
                    elif 'name' in connected_to:
                        return connected_to.get('name', None)
                    else:
                        return None
        except Exception as e:
            print(f"Error retrieving connected_to for {device_name}: {e}")
            return None


