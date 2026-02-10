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
    return {"csrftoken": get_token(request)}
 
@auth_router.post("/login")
def login_view(request, payload: schemas.SignInSchema):
    user = authenticate(request, username=payload.email, password=payload.password)
    if user is not None:
        login(request, user)
        return {"success": True}
    return {"success": False, "message": "Invalid credentials"}
 
@auth_router.post("/logout", auth=django_auth)
def logout_view(request):
    logout(request)
    return {"message": "Logged out"}
 
@auth_router.get("/user", auth=django_auth)
def user(request):
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
    try:
        User.objects.create_user(username=payload.email, email=payload.email, password=payload.password)
        return {"success": "User registered successfully"}
    except Exception as e:
        return {"error": str(e)}
    
# @auth_router.post("/forgot-password,")
# def forgot_password(request, payload: schemas.ForgotPasswordSchema):
#     try:
#         user = User.objects.get(email=payload.email)
#         # Here you would normally send an email with a reset link
#         return {"success": f"Password reset link sent to {payload.email}"}
#     except User.DoesNotExist:
#         return {"error": "Email not found"}
 