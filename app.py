from fastmcp import FastMCP, Context
from dotenv import load_dotenv
from src.accedian import AccedianConnection
from src.juniper.connection import JuniperConnection
from src.quickbase.quickbase import Quickbase
from src.netbox.netbox import Netbox
from src.is_tools.is_tools import IsTools
from src.mikrotik.connection import MikrotikConnection
from src.cisco.connection import CiscoConnectionRouter, CiscoConnectionSwitch
from src.datacom.connection import DatacomConnection
from pydantic import BaseModel, Field
import subprocess
import platform

from src.versa.connection import VersaConnection
from src.zabbix.connection import ZabbixPingCheckAction
load_dotenv()



mcp = FastMCP('igbot_mcp')

@mcp.tool(
    name="CheckCpe",
    description="Check the CPE of a service including system resource, interface status, EOIP interfaces, L2TP interfaces, GRE interfaces, customer interface status, external MACs, and traffic statistics."
)
async def Check_cpe(service_id: str, ctx: Context):
    """
    Check the CPE of a service.
    """
    
    netbox = Netbox()
    await ctx.info(f"Fetching management IP for service {service_id} ...")
    await ctx.report_progress(10, 100)

    devices = netbox.get_devices_by_site(service_id)
    await ctx.info(f"Fetching devices for service {service_id} ...")
    
    if devices:
        for device in devices:
            management_ip = netbox.get_management_ip(device)
            print(f"Management IP for service {device}: {management_ip}")
            if not management_ip:
                return f"Management IP not found for service {device}."
            
            await ctx.info(f"Fetching device type and manufacturer for service {device} ...")
            await ctx.report_progress(20, 100)
            device_type = netbox.get_device_type(device)
            if not device_type:
                return f"Device name not found for service {device}."
            manufacturer = netbox.get_manufacturer(device)
            if not manufacturer:
                return f"Manufacturer not found for device {device}."
        
            await ctx.info(f"Identified manufacturer: {manufacturer}...")
            await ctx.report_progress(30, 100)
            if "mikrotik" in manufacturer.lower():
                mikrotik = MikrotikConnection()
                try:
                    await ctx.info(f"Fetching system resource ...")
                    await ctx.report_progress(70, 100)
                    system_resource = mikrotik.get_system_resource(type="cpe", ip=management_ip)
                    all_interface_status = mikrotik.get_allinterface_status(type="cpe", ip=management_ip)
                    eoip_interfaces = mikrotik.get_eoip_interfaces(type="cpe", ip=management_ip)
                    l2tp_interfaces = mikrotik.get_l2tp_interfaces(type="cpe", ip=management_ip)
                    gre_interfaces = mikrotik.get_gre_interfaces(type="cpe", ip=management_ip)
                    customer_interface_status = mikrotik.get_customer_interface_status(type="cpe", ip=management_ip)
                    external_macs = mikrotik.get_external_macs_bridge_learned(type="cpe", ip=management_ip)
                    traffic_statistics = mikrotik.get_traffic_statistics(type="cpe", ip=management_ip)

                    return {
                        "system_resource": system_resource,
                        "all_interface_status": all_interface_status , 
                        "eoip_interfaces": eoip_interfaces,
                        "l2tp_interfaces": l2tp_interfaces,
                        "gre_interfaces": gre_interfaces,
                        "customer_interface_status": customer_interface_status,
                        "external_macs": external_macs,
                        "traffic_statistics": traffic_statistics
                        }
                except Exception as e:
                    return f"Error connecting to Mikrotik device: {e}"
            elif "cisco" in manufacturer.lower():
                cisco = CiscoConnectionRouter()
                try:
                    await ctx.info(f"Fetching interfaces ...")
                    await ctx.report_progress(70, 100)
                    interfaces = cisco.get_interfaces(type="cpe", ip=management_ip)
                    system_info = cisco.get_system_information(type="cpe", ip=management_ip)
                    logs = cisco.get_logs(type="cpe", ip=management_ip)
                    routes = cisco.get_route_table(type="cpe", ip=management_ip)
                    arp_table = cisco.get_arp_table(type="cpe", ip=management_ip)
                    
                    return {
                        "interfaces": interfaces,
                        "system_info": system_info,
                        "logs": logs,
                        "routes": routes,
                        "arp_table": arp_table
                    }
                except Exception as e:
                    return f"Error connecting to Cisco device: {e}"
            elif "accedian" in manufacturer.lower():
                accedian = AccedianConnection()
                try:
                    await ctx.info(f"Fetching system resource ...")
                    await ctx.report_progress(70, 100)
                    system_info = accedian.get_system_information(ip=management_ip)
                    logs = accedian.get_logs(ip=management_ip)
                    mac_learning_results = accedian.get_mac_learning_results(ip=management_ip, port="Client")
                    port_statistics = accedian.get_port_statistics(ip=management_ip)

                    return {
                        "system_info": system_info,
                        "logs": logs,
                        "mac_learning_results": mac_learning_results,
                        "port_statistics": port_statistics
                    }
                except Exception as e:
                    return f"Error connecting to Accedian device: {e}"
    
    else:
        return f"There werent any devices found for service {service_id}."

