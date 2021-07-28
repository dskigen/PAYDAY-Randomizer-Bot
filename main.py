# Test
import discord
import json
import time
import sqlite3 as sql
import os

from discord.ext import commands
from discord.ext.commands import cooldown, BucketType, has_permissions, CheckFailure
import random

prefix = "!"  # Changing this will change the prefix that the bot will listen for
uses = 0  # This will be tracking how many times the bot gets used -- it's mainly so I can see if its worthwhile to
# develop updates for or if the bot has died down

############################################### JSON FILE LOADING

with open("heists.json", "r") as json_file:
    heist_dict = json.load(json_file)

with open("loudheists.json", "r") as json_file:
    lheist_dict = json.load(json_file)

with open("stealthheists.json", "r") as json_file:
    sheist_dict = json.load(json_file)

with open("primaries.json", "r") as json_file:
    prim_dict = json.load(json_file)

with open("secondaries.json", "r") as json_file:
    sec_dict = json.load(json_file)

with open("throwables.json", "r") as json_file:
    throw_dict = json.load(json_file)

with open("perk.json", "r") as json_file:
    perk_dict = json.load(json_file)

with open("deployable.json", "r") as json_file:
    deploy_dict = json.load(json_file)

with open("armor.json", "r") as json_file:
    armor_dict = json.load(json_file)

with open("smallmelee.json", "r") as json_file:
    smelee_dict = json.load(json_file)

with open("largemelee.json", "r") as json_file:
    lmelee_dict = json.load(json_file)

with open("skills.json", "r") as json_file:
    skill_dict = json.load(json_file)

############################################# BOT SETUP THINGS

intents = discord.Intents(typing=True, presences=True, guilds=True,
                          members=True, reactions=True, messages=True,
                          invites=True, bans=True)

client = discord.Client()
client = commands.Bot(command_prefix=prefix, case_insensitive=True, intents=intents)
client.remove_command('help')

############################################# SQL DATABASE CREATION

path = os.path.dirname(os.path.realpath(__file__))

conn = sql.connect(path + 'whitelisted.db')
c = conn.cursor()

try:  # In the case the database ever needs to be fully wiped, this will set it up again.
    c.execute("CREATE TABLE channels (serverId int, channelId int)")
    print("Database for channels was wiped, setting up database.")
except sql.OperationalError as e:
    print("Database for channels loaded, no errors.")


############################################# START WHITELIST RELATED FUNCTIONS

def addToWhitelist(serverId, channelId):
    values = (serverId, channelId)
    c.execute(f"INSERT INTO channels VALUES (?, ?)", values)
    conn.commit()
    print(f"New channel added to whitelist: {channelId}")
    print("____________________________________________")


def removeFromWhitelist(channelId):
    query = f"DELETE FROM channels WHERE channelId = ?"
    c.execute(query, (channelId,))
    conn.commit()
    print(f"Channel removed from whitelist: {channelId}")
    print("____________________________________________")


def getAllChannels(guildId):
    query = f"SELECT channelId FROM channels WHERE serverId = ?"
    c.execute(query, (guildId,))
    output = c.fetchall()
    return output


def isChannelWhitelisted(channelId, guildId):
    output = getAllChannels(guildId)
    channelGood = False
    for x in output:
        if channelId in x:
            channelGood = True
            break
    return channelGood


#############################################  SOME FUNCTIONS


def checkThrow(perk):
    perk = perk['name']
    if perk == "Kingpin":
        throw = "Injector"
    elif perk == "Sicario":
        throw = "Smoke Bomb"
    elif perk == "Stoic":
        throw = "Stoic's Flask"
    elif perk == "Tag Team":
        throw = "Gas Dispenser"
    elif perk == "Hacker":
        throw = "Pocket ECM"
    else:
        throw = random.choice(throw_dict)
        throw = throw['name']
    return throw


def common_data(list1, list2):
    result = False
    # traverse in the 1st list
    for x in list1:
        # traverse in the 2nd list
        for y in list2:
            # if one common
            if x == y:
                result = True
                return result
    return result

############################################# BOT SETUP

@client.event
async def on_ready():
    activity = discord.Game(name="!help for help", type=3)
    await client.change_presence(status=discord.Status.online, activity=activity)
    print("__________________________")
    print("Ready to do some gamering")
    print("__________________________")

############################################# START OF THE ACTUAL COMMANDS

