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
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Album.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
class Comment(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(User, through='CommentLike', related_name='liked_comments')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.album.title}"

class CommentLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'comment')