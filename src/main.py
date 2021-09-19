import os

import discord
import logging
import random
import youtube_dl
import getLatestTweet
import getSpotifyUserTopTracks
from time import sleep
from dotenv import load_dotenv
from discord.ext import commands
from googleapiclient.discovery import build

load_dotenv()

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    # bind to ipv4 since ipv6 addresses cause issues sometimes
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    "!"), description='Relatively simple music bot example')

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


def youtubeLogin():
    key = os.getenv('YOUTUBE_KEY')

    return build('youtube', 'v3', developerKey=key)


@bot.command(name='join')
async def join(ctx):
    try:
        await ctx.author.voice.channel.connect()
    except:
        await ctx.send(f'{ctx.author.nick} is not in a channel')


async def playAudioFile(ctx, filepath):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(filepath))
    ctx.voice_client.play(source, after=lambda e: print(
        'Player error: %s' % e) if e else None)


@bot.command(name='wap')
async def wap(ctx, arg=None):
    wapVoices = ['ben-shapiro', 'david-attenborough', 'dubya',
                 'mitch-mcconnell', 'reagan', 'tucker-carlson']

    if arg is None:
        chosenVoice = random.choice(wapVoices)
    elif wapVoices.__contains__(arg):
        chosenVoice = arg
    elif arg == 'help':
        await ctx.send('```Possible voices:\nben-shapiro\ndavid-attenborough\ndubya\nmitch-mcconnell\nreagan\ntucker-carlson```')
    else:
        await ctx.send('Invalid argument')

    voicePath = f'assets/WAP/{chosenVoice}.wav'

    if ctx.voice_client.is_playing() is True:
        await ctx.send('Please wait for current audio to finish. Use `!stop` to stop current audio.')
    else:
        await playAudioFile(ctx, voicePath)
        await ctx.send('Now playing: {}'.format(chosenVoice))


@bot.command(name='play')
async def play(ctx, arg=None):

    if arg == '-h':
        await ctx.send('```Searches Youtube for videos relating to argument and chooses first one. \nWrap argument in quotes for multi-word args\nEx: !play "wet ass pussy"```')

    elif arg is None:
        await ctx.send('```Please specify something to play. Use argument `play -h` for details```')

    elif len(arg) > 0:

        youtube = youtubeLogin()

        videos = youtube.search().list(part='snippet', q=arg).execute()
        videoUrl = 'https://www.youtube.com/watch?v=' + \
            videos['items'][0]['id']['videoId']
        youtube.close()

        if ctx.voice_client.is_playing() is True:
            await ctx.send('```Please wait for current audio to finish. Use `!stop` to stop current audio.```')
        else:

            async with ctx.typing():
                player = await YTDLSource.from_url(videoUrl, loop=bot.loop, stream=True)
                ctx.voice_client.play(player, after=lambda e: print(
                    'Player error: %s' % e) if e else None)

            await ctx.send('Now playing: {}'.format(player.title))
            await ctx.send(videoUrl)


@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client.is_playing() is True:
        ctx.voice_client.stop()
    else:
        await ctx.send('No audio being played.')


@bot.command(name='benny')
async def benny(ctx):
    async with ctx.typing():
        player = await YTDLSource.from_url('https://www.youtube.com/watch?v=MK6TXMsvgQg', loop=bot.loop, stream=True)
        ctx.voice_client.play(player, after=lambda e: print(
            'Player error: %s' % e) if e else None)

    await ctx.send('Now playing: {}'.format(player.title))


@bot.command(name='philosophers')
async def philosophers(ctx, arg=None):
    if arg == '-h':
        await ctx.send("```Get the latest tweet for a specific twitter handle.\nex. !philosophers RealCandaceO will return Candace Owens's latest tweet.```")
    elif arg is None:
        arg = 'benshapiro'
    elif len(arg) > 0:
        try:
            url = getLatestTweet.main(arg)
            await ctx.send("https://twitter.com/{}/status/{}".format(arg, url))
        except:
            await ctx.send("```Invalid Twitter user. Please use arg 'philosophers -h' for details```")


@bot.command(name='topTracks')
async def topTracks(ctx, arg=None):
    print(arg)
    if arg == '-h':
        await ctx.send("Get your top tracks from spotify. Provide your username in the command, ex `!top-tracks My_Username")
    elif arg is None:
        await ctx.send('Please specify your spotify username. See `!top-tracks -h for instructions')
    elif len(arg) > 0:
        await getSpotifyUserTopTracks.topTracks(ctx, bot, arg)


@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client.is_playing() is True:
        ctx.voice_client.stop()

    await playAudioFile(ctx, 'assets/quips/facts.wav')

    while ctx.voice_client.is_playing():
        sleep(1)

    await ctx.send('**Facts don\'t care about your feelings**')
    await ctx.voice_client.disconnect()

bot.run(TOKEN)
