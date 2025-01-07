from django.db import models

class Memory(models.Model):
    workspace_slug = models.CharField(max_length=255)
    summary = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(
        max_length=50,
        choices=[("pending", "Pending"), ("verified", "Verified")],
        default="pending",
    )

    def __str__(self):
        return f"{self.workspace_slug} - {self.verification_status} - {self.date_created}"