@client.command()
async def help(ctx):
    embed = discord.Embed(color=discord.Color.random(), title="All commands")
    embed.add_field(name="!build (!b)",
                    value="Gives you a random build (weapons, throwables, perk deck, deployables",
                    inline=False)
    embed.add_field(name="!skills [!s]", value="Gives you random skill allocation.", inline=False)
    embed.add_field(name="!full [!f]", value="Gives you a random build and skill allocation simultaniously.", inline=False)
    embed.add_field(name="!heist [!h]", value="Gives you a random heist to play, including stealth and loud only heists.", inline=False)
    embed.add_field(name="!stealthHeist [!sh]", value="Gives you a random stealth-able heist to play.",
                    inline=False)
    embed.add_field(name="!loudHeist [!lh]", value="Gives you a random loud-able heist to play.",
                    inline=False)
    embed.add_field(name="Admin Commands", value="These require the permission 'Administrator' to be used.",
                    inline=False)
    embed.add_field(name="!whitelist [!wl]", value="Will tell you whether or not the bot can be used in this channel.",
                    inline=False)
    embed.add_field(name="!whitelistAdd [!wla]", value="Adds the channel to the whitelist.", inline=False)
    embed.add_field(name="!whitelistRemove [!wlr]", value="Removes the channel from the whitelist", inline=False)
    embed.set_footer(text="A bot by Soariticus#0666, modified by scout#0001")
    await ctx.send(embed=embed)


@client.command(aliases=['b'])
@commands.cooldown(1, 1, commands.BucketType.user)
async def build(ctx):
    if isChannelWhitelisted(ctx.message.channel.id, ctx.message.guild.id):  # FUCK SAKE
        global uses
        uses = uses + 1
        await ctx.message.delete()

        prim = random.choice(prim_dict)
        sec = random.choice(sec_dict)
        perk = random.choice(perk_dict)
        throw = checkThrow(perk)
        armor = random.choice(armor_dict)
        deploy = random.choice(deploy_dict)
        smelee = random.choice(smelee_dict)
        lmelee = random.choice(lmelee_dict)
        moreDeploy = random.randrange(0, 100)
        ICTV = random.randrange(0, 100)
        deploy2 = None
        if ICTV > 92:
            armor = {"name": "Improved Combined Tactical Vest"}
        if moreDeploy >= 90:
            deploy2 = random.choice(deploy_dict)
            while deploy == deploy2:
                deploy2 = random.choice(deploy_dict)
            deploy2 = deploy2['name']
        if not deploy2:
            deploy2 = "None"

        embed = discord.Embed(color=discord.Colour.random(), title=f"For {ctx.author.name}",
                              description="A completely random build!")
        embed.add_field(name="Primary", value=f"{prim['type']}: {prim['name']}")
        embed.add_field(name="Secondary", value=f"{sec['type']}: {sec['name']}")
        embed.add_field(name="Throwable", value=throw)
        embed.add_field(name="Perk Deck", value=perk['name'])
        embed.add_field(name="Primary Deployable", value=deploy['name'])
        embed.add_field(name="Secondary Deployable", value=deploy2)
        embed.add_field(name="Armor", value=armor['name'])
        embed.add_field(name="Small Melee", value=smelee['name'])
        embed.add_field(name="Large Melee", value=lmelee['name'])
        embed.set_footer(text="A bot by Soariticus#0666, modified by scout#0001")
        await ctx.send(embed=embed)
    else:
        await ctx.message.delete()
        await ctx.send("Please use a whitelisted channel (!whitelist / !wl) to interact with me! (If your server has "
                       "none, request an admin to add some channels to the whitelist, instructions can be found under !help)")


@client.command(aliases=["h"])
@commands.cooldown(1, 1, commands.BucketType.user)
async def heist(ctx):
    if isChannelWhitelisted(ctx.message.channel.id, ctx.message.guild.id):
        global uses
        uses = uses + 1
        await ctx.message.delete()
        heist = random.choice(heist_dict)
        embed = discord.Embed(color=discord.Colour.random(), title=heist['name'])
        embed.add_field(name=f"For {ctx.message.author.name}", value="Good luck!")
        await ctx.send(embed=embed)
    else:
        await ctx.message.delete()
        await ctx.send("Please use a whitelisted channel (!whitelist / !wl) to interact with me! (If your server has "
                       "none, request an admin to add some channels to the whitelist, instructions can be found under !help)")

@client.command(aliases=["sh"])
@commands.cooldown(1, 1, commands.BucketType.user)
async def stealthHeist(ctx):
    if isChannelWhitelisted(ctx.message.channel.id, ctx.message.guild.id):
        global uses
        uses = uses + 1
        await ctx.message.delete()
        heist = random.choice(sheist_dict)
        embed = discord.Embed(color=discord.Colour.random(), title=heist['name'])
        embed.add_field(name=f"For {ctx.message.author.name}", value="Keep it quiet!")
        await ctx.send(embed=embed)
    else:
        await ctx.message.delete()
        await ctx.send("Please use a whitelisted channel (!whitelist / !wl) to interact with me! (If your server has "
                       "none, request an admin to add some channels to the whitelist, instructions can be found under !help)")


