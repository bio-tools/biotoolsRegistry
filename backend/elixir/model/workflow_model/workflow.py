from django.db import models

# table to hold workflow data
class Workflow(models.Model):
    textId = models.CharField(max_length=50) 
    description = models.TextField(blank=True, null=True)
    sourceURL = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="workflows/", blank=False, null=False, width_field="image_width", height_field="image_height")
    image_width = models.IntegerField(default=0)
    image_height = models.IntegerField(default=0)