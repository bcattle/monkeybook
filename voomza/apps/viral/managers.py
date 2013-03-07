from django.db import models

class InviteRequestSentManager(models.Manager):
    def outstanding_invites(self):
        return self.filter(accepted_at__isnull=True)
