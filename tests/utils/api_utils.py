from typing import List, Dict, Any, Optional
import requests

def call_api(api_session, who: str,method: str, url: str, json_data: Optional[Any] = None) -> requests.Response:
    """Make an API request."""
    response = api_session.request(
            method=method,
            url=url,
            json=json_data)
        # proxies=PROXIES)
        # verify=not bool(PROXIES))  # Disable verify if using proxy
    #assert response.status_code == 200,f"calling to {who} return {response.status_code} "
    return response