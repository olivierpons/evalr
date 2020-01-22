from django.db import models

from app.models.base import BaseModel


class PhoneType(BaseModel):
    name = models.CharField(max_length=200, blank=True, null=True)
