import os
import sys
import json
import spotipy
import time
import spotipy.util as util
from json.decoder import JSONDecodeError
from shuffle.shufflers import *


def get_pl_track_items(pl_id, spotify):
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


def replace_tracks(username, pl_id, tracklist, spotify):
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


def customshuffle(username, pl_id, method, n, spotify):
	pl_track_items = get_pl_track_items(pl_id, spotify)

	print(len(pl_track_items))

	# Get the new song order - returns list of track ID's
	if(method == 'custom_w'):
		new_order = Custom_w(pl_track_items, n)
	else:
		new_order = Custom_ch(pl_track_items, n)

	replace_tracks(username, pl_id, new_order, spotify)