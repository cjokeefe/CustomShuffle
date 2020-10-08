import random

def PureRandom(pl_track_items):
	track_ids = []
	for track in pl_track_items:
		track_ids.append(track['track']['id'])

	random.shuffle(track_ids)
	print(track_ids)

	return track_ids


# User gives number of chunks
def Custom_ch(pl_track_items, n_chunks):
	result = []
	length = len(pl_track_items)

	# Get dict of {artist_id:[track_ids]}
	artist_tracks = TracksByArtists(pl_track_items)

	# Get sorted list of artist id's by length of track list
	def lenSort(x):
		return len(artist_tracks[x])

	artist_ids = list(artist_tracks.keys())
	artist_ids.sort(key=lenSort)
	artist_ids.reverse()

	# Initialize list for each chunk
	for i in range(n_chunks):
		result.append([])

	# Distribute tracks to the chunks
	curr_chunk = 0
	for artist in artist_ids:
		for track in artist_tracks[artist]:
			result[curr_chunk].append(track)
			curr_chunk = (curr_chunk+1)%n_chunks

	for chunk in result:
		random.shuffle(chunk)

	random.shuffle(result)

	result = flatten_list(result)

	return result


# User gives maximum width of chunks
def Custom_w(pl_track_items, width):
	result = []
	length = len(pl_track_items)
	remainder = length%width
	n_chunks = (length//width) + int(bool(remainder))

	# Get dict of {artist_id:[track_ids]}
	artist_tracks = TracksByArtists(pl_track_items)

	# Get sorted list of artist id's by length of track list
	def lenSort(x):
		return len(artist_tracks[x])

	artist_ids = list(artist_tracks.keys())
	artist_ids.sort(key=lenSort)
	artist_ids.reverse()

	# Initialize list for each chunk
	for i in range(n_chunks):
		result.append([])

	# Distribute tracks to the chunks
	curr_chunk = 0
	for artist in artist_ids:
		for track in artist_tracks[artist]:
			result[curr_chunk].append(track)
			curr_chunk = (curr_chunk+1)%n_chunks


	for chunk in result:
		random.shuffle(chunk)

	random.shuffle(result)

	result = flatten_list(result)

	return result


def flatten_list(l):
	result = []
	for sublist in l:
		result.extend(sublist)

	return result



# Returns dictionary of {artist_id:[track_ids]}
def TracksByArtists(track_items):
	result = {}
	for track in track_items:
		artist_id = track['track']['artists'][0]['id']
		if artist_id in result:
			result[artist_id].append(track['track']['id'])
		else:
			result[artist_id] = [track['track']['id']]

	return result