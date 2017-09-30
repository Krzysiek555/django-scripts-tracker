from django.db import models


class AppliedManagementScripts(models.Model):
    """ Model for tracking management scripts execution """
    file_path = models.CharField(max_length=500)
    file_hash = models.CharField(max_length=100)
    applied_date = models.DateTimeField(auto_now_add=True)