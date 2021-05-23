import discord
from colorama import Fore
from discord.ext import commands
from utils.configs import color

class errors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed=discord.Embed(description=f"this command is on cooldown, try again in `{round(error.retry_after, 1)}` seconds.", color=color())
            await ctx.send(embed=embed)
        elif isinstance(error, commands.MissingRequiredArgument):
            embed=discord.Embed(description=f"`{error.param}` is a required parameter that is missing", color=color())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(description=f"```{error}```", color=color())
            await ctx.send(embed=embed)
            raise error


def setup(bot):
    bot.add_cog(errors(bot))