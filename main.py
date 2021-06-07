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


TOKEN = os.getenv("DISCORD_TOKEN")
bot = commands.Bot(command_prefix='$')

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
async def fetch(ctx, member: discord.Member):
    if ctx.author.id == ctx.me.id:
        return
    
    #Scraping history
    messages = await ctx.channel.history(limit=None).flatten()
    for n in messages:
        if n.content == '' or validators.url(n.content):
            continue
        
        if '$fetch' in n.content or '$sus' in n.content:
            continue
        
        if n.author.id == member.id:
            try:
                user = User.get(User.id == n.author.id)
            except User.DoesNotExist:
                user = User.create(id=n.author.id, username=n.author)
            
            try:
                Message.create(user=user, id=n.id, content=n.content, created_date=n.created_at)
                print(n.author, n.content)
            except:
                pass
        
    print("Fetch successfull")
    
    
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
        ctx.send("User has typed any messages yet")
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
    
    msg = None
    while msg is None:
        msg = text_model.make_short_sentence(280)
    
    if msg is None:
        await webhook.send("Failed to generate text, try again", username = member.name, avatar_url = member.avatar_url)
        return
    
    await webhook.send(msg, username = member.name, avatar_url = member.avatar_url)
    print(msg)

@bot.command()
async def whitelist(ctx, member: discord.Member):
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
    

def updateList():
    with open("cfg.ini", "w") as configfile:
        config.write(configfile)


db.connect()
db.create_tables([User, Message])
bot.run(TOKEN)

