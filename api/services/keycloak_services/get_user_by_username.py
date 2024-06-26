import requests
from api.config import keycloak_settings
from .get_admin_token import get_admin_token

def get_user_by_username(username):
    admin_token = get_admin_token()
    url = f"{keycloak_settings.keycloak_url}/admin/realms/" + \
        "{keycloak_settings.realm_name}/users"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    params = {
        "username": username
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()
