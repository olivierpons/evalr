from django.db import models

from app.models.base import BaseModel
from app.models.document.state import DocumentState


class Document(BaseModel):
    state = models.ForeignKey(DocumentState, on_delete=models.CASCADE,
                              default=None, blank=False, null=True)

    def __str__(self):
        if self.state is None:
            return _("no state")
        return f'{self.state.full_chain()}'