@mcp.tool(
    name="Check_versa",
    description="Check the Versa device of a service including system information, interfaces status, and troubleshooting."
)
def Check_versa(device_name: str):
    """
    Check the Versa device of a service.
    """
    versa = VersaConnection()
    try:
        troubleshooting = versa.get_troubleshooting(device=device_name)
        return troubleshooting
    except Exception as e:
        return f"Error connecting to Versa device: {e}"
    




@mcp.tool(
    name="CheckConfigCpe",
    description="Check the configuration of a CPE device including IPs, firewall, and running config."
)
async def Check_config_cpe(service_id: str, ctx: Context):
    """
    check config into cpe including ips and firewall and running config

    """
    netbox = Netbox()

    devices = netbox.get_devices_by_site(service_id)
    for device in devices:
        management_ip = netbox.get_management_ip(device)
        print(f"Management IP for device {device}: {management_ip}")
        await ctx.info(f"Management IP for device {device}: {management_ip}")
        await ctx.report_progress(10, 100)
        if not management_ip:
            return f"Management IP not found for device {device}."
        device_type = netbox.get_device_type(device)
        if not device_type:
            return f"Device name not found for device {device}."
        await ctx.report_progress(20, 100)
        manufacturer = netbox.get_manufacturer(device)
        if not manufacturer:
            return f"Manufacturer not found for device {device}."
        await ctx.report_progress(30, 100)
        await ctx.info(f"Manufacturer not found for device {device}.")
        if "mikrotik" in manufacturer.lower():
            mikrotik = MikrotikConnection()
            try:
                await ctx.info(f"Fetching running config ...")
                config = mikrotik.get_running_config(type="cpe", ip=management_ip)
                await ctx.report_progress(50, 100)
                await ctx.info(f"Fetching IPs ...")
                ips = mikrotik.get_ip_address(type="cpe", ip=management_ip)
                await ctx.report_progress(60, 100)
                await ctx.info(f"Fetching firewall ...")
                firewall = mikrotik.get_firewall_filter(type="cpe", ip=management_ip)
                await ctx.report_progress(80, 100)
                await ctx.info(f"Fetching running config ...")
                return {
                    "config": config,
                    "ips": ips,
                    "firewall": firewall
                }
            
            except Exception as e:
                return f"Error connecting to Mikrotik device: {e}"
        elif "cisco" in manufacturer.lower():
            cisco = CiscoConnectionRouter()
            try:
                config = cisco.get_running_config(type="cpe", ip=management_ip)
                return {
                    "config": config,
                }
            except Exception as e:
                return f"Error connecting to Cisco device: {e}"

        elif "accedian" in manufacturer.lower():
            # Placeholder for Accedian device handling
            return "Accedian device handling is not implemented yet."

        elif "accedian" in manufacturer.lower():
            # Placeholder for Accedian device handling
            return "Accedian device handling is not implemented yet."     

 
