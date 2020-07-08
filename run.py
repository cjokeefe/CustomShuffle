import os
import sys
import json
import spotipy
import time
import spotipy.util as util
from json.decoder import JSONDecodeError
from shufflers import *


def get_pl_track_items(pl_id):
	offset = 0

	done = False

	result = []

	while(not done):
		# Get playlist tracks (format specified above)
		pl_track_items = spotify.playlist_tracks(playlist_id=pl_id,
							fields='items(track(name,id,artists.name,artists.id,album.name,album.id))', offset=offset)['items']

		result.extend(pl_track_items)

		if(len(pl_track_items) < 100):
			done = True

		offset = offset + 100

	return result


def replace_tracks(username, pl_id, tracklist):
	length = len(tracklist)
	batches = []
	offset = 0

	# Append batches of 100
	for i in range(length//100):
		batches.append(tracklist[offset:offset+100])
		offset = offset + 100

	# Append remainder if needed
	remainder = tracklist[offset:]
	if(remainder):
		batches.append(remainder)

	# Do 'replace' on first 100 (or less)
	spotify.user_playlist_replace_tracks(username, pl_id, batches[0])

	# Do 'add' on the remaining batches
	for tracks in batches[1:]:
		spotify.user_playlist_add_tracks(username, pl_id, tracks)

	print('success')



startTime = time.time()

# Set scope
scope = 'playlist-modify-public'

# Get username
username = sys.argv[1]

# My Username ID: 12930687

# Prompt user permission
try:
	token = util.prompt_for_user_token(username, scope)
except:
	os.remove(f".cache-{username}")
	token = util.prompt_for_user_token(username, scope)

# Spotify object
spotify = spotipy.Spotify(auth=token)

# Printing readable JSON
# print(json.dumps(VAR, sort_keys=True, indent=4))

# Get playlist tracks with id and name of track, album, artist(s)
''' Format:
pl_track_items[
	{
	track{
		id,
		name,
		album{
			id
			name
		},
		artists[
			{
			id
			name
			},...
		]
	},... 
]

'''
# ID of playlist to shuffle
# spotify:playlist:0qfJQD123jdsapEus1MjJM

pl_id = '0qfJQD123jdsapEus1MjJM'

pl_track_items = get_pl_track_items(pl_id)

print(len(pl_track_items))

# print(json.dumps(pl_track_items, sort_keys=True, indent=4))

# Get the new song order - returns list of track ID's
new_order = Custom_w(pl_track_items, 10)

# print(new_order)

replace_tracks(username, pl_id, new_order)

endTime = time.time()

print('Execution time:', endTime-startTime)