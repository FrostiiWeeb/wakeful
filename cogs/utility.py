import discord, datetime, async_cse, psutil, humanize, os, sys
from discord.ext import commands
from utils.configs import color

google = async_cse.Search(os.getenv("GOOGLE"))

class utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["g"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def google(self, ctx, *, term):
        async with ctx.typing():
            if ctx.channel.is_nsfw():
                safe_search_setting=False
                safe_search="disabled"
            else:
                safe_search_setting=True
                safe_search="enabled"
            value=0
            results = await google.search(str(term), safesearch=safe_search_setting)
            em=discord.Embed(
                title=f"results for: `{term}`",
                timestamp=datetime.datetime.utcnow(),
                color=color()
            ).set_footer(text=f"requested by {ctx.author.name}#{ctx.author.discriminator} | safe-search: {safe_search}", icon_url=ctx.author.avatar_url)
            for result in results:
                if not value > 4:
                    epic = results[int(value)]
                    em.add_field(
                        name=f" \uFEFF",
                        value=f"**[{str(epic.title)}]({str(epic.url)})**\n{str(epic.description)}\n",
                        inline=False
                    )
                    value+=1
        await ctx.send(embed=em)

    @commands.command(aliases=["guildav", "servericon", "serverav"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def serveravatar(self, ctx, member : discord.Member = None):
        async with ctx.typing():
            avatar_png = ctx.guild.icon_url_as(format="png")
            avatar_jpg = ctx.guild.icon_url_as(format="jpg")
            avatar_jpeg = ctx.guild.icon_url_as(format="jpeg")
            avatar_webp = ctx.guild.icon_url_as(format="webp")
            if ctx.guild.is_icon_animated():
                avatar_gif = ctx.guild.icon_url_as(format="gif")
            if ctx.guild.is_icon_animated():
                embed=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp}) | [gif]({avatar_gif})", color=color(), timestamp=datetime.datetime.utcnow())
            else:
                embed=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp})", color=color(), timestamp=datetime.datetime.utcnow())
            embed.set_image(url=ctx.guild.icon_url)
            embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["si", "guildinfo", "gi"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def serverinfo(self, ctx):
        online = 0
        dnd = 0
        idle = 0
        offline = 0
        bots = 0
        if ctx.guild.description == None:
            description=""
        else:
            description = ctx.guild.description
        for member in ctx.guild.members:
            if member.bot:
                bots+=1
            elif member.raw_status == "online":
                online += 1
            elif member.raw_status == "dnd":
                dnd += 1
            elif member.raw_status == "offline":
                offline += 1
            elif member.raw_status == "idle":
                idle += 1
        created_at = ctx.guild.created_at.strftime("20%y/%m/%d at %H:%M:%S")
        em=discord.Embed(
            title=ctx.guild.name,
            description=f"{description}",
            timestamp=datetime.datetime.utcnow(),
            color=color()
        ).set_image(url=ctx.guild.banner_url).set_thumbnail(url=ctx.guild.icon_url)
        em.add_field(
            name="members",
            value=f"online: `{online}`\ndnd: `{dnd}`\nidle: `{idle}`\noffline: `{offline}`\nbots: `{bots}`",
            inline=True
        )
        try:
            booster_role = ctx.guild.premium_subscriber_role.mention or "none"
        except AttributeError:
            booster_role = "none"
        em.add_field(
            name="boosts",
            value=f"- amount: `{ctx.guild.premium_subscription_count}`\n- role: {booster_role}",
            inline=True
        )
        em.add_field(
            name="channels",
            value=f"- all `{len(ctx.guild.channels)}`\n- text: `{len(ctx.guild.text_channels)}`\n- voice: `{len(ctx.guild.voice_channels)}`",
            inline=True
        )
        em.add_field(
            name="other",
            value=f"- owner: {ctx.guild.owner.mention}\n- roles: `{len(ctx.guild.roles)}`\n- region: `{ctx.guild.region}`\n- created at: `{created_at}` ({humanize.naturaltime(ctx.guild.created_at)})",
            inline=True
        )
        em.set_footer(
            text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}",
            icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=em)

    @commands.command(aliases=["ui", "whois"], description="A command to get information about the given member", usage="[@member]")
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def userinfo(self, ctx, member : discord.Member = None):
        if member == None:
            member = ctx.author
        #-----------------------------------------------------------
        if not "offline" == str(member.mobile_status):
            mobile_status = self.bot.greenTick
        else:
            mobile_status = self.bot.redTick
        #-----------------------------------------------------------
        if not "offline" == str(member.web_status):
            web_status = self.bot.greenTick
        else:
            web_status = self.bot.redTick
        #-----------------------------------------------------------
        if not "offline" == str(member.desktop_status):
            desktop_status = self.bot.greenTick
        else:
            desktop_status = self.bot.redTick
        #-----------------------------------------------------------
        if member.id == 797044260196319282:
            bot_owner = self.bot.greenTick
        else:
            bot_owner = self.bot.redTick
        #-----------------------------------------------------------
        if member.id == ctx.guild.owner_id:
            guild_owner = self.bot.greenTick
        else:
            guild_owner = self.bot.redTick
        #-----------------------------------------------------------
        if member.bot == True:
            member_bot = self.bot.greenTick
        else:
            member_bot = self.bot.redTick
        #-----------------------------------------------------------
        if member.raw_status == "online":
            member_status = "online"
        elif member.raw_status == "dnd":
            member_status = "dnd"
        elif member.raw_status == "offline":
            member_status = "offline"
        elif member.raw_status == "idle":
            member_status = "idle"
        #-----------------------------------------------------------    
        created_at = member.created_at.strftime("20%y/%m/%d at %H:%M:%S")
        joined_at = member.joined_at.strftime("20%y/%m/%d at %H:%M:%S")
        em=discord.Embed(
            title=member.name + "#" + member.discriminator,
            timestamp=datetime.datetime.utcnow(),
            color=color()
        )
        em.add_field(
            name="info",
            value=f"- name: `{member.name}`\n- tag: `{member.discriminator}`\n- nickname: `{member.display_name}`\n- mention: {member.mention}\n- id: `{member.id}`\n- status: `{member_status}`\n- bot: {member_bot}\n- mobile: {mobile_status}\n- web: {web_status}\n- desktop: {desktop_status}\n- created at: `{created_at}` ({humanize.naturaltime(member.created_at)})\n- avatar: [click here]({member.avatar_url})",
            inline=True
        )
        if member.top_role.name == "@everyone":
            top_role="none"
        else:
            top_role=member.top_role.mention
        em.add_field(
            name="guild",
            value=f"- owner: {guild_owner}\n- roles: `{len(member.roles)}`\n- top role: {top_role}\n- joined at: `{joined_at}` ({humanize.naturaltime(member.joined_at)})",
            inline=False
        )
        if ctx.message.content.endswith("--roles"):
            em.add_field(
                name=f"roles ({len([e for e in ctx.author.roles if not e.name == '@everyone'])})",
                value=", ".join(f"`{e.name}`" for e in reversed(ctx.author.roles) if not e.name == "@everyone"),
                inline=False
            )
        if member.bot:
            try:
                mutual_guilds=len(member.mutual_guilds)
            except AttributeError:
                mutual_guilds=len(self.bot.guilds)
            em.add_field(
                name="other",
                value=f"- bot owner: {bot_owner}\n- mutual guilds: `{mutual_guilds}`",
                inline=False
            )
        else:
            em.add_field(
                name="other",
                value=f"- mutual guilds: `{len(member.mutual_guilds)}`",
                inline=False
            )
        em.set_footer(
            text=f"Requested by {ctx.author.name}#{ctx.author.discriminator}",
            icon_url=ctx.author.avatar_url
        )
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def source(self, ctx):
        em=discord.Embed(description=f"my source code can be found [here](https://github.com/pvffyn/wakeful)", color=color())
        await ctx.send(embed=em)

    @commands.command(aliases=["icon", "av"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx, member : discord.Member = None):
        async with ctx.typing():
            if not member:
                member = ctx.author
            avatar_png = member.avatar_url_as(format="png")
            avatar_jpg = member.avatar_url_as(format="jpg")
            avatar_jpeg = member.avatar_url_as(format="jpeg")
            avatar_webp = member.avatar_url_as(format="webp")
            if member.is_avatar_animated():
                avatar_gif = member.avatar_url_as(format="gif")
            if member.is_avatar_animated():
                embed=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp}) | [gif]({avatar_gif})", color=color(), timestamp=datetime.datetime.utcnow())
            else:
                embed=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp})", color=color(), timestamp=datetime.datetime.utcnow())
            embed.set_image(url=member.avatar_url)
            embed.set_author(name=f"{member}", icon_url=member.avatar_url)
        await ctx.send(embed=embed)

    @commands.command(aliases=["lc"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def lettercount(self, ctx, *, text):
        em=discord.Embed(description=f"your text is {len(text)} letters long", color=color())
        await ctx.send(embed=em)

    @commands.command(aliases=["wc"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def wordcount(self, ctx, *, text):
        text_list = text.split(" ")
        em=discord.Embed(description=f"your text is {len(text_list)} words long", color=color())
        await ctx.send(embed=em)

    @commands.command(aliases=["botinfo", "about", "bi"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx):
        operating_system=None
        if os.name == "nt":
            operating_system = "windows"
        elif os.name == "posix":
            operating_system = "linux"
        await ctx.trigger_typing()
        process = psutil.Process()
        version = sys.version_info
        embed = discord.Embed(color=color())
        delta_uptime = datetime.datetime.utcnow() - self.bot.uptime
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        embed.add_field(name="system", value=f"- **os**: `{operating_system}`\n- **cpu**: `{process.cpu_percent()}`%\n- **memory**: `{humanize.naturalsize(process.memory_full_info().rss).lower()}`\n- **process**: `{process.pid}`\n- **threads**: `{process.num_threads()}`\n- **language**: `python`\n- **python version**: `{version[0]}.{version[1]}.{version[2]}`\n- **discord.py version**: `{discord.__version__}`", inline=True)
        embed.add_field(name="bot", value=f"- **guilds**: `{len(self.bot.guilds)}`\n- **users**: `{len(self.bot.users)}`\n- **commands**: `{len(self.bot.commands)}`\n- **cogs**: `{len(self.bot.cogs)}`\n- **uptime**: `{days}d {hours}h {minutes}m {seconds}s`\n- [**source**](https://github.com/pvffyn/wakeful)", inline=True)
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        msg = await ctx.send(embed=embed)

class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page, color=color())
            await destination.send(embed=emby)

def setup(bot):
    bot.help_command = MyNewHelp()
    bot.add_cog(utility(bot))