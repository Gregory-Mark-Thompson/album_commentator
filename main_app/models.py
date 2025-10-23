from django.db import models
from django.urls import reverse
from datetime import date
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField

class Album(models.Model):
    title = models.CharField()
    year = models.CharField()
    genre = ArrayField(models.CharField())
    style = ArrayField(models.CharField())
    cover_image = models.CharField()
    master_id = models.IntegerField()



# Create your models here.