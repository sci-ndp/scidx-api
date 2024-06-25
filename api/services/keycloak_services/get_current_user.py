from fastapi import Depends, HTTPException, status
from typing import Optional

from . import oauth2_scheme
from .get_user_info_from_token import get_user_info_from_token


def get_current_user(token: Optional[str] = Depends(oauth2_scheme)):
    """
    The get_current_user function retrieves the current user's details using a
     provided token.
    If the token is valid, the function returns the user details as a
     dictionary.
    If the credentials cannot be validated, a 401 Unauthorized exception is
     raised.
    In case of other errors, a 500 Internal Server Error exception is raised.
    """
    # Define an exception to be raised if the credentials cannot be validated
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    print('token:', token)
    try:
        # Get the user information using the provided token
        user = get_user_info_from_token(token)
    except:
        # Raise the credentials exception if an error occurs while getting the
        # user information
        raise credentials_exception

    # Check if the user information contains an error
    if 'error' in user:
        if user['error'] == 'Could not validate credentials':
            # Raise the credentials exception if the error is due to invalid
            # credentials
            raise credentials_exception
        else:
            # Raise a 500 Internal Server Error exception for other errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Server Error - Please try to authenticate again",
                headers={"WWW-Authenticate": "Bearer"},
            )
    else:
        # Return the user details if there are no errors
        return user
