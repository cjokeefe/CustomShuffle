from django.shortcuts import render
from django.http import HttpResponse
from django.core.cache import caches
import spotipy
import uuid
import os
import json

# Create your views here.

def index(request):
	if not 'id' in request.session:
		request.session['id'] = str(uuid.uuid4())

	username=str(request.session['id'])

	auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-public user-top-read', username=username, show_dialog=True)

	if request.GET.get('code'):
		code = request.GET.get('code')
		print("About to get_access_token")
		auth_manager.get_access_token(code)
		print("Just did get_access_token")

	if not auth_manager.get_cached_token():
		auth_url=auth_manager.get_authorize_url()
		return HttpResponse(f'<h2><a href="{auth_url}">Sign in</a></h2>')

	spotify = spotipy.Spotify(auth_manager=auth_manager)


	#return HttpResponse(f'<h2>Welcome {spotify.me()["display_name"]}</h2>')

	name = spotify.me()["display_name"]
	toptracks = spotify.current_user_top_tracks(limit=5)['items']

	toptracklist = []

	for track in toptracks:
		toptracklist.append(track['name'])

	context = {
		'name': name,
		'toptracks': toptracklist,
	}

	print(json.dumps(toptracks, sort_keys=True, indent=4))
	
	#return HttpResponse("Hi")
	return render(request, 'shuffle/home.html', context)


def callback(request):
	cache_path = caches_folder + str(request.session['id'])
	auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
	if request.GET['code']:
		code = request.GET['code']
		auth_manager.get_access_token(code)

	spotify = spotipy.Spotify(auth_manager=auth_manager)

	#return HttpResponse("code:" + code)
	return HttpResponse(f'<h2>Welcome {spotify.me()["display_name"]}</h2>')