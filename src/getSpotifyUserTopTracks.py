from discord.ext.commands.core import check
import spotipy
import spotipy.util as util
import sys
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth


def authCode(username):
    load_dotenv()

    clientID = os.getenv('SPOTIFY_CLIENT_ID')
    clientSecret = os.getenv('SPOTIFY_CLIENT_SECRET')
    redirect_URI = os.getenv('REDIRECT_URI')

    # scope = "user-library-read user-read-recently-played user-top-read"

    # username = input("Enter username:")

    try:
        # token = util.prompt_for_user_token(
        #     username, scope, clientID, clientSecret, redirect_URI
        # )

        # sp = spotipy.Spotify(auth=token)

        sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=clientID, client_secret=clientSecret,
                                                       redirect_uri=redirect_URI, scope='user-top-read playlist-modify-public', username=username))

    except spotipy.client.SpotifyException as e:
        print("====AUTH ERROR====")
        print(e)
        exit()
    return sp


async def topTracks(ctx, bot, username):

    await ctx.send("""Please enter the number of the time range you wish to track 
        1. short term (past 30 days)
        2. medium-term (past 6 months)
        3. long-term (all time)
    """)

    timeRange = await bot.wait_for('message', check=check)
    spotifyRange = ''

    if len(timeRange.content.strip()) > 1:
        await ctx.send('Please enter a single number value')
    elif timeRange.content == '1':
        spotifyRange = 'short_term'
    elif timeRange.content == '2':
        spotifyRange = 'medium_term'
    elif timeRange.content == '3':
        spotifyRange = 'long_term'

    print(spotifyRange)

    client = authCode(username)
    print("++++++++++++++++++")

    results = client.current_user_top_tracks(
        limit=50, time_range=spotifyRange)
    print("======================")

    tracks = results['items']

    uriList = []

    for idx, item in enumerate(tracks):
        uriList.append(item['uri'])
        trackObject = item['album']

        artist = trackObject['artists'][0]['name']
        songName = item['name']
        await ctx.send(f'{idx + 1}. {artist} - {songName}')

    # createOption = input("would you like to make this a playlist? y/n\n")

    # if createOption == "y":
    #   playlistName = input("please enter a name for the playlist:\n")

    #   user = client.me()
    #   createResults = client.user_playlist_create(user['id'], playlistName)

    #   newPlaylistID = createResults['id']

    #   client.user_playlist_add_tracks(user['id'], newPlaylistID, uriList)

    return
