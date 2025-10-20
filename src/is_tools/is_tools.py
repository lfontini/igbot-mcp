from infra.config import  IsToolsConfig
import requests
from typing import Optional
import json 
import re
class IsTools:
    """
    Get data from is_tools application
    """

    @staticmethod
    def  get_equipment(name: str) -> Optional[str]:
        """
        Retrieves the equipment name associated with a given NNI (e.g., 'EMB.5571.N001')
        by querying the IS Tools layout API.

        The function searches for equipment names that contain specific patterns
        (e.g., 'ASW' or 'LER') in the response.

        Args:
            nni (str): The NNI identifier string.

        Returns:
            str or None: The first matching equipment name found containing 'ASW' or 'LER',
            or None if no match is found or the request fails.

        Notes:
            - Make sure to provide valid authentication cookies if required.
            - This function assumes the API response is either a list of strings
            or a dictionary containing the equipment data as strings.
        """
        url = 'https://is-tools.master.ignetworks.com/review_layout_result'
        headers = {
            'Content-Type': 'application/json'
        }

        payload = {'value': name}

        try:

            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()
            data = response.json()


            equipment_set = set()
            pattern = re.compile(r'\b[A-Z0-9]{3,4}-(?:ASW|LER)\d*\b', re.IGNORECASE)

            if isinstance(data, list):
                for item in data:
                    matches = pattern.findall(item)
                    equipment_set.update(matches)

            elif isinstance(data, dict):
                text = json.dumps(data)
                matches = pattern.findall(text)
                equipment_set.update(matches)

            return list(equipment_set)[0] if equipment_set else None

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return None
        except ValueError as e:
            print(f"Response parsing error: {e}")
            return None
        



        
 
 


    


   