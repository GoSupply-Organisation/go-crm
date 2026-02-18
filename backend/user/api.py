"""API endpoints for user authentication in Go CRM.

This module provides Django Ninja API endpoints for user authentication
including login, logout, registration, and user information retrieval.
"""

from ninja import Router
from ninja.security import django_auth
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from .models import CustomUser as User
from . import schemas


auth_router = Router()


@auth_router.get("/set-csrf-token")
def get_csrf_token(request):
    """Retrieve a CSRF token for the session.

    This endpoint returns a CSRF token that must be included in
    subsequent POST requests to protect against Cross-Site Request
    Forgery attacks.

    Args:
        request: Django request object.

    Returns:
        dict: Dictionary containing the CSRF token.
    """
    return {"csrftoken": get_token(request)}


@auth_router.post("/login")
def login_view(request, payload: schemas.SignInSchema):
    """Authenticate a user and create a session.

    This endpoint authenticates a user using their email and password.
    On successful authentication, a Django session is created.

    Args:
        request: Django request object.
        payload: SignInSchema containing email and password.

    Returns:
        dict: Dictionary with success status (True) on successful login,
              or success status (False) with error message on failure.
    """
    user = authenticate(request, username=payload.email, password=payload.password)
    if user is not None:
        login(request, user)
        return {"success": True}
    return {"success": False, "message": "Invalid credentials"}


@auth_router.post("/logout", auth=django_auth)
def logout_view(request):
    """Log out the authenticated user and destroy the session.

    This endpoint terminates the user's session, effectively logging them out.

    Args:
        request: Django request object with authenticated user.

    Returns:
        dict: Dictionary confirming logout was successful.

    Authentication:
        Requires valid Django session authentication.
    """
    logout(request)
    return {"message": "Logged out"}


@auth_router.get("/user", auth=django_auth)
def user(request):
    """Retrieve information about the currently authenticated user.

    This endpoint returns user information for the authenticated session.

    Args:
        request: Django request object with authenticated user.

    Returns:
        dict: Dictionary containing:
            - username: User's username
            - email: User's email address
            - secret_fact: A motivational quote

    Authentication:
        Requires valid Django session authentication.
    """
    secret_fact = (
        "The moment one gives close attention to any thing, even a blade of grass",
        "it becomes a mysterious, awesome, indescribably magnificent world in itself."
    )
    return {
        "username": request.user.username,
        "email": request.user.email,
        "secret_fact": secret_fact
    }


def register(request, payload: schemas.SignInSchema):
    """Register a new user account.

    This endpoint creates a new user account with the provided credentials.
    The username is automatically set to the email address.

    Args:
        request: Django request object.
        payload: SignInSchema containing email and password.

    Returns:
        dict: Dictionary with success message on successful registration,
              or error details if registration fails.
    """
    try:
        User.objects.create_user(username=payload.email, email=payload.email, password=payload.password)
        return {"success": "User registered successfully"}
    except Exception as e:
        return {"error": str(e)}


# @auth_router.post("/forgot-password")
# def forgot_password(request, payload: schemas.ForgotPasswordSchema):
#     """Initiate password reset process.
#
#     This endpoint sends a password reset link to the user's email address.
#     (Currently commented out - requires email configuration)
#
#     Args:
#         request: Django request object.
#         payload: ForgotPasswordSchema containing email address.
#
#     Returns:
#         dict: Dictionary with success message or error details.
#     """
#     try:
#         user = User.objects.get(email=payload.email)
#         # Here you would normally send an email with a reset link
#         return {"success": f"Password reset link sent to {payload.email}"}
#     except User.DoesNotExist:
#         return {"error": "Email not found"}
