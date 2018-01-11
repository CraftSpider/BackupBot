"""
    Bot to backup a discord server. Can do just one channel, or whole server at once.

    author: CraftSpider
"""

import discord
import discord.ext.commands as commands
import zipfile
import os


def readlines_reverse(filename):
    with open(filename, encoding='utf-8') as qfile:
        qfile.seek(0, os.SEEK_END)
        position = qfile.tell()
        line = ''
        while position >= 0:
            qfile.seek(position)
            try:
                next_char = qfile.read(1)
            except UnicodeDecodeError:
                position -= 1
                continue
            if next_char == "\n":
                yield line[::-1]
                line = ''
            else:
                line += next_char
            position -= 1
        yield line[::-1]


def reverse_string(string, prefix=""):
    return prefix + ("\n" + prefix).join(reversed(string.split("\n")))


def message_formatter(message):
    if message.type == discord.MessageType.new_member:
        return "Member " + str(message.author) + " joined the server.\n"
    out = ""
    for attachment in message.attachments:
        out += "    Attached File: " + attachment.filename + "\n"
    for embed in message.embeds:
        out += "    " + "-" * 15 + "\n"
        out += "    Footer: " + str(embed.footer.text) + "\n"
        for field in embed.fields:
            out += "        - " + str(field.name) + " - " + reverse_string(str(field.value)) + "\n"
        out += "    Fields:\n"
        out += reverse_string("Description: " + str(embed.description), "    ") + "\n"
        out += "    Title: " + str(embed.title) + "\n"
        out += "    Author: " + str(embed.author.name) + "\n"
        out += "    -----Embed-----\n"
    out += reverse_string("<" + str(message.author) + "> " + message.content) + "\n"
    return out


bot = commands.Bot(command_prefix="^")

@bot.event
async def on_ready():
    print('| Now logged in as')
    print('| {}'.format(bot.user.name))
    print('| {}'.format(bot.user.id))

@bot.command()
async def channel_log(ctx):
    filename = "{}_log.txt".format(ctx.channel)
    try:
        with open(filename + ".temp", "a+b") as file:
            async for message in ctx.channel.history(limit=None):
                file.write(message_formatter(message).encode('utf-8'))
        with open(filename, "w", encoding='utf-8') as file:
            for line in readlines_reverse(filename + ".temp"):
                file.write(line + "\n")
        file = discord.File(filename)
        await ctx.send("Here's your channel log file:", file=file)
    finally:
        try:
            os.remove(filename + ".temp")
        except FileNotFoundError:
            pass
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass


@bot.command()
@commands.guild_only()
async def guild_log(ctx):
    files = []
    for channel in ctx.guild.channels:
        if isinstance(channel, discord.TextChannel):
            filename = "{}_log.txt".format(ctx.channel)
            try:
                with open(filename + ".temp", "a+b") as file:
                    async for message in ctx.channel.history(limit=None):
                        file.write(message_formatter(message).encode('utf-8'))
                with open(filename, "w", encoding='utf-8') as file:
                    for line in readlines_reverse(filename + ".temp"):
                        file.write(line + "\n")
                files.append(filename)
            finally:
                try:
                    os.remove(filename + ".temp")
                except FileNotFoundError:
                    pass
    with zipfile.ZipFile("guild_log.zip", "w") as file:
        for filename in files:
            file.write(filename)
    file = discord.File("guild_log.zip")
    await ctx.send("Here's your guild-wide log file:", file=file)
    for file in files:
        try:
            os.remove(file)
        except FileNotFoundError:
            pass
    try:
        os.remove("guild_log.zip")
    except FileNotFoundError:
        pass



bot.run("")