@mcp.tool(
    name="get_nni",
    description="Get the NNI of a service."
)
async def get_nni(service_id: str, ctx: Context):
    """
    Get the NNI of a service.
    """
    quickbase = Quickbase()
    await ctx.info(f"Fetching NNI ...")
    await ctx.report_progress(10, 100)
    nni = quickbase.get_NNI(service_id)
    if not nni:
        return f"NNI not found for service {service_id}."
    
    await ctx.info(f"Fetching equipment ...")
    await ctx.report_progress(20, 100)
    equipment = quickbase.Get_equipment(nni)
    await ctx.info(f"Fetching equipment from quickbase...")
    await ctx.report_progress(70, 100)
    if not equipment:
        await ctx.info(f"No equipment found in quickbase, fetching equipment from is-tools...")
        await ctx.info(f"Fetching equipment ...")
        await ctx.report_progress(70, 100)
        istools = IsTools()
        equipment = istools.get_equipment(name=nni)
        if not equipment:
            return {
                    "nni": nni,
                    "equipment": equipment
                }
    
    return {
        "nni": nni,
        "equipment": equipment
    }
     
@mcp.tool(
    name="get_cross_connect",
    description="Get the cross connect of a service.",
)
def get_cross_connect(service_id: str):
    """
    Get the cross connect of a service.

    """
    quickbase = Quickbase()
    cross_connect = quickbase.Get_cross_connect(service_id)
    if not cross_connect: 
        return f"Cross connect not found for service {service_id}."

    istools = IsTools()
    equipment = istools.get_equipment(name=cross_connect)
    if not equipment:
        return f"Equipment not found for cross connect {cross_connect}."
    
    else:
        return {
        "cross_connect": cross_connect,
        "equipment": equipment
                }

@mcp.tool(
    name="check_service_on_cross",
    description="Check if a service is on a cross equipment.",
)   
async def check_service_on_cross(cross_equipment: str, service_id: str, ctx: Context):
    """
    Check if a service is on a cross equipment.
    """
    if cross_equipment:
        netbox = Netbox()
        await ctx.info(f"Fetching management IP ...")
        await ctx.report_progress(20, 100)
        management_ip = netbox.get_management_ip(cross_equipment)
        if not management_ip:
            return f"Management IP not found for cross equipment {cross_equipment}."
        await ctx.info(f"Fetching device type and manufacturer ...")
        await ctx.report_progress(30, 100)
        
        device_type = netbox.get_device_type(cross_equipment)
        if not device_type:
            return f"Device type not found for cross equipment {cross_equipment}."
        manufacturer = netbox.get_manufacturer(cross_equipment)
        if not manufacturer:
            return f"Manufacturer not found for cross equipment {cross_equipment}."

        await ctx.info(f"Identified manufacturer: {manufacturer}...")
        await ctx.report_progress(40, 100)
        if "datacom" in manufacturer.lower():
            datacom = DatacomConnection()
            try:
                await ctx.info(f"Fetching troubleshooting ...")
                await ctx.report_progress(70, 100)
                result = datacom.troubleshooting_datacom(hostname=management_ip, service=service_id)
                return result
            except Exception as e:
                return f"Error connecting to Datacom device: {e}"
        elif "cisco" in manufacturer.lower():
            cisco = CiscoConnectionSwitch()
            try:
                await ctx.info(f"Fetching system information ...")
                await ctx.report_progress(70, 100)
                result = cisco.get_system_information(ip=management_ip)
                await ctx.info(f"Fetching interface status ...")
                await ctx.report_progress(80, 100)
                result += cisco.get_interface_status(ip=management_ip, service=service_id )
                return result
            except Exception as e:
                return f"Error connecting to Cisco device: {e}"

        elif "juniper" in manufacturer.lower():
            juniper = JuniperConnection()
            try:
                await ctx.info(f"Fetching system information...")
                await ctx.report_progress(70, 100)
                result = juniper.get_system_information(ip=management_ip)
                await ctx.info(f"Fetching interface information... and other info ... ")
                await ctx.report_progress(70, 100)
                result += juniper.get_junos_troubleshooting(ip=management_ip, service=service_id)
                return result
            except Exception as e:
                return f"Error connecting to Juniper device: {e}"
    else:
        return f"Cross equipment not found for service {service_id}."


