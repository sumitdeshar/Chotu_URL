from __future__ import annotations
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import User

class UserService:
    
    @staticmethod
    def create_user_account(email: str, password: str, username: str | None = None, **extra_fields) -> User:
        """
        Executes the entire orchestration of setting up a new user in the platform.
        """
        # Clean data variables
        clean_email = email.lower().strip()
        final_username = username or clean_email.split('@')[0]

        # Enforce atomic operations (If profile creation fails, the user is rolled back!)
        with transaction.atomic():
            
            if User.objects.filter(email=clean_email).exists():
                raise ValidationError("This email is already registered in our system.")

            user = User.objects.create_user(
                username=final_username,
                email=clean_email,
                password=password,      
                **extra_fields
            )


        # Asynchronous triggers (Safe to run because transaction.atomic successfully committed)
        # transaction.on_commit(lambda: send_welcome_email.delay(user.id))

        return user