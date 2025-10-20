import requests
from infra.config import QuickbaseConfig
import re
 
class Quickbase:
    def __init__(self):
        self.api_token = QuickbaseConfig.get_quickbase_api_token()
        self.hostname = QuickbaseConfig.get_quickbase_hostname()
        

    def _make_request(self, body):
        headers = {
            'QB-Realm-Hostname': self.hostname,
            'Authorization': self.api_token
        }
        response = requests.post(
            'https://api.quickbase.com/v1/records/query',
            headers=headers,
            json=body
        )
        return response.json()

    def Get_cross_connect(self, service_id):
        '''
        Returns the xconnect of the input service.
        '''

        body = {"from": "bjvepvncz", "select": [], "where": "{8.CT." + f"'{service_id}'" + "}"}
        response =  self._make_request(body)
        
        try:
            if response["data"][0]['9']["value"]:
                cross = response["data"][0]['9']["value"]
                return cross
            else:
                return None
        except:
            return  f'Field data empty', response["data"]
 

    def Get_equipment(self, nni):
        """
        Returns the first equipment name found containing 'ASW' or 'LER' in the NNI.
        """

        body = {"from": "bmdkybxpd", "select": [39, 41], "where": "{41.CT." + f"'{nni}'" + "}OR{36.CT." + f"'{nni}'" + "}"}
        #{"from": "bmdkybxpd", "select": [39, 41 ], "where": "{41.CT.'EMB.5571.N001'}"}
        response = self._make_request(body)
        
        try:
            if response["data"][0]['39']['value']:
                device = response["data"][0]['39']['value']
                return device
            else:
                return None
        except:
            print(response["data"])
            return None
        

    def get_NNI(self , service_id):
        """
        
        returns the NNI of the input service_id.

        """
        body = {"from": "bmeeuqk9d", "select": [21], "where": "{7.CT." + f"'{service_id}'" + "}"}
        response =  self._make_request(body)
        if response['data']:
            NNI = response['data'][0]["21"]["value"]
            return NNI
        else:
            return None

    def get_service_information(self, service_id):
        """
        Returns the service information for the given service_id.
        """
        body = {"from": "bfwgbisz4", "select": [766 , 838], "where": "{7.CT." + f"'{service_id}'" + "}"}
        response = self._make_request(body)
        try: 
            if response["data"][0]:
                solution = response["data"][0]['838']['value']
                offnetoronnet = response["data"][0]['766']['value']
                return {"solution": solution ,"offnetoronnet":offnetoronnet}
            else: 
                return response
        except Exception as error:
                 return(False , error)
        
    def get_vendor_public_ip(self, service_id):
        """
        Returns the vendor public IP for the given service_id.
        """
        body = {"from": "bkr26d56f", "select": [306, 309], "where": "{234.CT." + f"'{service_id}'" + "}"}

        response = self._make_request(body)
        if response['data']:
            wan_ips, gateway_ips = self.extract_ips(response['data'])
            if wan_ips and gateway_ips:
                return {"wan_ips": wan_ips, "gateway_ips": gateway_ips}
            else:
                return {"wan_ips": [], "gateway_ips": []}
        else:
            return {"wan_ips": [], "gateway_ips": []}
        

    def extract_ips(self, data):
        wan_ips = []
        gateway_ips = []

        for entry in data:
            wan_value = entry.get('306', {}).get('value')
            gateway_value = entry.get('309', {}).get('value')

            if wan_value:
                wan_ip = self.extract_ip_from_cidr(wan_value.strip())
                if wan_ip:
                    wan_ips.append(wan_ip)

            if gateway_value:
                gateway_ip = self.extract_ip_from_cidr(gateway_value.strip())
                if gateway_ip:
                    gateway_ips.append(gateway_ip)
        return wan_ips, gateway_ips

    def extract_ip_from_cidr(self, cidr):
        ip_regex = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        match = re.match(ip_regex, cidr)
        if match:
            return match.group(1)
        return None
