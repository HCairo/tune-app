import requests
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlencode

def home(request):
    return render(request, 'tune/home.html')

def login(request):
    access_token = request.session.get('access_token')
    if access_token:
        return redirect('user')
    
    scope = "user-read-private user-read-email user-top-read"
    params = {
        "response_type": "code",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "redirect_uri": "http://localhost:8000/tune/callback/",
        "scope": scope,
    }
    url = f"https://accounts.spotify.com/authorize?{urlencode(params)}"
    return redirect(url)

def logout(request):
    request.session.pop('access_token', None)
    return redirect(home)

def callback(request):
    # Étape 2 : Gérer le callback et échanger le code contre un token
    code = request.GET.get("code")
    token_url = "https://accounts.spotify.com/api/token"
    
    # Étape 3 : Envoyer une requête POST pour obtenir le token d'accès
    response = requests.post(token_url, data={
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": "http://localhost:8000/tune/callback/",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "client_secret": settings.SPOTIFY_CLIENT_SECRET,
    })

    token_data = response.json()
    access_token = token_data.get("access_token")

    # Stocker le token dans la session ou un modèle
    request.session['access_token'] = access_token
    return redirect('home')

import requests
from django.shortcuts import render
from django.conf import settings

import requests
from django.shortcuts import render, redirect
from django.conf import settings

def user(request):
    access_token = request.session.get('access_token')
    
    if not access_token:
        return redirect('login')
    
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    
    # Récupérer les informations de profil de l'utilisateur
    profile_response = requests.get("https://api.spotify.com/v1/me", headers=headers)
    user_data = profile_response.json() if profile_response.status_code == 200 else None
    
    # Récupérer les artistes les plus écoutés
    top_artists_response = requests.get(
        "https://api.spotify.com/v1/me/top/artists?limit=5&time_range=long_term", headers=headers
    )
    top_artists_data = top_artists_response.json().get('items', []) if top_artists_response.status_code == 200 else []

    # Récupérer les titres les plus écoutés
    top_tracks_response = requests.get(
        "https://api.spotify.com/v1/me/top/tracks?limit=5&time_range=long_term", headers=headers
    )
    top_tracks_data = top_tracks_response.json().get('items', []) if top_tracks_response.status_code == 200 else []

    # Extraire et dédupliquer les genres
    genres = [genre for artist in top_artists_data for genre in artist.get('genres', [])]
    top_genres = list(set(genres))  # Dédupliquer les genres
    
    context = {
        'user_data': user_data,
        'top_artists': top_artists_data,
        'top_tracks': top_tracks_data,
        'top_genres': top_genres
    }
    
    return render(request, 'tune/user.html', context)