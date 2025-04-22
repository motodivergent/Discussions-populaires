import random
import discord
import asyncio
from secret import TO

intents = discord.Intents.default()
intents.messages = True  # Suivre les messages
intents.message_content = True  # Important pour lire le contenu des messages

client = discord.Client(intents=intents)

# Dictionnaire pour stocker les timers par canal
timers = {}
durs = {}
anims = {}


@client.event
async def on_ready():
    print(f'{client.user} ready !')


def format_time(seconds):
    """Convert seconds in minutes & seconds"""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}min{remaining_seconds}s"


def format_rule(anim, mandat):
    """Write on the rule"""
    mess = f"""
    **{anim}**=:crown: {mandat }
    `!pass` -> :stop_button:
    d | :raised_hand: -> :speaking_head:
    """
    return mess


def next_anim(m_list, anim):
    """Find the next animator in the list of members"""
    if anim not in m_list:
        m_list.append(anim)
    m_list.sort()
    n = m_list.index(anim)
    if n + 1 < len(m_list):
        return m_list[n + 1]
    else:
        return m_list[0]


@client.event
async def on_message(message):
    """Respond to !start !pass and !stop"""
    channel_id = message.channel.id
    chan = client.get_channel(channel_id)
    m_list = sorted(m.display_name for m in chan.members)

    if message.author == client.user:
        return

    if message.content.startswith('!start'):
        try:
            _, duration = message.content.split()
            duration = int(duration)
        except ValueError:
            duration = 900
        durs[channel_id] = duration

        if channel_id in timers and not timers[channel_id].done():
            await message.channel.send("Timer in channel need to !stop.")
            return

        anim = random.choice(m_list)
        anims[channel_id] = anim
        mandat = format_time(duration)
        await message.channel.send(format_rule(anim, mandat))
        timers[channel_id] = asyncio.create_task(timer(duration, message))


    elif message.content == '!pass':
        # On redemarre alors le timer
        if channel_id in timers and not timers[channel_id].done():
            timers[channel_id].cancel()
            dur = durs[channel_id]
            c_anim = anims[channel_id]
            mandat = format_time(durs[channel_id])
            anim = next_anim(m_list, c_anim)
            anims[channel_id] = anim
            await message.channel.send(format_rule(anim, mandat))
            timers[channel_id] = asyncio.create_task(timer(dur, message))
        else:
            await message.channel.send("No timer")

    elif message.content == '!stop':
        channel_id = message.channel.id

        if channel_id in timers and not timers[channel_id].done():
            timers[channel_id].cancel()  # Arrêter le timer
            await message.channel.send("Timer stopped")
        else:
            await message.channel.send("No timer")


async def timer(duration, message):
    """Manage the timer"""
    channel_id = message.channel.id
    mandat = format_time(durs[channel_id])
    while True:
        await asyncio.sleep(duration)
        chan = client.get_channel(channel_id)
        m_list = sorted(m.display_name for m in chan.members)
        if not m_list:
            timers[channel_id].cancel()
        c_anim = anims[channel_id]
        anim = next_anim(m_list, c_anim)
        anims[channel_id] = anim
        await message.channel.send(format_rule(anim, mandat))

client.run(TO)