@client.command(aliases=["lh"])
@commands.cooldown(1, 1, commands.BucketType.user)
async def loudHeist(ctx):
    if isChannelWhitelisted(ctx.message.channel.id, ctx.message.guild.id):
        global uses
        uses = uses + 1
        await ctx.message.delete()
        heist = random.choice(lheist_dict)
        embed = discord.Embed(color=discord.Colour.random(), title=heist['name'])
        embed.add_field(name=f"For {ctx.message.author.name}", value="Make sure to pack some ammo!")
        await ctx.send(embed=embed)
    else:
        await ctx.message.delete()
        await ctx.send("Please use a whitelisted channel (!whitelist / !wl) to interact with me! (If your server has "
                       "none, request an admin to add some channels to the whitelist, instructions can be found under !help)")


@client.command(aliases=["wla"], pass_context=True)
@has_permissions(administrator=True)
async def whitelistAdd(ctx):
    await ctx.message.delete()
    guildId = ctx.message.guild.id
    channelId = ctx.message.channel.id
    addToWhitelist(guildId, channelId)
    await ctx.send(f"Successfully added channel <#{channelId}> to the whitelist.")


@client.command(aliases=["wlr"], pass_context=True)
@has_permissions(administrator=True)
async def whitelistRemove(ctx):
    await ctx.message.delete()
    channelId = ctx.message.channel.id
    removeFromWhitelist(channelId)
    await ctx.send(f"Successfully removed channel <#{channelId}> from the whitelist.")


@client.command(aliases=["wl"])
async def whitelist(ctx):
    await ctx.message.delete()
    result = isChannelWhitelisted(ctx.message.channel.id, ctx.message.guild.id)
    if result:
        output = f"This channel **is** on the whitelist."
    else:
        output = f"This channel is **not** on the whitelist."
    await ctx.send(output)


@client.command()
async def devOutput(ctx):
    await ctx.message.delete()
    if ctx.message.author.id == 638494850861367296:
        me = client.get_user(638494850861367296)
        await me.send(f"{uses} || {time.time()}")


@commands.cooldown(1, 1, commands.BucketType.user)
@client.command(aliases=['s'])
async def skills(ctx):
    uses = + 1
    await ctx.message.delete()
    if isChannelWhitelisted(ctx.message.channel.id, ctx.message.guild.id):
        forced = ["x", "x", "x"]
        banned = ["x", "x", "x"]

        while (common_data(forced, banned)):
            forced[0] = random.choice(skill_dict)
            forced[1] = random.choice(skill_dict)
            forced[2] = random.choice(skill_dict)

            banned[0] = random.choice(skill_dict)
            banned[1] = random.choice(skill_dict)
            banned[2] = random.choice(skill_dict)

        embed = discord.Embed(title=f"For {ctx.message.author.name}", color=discord.Color.random())
        embed.add_field(name="Forced Skills", value="These **MUST** be picked in your build! (If a skill rolls twice, you must ace it)", 
                        inline=False)
        embed.add_field(name="1st Forced:", value=f"{forced[0]['tree']}: {forced[0]['name']}", inline=True)
        embed.add_field(name="2nd Forced:", value=f"{forced[1]['tree']}: {forced[1]['name']}", inline=True)
        embed.add_field(name="3rd Forced:", value=f"{forced[2]['tree']}: {forced[2]['name']}", inline=True)

        embed.add_field(name="Banned Skills", value="These are **NOT** allowed to be picked in your build! (If a skill rolls twice, lucky you)",
                        inline=False)
        embed.add_field(name="1st Banned:", value=f"{banned[0]['tree']}: {banned[0]['name']}", inline=True)
        embed.add_field(name="2nd Banned:", value=f"{banned[1]['tree']}: {banned[1]['name']}", inline=True)
        embed.add_field(name="3rd Banned:", value=f"{banned[2]['tree']}: {banned[2]['name']}", inline=True)
        embed.set_footer(text="A bot by Soariticus#0666, modified by scout#0001")

        await ctx.send(embed=embed)
    else:
        await ctx.send("Please use a whitelisted channel (!whitelist / !wl) to interact with me! (If your server has "
                       "none, request an admin to add some channels to the whitelist, instructions can be found under !help)")

