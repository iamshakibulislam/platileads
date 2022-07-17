from django.db import models
from users.models import *

class lead_file(models.Model):
    uploaded_by = models.ForeignKey(User,on_delete=models.CASCADE)
    uploaded_file = models.FileField(upload_to='uploads/',null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.uploaded_by.email
