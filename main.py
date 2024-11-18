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
RULE_long = '''
- La personne qui anime donne son feu vert a celles qui écrivent la lettre 'd' dans ce salon. On peut utiliser :ok_hand: en reaction au message ou le faire à l'oral.
- Elle choisie aussi de quoi on parle pendant son mandat (en manque d'inspiration? avec le mot clé 'sujet' dans ce salon forum https://discord.com/channels/1064477854764638278/1287366716531282012 )
- On exprime son accord (ou non) *sans interrompre* la personne qui parle en écrivant la lettre 'w' ('x') ici.
- On demande à poser une question techniquue en écrivant la lettre 't' ici.
- Il est possible de passer son tour à tout instant en écrivant `!pass`.
'''

RULE = '''
On demande à parler en écrivant la lettre `d` et la personne qui anime vous donne son feu vert.
'''
RULE_aft ='''
Cette personne peut passer son tour n'importe quand en écrivant `!pass`.
'''


@client.event
async def on_ready():
    print(f'{client.user} est prêt !')


def format_time(seconds):
    """Convertit des secondes en format minutes et secondes"""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}min {remaining_seconds}s"


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
    """Répond aux commandes !start et !stop"""
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
        await message.channel.send(RULE + f'**{anim}** anime pour {mandat}' + RULE_aft)
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
            await message.channel.send(f'**{anim}** anime pour {mandat}')
            timers[channel_id] = asyncio.create_task(timer(dur, message))
        else:
            await message.channel.send("No timer")

    elif message.content == '!split':
        if len(m_list) < 6:
            await message.channel.send("No need")
        else:
            ch = random.sample(m_list, 3)
            await message.channel.send(f'{ch} peuvent aller dans un autre salon')

    elif message.content == '!stop':
        channel_id = message.channel.id

        if channel_id in timers and not timers[channel_id].done():
            timers[channel_id].cancel()  # Arrêter le timer
            await message.channel.send("Timer stopped")
        else:
            await message.channel.send("No timer")


async def timer(duration, message):
    """Fonction qui gère le timer"""
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
        await message.channel.send(f'{anim} anime pour {mandat}' + RULE)

client.run(TO)
