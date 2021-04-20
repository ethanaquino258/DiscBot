import os

import discord
import logging
import random
import youtube_dl

from dotenv import load_dotenv
from discord.ext import commands

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
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix=commands.when_mentioned_or("!"), description='Relatively simple music bot example')

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

@bot.command(name='join')
async def join(ctx):
    print("GET GIPPED M8")
    if ctx.voice_client is not None:
        return await ctx.voice_client.move_to(channel)

    await ctx.author.voice.channel.connect()

@bot.command(name='talk')
async def talk(ctx):
    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('assets/vocode.mp4'))
    ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('Now playing: {}'.format('David attenborough'))

@bot.command(name='wap')
async def wap(ctx):
    wapVoices = ['ben-shapiro', 'david-attenborough', 'dubya', 'mitch-mcconnell', 'reagan', 'tucker-carlson']
    chosenVoice = random.choice(wapVoices)

    source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(f'assets/WAP/{chosenVoice}.wav'))
    ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('Now playing: {}'.format(chosenVoice))

@bot.command(name='benny')
async def benny(ctx):
    async with ctx.typing():
            player = await YTDLSource.from_url('https://www.youtube.com/watch?v=MK6TXMsvgQg', loop=bot.loop, stream=True)
            ctx.voice_client.play(player, after=lambda e: print('Player error: %s' % e) if e else None)

    await ctx.send('Now playing: {}'.format(player.title))

@bot.command(name='leave')
async def leave(ctx):
    await ctx.voice_client.disconnect()

bot.run(TOKEN)


