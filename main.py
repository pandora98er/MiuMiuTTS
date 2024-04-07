import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
from gtts import gTTS
from datetime import datetime
import os
import asyncio
from collections import deque
from keep_alive import keep_alive

os.system('clear')

class color():
    green = '\033[92m'
    pink = '\033[95m'
    red = '\33[91m'
    yellow = '\33[93m'
    blue = '\33[94m'
    gray = '\33[90m'
    reset = '\33[0m'
    bold = '\33[1m'
    italic = '\33[3m'
    unline = '\33[4m'

bot = commands.Bot(command_prefix=',', intents=discord.Intents.all())
bot.remove_command('help')
voice = None
playing = False
queue = deque()
keep_alive()

@bot.event
async def on_ready():
    print(f'{color.gray + color.bold}{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} {color.blue}CONSOLE{color.reset}  {color.pink}discord.on_ready{color.reset} Đã đăng nhập bot {color.bold}{bot.user}{color.reset}')
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.listening, name='Bích Phương\'s playlist'))
  
@bot.command(name='join')
async def join(ctx):
    global voice

    if ctx.author.voice is None:
        await ctx.send('Tạo room voice chat đi bae ~')
        return

    if ctx.voice_client is not None:
        await ctx.voice_client.move_to(ctx.author.voice.channel)
    else:
        voice = await ctx.author.voice.channel.connect()


@bot.command(name='s')
async def s(ctx, *, arg:str):
    global voice, playing

    if not arg:
        return

    if ctx.message.author.voice is None:
        await ctx.send('Tạo room voicechat đê!')
        return

    if ctx.guild.voice_client is None:
        try:
            voice = await ctx.message.author.voice.channel.connect()
        except Exception as e:
            print('error', e)
            return
    elif ctx.guild.voice_client.channel != ctx.message.author.voice.channel:
        await ctx.send('Đang ở room voice chat khác')
        return

    tts = gTTS(text=arg, lang='vi')
    tts.save('tts-audio.mp3')
    queue.append(('tts-audio.mp3', ctx))
    if not playing:
        await play_next()

async def play_next():
    global playing
    if queue:
        playing = True
        file, ctx = queue.popleft()
        voice.play(FFmpegPCMAudio(file), after=lambda e: asyncio.run_coroutine_threadsafe(play_next(), bot.loop))
        while voice.is_playing():
            await asyncio.sleep(1)
        os.remove(file)
        playing = False
    else:
        playing = False

@bot.command(name='leave')
async def leave(ctx):
    global voice, playing

    if ctx.guild.voice_client is None:
        await ctx.send('Bot không ở trong room này')
        return

    if voice is not None and voice.is_playing():
        voice.stop()

    await ctx.guild.voice_client.disconnect()
    voice = None
    playing = False


bot.run(os.environ.get('TOKEN'))
