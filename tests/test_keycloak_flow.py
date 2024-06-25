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
    print("Response Status Code (Admin Token):", response.status_code)
    print("Response Text (Admin Token):", response.text)
    response.raise_for_status()
    return response.json()["access_token"]

# Helper function to get user token
def get_user_token(username, password):
    url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]


# Helper function to introspect user token
def introspect_user_token(admin_token, user_token):
    introspection_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token/introspect"
    data = {
        "token": user_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
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

# Helper function to create a user
def create_user(admin_token, username, email):
    existing_users = get_user_by_username(admin_token, username)
    if existing_users:
        user_id = existing_users[0]["id"]
        print(f"User {username} already exists with ID {user_id}.")
        return user_id
    
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
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
                "value": USER_SECRET,
                "temporary": False
            }
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    print("Create User Response Status Code:", response.status_code)
    print("Create User Response Text:", response.text)
    response.raise_for_status()
    return response.headers["Location"].split("/")[-1]

# Helper function to delete a user
def delete_user(admin_token, user_id):
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/{user_id}"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()

# Helper function to get user by username
def get_user_by_username(admin_token, username):
    url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    params = {
        "username": username
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def test_create_user_success():
    admin_token = get_admin_token()
    username = USER_ID
    email = USER_ID
    
    # Create user
    user_id = create_user(admin_token, username, email)
    
    # Verify user exists and validate token
    try:
        user_token = get_user_token(username, USER_SECRET)
        user_info = introspect_user_token(admin_token, user_token)
        assert user_info["active"]
        assert user_info["preferred_username"] == username
    except requests.exceptions.HTTPError as e:
        print(f"Error getting user token or introspecting: {e}")
        raise e
    
    # Delete user
    delete_user(admin_token, user_id)
    
    # Verify user no longer exists
    users = get_user_by_username(admin_token, username)
    assert len(users) == 0

def test_create_user_failure():
    admin_token = get_admin_token()
    username = USER_ID
    email = "invalid-email"  # Invalid email format
    
    # Try to create user with invalid email
    with pytest.raises(requests.exceptions.HTTPError):
        create_user(admin_token, username, email)

# Run the tests
if __name__ == "__main__":
    pytest.main()
