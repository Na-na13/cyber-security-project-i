from django.db import models

# Create your models here.

class Message(models.Model):
    class Meta:
        db_table = "messages"
    messagetext = models.TextField()
    sender = models.CharField(max_length=150)
    receiver = models.CharField(max_length=150)
