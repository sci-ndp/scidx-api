from api.config import keycloak_settings
from .introspect_user_token import introspect_user_token

def get_user_info_from_token(token):
    """
    This function is used to get the details of a user from a token

    Parameters
    ----------
    token : str
        token of the user

    Returns
    -------
    user_info : dict
        details of the user
    """
    try:
        user_keycloak=introspect_user_token(token)
        # If the response is successful
        # Extract the relevant information from the response
        user_info = {}
        user_info['id'] = user_keycloak.get('sub')
        user_info['username'] = user_keycloak.get('preferred_username')
        user_info['email'] = user_keycloak.get('profile email')
        user_info['first_name'] = user_keycloak.get('given_name')
        user_info['last_name'] = user_keycloak.get('family_name')
        return user_info
    except Exception as e:
        return {'error': 'Could not validate credentials'}
