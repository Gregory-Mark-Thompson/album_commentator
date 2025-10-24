from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
import os
import requests
from urllib.parse import quote
from django.utils.text import slugify
from django.contrib import messages
from .models import Album, Comment, CommentLike
from .forms import CommentForm
from django.views.decorators.http import require_POST

class Home(LoginView):
    template_name = 'home.html'

def about(request):
    return render(request, 'about.html')

def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
        else:
            error_message = 'Invalid sign-up: please try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

def album_index(request):
    consumer_key = os.getenv('DISCOGS_CONSUMER_KEY')
    consumer_secret = os.getenv('DISCOGS_CONSUMER_SECRET')
    search_type = request.GET.get('type', '')
    search_query = request.GET.get('q', '').strip()
    albums = []

    if not Album.objects.exists() and not search_type:
        url = f"https://api.discogs.com/database/search?q={quote('The')}&genre={quote('rock')}&key={consumer_key}&secret={consumer_secret}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            for album_data in response.json().get("results", []):
                Album.objects.update_or_create(
                    master_id=album_data["master_id"],
                    defaults={
                        'title': album_data["title"],
                        'year': album_data.get("year", ""),
                        'genre': album_data.get("genre", []),
                        'style': album_data.get("style", []),
                        'cover_image': album_data["cover_image"],
                    }
                )
        except requests.RequestException as e:
            messages.error(request, f"API error: {str(e)}")
        albums = list(Album.objects.all())


    elif search_type and search_query:
        param = 'genre' if search_type == 'genre' else 'style'
        url = f"https://api.discogs.com/database/search?{param}={quote(search_query)}&type=release&per_page=50&key={consumer_key}&secret={consumer_secret}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            for album_data in response.json().get("results", []):
                Album.objects.update_or_create(
                    master_id=album_data["master_id"],
                    defaults={
                        'title': album_data["title"],
                        'year': album_data.get("year", ""),
                        'genre': album_data.get("genre", []),
                        'style': album_data.get("style", []),
                        'cover_image': album_data["cover_image"],
                    }
                )
            albums = Album.objects.filter(**{f"{param}__contains": [search_query]})
        except requests.RequestException as e:
            messages.error(request, f"API error: {str(e)}")
    else:
        albums = Album.objects.all()

    context = {
        'albums': albums,
        'search_type': search_type,
        'search_query': search_query,
    }
    return render(request, 'albums/index.html', context)

def album_detail(request, album_slug):
    album = get_object_or_404(Album, slug=album_slug)
    return render(request, 'albums/detail.html', {'album': album})

@login_required
def comment_create(request, album_slug):
    album = get_object_or_404(Album, slug=album_slug)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.album = album
            comment.user = request.user
            comment.save()
            return redirect('album_detail', album_slug=album_slug)
    else:
        form = CommentForm()
    return render(request, 'comments/form.html', {'form': form, 'album': album})

@login_required
def comment_edit(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user != request.user:
        return redirect('album_detail', album_slug=comment.album.slug)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('album_detail', album_slug=comment.album.slug)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'comments/form.html', {'form': form, 'album': comment.album})

@login_required
def comment_delete(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user:
        comment.delete()
    return redirect('album_detail', album_slug=comment.album.slug)

@login_required
@require_POST
def toggle_like(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    user = request.user
    if user == comment.user:
        return JsonResponse({
            'error': 'You cannot like your own comment',
            'liked': False,
            'like_count': comment.likes.count()
        }, status=403)
    like_exists = CommentLike.objects.filter(user=user, comment=comment).exists()
    if like_exists:
        CommentLike.objects.filter(user=user, comment=comment).delete()
        liked = False
    else:
        CommentLike.objects.create(user=user, comment=comment)
        liked = True
    return JsonResponse({
        'liked': liked,
        'like_count': comment.likes.count()
    })