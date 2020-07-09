from django.db import models
import uuid

# Create your models here.
class SearchSequence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=128, db_index=True)
    search_sequence = models.TextField()
    created = models.DateTimeField('Created date', db_index=True)
    status = models.CharField(max_length=32)
    result = models.TextField()