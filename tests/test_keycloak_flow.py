import os
import time
import pytest
import requests
from dotenv import load_dotenv

from api.services.keycloak_services.get_admin_token import get_admin_token
from api.services.keycloak_services.create_user import create_user
from api.services.keycloak_services.user_token import get_user_token
from api.services.keycloak_services.introspect_user_token import introspect_user_token
from api.services.keycloak_services.get_user_by_username import get_user_by_username
from api.services.keycloak_services.delete_user import delete_user

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


def test_create_user_success():
    admin_token = get_admin_token()
    print("Admin Token:", admin_token)
    username = USER_ID
    email = USER_ID
    password = USER_SECRET
    
    # Check if user already exists and delete it
    existing_users = get_user_by_username(username)
    if existing_users:
        user_id = existing_users[0]["id"]
        print(f"User {username} already exists with ID {user_id}. Deleting existing user.")
        delete_user(user_id)
        # Verify the user is deleted before proceeding
        users_after_deletion = get_user_by_username(username)
        assert len(users_after_deletion) == 0

    # Wait for a short period to ensure the deletion propagates
    time.sleep(5)

    # Create user
    user_id = create_user(username, email, password)
    print(f"User ID: {user_id}")

    # Verify user exists and validate token
    try:
        print(f"Getting user token for username: {username} and password: {password}")
        user_token = get_user_token(username, password)
        print("User Token:", user_token)
        user_info = introspect_user_token(user_token)
        assert user_info["active"]
        assert user_info["preferred_username"] == username
    except requests.exceptions.HTTPError as e:
        print(f"Error getting user token or introspecting: {e}")
        print("Request Headers:", e.request.headers)
        print("Request Body:", e.request.body)
        print("Response Headers:", e.response.headers)
        print("Response Text:", e.response.text)
        raise e
    
    # Delete user
    delete_user(user_id)
    
    # Verify user no longer exists
    users = get_user_by_username(username)
    assert len(users) == 0


# Run the tests
if __name__ == "__main__":
    pytest.main()
