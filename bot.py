import discord
from discord.ext import commands
import os
import utils_ec2

bot = commands.Bot(command_prefix='!')


@bot.group()
async def vh(ctx):
    await ctx.invoke(bot.get_command(f'valheim {ctx.invoked_subcommand}'))

@bot.group()
async def valheim(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.invoke(bot.get_command('valheim help'))

@valheim.command()
async def help(ctx):
    await ctx.send('help: !valheim start/stop/restart/status')

@valheim.command()
async def start(ctx):
    await ctx.send('starting server...')
    instances, num = utils_ec2.check_ec2_instances()
    utils_ec2.start_ec2(instances)
    ctx.invoke(bot.get_command('valheim status'))

@valheim.command()
async def stop(ctx):
    await ctx.send('stopping server...')
    instances, num = utils_ec2.check_ec2_instances()
    utils_ec2.stop_ec2(instances)
    ctx.invoke(bot.get_command('valheim status'))

@valheim.command()
async def restart(ctx):
    await ctx.send('restarting server...')
    instances, num = utils_ec2.check_ec2_instances()
    utils_ec2.restart_ec2(instances)
    ctx.invoke(bot.get_command('valheim status'))

@valheim.command()
async def status(ctx):
    await ctx.send('checking status...')
    instances, num = utils_ec2.check_ec2_instances()
    fstr = utils_ec2.status_ec2(instances)
    await ctx.send(fstr)


bot.run(os.getenv('DISCORD_TOKEN'))