@mcp.tool(
    name="Check_status_service_on_nni",
    description="Check the status of a service on a NNI.",
)
async def Check_status_service_on_nni(nni: str , service_id: str, ctx: Context):
    """
    Check the status of a service on a NNI. 
    """
    await ctx.info(f"Fetching status of service {service_id} on NNI {nni} ...")
    await ctx.report_progress(10, 100)
    quickbase = Quickbase()
    equipment = quickbase.Get_equipment(nni)

    if not equipment:
        istools = IsTools()
        equipment = istools.get_equipment(name=nni)
        if not equipment:
            return f"Equipment not found for NNI {nni}."
    netbox = Netbox()
    await ctx.info(f"Fetching management IP ...")
    await ctx.report_progress(20, 100)
    management_ip = netbox.get_management_ip(equipment)
    if not management_ip:
        return f"Management IP not found for equipment {equipment}."
    device_type = netbox.get_device_type(equipment)
    await ctx.info(f"Fetching Device type and Manufacturer...")
    await ctx.report_progress(20, 100)
    if not device_type:
        return f"Device type not found for equipment {equipment}."
    manufacturer = netbox.get_manufacturer(equipment)
    if not manufacturer:
        return f"Manufacturer not found for equipment {equipment}."
    
    await ctx.info(f"Identified manufacturer: {manufacturer}...")
    await ctx.report_progress(20, 100)
    if "datacom" in manufacturer.lower():
        datacom = DatacomConnection()
        try:
            await ctx.info(f"Fetching troubleshooting ...")
            await ctx.report_progress(70, 100)
            result = datacom.troubleshooting_datacom(hostname=management_ip, service=service_id)
            return result
        except Exception as e:
            return f"Error connecting to Datacom device: {e}"
    elif "cisco" in manufacturer.lower():
        cisco = CiscoConnectionSwitch()
        print(cisco)
        try:
            await ctx.info(f"Fetching system information ...")
            await ctx.report_progress(70, 100)
            result = cisco.get_system_information(ip=management_ip)
            await ctx.info(f"Fetching interface status ...")
            await ctx.report_progress(80, 100)
            await ctx.info(f" ip {management_ip} and service {service_id} ...")
            result += cisco.get_interface_status(ip=management_ip, service=service_id)
            return result
        except Exception as e:
            return f"Error connecting to Cisco device: {e}"

    elif "juniper" in manufacturer.lower():
        juniper = JuniperConnection()
        try:
            await ctx.info(f"Fetching system information...")
            await ctx.report_progress(70, 100)
            result = juniper.get_system_information(ip=management_ip)
            await ctx.info(f"Fetching interface information... and other info ... ")
            await ctx.report_progress(70, 100)
            result += juniper.get_junos_troubleshooting(ip=management_ip, service=service_id)
            return result
        except Exception as e:
            return f"Error connecting to Juniper device: {e}"
       
@mcp.tool(
    name="CheckDevicesOnNetbox",
    description="Check devices on Netbox for a given site."
)
async def get_devices_by_site(site , ctx: Context):
    """
    Check devices on Netbox for a given site.
    """
    netbox = Netbox()
    await ctx.info(f"Fetching devices for site {site} ...")
    await ctx.report_progress(10, 100)
    devices = netbox.get_devices_by_site(site)
    
    if not devices:
        return f"No devices found for site {site}."
    
    device_info = []
    for device in devices:
        await ctx.info(f"Fetching management IP for device {device} ...")
        management_ip = netbox.get_management_ip(device)
        if not management_ip:
            continue
        await ctx.info(f"Fetching device type and manufacturer for device {device} ...")
        await ctx.report_progress(90, 100)
        device_type = netbox.get_device_type(device)
        manufacturer = netbox.get_manufacturer(device)
        device_info.append({
            "device": device,
            "management_ip": management_ip,
            "device_type": device_type,
            "manufacturer": manufacturer
        })
    
    return device_info


