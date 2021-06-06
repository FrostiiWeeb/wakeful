import os, tempfile, discord
from jishaku.functools import executor_function

@executor_function
def makeFile(text, end):
    file_ = tempfile.NamedTemporaryFile()
    file_.write(text.encode())
    file_.seek(os.SEEK_SET)
    yield discord.File(file_.name, filename=f"message.{end}")
    file_.close()

async def getFile(text, end = "txt"):
    result = await makeFile(text, end)
    return list(set(result))[0]

async def makeEmbed(channel : discord.TextChannel, embed : discord.Embed, mention : bool = False):
    embed = embed.to_dict()
    file_ = None
    if len(embed["description"]) > 1024:
        file_ = getFile(embed["description"])
    if file_ is not None:
        await channel.reply(embed=discord.Embed().from_dict(embed), mention_author=mention, file=file_)
    else:
        embed["description"] == "The description was too large, so I've put it into a file"
        await channel.reply(embed=discord.Embed().from_dict(embed), mention_author=mention)