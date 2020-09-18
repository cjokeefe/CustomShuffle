from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.core.cache import caches
from shuffle.shuffle import customshuffle
import spotipy
import uuid
import os
import json

# Create your views here.

def index(request):
	if not 'id' in request.session:
		request.session['id'] = str(uuid.uuid4())

	username=str(request.session['id'])

	auth_manager = spotipy.oauth2.SpotifyOAuth(scope='playlist-modify-public user-top-read playlist-read-private', username=username, show_dialog=True)

	if request.GET.get('code'):
		code = request.GET.get('code')
		print("About to get_access_token")
		auth_manager.get_access_token(code)
		print("Just did get_access_token")

	if not auth_manager.get_cached_token():
		auth_url=auth_manager.get_authorize_url()
		return HttpResponse(f'<h2><a href="{auth_url}">Sign in</a></h2>')

	spotify = spotipy.Spotify(auth_manager=auth_manager)


	#print(json.dumps(spotify.me(), sort_keys=True, indent=4))

	name = spotify.me()["display_name"]
	topTracks = spotify.current_user_top_tracks(limit=5)['items']

	topTrackList = []

	for track in topTracks:
		topTrackList.append(track['name'])

	context = {
		'name': name,
		'topTracks': topTrackList,
	}

	#print(json.dumps(toptracks, sort_keys=True, indent=4))
	
	return render(request, 'shuffle/home.html', context)


def ListPlaylists(request):
	username = str(request.session['id'])
	auth_manager = spotipy.oauth2.SpotifyOAuth(username=username)
	if not auth_manager.get_cached_token():
		print("Did not get cached token")
		return HttpResponseRedirect('index')
	spotify = spotipy.Spotify(auth_manager=auth_manager)
	playlists = spotify.current_user_playlists(limit=20)['items']
	plList = []
	for pl in playlists:
		item = {'name': pl['name'], 'id': pl['id']}
		plList.append(item)

	context = {
		'playlists': plList,
	}

	#print(json.dumps(playlists, sort_keys=True, indent=4))

	#return HttpResponse("Made it to end of ListPlaylists View")
	return render(request, 'shuffle/playlists.html', context)


def ShufflePlaylist(request, pl_id):
	username = str(request.session['id'])
	auth_manager = spotipy.oauth2.SpotifyOAuth(username=username)
	if not auth_manager.get_cached_token():
		print("Did not get cached token")
		return HttpResponseRedirect('index')
	spotify = spotipy.Spotify(auth_manager=auth_manager)
	userID = spotify.me()['id']
	method = request.POST.get('method')
	n = request.POST.get('n')
	try:
		n = int(n)
	except ValueError:
		return HttpResponseRedirect(reverse('view-playlist', args=(pl_id,)))

	customshuffle(userID, pl_id, method, n, spotify)

	return HttpResponseRedirect(reverse('view-playlist', args=(pl_id,)))


def PlaylistView(request, pl_id):
	username = str(request.session['id'])
	auth_manager = spotipy.oauth2.SpotifyOAuth(username=username)
	if not auth_manager.get_cached_token():
		print("Did not get cached token")
		return HttpResponseRedirect('index')
	spotify = spotipy.Spotify(auth_manager=auth_manager)

	pl = spotify.playlist(pl_id, fields='name,tracks(items(track(name,artists.name,album.name)))')
	#print(json.dumps(pl, sort_keys=True, indent=4))

	tracks = []
	for item in pl['tracks']['items']:
		trackItem = {
			'name': item['track']['name'],
			'artist': item['track']['artists'][0]['name'],
			'album': item['track']['album']['name']
		}
		tracks.append(trackItem)

	context = {
		'pl_name': pl['name'],
		'tracks': tracks,
		'pl_id': pl_id,
	}
	return render(request, 'shuffle/view_playlist.html', context)




def callback(request):
	cache_path = caches_folder + str(request.session['id'])
	auth_manager = spotipy.oauth2.SpotifyOAuth(cache_path=cache_path)
	if request.GET['code']:
		code = request.GET['code']
		auth_manager.get_access_token(code)

	spotify = spotipy.Spotify(auth_manager=auth_manager)

	#return HttpResponse("code:" + code)
	return HttpResponse(f'<h2>Welcome {spotify.me()["display_name"]}</h2>')