@mcp.tool(
    name="get_pop_for_service",
    description="Check the POP service for a given service ID.",
)
def get_pop_for_service(service_id: str) -> dict: 
    """
    Check the POP service for a given service ID.
    """
    netbox = Netbox() 
    devices = netbox.get_devices_by_site(service_id)
    if devices:
        device_and_pop = {}
        for device in devices:
            pop = netbox.get_connected_to(device)
            device_and_pop[device] = pop if pop else None
        
        return device_and_pop
    else:
        return {"error": "No devices found for service ID."}

@mcp.tool(
    name="check_service_in_pop",
    description="Check if a service is in the POP.",
)
async def check_service_in_pop(service_id: str, pop_device: str , ctx: Context):
    """
    Check if a service is in the POP.
    """
    await ctx.info(f"Checking service {service_id} in POP {pop_device} ...")
    if pop_device: 
        netbox = Netbox()
        management_ip = netbox.get_management_ip(pop_device)
        print(f"Found ip for device {pop_device}:  {management_ip}")
        if not management_ip:
            return f"Management IP not found for device {pop_device}."
        await ctx.info(f"Fetching device type and manufacturer for device {pop_device} ...")
        await ctx.report_progress(20, 100)
        device_type = netbox.get_device_type(pop_device)
        await ctx.report_progress(30, 100)
        await ctx.info(f"Identified device type: {device_type}...")
        if not device_type:
            return f"Device type not found for device {pop_device}."
        await ctx.info(f"Fetching manufacturer for device {pop_device} ...")
        await ctx.report_progress(40, 100)
        manufacturer = netbox.get_manufacturer(pop_device)
        await ctx.report_progress(50, 100)
        await ctx.info(f"Identified manufacturer: {manufacturer}...")
        if not manufacturer:
            return f"Manufacturer not found for device {pop_device}."
        if "datacom" in manufacturer.lower():
                datacom = DatacomConnection()
                try:
                    await ctx.info(f"Fetching troubleshooting ...")
                    await ctx.report_progress(70, 100)
                    result = datacom.troubleshooting_datacom(hostname=management_ip, service=service_id)
                    return result
                except Exception as e:
                    return f"Error connecting to Datacom device: {e}"
        elif "cisco" in manufacturer.lower():
            cisco = CiscoConnectionSwitch()
            try:
                await ctx.info(f"Fetching system information ...")
                await ctx.report_progress(70, 100)
                result = cisco.get_system_information(ip=management_ip)
                await ctx.info(f"Fetching interface status ...")
                await ctx.report_progress(80, 100)
                result += cisco.get_interface_status(ip=management_ip, service=service_id )
                return result
            except Exception as e:
                return f"Error connecting to Cisco device: {e}"

        elif "juniper" in manufacturer.lower():
            juniper = JuniperConnection()
            try:
                await ctx.info(f"Fetching system information...")
                await ctx.report_progress(70, 100)
                result = juniper.get_system_information(ip=management_ip)
                await ctx.info(f"Fetching interface information... and other info ... ")
                await ctx.report_progress(70, 100)
                result += juniper.get_junos_troubleshooting(ip=management_ip, service=service_id)
                return result
            except Exception as e:
                return f"Error connecting to Juniper device: {e}"
            
        elif "mikrotik" in manufacturer.lower():
            mikrotik = MikrotikConnection()
            try:
                await ctx.info(f"Fetching system resource ...")
                await ctx.report_progress(70, 100)
                system_resource = mikrotik.get_system_resource(type="pop", ip=management_ip)
                await ctx.info(f"Fetching EOIP interfaces ...")
                print("resource", system_resource)
                interfaces = mikrotik.get_eoip_interfaces(type="pop", ip=management_ip, service=service_id)
                print("interfaces", interfaces)
                await ctx.info(f"Fetching L2TP interfaces ...")
                await ctx.report_progress(80, 100)
                l2tp_interfaces = mikrotik.get_l2tp_interfaces(type="pop", ip=management_ip, service=service_id)
                print("l2tp_interfaces", l2tp_interfaces)
                await ctx.info(f"Fetching GRE interfaces ...")
                await ctx.report_progress(90, 100)
                gre_interfaces = mikrotik.get_gre_interfaces(type="pop", ip=management_ip, service=service_id)
                print("gre_interfaces", gre_interfaces)
                await ctx.info(f"Fetching macs learned into bridge ...")
                await ctx.report_progress(100, 100)
                external_macs = mikrotik.get_external_macs_bridge_learned(type="pop", ip=management_ip, service=service_id)
                print("external_macs", external_macs)
                return {
                    "system_resource": system_resource,
                    "eoip_interfaces": interfaces,
                    "l2tp_interfaces": l2tp_interfaces,
                    "gre_interfaces": gre_interfaces, 
                    "external_macs": external_macs
                }
            except Exception as e:
                return f"Error connecting to Mikrotik device: {e}"
                
    return f"Service check in POP for service ID {service_id} is not implemented yet."


