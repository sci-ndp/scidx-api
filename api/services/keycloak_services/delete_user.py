import requests
from api.config import keycloak_settings
from .get_admin_token import get_admin_token

def delete_user(user_id):
    admin_token = get_admin_token()
    url = f"{keycloak_settings.keycloak_url}/admin/realms/" + \
        f"{keycloak_settings.realm_name}/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
