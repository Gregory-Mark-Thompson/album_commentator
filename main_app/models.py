from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.utils.text import slugify

class Album(models.Model):
    title = models.CharField(max_length=500)
    year = models.CharField(max_length=20, blank=True)
    genre = ArrayField(models.CharField(max_length=200), blank=True)
    style = ArrayField(models.CharField(max_length=200), blank=True)
    cover_image = models.CharField(max_length=1000)
    master_id = models.IntegerField(unique=True)
    slug = models.SlugField(max_length=500, unique=True, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

