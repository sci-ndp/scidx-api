import requests

from api.config import keycloak_settings
from .get_admin_token import get_admin_token

def introspect_user_token(user_token):
    admin_token = get_admin_token()

    introspection_url = f"{keycloak_settings.keycloak_url}/realms/" + \
        f"{keycloak_settings.realm_name}/protocol/openid-connect/token/introspect"
    data = {
        "token": user_token,
        "client_id": keycloak_settings.client_id,
        "client_secret": keycloak_settings.client_secret
    }
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(introspection_url, data=data, headers=headers)
    print("Introspection Response Status Code:", response.status_code)
    print("Introspection Response Text:", response.text)
    response.raise_for_status()
    return response.json()
