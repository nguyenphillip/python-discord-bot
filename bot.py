import discord
from discord.ext import commands
import os

bot = commands.Bot(command_prefix='!')


@bot.group()
async def valheim(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.invoke(bot.get_command('valheim help'))

@valheim.command()
async def help(ctx):
    await ctx.send('help: !valheim start/stop/restart/status')

@valheim.command()
async def start(ctx):
    await ctx.send('starting... test')

@valheim.command()
async def stop(ctx):
    await ctx.send('stopping... test')

@valheim.command()
async def restart(ctx):
    await ctx.send('restart... test')    

@valheim.command()
async def status(ctx):
    await ctx.send('status... test')





bot.run(os.getenv('DISCORD_TOKEN'))