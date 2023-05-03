# bot.py
import asyncio
import os

import discord
from dotenv import load_dotenv
from discord.ext import commands
import requests
import os
from pathlib import Path

import openai

from dateutil.parser import parse

import yaml
import pytz

import pokegame

import random

import shutil

from Archipelago.APVersionClient import APVersionContext, server_loop

pokegame = pokegame.PokeGame()

load_dotenv()
openai.api_key = os.getenv('CHATGPT_TOKEN')
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(intents=intents, command_prefix='uwu ')

@bot.command()
async def test(ctx, arg="Test successful!"):
    await ctx.send(arg)

@bot.command()
async def connectAP(ctx, address="localhost", slot_name="", password = ""):
    ctx2 = APVersionContext(address, password)
    ctx2.auth = slot_name
    ctx2.messagecontext = ctx
    ctx2.messagecallback = test
    ctx2.server_task = asyncio.create_task(server_loop(ctx2), name="server loop")

    ctx2.run_cli()


def downloadFile(URL=None):
    import httplib2
    h = httplib2.Http(".cache")
    resp, content = h.request(URL, "GET")
    return content

@bot.command()
async def collectyamls(ctx, *, arg="1/1/1970", download=True):
    startDate = parse(arg)

    startDate = startDate.replace(tzinfo=pytz.UTC)
    
    print(download)

    chat_history = ctx.channel.history(limit=None)
    
    history = []
    
    yamlcounts = dict()
    gamecounts = dict()
    
    if download == True or download == "True":
        Path("./yamls").mkdir(parents=True, exist_ok=True)
        for f in os.listdir("./yamls"):
            os.remove(os.path.join("./yamls", f))
    
    async for message in chat_history:
        if message.attachments:
            if message.created_at < startDate:
                continue
         
            for att in message.attachments:
                url = att.url
                if not url.lower().endswith(".yaml"):
                    continue
                    
                history.append(url)
                
                usr = str(message.author)
                
                yamlcounts.setdefault(usr, 0)

                gamesInYaml = 1
                
                req = requests.get(url)
                txt = req.text
               
                if download == True or download == "True":
                    fileName = "./yamls/" + os.path.basename(url)
                    file = open(fileName, 'w')
                    file.write(txt)
                    file.close()
                
                yamlcounts[usr] += 1 + txt.count("---")
                
                indiv_games = txt.split("---")
                for indiv_game in indiv_games:
                    parsed_yaml = yaml.safe_load(indiv_game)
                    game = parsed_yaml["game"]
                    if type(game) == str:
                        print(game)
                    else:
                        games = [k for k,v in game.items() if v != 0]
                        if len(games) != 1:
                            game = "Random choice of " + ", ".join(games)
                        else:
                            game = games[0]
                    gamecounts.setdefault(game, 0)
                    gamecounts[game] += 1
                   
                    
                
    yamlcounts = {k: v for k, v in sorted(yamlcounts.items(), key=lambda item: item[1], reverse=True)}
    gamecounts = {k: v for k, v in sorted(gamecounts.items(), key=lambda item: item[1], reverse=True)}
    
    #messages_in_channel = chat_history.map(transform).flatten()
        
    outmsg = "Downloaded yamls. Counts:\n\n"
    if not download:
        outmsg = "Counted yamls. Counts:\n\n"

    for k,v in yamlcounts.items():
        outmsg += "**" + k + "**: " + str(v) + "\n"
        
    totalsum = sum(yamlcounts.values())
   
    
    outmsg += "\n\nGame counts:\n\n"
    
    for k,v in gamecounts.items():
        outmsg += "**" + k + "**: " + str(v) + "\n"
    
    outmsg += "\n**Total**: " + str(totalsum)
    
    shutil.make_archive("./yamls", 'zip', "./yamls")
    
    if download:
        await ctx.send(outmsg, file=discord.File("./yamls.zip"))
    else:
        await ctx.send(outmsg)

@bot.command()
async def countyamls(ctx, *, arg="1/1/1970"):
    await collectyamls(ctx, arg=arg, download=False)
    
@bot.command()
async def countmeows(ctx):
    print("Test")

    chat_history = ctx.channel.history(limit=None)
    
    counts = dict()
    async for message in chat_history:
        meows = message.content.lower().count('meow')
        if not meows:
            continue
      
        usr = str(message.author)
        counts.setdefault(usr, 0)
        counts[usr] += meows
        
    outmsg = "Counted meows. Counts:\n\n"

    for k,v in counts.items():
        outmsg += "**" + k + "**: " + str(v) + "\n"
        
    await ctx.send(outmsg)
    
    
    
@bot.event
async def on_message(message):
    ctx = await bot.get_context(message)
    
    channel = message.channel

    guild = ctx.guild
    await guild.chunk()

    if not channel.permissions_for(ctx.guild.me).send_messages:
        return

    if message.author == bot.user:
        return

    if random.random() > 0.02:
        print("Random roll for ChatGPT response failed")
        return
    
    chatgpt_formatted_messages = ""
    
    last_user = None
    
    most_recent_message = ""
    
    most_recent_messages = [msg async for msg in channel.history(limit=15)]
    most_recent_messages.reverse()
    
    user_amt = 0
    
    for msg in most_recent_messages:
        if msg.author == bot.user:
            continue
    
        if not msg.content:
            continue
           
            
        member = guild.get_member(msg.author.id)
        
        if last_user != member:
            last_user = member
            user_amt += 1
            chatgpt_formatted_messages += f"\n{member.display_name}\n"
        
        chatgpt_formatted_messages += msg.content.strip() + "\n"

        most_recent_message = msg.content
        
    chatgpt_start = f"""Below will be a chatlog from a group chat. The messages are seperated by empty lines. The top line is the username, and the following lines are the messages they wrote.

Come up with a witty dunk response message to the latest message in the chat log. The response is written by a user called "ViBot". In your response, include the name of the person you are responding to (which in this case, should be {last_user.display_name}), so it is clear who you are replying to.

Keep it light-hearted.

Here is the chatlog:
"""
        
    if len(most_recent_message) <= 15:
        print("message too short to respond to")
        return
        
    if user_amt < 3:
        print("Not enough users participated.")
        return
        
    chatgpt_input = chatgpt_start + chatgpt_formatted_messages 
        
    messages = [
        {"role": "user", "content": chatgpt_input},
    ]
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    
    for message in chat.choices:
        if last_user.display_name in message.message.content:
            reply = message.message.content.replace('@','')
            reply = "\n".join([item for item in reply.split("\n")[1:] if item.strip()])
            await channel.send(reply + "\n\n(This is an auto-generated response on a random chance, using ChatGPT.)")
            return
        
    print("Couldn't come up with a good reply")
    
    
@bot.command()
async def encounter(ctx):
    pokemon = await pokegame.catch_pokemon()

    await ctx.send("You caught a level " + str(pokemon.level) + " " + pokemon.name + "!")

bot.run(TOKEN)