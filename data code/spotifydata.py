# #client ID = 5446a1ccadbc44c191efd7001352dba5
# #client secret = a85122a8ac074332b302de3641cef77d

# import spotipy
# from spotipy.oauth2 import SpotifyClientCredentials
# import csv

# # Authenticate with Spotify API
# client_credentials_manager = SpotifyClientCredentials(client_id='5446a1ccadbc44c191efd7001352dba5', client_secret='a85122a8ac074332b302de3641cef77d')
# sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# # Initialize CSV writer
# with open('spotify_data.csv', 'w', newline='', encoding='utf-8') as csv_file:
#     csv_writer = csv.writer(csv_file)
#     csv_writer.writerow(['Track ID', 'Track Name', 'Album ID', 'Album Name', 'Total Tracks', 'Artist ID', 'Artist Name', 'Followers', 'Release Date', 'Popularity', 'Duration', 'Explicit', 'Available Markets', 'Track Number', 'Genre', 'Preview URL'])

#     query = 'country:pakistan'
#     results = sp.search(q=query, type='artist', limit=50)

#     artist_ids = [artist['id'] for artist in results['artists']['items']]

#     for artist_id in artist_ids:
#         top_tracks = sp.artist_top_tracks(artist_id)
#         artist_info = sp.artist(artist_id)
#         artist_followers = artist_info['followers']['total']
#         artist_genre = artist_info['genres'][0] if artist_info['genres'] else None
#         for track in top_tracks['tracks']:
#             track_id = track['id']
#             track_name = track['name']
#             album_id = track['album']['id']
#             album_name = track['album']['name']
#             total_tracks = track['album']['total_tracks']
#             release_date = track['album']['release_date']
#             popularity = track['popularity']
#             duration = track['duration_ms']
#             explicit = track['explicit']
#             preview_url = track['preview_url']
#             available_markets = track['available_markets']
#             track_number = track['track_number']
#             csv_writer.writerow([track_id, track_name, album_id, album_name, total_tracks, artist_id, artist_name, artist_followers, release_date, popularity, duration, explicit,  available_markets, track_number, artist_genre, preview_url])



# # Close CSV file
# csv_file.close()


import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import csv

# Authenticate with Spotify API
client_credentials_manager = SpotifyClientCredentials(client_id='5446a1ccadbc44c191efd7001352dba5', client_secret='a85122a8ac074332b302de3641cef77d')
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def fetch_results(endpoint, params):
    results = sp._get(endpoint, **params)
    data = results.get('items', [])  # Use .get() to handle KeyError
    while results.get('next'):
        results = sp._get(results['next'])
        data.extend(results.get('items', []))  # Use .get() to handle KeyError
    return data

# Initialize CSV writer
csv_file = open('spotify_data.csv', 'w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(['Track ID', 'Track Name', 'Album ID', 'Album Name', 'Artist ID', 'Artist Name', 'Release Date', 'Popularity', 'Duration', 'Preview URL', 'Genre', ])

query = 'country:pakistan'
results = sp.search(q=query, type='artist', limit=50)

artist_ids = [artist['id'] for artist in results['artists']['items']]

for artist_id in artist_ids:
    top_tracks = sp.artist_top_tracks(artist_id)
    artist_info = sp.artist(artist_id)
    artist_genre = artist_info['genres'][0] if artist_info['genres'] else None
    for track in top_tracks['tracks']:
        ArtistID = artist_id
        ArtistName = track['artists'][0]['name']
        TrackID = track['id']
        TrackName =track['name']
        AlbumID = track['album']['id']
        AlbumName = track['album']['name']
        ReleaseDate = track['album']['release_date']
        Popularity = track['popularity']
        Duration = track['duration_ms']
        PreviewURL= track['preview_url']
        Genre = artist_genre
        csv_writer.writerow([TrackID, TrackName, AlbumID, AlbumName, ArtistID, ArtistName, ReleaseDate, Popularity, Duration, PreviewURL, Genre])

# Fetch more tracks if needed
offset = 50
while len(artist_ids) < 1500:
    results = sp.search(q=query, type='artist', limit=50, offset=offset)
    artist_ids.extend([artist['id'] for artist in results['artists']['items']])
    offset += 50

    for artist_id in artist_ids:
        top_tracks = sp.artist_top_tracks(artist_id)
        artist_info = sp.artist(artist_id)
        artist_genre = artist_info['genres'][0] if artist_info['genres'] else None
        for track in top_tracks['tracks']:
            ArtistID = artist_id
            ArtistName = track['artists'][0]['name']
            TrackID = track['id']
            TrackName =track['name']
            AlbumID = track['album']['id']
            AlbumName = track['album']['name']
            ReleaseDate = track['album']['release_date']
            Popularity = track['popularity']
            Duration = track['duration_ms']
            PreviewURL= track['preview_url']
            Genre = artist_genre
            csv_writer.writerow([TrackID, TrackName, AlbumID, AlbumName, ArtistID, ArtistName, ReleaseDate, Popularity, Duration, PreviewURL, Genre])

# Close CSV file
csv_file.close()
