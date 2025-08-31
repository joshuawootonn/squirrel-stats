"""
Authentication API views for user registration, login, logout, and password reset.
"""

import logging

import requests
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

logger = logging.getLogger(__name__)


def send_mailpace_email(to_email, subject, text_body, html_body=None):
    """
    Send email using MailPace API.

    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        text_body (str): Plain text email body
        html_body (str, optional): HTML email body

    Returns:
        bool: True if email sent successfully, False otherwise

    Raises:
        Exception: If API call fails
    """
    if not settings.MAILPACE_API_KEY:
        raise Exception("MAILPACE_API_KEY not configured")

    payload = {
        "from": settings.DEFAULT_FROM_EMAIL,
        "to": to_email,
        "subject": subject,
        "textbody": text_body,
    }

    if html_body:
        payload["htmlbody"] = html_body

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "MailPace-Server-Token": settings.MAILPACE_API_KEY,
    }

    logger.debug(f"Sending email to {to_email} via MailPace API")

    response = requests.post(settings.MAILPACE_API_URL, json=payload, headers=headers, timeout=30)

    if response.status_code == 200:
        logger.debug("Email sent successfully via MailPace API")
        return True
    else:
        error_msg = f"MailPace API error: {response.status_code} - {response.text}"
        logger.error(error_msg)
        raise Exception(error_msg)


@api_view(["POST"])
@permission_classes([AllowAny])
def signup_view(request):
    """
    Create a new user account.

    Expected payload:
    {
        "email": "string",
        "password": "string"
    }
    """
    try:
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        # Basic validation
        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "Email already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create user - use email as username since Django requires a username
        user = User.objects.create_user(username=email, email=email, password=password)

        # Log the user in
        login(request, user)

        return Response(
            {
                "message": "Account created successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    except Exception as e:
        logger.error(f"Signup error: {e}")
        return Response(
            {"error": "Registration failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    """
    Authenticate user and create session.

    Expected payload:
    {
        "email": "string",
        "password": "string"
    }
    """
    try:
        email = request.data.get("email", "").strip()
        password = request.data.get("password", "")

        if not email or not password:
            return Response(
                {"error": "Email and password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate user using email as username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return Response(
                {
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                    },
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

    except Exception as e:
        logger.error(f"Login error: {e}")
        return Response(
            {"error": "Login failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
def logout_view(request):
    """
    Logout user and destroy session.
    """
    try:
        logout(request)
        return Response(
            {"message": "Logout successful"},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return Response(
            {"error": "Logout failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def forgot_password_view(request):
    """
    Send password reset email.

    Expected payload:
    {
        "email": "string"
    }
    """
    try:
        email = request.data.get("email", "").strip()

        if not email:
            return Response(
                {"error": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response(
                {"message": "If an account with that email exists, a password reset link has been sent"},
                status=status.HTTP_200_OK,
            )

        # Generate password reset token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Create reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password?uid={uid}&token={token}"

        # Send email via MailPace API
        subject = "Password Reset - Squirrel Stats"
        text_body = f"""Hi {user.username},

You requested a password reset for your Squirrel Stats account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this reset, please ignore this email.

Best regards,
The Squirrel Stats Team"""

        html_body = f"""
        <html>
        <body>
            <h2>Password Reset Request</h2>
            <p>Hi {user.username},</p>
            <p>You requested a password reset for your Squirrel Stats account.</p>
            <p><a href="{reset_url}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">Reset Your Password</a></p>
            <p>Or copy and paste this link into your browser:</p>
            <p><a href="{reset_url}">{reset_url}</a></p>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't request this reset, please ignore this email.</p>
            <p>Best regards,<br>The Squirrel Stats Team</p>
        </body>
        </html>
        """

        send_mailpace_email(user.email, subject, text_body, html_body)

        return Response(
            {"message": "If an account with that email exists, a password reset link has been sent"},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Password reset error: {e}")
        return Response(
            {"error": "Password reset failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def reset_password_view(request):
    """
    Reset password using token from email.

    Expected payload:
    {
        "uid": "string",
        "token": "string",
        "new_password": "string"
    }
    """
    try:
        uid = request.data.get("uid", "")
        token = request.data.get("token", "")
        new_password = request.data.get("new_password", "")

        if not uid or not token or not new_password:
            return Response(
                {"error": "UID, token, and new password are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Decode user ID
            user_id = urlsafe_base64_decode(uid).decode()
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"error": "Invalid reset link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Verify token
        if not default_token_generator.check_token(user, token):
            return Response(
                {"error": "Invalid or expired reset link"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Set new password
        user.set_password(new_password)
        user.save()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Password reset confirmation error: {e}")
        return Response(
            {"error": "Password reset failed"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def user_info_view(request):
    """
    Get current user information.
    """
    try:
        if request.user.is_authenticated:
            return Response(
                {
                    "user": {
                        "id": request.user.id,
                        "username": request.user.username,
                        "email": request.user.email,
                    }
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"error": "Not authenticated"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
    except Exception as e:
        logger.error(f"User info error: {e}")
        return Response(
            {"error": "Failed to get user info"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
