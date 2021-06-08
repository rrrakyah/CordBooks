from enum import unique
import discord
from discord import message
from discord.ext import commands
from discord import utils
import configparser
import validators
import peewee
import os
from validators.url import url
import datetime
import markovify
import re


intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.guild_messages = True
intents.presences = True
intents.webhooks = True

TOKEN = "ODUxMTQ1MjUyNjA5NTg5Mjgw.YL0AyQ.mRaHYsCir897abRvmE577qz4poA"
bot = commands.Bot(command_prefix='=', intents=intents)
client = discord.Client()

config = configparser.ConfigParser()
config.read("cfg.ini")

BLACKLIST = config.get("lists", "channel_blacklist")
WHITELIST = config.get("lists", "user_whitelist")


#Database stuff
db = peewee.SqliteDatabase("cordbooks.db")

class BaseModel(peewee.Model):
    class Meta:
        database = db
        
class User(BaseModel):
    username = peewee.CharField(unique=False)
    id = peewee.CharField(unique=True)

class Message(BaseModel):
    user = peewee.ForeignKeyField(User, backref='messages')
    id = peewee.CharField(unique=True)
    content = peewee.TextField()
    created_date = peewee.DateTimeField(default=datetime.datetime.now)


@bot.command()
async def fetch(ctx, day=7, lim=1500):
    await ctx.message.delete()
    
    if day >=1000:
        day=1000
    
    if ctx.author.id == ctx.me.id:
        return
    
    if ctx.channel.name in config.get("lists", "channel_blacklist"):
        await ctx.send("This channel is blacklisted!")
        return
    
    if day != 7:
        print("\nAmount of days before: " + str(day))
    
    if lim >= 10000:
        lim=10000
        
    print("For amount of messages: " + str(lim) + "\n")
    
    #Scraping history
    d = datetime.datetime.now() - datetime.timedelta(days=day)
    
    messages = await ctx.channel.history(limit=lim, before=d).flatten()
    #await ctx.send("Now fetching " + str(lim) + " messages from " + str(d))
    
    i=0
    a=0
    b=0
    with db.atomic():
        for n in messages:
            if n.content == '' or validators.url(n.content):
                b = b+1
                continue
        
            if '$fetch' in n.content or '$sus' in n.content or '$hi' in n.content or '$test' in n.content or '$whitelist' in n.content:
                b = b+1
                continue
        
        #   if n.author.id == member.id:
            try:
                user = User.get(User.id == n.author.id)
            except User.DoesNotExist:
                user = User.create(id=n.author.id, username=n.author)
            
            try:
                Message.create(user=user, id=n.id, content=n.content, created_date=n.created_at)
                a = a+1
            except:
                #print("Didnt work:  ", n.author.name, n.content, n.created_at)
                i = i+1
                pass
        
    print("Fetch successful")
    print(str(a) + " messages success")
    print(str(i) + " messages failed")
    print(str(b) + " messages were commands/links\n")
    
    
@bot.command()
async def sus(ctx, member: discord.Member):
    if ctx.author.id == ctx.me.id:
        return    
    
    id = member.id
    
    list = []
    sep = "\n"
    
    try:
        user = User.get(id=id)
        for message in user.messages:
            list.append(message.content)
    except:
        await ctx.send("User has database entries yet")
        return
    
    markovText = sep.join(list)

    nlines = markovText.count("\n")
    
    text_model = markovify.NewlineText(markovText)
    
    #Handling webhooks
    #webhooks = await ctx.channel.webhooks()
    #webhook = utils.get(webhooks, name = "sus")
    #if webhook == None:
    #    webhook = await ctx.channel.create_webhook(name = "sus")
    
    #Handling black-/whitelists 
    #if ctx.channel.name in BLACKLIST or ctx.author.name not in USER_WHITELIST:
    #    return
    
    #Sending message 
    await ctx.message.delete()
    
    i=0
    msg = None
    while msg is None:

        filtered = text_model.make_short_sentence(280)

        for badWord in config.get("lists", "word_blacklist"):
            if badWord not in filtered:
                continue
            else:
                msg = None
    
        msg = filtered
        
        i = i+1
        if i == 500:
            #await webhook.send("Failed to generate text, try again", username = member.display_name, avatar_url = member.avatar_url)
            await hook(ctx, member, "Failed to generate text, try again")
            return
    
    if msg is None:
        #await webhook.send("Failed to generate text, try again", username = member.display_name, avatar_url = member.avatar_url)
        await hook(ctx, member, "Failed to generate text, try again")
        return

    await hook(ctx, member, msg)
    #await webhook.send(msg.replace("@", ""), username = member.display_name, avatar_url = member.avatar_url)


@bot.command()
async def sussy(ctx, id):
    if ctx.author.id == ctx.me.id:
        return
    
    list = []
    sep = "\n"
    
    try:
        user = User.get(id=id)
        for message in user.messages:
            list.append(message.content)
    except:
        await ctx.send("User has database entries yet")
        return
    
    markovText = sep.join(list)
    
    text_model = markovify.NewlineText(markovText)
    
    #Handling webhooks
    webhooks = await ctx.channel.webhooks()
    webhook = utils.get(webhooks, name = "sus")
    if webhook == None:
        webhook = await ctx.channel.create_webhook(name = "sus")
    
    #Handling black-/whitelists 
    #if ctx.channel.name in BLACKLIST or ctx.author.name not in USER_WHITELIST:
    #    return
    
    #Sending message 
    await ctx.message.delete()
    
    i=0
    msg = None
    while msg is None:
        msg = text_model.make_short_sentence(280)
        i = i+1
        if i == 500:
            await ctx.send("Failed to generate text, try again")
            return
    
    if msg is None:
        await ctx.send("Failed to generate text, try again")
        return
    
    await ctx.send(msg.replace("@", "@_"))



@bot.command()
async def whitelist(ctx):
    await ctx.send("This command isnt ready yet!")
    return
    if ctx.author.id == ctx.me.id:
        return
    
    if member == None:
        return
    
    newList = config.get("lists", "user_whitelist")
    print(newList)
    
    if newList :
        List = str(member.id)
    else:
        List = newList + "," + str(member.id)
    
    config["lists"]["user_whitelist"] = List 
    
    updateList()
    
@bot.command()
async def say(ctx, *content):
    await ctx.message.delete()
    if ctx.author.id == ctx.me.id:
        return
    
    if content == "" or content == None:
        await ctx.send("You need to specify something to say!")
        
    msg = ""
    
    for n in content:
        msg = msg + ' ' + n
    
    print("I worked this many times")
    await hook(ctx, ctx.author, msg)
    
@bot.command()
async def info(ctx, member: discord.Member):
    await ctx.message.delete()
    if ctx.author.id == ctx.me.id:
        return    
    
    id = member.id
    
    list = []
    sep = "\n"
    
    try:
        user = User.get(id=id)
        for message in user.messages:
            list.append(message.content)
    except:
        await ctx.send("User has database entries yet")
        return
    
    markovText = sep.join(list)

    nlines = markovText.count("\n")

    msg = member.display_name + " has " + str(nlines) + " messages in the database"

    await hook(ctx, member, msg)
    
    
async def hook(ctx, member, content):
    webhooks = await ctx.channel.webhooks()
    webhook = utils.get(webhooks, name = "sus")
    if webhook == None:
        webhook = await ctx.channel.create_webhook(name = "sus")
        
    await webhook.send(content, username = member.display_name, avatar_url = member.avatar_url)

def updateList():
    with open("cfg.ini", "w") as configfile:
        config.write(configfile)


db.connect()
db.create_tables([User, Message])
bot.run(TOKEN)

