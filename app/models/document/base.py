from django.db import models

from app.models.document.state import DocumentState
from core.models.base import BaseModel


class Document(BaseModel):
    state = models.ForeignKey(DocumentState, on_delete=models.CASCADE,
                              default=None, blank=False, null=True)

    def __str__(self):
        if self.state is None:
            return _("no state")
        return f'{self.state.full_chain()}'