@mcp.tool(
    name="ping",
    description="ping to host, parameters host and count",
)
def ping(ip: str, count=5):
    import subprocess
    import platform
    operational_system = platform.system().lower()
    if operational_system == "windows":
        command = ["ping", "-n", str(count), ip]
    else:
        command = ["ping", "-c", str(count), ip]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {
            "sucesso": result.returncode == 0,
            "saida": result.stdout,
            "erro": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"sucesso": False, "erro": "Timeout"}
    

@mcp.tool(
    name="traceroute",
    description="traceroute to host, parameters host",
)
def traceroute(ip: str):
    """
    perform traceroute to host, parameters host
    """
    operational_system = platform.system().lower()
    if operational_system == "windows":
        command = ["tracert", "-d", "-h", "10", "-w", "1000", "-4", ip]
    else:
        command = ["traceroute", "-q", "1", "-w", "1", "-m", "10", ip]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return {
            "sucesso": result.returncode == 0,
            "saida": result.stdout,
            "erro": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"sucesso": False, "erro": "Timeout"}

@mcp.tool(
    name="get_solution",
    description="Get the solution for a service from Quickbase.",
)
def get_solution(service: str) -> str:
    quickbase = Quickbase()
    service_info = quickbase.get_service_information(service)
    if not service_info:
        return f"Service {service} not found."
    return service_info


@mcp.tool(
    name="get_public_ips",
    description="Get the public IPs for a service from Quickbase.",
)
def get_public_ips(service: str) -> dict:
    quickbase = Quickbase()
    public_ips = quickbase.get_vendor_public_ip(service)
    if not public_ips:
        return {"wan_ips": [], "gateway_ips": []}
    return {
        "wan_ips": public_ips.get("wan_ips", []),
        "gateway_ips": public_ips.get("gateway_ips", [])
    }


@mcp.tool(
    name="get_zabbix_service_analysis",
    description="Get Zabbix analysis for a service.",
)
def get_zabbix_service_analysis(service: str, hours: int = 12):
    """
    Get Zabbix analysis for a service.
    """
    zabbix_service = ZabbixPingCheckAction()
    return zabbix_service.zabbix_troubleshooting(service, hours=hours)

@mcp.prompt(title="Troubleshooting cpe")
def troubleshooting(service: str) -> str:
    
    prompt = f"""
    Troubleshooting steps 

    - Check devices avaiable on netbox using igbot tools
    - check ping to cpe 
    - if success, check status of cpe 
    - check nni and check status of service
    - compare mac learned from customer interface on cpe with mac learned from nni interface on nni 
    - return  a summary of all of it

    EX : 
    Verified in network, cpe reacheable, learning external macs from the customer port, in nni device, receiving the 
    mac from for the NNI interface, mac address are transported both sides and service seems to be operative

    evidences : 
    <evidences here>


    now check this service {service}
    
    """
    return prompt

if __name__ == "__main__":
    mcp.run(transport='sse', port=8081, host='0.0.0.0')


    
