import discord
from discord.ext import commands
import os
import asyncio
import utils
import datetime
from pytz import timezone
tz = timezone('EST')

bot = commands.Bot(command_prefix='!')


@bot.group(aliases=['vh'])
async def valheim(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.invoke(bot.get_command('valheim help'))

@valheim.command()
async def help(ctx):
    await ctx.send('help: !valheim start/stop/restart/status')

@valheim.command()
async def start(ctx):
    await ctx.send('starting server...')
    instances, num = utils.check_ec2_instances()
    utils.start_ec2(instances)
    await asyncio.sleep(10)
    await ctx.invoke(bot.get_command('valheim status'))

@valheim.command()
async def stop(ctx):
    await ctx.send('stopping server...')
    instances, num = utils.check_ec2_instances()
    utils.stop_ec2(instances)
    await ctx.invoke(bot.get_command('valheim status'))

@valheim.command()
async def restart(ctx):
    await ctx.send('restarting server...')
    instances, num = utils.check_ec2_instances()
    utils.restart_ec2(instances)
    await asyncio.sleep(10)
    await ctx.invoke(bot.get_command('valheim status'))

@valheim.command()
async def status(ctx):
    await ctx.send('checking status...')
    instances, num = utils.check_ec2_instances()
 
    if num == 0:
        await ctx.send('No EC2 instances found.')
    else:
        records = utils.list_r53_a_records()

        for instance in instances:
            server = utils.get_r53_dns_name(records, instance.public_ip_address)
            color = 0xff0000

            if instance.state['Name'] == 'running':
                color = 0x00ff00

            message = discord.Embed(title='Server Status', color=color)
            message.set_thumbnail(url='https://static.wikia.nocookie.net/valheim/images/d/d9/Rested.png')
            message.add_field(name='Server', value=server)
            message.add_field(name='IP', value=instance.public_ip_address)
            message.add_field(name='Status', value=instance.state['Name'].upper())
            message.set_footer(text=instance.id)
            message.timestamp = datetime.datetime.now(tz)
            await ctx.send(embed=message)
            

bot.run(os.getenv('DISCORD_TOKEN'))