@client.command(aliases=['f'])
@commands.cooldown(1, 5, commands.BucketType.user)
async def full(ctx):
    uses = + 1;
    await ctx.message.delete()
    if isChannelWhitelisted(ctx.message.channel.id, ctx.message.guild.id):
        prim = random.choice(prim_dict)
        sec = random.choice(sec_dict)
        perk = random.choice(perk_dict)
        throw = checkThrow(perk)
        armor = random.choice(armor_dict)
        deploy = random.choice(deploy_dict)
        smelee = random.choice(smelee_dict)
        lmelee = random.choice(lmelee_dict)
        moreDeploy = random.randrange(0, 100)
        ICTV = random.randrange(0, 100)
        deploy2 = None
        if ICTV > 92:
            armor = {"name": "Improved Combined Tactical Vest"}
        if moreDeploy >= 90:
            deploy2 = random.choice(deploy_dict)
            while deploy == deploy2:
                deploy2 = random.choice(deploy_dict)
            deploy2 = deploy2['name']
        if not deploy2:
            deploy2 = "None"

        embed = discord.Embed(color=discord.Colour.random(), title=f"For {ctx.author.name}",
                              description="A completely random build!")
        embed.add_field(name="Primary", value=f"{prim['type']}: {prim['name']}", inline=True)
        embed.add_field(name="Secondary", value=f"{sec['type']}: {sec['name']}", inline=True)
        embed.add_field(name="Throwable", value=throw, inline=True)
        embed.add_field(name="Perk Deck", value=perk['name'], inline=True)
        embed.add_field(name="Primary Deployable", value=deploy['name'], inline=True)
        embed.add_field(name="Secondary Deployable", value=deploy2, inline=True)
        embed.add_field(name="Armor", value=armor['name'], inline=True)
        embed.add_field(name="Small Melee", value=smelee['name'])
        embed.add_field(name="Large Melee", value=lmelee['name'])
        
        forced = ["x", "x", "x"]
        banned = ["x", "x", "x"]

        while (common_data(forced, banned)):
            forced[0] = random.choice(skill_dict)
            forced[1] = random.choice(skill_dict)
            forced[2] = random.choice(skill_dict)

            banned[0] = random.choice(skill_dict)
            banned[1] = random.choice(skill_dict)
            banned[2] = random.choice(skill_dict)
        
        embed.add_field(name="Forced Skills", value="These **MUST** be picked in your build! (If a skill rolls twice, you must ace it)", 
                        inline=False)
        embed.add_field(name="1st Forced:", value=f"{forced[0]['tree']}: {forced[0]['name']}", inline=True)
        embed.add_field(name="2nd Forced:", value=f"{forced[1]['tree']}: {forced[1]['name']}", inline=True)
        embed.add_field(name="3rd Forced:", value=f"{forced[2]['tree']}: {forced[2]['name']}", inline=True)

        embed.add_field(name="Banned Skills", value="These are **NOT** allowed to be picked in your build! (If a skill rolls twice, lucky you)",
                        inline=False)
        embed.add_field(name="1st Banned:", value=f"{banned[0]['tree']}: {banned[0]['name']}", inline=True)
        embed.add_field(name="2nd Banned:", value=f"{banned[1]['tree']}: {banned[1]['name']}", inline=True)
        embed.add_field(name="3rd Banned:", value=f"{banned[2]['tree']}: {banned[2]['name']}", inline=True)
        embed.set_footer(text="A bot by Soariticus#0666, modified by scout#0001")

        await ctx.send(embed=embed)
    else:
        await ctx.send("Please use a whitelisted channel (!whitelist / !wl) to interact with me! (If your server has "
                       "none, request an admin to add some channels to the whitelist, instructions can be found under !help)")

################################################## ERROR HANDLING

@build.error
async def build(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.delete()
        em = discord.Embed(title=f"Slow it down.", description=f"Try again in {error.retry_after:.2f}s.")
        await ctx.send(embed=em)


@heist.error
async def heist(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.delete()
        em = discord.Embed(title=f"Slow it down.", description=f"Try again in {error.retry_after:.2f}s.")
        await ctx.send(embed=em)


@stealthHeist.error
async def stealthHeist(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.delete()
        em = discord.Embed(title=f"Slow it down.", description=f"Try again in {error.retry_after:.2f}s.")
        await ctx.send(embed=em)

@loudHeist.error
async def loudHeist(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.message.delete()
        em = discord.Embed(title=f"Slow it down.", description=f"Try again in {error.retry_after:.2f}s.")
        await ctx.send(embed=em)


@whitelistAdd.error
async def whitelistAdd(ctx, error):
    await ctx.message.delete()
    em = discord.Embed(title=f"Insufficient permissions", description=f"You require the permission 'Administrator' "
                                                                      f"for this command")
    await ctx.send(embed=em)


@whitelistRemove.error
async def whitelistRemove(ctx, error):
    await ctx.message.delete()
    em = discord.Embed(title=f"Insufficient permissions", description=f"You require the permission 'Administrator' "
                                                                      f"for this command")
    await ctx.send(embed=em)

@full.error
async def full(ctx, error):
    await ctx.message.delete()
    em = discord.Embed(title=f"Slow it down.", description=f"Try again in {error.retry_after:.2f}s.")
    await ctx.send(embed=em)

client.run('INSERT TOKEN HERE')
