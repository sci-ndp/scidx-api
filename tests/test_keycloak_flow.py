import os
import pytest
import requests
from dotenv import load_dotenv

# Load environment variables from .env_keycloak file
load_dotenv(os.path.join(os.path.dirname(__file__), '../env_variables/.env_keycloak'))

KEYCLOAK_URL = os.getenv("KEYCLOAK_URL")
KEYCLOAK_ADMIN_USERNAME = os.getenv("KEYCLOAK_ADMIN_USERNAME")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD")
REALM_NAME = os.getenv("REALM_NAME")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USER_ID = os.getenv("USER_ID")
USER_SECRET = os.getenv("USER_SECRET")


# Helper function to get admin token
def get_admin_token():
    url = f"{KEYCLOAK_URL}/realms/master/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": "admin-cli",
        "username": KEYCLOAK_ADMIN_USERNAME,
        "password": KEYCLOAK_ADMIN_PASSWORD
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    print("Response Status Code:", response.status_code)
    print("Response Text:", response.text)
    response.raise_for_status()
    return response.json()["access_token"]


# Helper function to create a user
def create_user(token, username, email):
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "username": username,
        "email": email,
        "enabled": True,
        "credentials": [
            {
                "type": "password",
                "value": USER_SECRET,
                "temporary": False
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.headers["Location"]


# Helper function to delete a user
def delete_user(token, user_id):
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


# Helper function to get user by username
def get_user_by_username(token, username):
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "username": username
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def test_create_user_success():
    token = get_admin_token()
    username = USER_ID
    email = USER_ID
    
    # Create user
    user_url = create_user(token, username, email)
    user_id = user_url.split("/")[-1]
    
    # Verify user exists
    users = get_user_by_username(token, username)
    assert len(users) == 1
    assert users[0]["username"] == username
    
    # Delete user
    delete_user(token, user_id)
    
    # Verify user no longer exists
    users = get_user_by_username(token, username)
    assert len(users) == 0

def test_create_user_failure():
    token = get_admin_token()
    username = USER_ID
    email = "invalid-email"  # Invalid email format
    
    # Try to create user with invalid email
    with pytest.raises(requests.exceptions.HTTPError):
        create_user(token, username, email)

# Run the tests
if __name__ == "__main__":
    pytest.main()
