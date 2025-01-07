from django.db import models

class Log(models.Model):
    log_text = models.TextField()
    machine = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    committed = models.BooleanField(default=False)  # New field to track commitment status

    def __str__(self):
        return f"Log for {self.machine} on {self.created_at}"

