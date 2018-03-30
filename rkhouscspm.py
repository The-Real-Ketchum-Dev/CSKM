import json
import subprocess
import os
import sys, traceback
import configparser
import MySQLdb
import discord
from discord.ext import commands
import asyncio
from pokemonlist import pokemon, pokejson
from config import bot_channel, token, host, user, password, database, website, log_channel
from datetime import datetime
from datetime import timedelta
import calendar
import logging
from datetime import time
from datetime import date
import datetime
## CREATED BY @rkhous#1447

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

bot = commands.Bot(command_prefix = '^')#set prefix

database = MySQLdb.connect(host,user,password,database)
cursor = database.cursor()

@bot.event
async def on_ready():
    print()
    print()
    print("Login successful.")
    print("-----------------")
    print("CSPM by @rkhous#1447")
    print("-----------------")
    print("BotUser = "+str(bot.user))
    print("-----------------")
    print("-----started-----")
    print("The time is now")
    print(datetime.datetime.now())

def find_pokemon_id(name):
    if name == 'Nidoran-F':
        return 29
    elif name == 'Nidoran-M':
        return 32
    elif name == 'Mr-Mime':
        return 122
    elif name == 'Ho-Oh':
        return 250
    elif name == 'Mime-Jr':
        return 439
    else:
        name = name.split('-')[0]
        for k in pokejson.keys():
            v = pokejson[k]
            if v == name:
                return int(k)
        return 0

def find_pokecp(name):
    with open('pokecp.json') as f:
        data = json.load(f)
        return (data[str(name).capitalize()])

#raid function
@bot.command(pass_context=True)
async def raid(ctx, arg, arg2, arg3, arg4):#arg = gym name, arg2 = pokemon name, arg3 = level, arg4 = time remaining
    if ctx and ctx.message.channel.id == str(bot_channel) and str(arg2).lower() in pokemon:
        """example: ^raid "Canandagua National Bank Clock Tower" Lugia 5 45"""

        pokemon_id = find_pokemon_id(str(arg2).capitalize())
        pokecp = find_pokecp(str(arg2).capitalize())
        now = datetime.datetime.utcnow() + timedelta(minutes=int(arg4))
        time = datetime.datetime.utcnow() + timedelta(minutes=1)

        try:
            cursor.execute("SELECT gym_id FROM gymdetails WHERE name LIKE '" + str(arg) + "%';")
            gym_id = str(cursor.fetchall())
            gym_id = gym_id.split(',')
            gym_id = gym_id[0].split('((')
            cursor.execute("REPLACE INTO raid("
                           "gym_id, level, spawn, start, "
                           "end, pokemon_id, cp, move_1, "
                           "move_2, last_scanned)"
                           " VALUES ("+str('{}').format(gym_id[1])+", "+str(arg3)+", "+str("'{}'").format(time)+", "+str("'{}'").format(time)+", "+str("'{}'").format(now)+", "+str(pokemon_id)+", "+str(pokecp)+", 1, 1, "+str("'{}'").format(time)+");")
                           #"VALUES (%s, %s, "+str("'{}'").format(time)+", "+str("'{}'").format(time)+", "+str("'{}'").format(now)+", %s, %s, 1, 1, "+str("'{}'").format(time)+");", (str(gym_id[1]), str(pokemon_id), str(arg3), str(arg5)))
            database.commit()
            await bot.say('Successfully added your raid to the live map.')
            await bot.send_message(discord.Object(id=log_channel), str(ctx.message.author.name) + ' said there was a ' + str(arg2) +
                                   ' raid going on at ' + str(arg)) and print(str(ctx.message.author.name) + ' said there was a ' + str(arg2) +
                                   ' raid going on at ' + str(arg))
            #await bot.send_message(discord.Object(id=log_channel), str(ctx.message.author.name) + " VALUES ("+str('{}').format(gym_id[1])+", "+str(arg3)+", "+str("'{}'").format(time)+", "+str("'{}'").format(time)+", "+str("'{}'").format(now)+", "+str(pokemon_id)+", "+str(arg5)+", 1, 1, "+str("'{}'").format(time)+");")
            #await bot.send_message(discord.Object(id=log_channel), str(ctx.message.author.name) + " INSERT INTO raid(gym_id, level, spawn, start, end, pokemon_id, cp, move_1, move_2, last_scanned)")

        except:
            database.rollback()
            await bot.say('Unsuccesful in database query, your raid was not added to the live map.')
            await bot.say("Could not find `{}` in my database. Please check your gym name. \nuse `^gym gym-name` to try and look it up".format(arg))
            tb = traceback.print_exc(file=sys.stdout)
            print(tb)


@bot.command(pass_context=True)
async def gym(ctx, arg):
    cursor.execute("SELECT name FROM gymdetails WHERE name LIKE '" + str(arg) + "%';")
    gym_name = str(cursor.fetchall())
    msg = "`{}`".format(gym_name)
    database.commit()
    await bot.send_message(discord.Object(id=log_channel), msg)

@bot.command()
async def commands():
    await bot.say("```^gym -- show gyms like name provided, also a way to know if they are in the db.\n       Example: ^gym \"Calvary Chapel Of The Finger Lakes\"\n\n"
                  "^raid -- input raid into database so that it shows on map for all to see\n\n"
                  "^example -- shows an example of an input\n\n"
                  "gym names must be in \"quotes\"```")

@bot.command()
async def example():
    await bot.say("```^raid \"Canandagua National Bank Clock Tower\" Lugia 5 45\n"
                  "'gym-name' poke-name level time-remaining```")

@bot.command()
async def cp(arg):
    with open('pokecp.json') as f:
        data = json.load(f)
        await bot.say(data[str(arg).capitalize()])

bot.run(token)
