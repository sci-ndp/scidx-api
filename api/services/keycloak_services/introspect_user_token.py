import requests
from api.config import keycloak_settings

def get_client_token():
    url = f"{keycloak_settings.keycloak_url}/realms/{keycloak_settings.realm_name}/protocol/openid-connect/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": keycloak_settings.client_id,
        "client_secret": keycloak_settings.client_secret
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def introspect_user_token(user_token):
    client_token = get_client_token()  # Use client credentials to get the token

    introspection_url = f"{keycloak_settings.keycloak_url}/realms/" + \
        f"{keycloak_settings.realm_name}/protocol/openid-connect/token/introspect"
    data = {
        "token": user_token,
        "client_id": keycloak_settings.client_id,
        "client_secret": keycloak_settings.client_secret
    }
    headers = {
        "Authorization": f"Bearer {client_token}",  # Use the client token here
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(introspection_url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()
