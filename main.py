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

with open("text") as f:
    text = f.read()


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
    content = peewee.TextField()
    created_date = peewee.DateTimeField(default=datetime.datetime.now)


@bot.command()
async def fetch(ctx, arg):
    if ctx.author == ctx.me:
        pass
    
    #Scraping history
    messages = await ctx.channel.history(limit=10).flatten()
    for n in messages:
        if n.content == '' or validators.url(n.content):
            return
        
        try:
            user = User.get(User.id == n.author.id)
        except User.DoesNotExist:
            user = User.create(id=n.author.id, username=n.author)
        
        Message.create(user=user, content=n.content, created_date=n.created_at)
    
    
@bot.command()
async def sus(ctx, member: discord.Member):
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
    
    text_model = markovify.NewlineText(f)
    
    #Handling webhooks
    webhooks = await ctx.channel.webhooks()
    webhook = utils.get(webhooks, name = "sus")
    if webhook == None:
        webhook = await ctx.channel.create_webhook(name = "sus")
    
    #Handling black-/whitelists 
    #if ctx.channel.name in BLACKLIST or ctx.author.name not in USER_WHITELIST:
    #    return
    #Sending message   
    #await webhook.send(text_model.make_sentence(), username = ctx.author.name, avatar_url = ctx.author.avatar_url)

    await ctx.send(markovText)
    print(text_model.make_sentence())
    

db.connect()
db.create_tables([User, Message])
bot.run(TOKEN)

