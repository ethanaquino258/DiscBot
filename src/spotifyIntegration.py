from discord.ext.commands.core import check
import spotipy
import spotipy.util as util
import sys
import os
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from spotipy import oauth2
from datetime import datetime
import csv
import pandas as pd
import numpy
import discord
from pathlib import Path


async def authCode(ctx, username, scope):
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
                                                       redirect_uri=redirect_URI, scope=scope, username=username))
        spotyOauth = oauth2.SpotifyOAuth(
            clientID, client_secret=clientSecret, redirect_uri=redirect_URI, scope=scope, cache_path='generated/caches')
        auth_url = SpotifyOAuth.get_authorize_url(spotyOauth)

        # if spotyOauth.parse_response_code(auth_url) == 200:
        #     await ctx.message.author.send('Authentication successful')
        # else:
        await ctx.message.author.send(f'Please login here: {auth_url}')

        # os.replace(f'.cache-{username}', f'generated/caches/.cache-{username}')

        # sp = oauth2.SpotifyOAuth(
        #     clientID, client_secret=clientSecret, redirect_uri=redirect_URI, scope=scope)
        # auth_url = sp.get_authorize_url()

    except spotipy.client.SpotifyException as e:
        print("====AUTH ERROR====")
        print(e)
        exit()
    return sp


def multiples(count):
    multipleList = []
    intendedRange = count//100
    for i in range(intendedRange):
        multipleList.append(i*100)
    return multipleList


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

    client = await authCode(ctx, username, 'user-top-read playlist-modify-public')

    results = client.current_user_top_tracks(
        limit=50, time_range=spotifyRange)

    tracks = results['items']

    uriList = []
    formattingList = []

    for idx, item in enumerate(tracks):
        uriList.append(item['uri'])
        trackObject = item['album']

        artist = trackObject['artists'][0]['name']
        songName = item['name']
        formattingList.append(f'{idx + 1}. {artist} - {songName}')

    firstHalf = formattingList[:len(formattingList)//2]
    secondHalf = formattingList[len(formattingList)//2:]

    firstMessage = ''
    secondMessage = ''
    for entry in firstHalf:
        firstMessage = f'{firstMessage}{entry}\n'
    for entry in secondHalf:
        secondMessage = f'{secondMessage}{entry}\n'

    await ctx.message.author.send(f'```{firstMessage}```')
    await ctx.message.author.send(f'```{secondMessage}```')

    await ctx.message.author.send('**Would you like to make this a playlist? Type yes or no**')

    createOption = await bot.wait_for('message', check=check)

    if createOption == "Yes" or "yes":
        await ctx.message.author.send('**Please enter a name for the playlist:**')

        playlistName = await bot.wait_for('message', check=check)
        print(playlistName)
        user = client.me()
        createResults = client.user_playlist_create(
            user['id'], playlistName.content)

        newPlaylistID = createResults['id']

        client.user_playlist_add_tracks(user['id'], newPlaylistID, uriList)
        return
        # try:
        #     user = client.me()
        #     createResults = client.user_playlist_create(
        #         user['id'], playlistName)

        #     newPlaylistID = createResults['id']

        #     client.user_playlist_add_tracks(user['id'], newPlaylistID, uriList)
        #     return
        # except:
        #     await ctx.message.author.send('**Error occurred. Please try again**')
    else:
        return


async def getUserLibrary(ctx, bot, username):
    # with open('user-library.csv', newline='') as readfile:
    #     fileReader = csv.reader(readfile)

    #     header = next(fileReader)
    #     firstLine = next(fileReader)

    #     mostRecent = datetime.strptime(firstLine[-1], "%Y-%m-%dT%H:%M:%S")

    client = await authCode(ctx, username, 'user-library-read')
    results = client.current_user_saved_tracks()

    tracks = results['items']

    await ctx.message.author.send('**Gathering all tracks from user library...**')
    while results['next']:
        results = client.next(results)
        tracks.extend(results['items'])

    songsDict = []
    overallGenres = set()
    trackTotal = len(tracks)
    await ctx.message.author.send(f'**{trackTotal} tracks compiled. Analyzing (this could take a while)...**')

    trackCounter = 0
    progressMarkers = multiples(trackTotal)
    for item in tracks:
        if trackCounter in progressMarkers:
            await ctx.message.author.send(f'{trackCounter}/{trackTotal} analyzed...')

        artistList = []
        genreList = []

        timeAdded = item['added_at'][:-1]

        # itemTime = datetime.strptime(timeAdded, "%Y-%m-%dT%H:%M:%S")

        # print(itemTime < mostRecent)
        # if itemTime < mostRecent:
        #     break

        trackObj = item['track']
        for artist in trackObj['artists']:
            artistList.append(artist['name'])

            artistResult = client.artist(artist['id'])

            # if artist['name'] == 'Iwalani Kahalewai':
            #     print(artistResult['genres'])
            if artistResult['genres'] == []:
                genreResult = 'no genre'
            else:
                genreResult = artistResult['genres']

            genreList.append(genreResult)

        for genreArray in genreList:
            for genre in genreArray:
                overallGenres.add(genre)

        trackItem = {'uri': trackObj['uri'], 'name': trackObj['name'],
                     'artists': artistList, 'genres': genreList, 'time added': timeAdded}
        songsDict.append(trackItem)
        trackCounter += 1

    await ctx.message.author.send('**Done! Writing tracks to file now.**')

    libPath = f'{username}-library.csv'
    genrePath = f'{username}-genres.csv'

    with open(libPath, 'w', newline='') as csvfile:
        fieldnames = ['name', 'artists', 'genres', 'uri', 'time added']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in songsDict:
            writer.writerow({'name': entry['name'], 'artists': entry['artists'],
                             'genres': entry['genres'], 'uri': entry['uri'], 'time added': entry['time added']})

    songs = pd.read_csv(libPath)
    df = pd.DataFrame(data=songs)

    genreDict = []

    for genre in overallGenres:
        rslt_df = df.loc[df['genres'].str.contains(genre)]

        genreObj = {'genre': genre, 'occurences': len(rslt_df)}
        genreDict.append(genreObj)

    await ctx.message.author.send('**Track file done. Writing genres to file now.**')

    with open(genrePath, 'w', newline='') as csvfile:
        fieldnames = ['genre', 'number of occurences']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for entry in genreDict:
            writer.writerow(
                {'genre': entry['genre'], 'number of occurences': entry['occurences']})

    desiredPath = f'generated/libraries/{username}'
    userDir = Path(desiredPath)

    if userDir.exists():
        pass
    else:
        try:
            original_umask = os.umask(0)
            os.makedirs(desiredPath, mode=0o777)
        finally:
            os.umask(original_umask)

    os.replace(libPath, f'{desiredPath}/{libPath}')
    os.replace(genrePath, f'{desiredPath}/{genrePath}')

    await ctx.message.author.send(file=discord.File(f'generated/libraries/{username}/{username}-library.csv'))
    await ctx.message.author.send(file=discord.File(f'generated/libraries/{username}/{username}-genres.csv'))
