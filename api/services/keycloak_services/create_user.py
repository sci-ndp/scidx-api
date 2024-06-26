import requests
from api.config import keycloak_settings
from .get_admin_token import get_admin_token
from .get_user_by_username import get_user_by_username


def create_user(username, email, password):
    admin_token = get_admin_token()
    existing_users = get_user_by_username(username)
    if existing_users:
        user_id = existing_users[0]["id"]
        print(f"User {username} already exists with ID {user_id}.")
        return user_id
    
    url = f"{keycloak_settings.keycloak_url}/admin/realms/" + \
        f"{keycloak_settings.realm_name}/users"
    headers = {
        "Authorization": f"Bearer {admin_token}",
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "email": email,
        "enabled": True,
        "emailVerified": True,
        "credentials": [
            {
                "type": "password",
                "value": password,
                "temporary": False
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    print("Create User Response Status Code:", response.status_code)
    print("Create User Response Text:", response.text)
    response.raise_for_status()
    return response.headers["Location"].split("/")[-1]
