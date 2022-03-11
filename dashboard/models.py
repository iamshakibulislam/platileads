from django.db import models
from users.models import User

def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.xlsx', '.xls','csv']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')


class file_uploader(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/',validators=[validate_file_extension])


    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name