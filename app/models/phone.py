from django.db import models

from app.models.base import BaseModel


class Phone(BaseModel):
    phone = models.CharField(max_length=30, blank=True, null=True)
