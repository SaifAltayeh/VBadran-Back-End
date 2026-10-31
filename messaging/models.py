from django.conf import settings
from django.db import models


class Conversation(models.Model):
    client = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="conversations", on_delete=models.CASCADE)
    subject = models.CharField(max_length=160, default="Coach messages")
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.email} · {self.subject}"


class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="sent_messages",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    body = models.TextField()
    attachment = models.FileField(upload_to="messages/", blank=True)
    is_coach = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.body[:48]
