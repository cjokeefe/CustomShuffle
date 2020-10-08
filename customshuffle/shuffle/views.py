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

	scope = 'playlist-modify-public user-top-read playlist-modify-private'

	auth_manager = spotipy.oauth2.SpotifyOAuth(scope=scope, username=username, show_dialog=True)

	if request.GET.get('code'):
		code = request.GET.get('code')
		print("About to get_access_token")
		auth_manager.get_access_token(code)
		print("Just did get_access_token")

	if not auth_manager.get_cached_token():
		auth_url=auth_manager.get_authorize_url()
		context = {'auth_url': auth_url}
		#return HttpResponse(f'<h2><a href="{auth_url}">Sign in</a></h2>')
		return render(request, 'shuffle/login.html', context)

	spotify = spotipy.Spotify(auth_manager=auth_manager)


	#print(json.dumps(spotify.me(), sort_keys=True, indent=4))

	name = spotify.me()["display_name"]
	topTracks = spotify.current_user_top_tracks(limit=5)['items']

	topTrackList = []

	for track in topTracks:
		topTrackList.append(
			{'title': track['name'], 'artist': track['artists'][0]['name']}
		)

	context = {
		'name': name,
		'topTracks': topTrackList,
	}

	#print(json.dumps(toptracks, sort_keys=True, indent=4))
	
	return render(request, 'shuffle/home.html', context)


def ListPlaylists(request, offset):
	username = str(request.session['id'])
	auth_manager = spotipy.oauth2.SpotifyOAuth(username=username)
	if not auth_manager.get_cached_token():
		print("Did not get cached token")
		return HttpResponseRedirect('index')
	spotify = spotipy.Spotify(auth_manager=auth_manager)
	playlists = spotify.current_user_playlists(limit=20, offset=offset)['items']

	plList = []
	for pl in playlists:
		if(pl['owner']['id'] == spotify.me()['id']):
			item = {'name': pl['name'], 'id': pl['id']}
			plList.append(item)

	context = {
		'playlists': plList,
		'offset': offset,
		'next': offset+20,
		'prev': offset-20,
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
	print(method, n)
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


	pl = spotify.playlist(pl_id, fields='name')
	try:
		pl_img = spotify.playlist_cover_image(pl_id)[1]['url']
	except:
		pl_img = None
	#print(json.dumps(pl, sort_keys=True, indent=4))

	done = False
	result = []
	offset = 0
	while(not done):
		# Get playlist tracks
		pl_track_items = spotify.playlist_tracks(playlist_id=pl_id,
							fields='items(track(name,artists.name,album.name))', offset=offset)['items']

		result.extend(pl_track_items)

		if(len(pl_track_items) < 100):
			done = True

		offset = offset + 100

	#print(json.dumps(result, sort_keys=True, indent=4))

	tracks = []
	counter = 1
	for item in result:
		trackItem = {
			'trackNum': counter,
			'name': item['track']['name'],
			'artist': item['track']['artists'][0]['name'],
			'album': item['track']['album']['name'],
		}
		tracks.append(trackItem)
		counter += 1

	context = {
		'pl_name': pl['name'],
		'tracks': tracks,
		'pl_id': pl_id,
		'pl_img': pl_img,
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