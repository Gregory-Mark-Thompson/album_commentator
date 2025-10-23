from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.http import HttpResponse
import requests, json
from django.utils.text import slugify
from .models import Album

# Create your views here.

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
    if not Album.objects.exists():
        print("🚀 First visit - fetching from API!")
        response = requests.get("https://api.discogs.com/database/search?q=The&genre=rock&key=sKHvVGbPNWqXPtxNqkyc&secret=LkehLbliRgkzCOOUbwFGCCXADMqgdMif").json()
        
        for album_data in response["results"]:
            Album.objects.get_or_create(
                master_id=album_data["master_id"],
                defaults={
                    'title': album_data["title"],
                    'year': album_data.get("year", ""),
                    'genre': album_data.get("genre", []),
                    'style': album_data.get("style", []),
                    'cover_image': album_data["cover_image"],
                    'slug': slugify(album_data["title"]),
                }
            )
        print("✅ All albums saved!")
    
    # ALWAYS show from DATABASE (fast!)
    albums = list(Album.objects.all())
    print(f"📊 Showing {len(albums)} albums from database")
    
    return render(request, 'albums/index.html', {'albums': albums})

def album_detail(request, album_slug):
    album = get_object_or_404(Album, slug=album_slug)
    return render(request, 'albums/detail.html', {'album': album})