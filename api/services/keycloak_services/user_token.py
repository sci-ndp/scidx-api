import requests

from api.config import keycloak_settings

def get_user_token(username, password):
    url = f"{keycloak_settings.keyloak_url}/realms/" + \
        f"{keycloak_settings.realm_name}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": keycloak_settings.client_id,
        "client_secret": keycloak_settings.client_secret,
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]
