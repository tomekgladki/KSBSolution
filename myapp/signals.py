from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserPreferences
from myapp.utils.mail import send_email


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    if created:
        UserPreferences.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_preferences(sender, instance, **kwargs):
    instance.preferences.save()


@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:  # Wysłanie maila tylko dla nowo utworzonych użytkowników
        send_email(
            receiver_email=instance.email,
            subject="Welcome to Our Platform!",
            name=instance.username,
            main_content="Thank you for registering on our platform. We hope you enjoy our services!"
        )