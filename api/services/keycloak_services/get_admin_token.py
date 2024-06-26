import requests

from api.config import keycloak_settings


def get_admin_token():
    url = f"{keycloak_settings.keycloak_url}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": keycloak_settings.keycloak_admin_username,
        "password": keycloak_settings.keycloak_admin_password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    print("Response Status Code (Admin Token):", response.status_code)
    print("Response Text (Admin Token):", response.text)
    response.raise_for_status()
    return response.json()["access_token"]
