import base64
import requests
import urllib3
from infra.config import VersaConfig

class VersaConnection:
    """
    This class is a placeholder for Versa device connections.
    It currently does not implement any methods or properties.
    """

    @staticmethod
    def _make_request_api_versa(url):
        """
        Makes a GET request to the Versa API with basic authentication.
        
        :param url: The URL of the Versa API endpoint.
        :param username: The username for basic authentication.
        :param password: The password for basic authentication.
        :return: The response from the API request.
        """

        username = VersaConfig.get_versa_username()
        password = VersaConfig.get_versa_password()
        

        try:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            payload = {}
            headers = {'Authorization': f'Basic {base64.b64encode((username + ":" + password).encode()).decode()}'}
            response = requests.request("GET", url, headers=headers, data=payload, verify=False)
            return response
        except requests.exceptions.RequestException as e:
            return f'Error Troubleshooting: Failed to make request for Versa {e}'

    @staticmethod
    def get_packet_replication_statistics(service, org ):
        """
        Retrieves the replication status from the Versa API.
        
        :param url: The URL of the Versa API endpoint.
        :param username: The username for basic authentication.
        :param password: The password for basic authentication.
        :return: The replication status as a string or an error message.
        """
        VERSA_URL = VersaConfig.get_url()
        try:
            service = service.replace(".", "-")
            url = f"{VERSA_URL}{service}/live?command=orgs/org-services/{org}/sd-wan/policies/sdwan-policy-group/Default-Policy/rules/statistics/extensive/stats-extensive/P2P_Packet_Replication_1/stats"
            response = VersaConnection._make_request_api_versa(url)
            if response.status_code == 200:
                resposta = response.json()
                ListRemoteBranch = []
                output = "Packet Replication Statistics:\n"
                output += " OBS: If none statistics is shown, the packet replication is not performing well or not configured\n"
                output += "{:<15}          {:<15}          {:<15}          {:<15}          {:<15}\n".format(
                    'local', 'remote', 'remote-circuit', 'multi-link-total-tx', 'multi-link-total-rx')
                for field in resposta['collection']['sdwan:stats']:
                    if (field['local-circuit'] != "-" and field['remote-branch'] != "-" and 
                        field['remote-circuit'] != "-" and field['multi-link-total-tx'] != "0" and 
                        field['multi-link-total-rx'] != "0"):
                        output += "{:<15}          {:<15}          {:<15}          {:<15}              {:<15}\n".format(
                            field['local-circuit'], field['remote-branch'], field['remote-circuit'], 
                            field['multi-link-total-tx'], field['multi-link-total-rx'])
                        remote_branch = field['remote-branch']
                        if remote_branch not in ListRemoteBranch:
                            ListRemoteBranch.append(remote_branch)
                return ListRemoteBranch, output
            else:
                return 'Error Troubleshooting: No data retrived'
        except Exception as e:
            return f'Error Troubleshooting: {e}'


    @staticmethod
    def _get_status_interfaces(device):
        URL_INTERFACES_BRIEF = "live?command=interfaces/brief/"
        try:
            URL_VERSA = VersaConfig.get_url()
            url = f"{URL_VERSA}{device}/{URL_INTERFACES_BRIEF}"
            
            response = VersaConnection._make_request_api_versa(url)
            if response.status_code == 200:
                resposta = response.json()
                desired_interfaces = []
                desired_names = ['vni-0/1.0', 'vni-0/0.0', 'vni-0/2.0']
                for interface in resposta['collection']['interfaces:brief']:
                    if interface['name'] in desired_names:
                        desired_interfaces.append(interface)

                # Format as table string
                if not desired_interfaces:
                    return "No desired interfaces found."
                table = "{:<12} {:<18} {:<10} {:<10} {:<18} {:<20}\n".format(
                    "Name", "MAC", "OperStatus", "AdminStatus", "VRF", "IP")
                table += "-"*88 + "\n"
                for iface in desired_interfaces:
                    ip_list = iface.get('address', [])
                    ip_str = ', '.join([ip.get('ip', '') for ip in ip_list])
                    table += "{:<12} {:<18} {:<10} {:<10} {:<18} {:<20}\n".format(
                        iface.get('name', ''),
                        iface.get('mac', ''),
                        iface.get('if-oper-status', ''),
                        iface.get('if-admin-status', ''),
                        iface.get('vrf', ''),
                        ip_str
                    )
                return table
            else:
                return "Error Troubleshooting: There is no data for this service, please check the configuration", response.status_code
        except Exception as e:
            return f'Error Troubleshooting: Falha Get_status_interfaces'

    @staticmethod
    def get_status_sla_paths(service, org, remote_branch):
        """
        Retrieves the SLA path status for a specific remote branch from the Versa API.
        
        :param service: The service name.
        :param org: The organization name.
        :param remote_branch: The remote branch identifier.
        :return: The SLA path status as a list or an error message.
        """
        username = VersaConfig.get_versa_username()
        password = VersaConfig.get_versa_password()
        
        URL_VERSA = VersaConfig.get_url()
        try:
            url = f"{URL_VERSA}{service}/live?command=orgs/org/{org}/sd-wan/sla-monitor/status/{remote_branch}/path-status"
            response = VersaConnection._make_request_api_versa(url)
            if response.status_code == 200:
                resposta = response.json()
                sla_paths = resposta['collection']['sdwan:path-status']
                if not sla_paths:
                    return "No SLA path status found."
                table = ("{:<12} {:<8} {:<14} {:<14} {:<10} {:<10} {:<8} {:<8} {:<8} {:<8} {:<12}\n"
                         .format("PathHandle", "Class", "LocalWAN", "RemoteWAN", "LocalID", "RemoteID", "Conn", "Flaps", "Damp", "DampFlaps", "LastFlapped"))
                table += "-"*110 + "\n"
                for path in sla_paths:
                    table += ("{:<12} {:<8} {:<14} {:<14} {:<10} {:<10} {:<8} {:<8} {:<8} {:<8} {:<12}\n"
                        .format(
                            str(path.get('path-handle', '')),
                            str(path.get('fwd-class', '')),
                            str(path.get('local-wan-link', '')),
                            str(path.get('remote-wan-link', '')),
                            str(path.get('local-wan-link-id', '')),
                            str(path.get('remote-wan-link-id', '')),
                            str(path.get('conn-state', '')),
                            str(path.get('flaps', '')),
                            str(path.get('damp-state', '')),
                            str(path.get('damp-flaps', '')),
                            str(path.get('last-flapped', ''))
                        ))
                return table
            else:
                return 'Error Troubleshooting: No data retrived'

        except Exception as e:
            return f'Error Troubleshooting: Failure : Get_status_sla_paths {e}'
        
    @staticmethod
    def get_replication_config(service, org):
        """
        Retrieves the replication configuration from the Versa API.
        :param service: The service name.
        :param org: The organization name.  
        :return: The replication configuration as a dictionary or an error message.
        """
        URL_VERSA = VersaConfig.get_url()

        try:

            url = f"{URL_VERSA}{service}/live?command=orgs/org-services/{org}/sd-wan/forwarding-profiles/forwarding-profile/Packet_Replication"
            response = VersaConnection._make_request_api_versa(url)
            if response.status_code == 200:
                resposta = response.json()
                output = {
                    "status replication": resposta['sdwan:forwarding-profile']["replication"]["mode"],
                    "status FEC": resposta['sdwan:forwarding-profile']['fec']['sender']['mode']
                }
                return output
            else:
                return None
        except Exception as e:
            return f'Error Troubleshooting: Failure : Get_replication_config {e}'
        


    @staticmethod
    def _identify_patter_circuit(service):
        '''
        This function identifies the pattern of the service 

        pattern_service_raw: ex EMB.5567.D023.PE03 (like quickbase patter)
        pattern_service_versa: ex PRM-5589-A007-Ponta-A (like versa patter)
        pattern_serviceAZ: ex PRM-5589-A007-Ponta-A (like AZ patter)

        If the service match with the pattern, the function returns the service with the versa pattern
        '''

        service_format = service.replace(".", "-")
        return service_format   

    @staticmethod
    def get_troubleshooting(device):
        """
        Retrieves troubleshooting information for a specific service and organization from the Versa API.
        
        :param service: The service name.
        :param org: The organization name.
        :return: The troubleshooting information as a string or an error message.
        """
        URL_VERSA = VersaConfig.get_url()

        result = ""
        service = VersaConnection._identify_patter_circuit(device)
        org = service.split("-")[0]
        if org == "TXB":
            org = "PRM"

        try:
            result += f"Troubleshooting for service: {service}\n"
            result += f"Organization: {org}\n"
            result += "Interfaces Status:\n"
            interfaces_status = VersaConnection._get_status_interfaces(service)
            result += interfaces_status + "\n"
            branch_list, output = VersaConnection.get_packet_replication_statistics(service, org)
            result += "packet replication statistics:\n"
            result += str(output) + "\n"
            result += "packet replication configuration:\n"
            replication_config = VersaConnection.get_replication_config(service, org)
            result += str(replication_config) + "\n"
            result += "SLA Paths Status:\n"
            for branch in branch_list:
                sla_paths_status = VersaConnection.get_status_sla_paths(service, org, branch)
                result += str(sla_paths_status) + "\n"

            return result
        except Exception as e:
            return f"Error Troubleshooting: Failed to get troubleshooting information for Versa {e}"