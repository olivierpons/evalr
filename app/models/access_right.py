from django.contrib.auth.models import User
from django.db import models


class AccessRight(models.Model):
    A_R = 1
    A_W = 2
    A_RW = A_R | A_W
    ACCESS_RIGHTS = {A_R: {'long': 'Read', 'short': 'R'},
                     A_W: {'long': 'Write', 'short': 'W'},
                     A_RW: {'long': 'Read/Write', 'short': 'RW'}, }
    table_name = models.CharField(max_length=50, default=None, blank=True,
                                  db_index=True)
    row_id = models.PositiveIntegerField(default=None, blank=True, )
    user = models.ForeignKey(User, blank=False, on_delete=models.CASCADE)
    right = models.IntegerField(
        choices=[(idx, '{} ({})'.format(desc['long'], desc['short']))
                 for idx, desc in ACCESS_RIGHTS.items()],
        default=A_R)
