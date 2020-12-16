import os
import asyncio

from discord import FFmpegPCMAudio
from discord.ext.commands import Bot
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

streams = [
    {"name": "Radiorecord.ru", "link": "https://air.radiorecord.ru:805/synth_320"},
    {"name": "Nightride.fm", "link": "https://stream.nightride.fm/nightride.m4a"},
    {"name": "Synthwave.hu", "link": "https://ecast.myautodj.com/public1channel"},
    {"name": "Laut.fm", "link": "https://nightdrive.stream.laut.fm/nightdrive"},
]


bot = Bot(command_prefix="-")


@bot.event
async def on_ready():
    print("radiowavey is up")


@bot.command("ping")
async def ping(ctx):
    await ctx.send(f"Pong! `{round(bot.latency * 1000)} ms`")


@bot.command("shutdown")
async def shutdown(ctx):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if not is_owner:
        return

    await ctx.guild.voice_client.disconnect(force=True) if ctx.guild.voice_client is not None else pass
    await ctx.bot.logout()


async def play_stream(ctx, msg):
    """ Plays a stream link"""

    if ctx.voice_client is None:
        global player
        channel = ctx.message.author.voice.channel
        player = await channel.connect()

    if player.is_playing():
        player.stop()

    player.play(
        FFmpegPCMAudio(
            streams[(int(msg.content) - 1) if type(msg) != int else (msg - 1)]["link"]
        )
    )
    await ctx.send(
        f"Playing Radio - **`{streams[(int(msg.content) -1) if type(msg) != int else (msg - 1)]['name']}`**"
    )


@bot.command(aliases=["p", "pla"], help="Plays a radio channel")
async def play(ctx, channel: int = 0):
    # not connected to a voice channel
    if not ctx.message.author.voice:
        await ctx.send("Connect to a voice channel to start listening.")
        return
    
    if channel > 4: 
        return

    # channel arg is given with the command
    if channel != 0:
        await play_stream(ctx, channel)
        return

    radio_channel_prompt = f"""
    `📻【ｒａｄｉｏｗａｖｅ】`
   Select a radio channel -
> 1. **`Radiorecord.ru`**
> 2. **`Nightride.fm`**
> 3. **`Synthwave.hu`**
> 4. **`Laut.fm`**
    """
    await ctx.send(radio_channel_prompt)

    def check(msg):
        return (
            msg.author == ctx.author
            and msg.channel == ctx.channel
            and msg.content.isnumeric()
            and int(msg.content) in [i + 1 for i in range(len(streams))]
        )

    msg = 0

    try:
        msg = await bot.wait_for("message", check=check, timeout=20)
    except asyncio.TimeoutError:
        await ctx.send("Sorry, you didn't reply in time!")
        return

    try:
        await play_stream(ctx, msg)

    except Exception as e:
        print(f"[Exception]: {e}")


@bot.command(aliases=["s", "sto"], help="Stops the radio.")
async def stop(ctx):
    if ctx.voice_client is None:
        await ctx.send("Not playing any radio!")
        return
    else:
        player.stop()
        await ctx.send("Player stopped")
        await ctx.guild.voice_client.disconnect(force=True)


bot.run(TOKEN)