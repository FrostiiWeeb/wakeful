import discord, datetime, async_cse, psutil, humanize, os, sys, inspect, mystbin, googletrans, asyncio, aiohttp, random, time, asyncdagpi, hashlib, asyncpg, io, base64
from discord.ext import commands
from discord import Webhook, AsyncWebhookAdapter
from utils.configs import color
from utils.get import *
from utils.checks import *
from jishaku.functools import executor_function
import idevision

@executor_function
def do_translate(output, text):
    """
    You have to install googletrans==3.1.0a0 for it to work, as the dev somehow broke it and it doesn't work else
    """
    translator = googletrans.Translator()
    translation = translator.translate(str(text), dest=str(output))
    return translation

google = async_cse.Search(get_config("GOOGLE"))
mystbinn = mystbin.Client()
dagpi = asyncdagpi.Client(get_config("DAGPI"))
idevisionn = idevision.async_client(get_config("IDEVISION"))

class Utility(commands.Cog):

    """Useful commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        mem=[]
        if message.guild:
            for m in message.guild.members:
                if not m.bot:
                    mem.append(m)
            if "@someone" in message.content:
                if message.author.guild_permissions.mention_everyone:
                    await message.channel.send(random.choice(mem).mention)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.id in list(self.bot.afks):
            self.bot.afks.pop(msg.author.id)
            em=discord.Embed(description=f"Welcome back, {msg.author.mention}, I've unmarked you as afk", color=color())
            await msg.channel.send(embed=em)
        for user in list(self.bot.afks):
            data = self.bot.afks[user]
            obj = self.bot.get_user(user)
            if f"<@!{user}>" in msg.content or f"<@{user}>" in msg.content:
                if data["reason"] is None:
                    mseg = f"Hey! {obj.name} is currently marked as afk"
                else:
                    mseg = f"Hey! {obj.name} is currently marked as afk for `{data['reason']}`"
                em=discord.Embed(description=mseg, color=color())
                await msg.reply(embed=em)

    @commands.Cog.listener()
    async def on_message(self, msg):
        if msg.author.bot:
            return
        if ";;" in msg.content:
            emojis = msg.content.split(";;")
            emoji_ = emojis[1]
            if emoji_ != "" and not " " in emoji_:
                res = await self.bot.db.fetchrow("SELECT commands FROM commands WHERE guild = $1", msg.guild.id)
                try:
                    res["commands"]
                except TypeError:
                    pass
                else:
                    commands = res["commands"]
                    commands = commands.split(",")
                    if len(commands) != 0 and commands != ['']:
                        if "emojis" in commands:
                            return
                        else:
                            pass
                    else:
                        pass
                res = await self.bot.db.fetchrow("SELECT user_id FROM emojis WHERE user_id = $1", msg.author.id)
                try:
                    res["user_id"]
                except TypeError:
                    return
                else:
                    emoji = None
                    for e in self.bot.emojis:
                        if e.name.lower().startswith(emoji_.lower()):
                            emoji = e
                    if emoji is not None:
                        await msg.reply(str(emoji), mention_author=False)

    @commands.group(invoke_without_command=True, aliases=["emoji"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def emojis(self, ctx):
        await ctx.invoke(self.bot.get_command("help"), **{"command": ctx.command})

    @emojis.command(aliases=["opt-in"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def optin(self, ctx):
        try:
            await self.bot.db.execute("INSERT INTO emojis (user_id) VALUES ($1)", ctx.author.id)
        except asyncpg.UniqueViolationError:
            em=discord.Embed(description=f"You've already opted into the emojis program", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"Alright! I've successfully opted you into the emojis program", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @emojis.command(aliases=["opt-out"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def optout(self, ctx):
        res = await self.bot.db.fetchrow("SELECT user_id FROM emojis WHERE user_id = $1", ctx.author.id)
        try:
            res["user_id"]
        except TypeError:
            em=discord.Embed(description=f"You aren't opted into the emojis program", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"Alright! I've successfully opted you out of the emojis program", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(name="sha256")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _sha(self, ctx, *, message):
        res = hashlib.sha256(message.encode()).hexdigest()
        await ctx.reply(f"`{message}` -> `{res}`", mention_author=False)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pypi(self, ctx, package):
        try:
            res = await self.bot.session.get(f"https://pypi.org/pypi/{package}/json")
            json = await res.json()
            name = json["info"]["name"] + " " + json["info"]["version"]
            author = json["info"]["author"] or "None"
            author_email = json["info"]["author_email"] or "None"
            url = json["info"]["project_url"] or "None"
            description = json["info"]["summary"] or "None"
            author = json["info"]["author"] or "None"
            license_ = json["info"]["license"] or "None"
            try:
                documentation = json["info"]["project_urls"]["Documentation"] or "None"
            except:
                documentation = "None"
            try:
                website = json["info"]["project_urls"]["Homepage"] or "None"
            except:
                website = "None"
            keywords = json["info"]["keywords"] or "None"
            em=discord.Embed(
                title=name,
                description=f"{description}\n**Author**: {author}\n**Author Email**: {author_email}\n\n**Website**: {website}\n**Documentation**: {documentation}\n**Keywords**: {keywords}\n**License**: {license_}",
                url=url,
                color=color()
            )
            em.set_thumbnail(url="https://cdn.discordapp.com/attachments/381963689470984203/814267252437942272/pypi.png")
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)
        except aiohttp.ContentTypeError:
            em=discord.Embed(description=f"this package wasn't found", color=color())
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["g"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def google(self, ctx, *, term):
        async with ctx.typing():
            if ctx.channel.is_nsfw():
                safe_search_setting=False
                safe_search="Disabled"
            else:
                safe_search_setting=True
                safe_search="Enabled"
            value=0
            results = await google.search(str(term), safesearch=safe_search_setting)
            em=discord.Embed(
                title=f"Results for: `{term}`",
                timestamp=datetime.datetime.utcnow(),
                color=color()
            )
            em.set_footer(text=f"Requested by {ctx.author} • Safe-Search: {safe_search}", icon_url=ctx.author.avatar_url)
            for result in results:
                if not value > 4:
                    epic = results[int(value)]
                    em.add_field(
                        name=f" \uFEFF",
                        value=f"**[{str(epic.title)}]({str(epic.url)})**\n{str(epic.description)}\n",
                        inline=False
                    )
                    value+=1
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["gimage"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def googleimage(self, ctx, *, query):
        if ctx.channel.is_nsfw():
            safe_search_setting=False
            safe_search="Disabled"
        else:
            safe_search_setting=True
            safe_search="Enabled"
        results = await google.search(query, safesearch=safe_search_setting)
        image = None
        for res in results:
            if res.image_url.endswith("png") or res.image_url.endswith("jpg") or res.image_url.endswith("jpeg") or res.image_url.endswith("webp"):
                image = res
        if image is not None:
            em=discord.Embed(title=f"Results for: `{query}`", description=f"[{image.title}]({image.url})", timestamp=datetime.datetime.utcnow(), color=color())
            em.set_footer(text=f"Requested by {ctx.author} • Safe-Search: {safe_search}", icon_url=ctx.author.avatar_url)
            em.set_image(url=image.image_url)
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"I couldn't find any images with the query `{query}`", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["trans", "tr"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def translate(self, ctx, output : str, *, text : str):
        async with ctx.typing():
            translation = await do_translate(output, text)
            em = discord.Embed(color=color())
            em.add_field(name=f"Input [{translation.src.upper()}]", value=f"```{text}```", inline=False)
            em.add_field(name=f"Output [{translation.dest.upper()}]", value=f"```{translation.text}```", inline=False)
            em.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=em, mention_author=False)

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
                em=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp}) | [gif]({avatar_gif})", color=color(), timestamp=datetime.datetime.utcnow())
            else:
                em=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp})", color=color(), timestamp=datetime.datetime.utcnow())
            em.set_image(url=ctx.guild.icon_url)
            em.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon_url)
        await ctx.send(embed=em)

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
            elif member.raw_status == "Online":
                online += 1
            elif member.raw_status == "Dnd":
                dnd += 1
            elif member.raw_status == "Offline":
                offline += 1
            elif member.raw_status == "Idle":
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
            value=f"Online: `{online}`\nDND: `{dnd}`\nIdle: `{idle}`\nOffline: `{offline}`\nBots: `{bots}`",
            inline=True
        )
        try:
            booster_role = ctx.guild.premium_subscriber_role.mention or "none"
        except AttributeError:
            booster_role = "none"
        em.add_field(
            name="Boosts",
            value=f"- Amount: `{ctx.guild.premium_subscription_count}`\n- Role: {booster_role}",
            inline=True
        )
        em.add_field(
            name="Channels",
            value=f"- All `{len(ctx.guild.channels)}`\n- Text: `{len(ctx.guild.text_channels)}`\n- Voice: `{len(ctx.guild.voice_channels)}`",
            inline=True
        )
        em.add_field(
            name="Other",
            value=f"- Owner: {ctx.guild.owner.mention}\n- Roles: `{len(ctx.guild.roles)}`\n- Ŕegion: `{ctx.guild.region}`\n- Created at: `{created_at}` ({humanize.naturaltime(ctx.guild.created_at)})",
            inline=True
        )
        em.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )
        await ctx.reply(embed=em, mention_author=False)

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
        created_at = member.created_at.strftime("20%y/%m/%d at %H:%M:%S")
        joined_at = member.joined_at.strftime("20%y/%m/%d at %H:%M:%S")
        em=discord.Embed(
            title=member.name + "#" + member.discriminator,
            timestamp=datetime.datetime.utcnow(),
            color=color()
        )
        em.add_field(
            name="info",
            value=f"- Name: `{member.name}`\n- Tag: `{member.discriminator}`\n- Nickname: `{member.display_name}`\n- Mention: {member.mention}\n- ID: `{member.id}`\n- Status: `{member.raw_status}`\n- Bot: {member_bot}\n- Mobile: {mobile_status}\n- Web: {web_status}\n- Desktop: {desktop_status}\n- Created at: `{created_at}` ({humanize.naturaltime(member.created_at)})\n- Avatar: [click here]({member.avatar_url})",
            inline=True
        )
        if member.top_role.name == "@everyone":
            top_role="none"
        else:
            top_role=member.top_role.mention
        em.add_field(
            name="guild",
            value=f"- Owner: {guild_owner}\n- Roles: `{len(member.roles)}`\n- Top Role: {top_role}\n- Joined at: `{joined_at}` ({humanize.naturaltime(member.joined_at)})",
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
                name="Other",
                value=f"- Bot Owner: {bot_owner}\n- Mutual Guilds: `{mutual_guilds}`",
                inline=False
            )
        else:
            em.add_field(
                name="Other",
                value=f"- Mutual guilds: `{len(member.mutual_guilds)}`",
                inline=False
            )
        em.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.avatar_url
        )
        await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def suggest(self, ctx):
        em=discord.Embed(description=f"Please now enter your suggestion below:", color=color())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        msg = await ctx.reply(embed=em, mention_author=False)
        try:
            suggestion = await self.bot.wait_for("message", check=lambda msg: msg.channel == ctx.channel and msg.author == ctx.author, timeout=30)
        except asyncio.TimeoutError:
            em=discord.Embed(description="You took too long to respond, now ignoring next messages", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await msg.edit(embed=em)
        else:
            if suggestion.content.lower() != "cancel":
                webhook = Webhook.from_url(str(self.bot.suggestions), adapter=AsyncWebhookAdapter(self.bot.session))
                em=discord.Embed(description=f"```{suggestion.clean_content}```", color=color())
                em.set_footer(text=f"suggestion by {ctx.author} ({ctx.author.id})", icon_url=ctx.author.avatar_url)
                attachment = None
                if ctx.message.attachments:
                    attachment = ctx.message.attachments[0].url
                if attachment is not None:
                    em.set_image(url=attachment)
                await webhook.send(embed=em)
                await suggestion.add_reaction("✅")
                em=discord.Embed(description="Your suggestion has been sent to the admins\nNote: abuse may get you blacklisted", color=color())
                em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                await msg.edit(embed=em)
            else:
                await msg.delete()



    @commands.command(aliases=["src"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def source(self, ctx, command_name : str = None):
        if command_name == None:
            em=discord.Embed(description=f"My source code can be found [here]({self.bot.github})", color=color())
            await ctx.reply(embed=em, mention_author=False)
        else:
            command = self.bot.get_command(command_name)
            if not command:
                em=discord.Embed(description=f"Couldn't find command `{command_name}`", color=color())
                await ctx.reply(embed=em, mention_author=False)
            else:
                try:
                    source_lines, _ = inspect.getsourcelines(command.callback)
                except (TypeError, OSError):
                    em=discord.Embed(description=f"Couldn't retrieve source for `{command_name}`", color=color())
                    await ctx.reply(embed=em, mention_author=False)
                else:
                    source_lines = ''.join(source_lines).split('\n')
                    src = "\n".join(line for line in source_lines).replace("`", "'")
                    em=discord.Embed(title=f"{command.name} source", description=f"Note: most of the \" ' \" stand for a \" ` \"\n\n```py\n{src}```", color=color(), timestamp=datetime.datetime.utcnow())
                    em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                    try:
                        await ctx.author.send(embed=em)
                    except discord.HTTPException:
                        async with ctx.author.typing():
                            post = await mystbinn.post(src)
                            em=discord.Embed(description=f"Note: most of the \" ' \" stand for a \" ` \"\nThe output was too long so it got uploaded to [mystbin]({post})", color=color(), timestamp=datetime.datetime.utcnow())
                            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                        await ctx.author.send(embed=em)
                    await ctx.message.add_reaction("✅")

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
                em=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp}) | [gif]({avatar_gif})", color=color(), timestamp=datetime.datetime.utcnow())
            else:
                em=discord.Embed(description=f"[png]({avatar_png}) | [jpg]({avatar_jpg}) | [jpeg]({avatar_jpeg}) | [webp]({avatar_webp})", color=color(), timestamp=datetime.datetime.utcnow())
            em.set_image(url=member.avatar_url)
            em.set_author(name=f"{member}", icon_url=member.avatar_url)
        await ctx.send(embed=em)

    @commands.command(aliases=["lc"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def lettercount(self, ctx, *, text):
        em=discord.Embed(description=f"Your text is {len(text)} letters long", color=color())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["wc"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def wordcount(self, ctx, *, text):
        text_list = text.split(" ")
        em=discord.Embed(description=f"Your text is {len(text_list)} words long", color=color())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def invite(self, ctx):
        em=discord.Embed(description=f"Here's my [invite](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot)", color=color())
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["botinfo", "about", "bi"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def info(self, ctx):
        operating_system=None
        if os.name == "nt":
            operating_system = "Windows"
        elif os.name == "posix":
            operating_system = "Linux"
        async with ctx.typing():
            process = psutil.Process()
            version = sys.version_info
            em = discord.Embed(color=color())
            delta_uptime = datetime.datetime.utcnow() - self.bot.uptime
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            channels = 0
            for guild in self.bot.guilds:
                for channel in guild.channels:
                    channels += 1
            cogs = []
            if ctx.guild is not None:
                disabled = await self.bot.db.fetchrow("SELECT commands FROM commands WHERE guild = $1", ctx.guild.id)
                try:
                    disabled = disabled["commands"]
                except:
                    pass
                else:
                    disabled = disabled.split(",")
            else:
                disabled = []
            for cog in self.bot.cogs:
                cog = get_cog(self.bot, cog)
                if not cog.qualified_name.lower() in ["jishaku"]:
                    if is_mod(self.bot, ctx.author):
                        cmds = [cmd for cmd in cog.get_commands()]
                    else:
                        cmds = [cmd for cmd in cog.get_commands() if not cmd.hidden and not cmd.name in disabled]
                    if len(cmds) != 0 and cmds != []:
                        cogs.append(cog)
            owner = self.bot.get_user(self.bot.ownersid)
            em.add_field(name="System", value=f"""
- **OS**: `{operating_system}`
- **CPU**: `{process.cpu_percent()}`%
- **Memory**: `{humanize.naturalsize(process.memory_full_info().rss)}`
- **Process**: `{process.pid}`
- **Threads**: `{process.num_threads()}`
- **Language**: `Python`
- **Python version**: `{version[0]}.{version[1]}.{version[2]}`
- **discord.py version**: `{discord.__version__}`""", inline=True)
            em.add_field(name="Bot", value=f"""
- **Guilds**: `{len(self.bot.guilds)}`
- **Users**: `{len(self.bot.users)}`
- **Channels**: `{channels}`:
- **Shards**: `{len(list(self.bot.shards))}`
- **Commands**: `{len([cmd for cmd in self.bot.commands if not cmd.hidden])}`
- **Commands executed**: `{self.bot.cmdsSinceRestart}`
- **Cogs**: `{len(cogs)}`
- **Uptime**: `{days}d {hours}h {minutes}m {seconds}s`""", inline=True)
            em.add_field(name="Links", value=f"""
- [Developer](https://discord.com/users/{owner.id})
- [Source]({self.bot.github})
- [Invite](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot)
""", inline=False)
            em.set_thumbnail(url=self.bot.user.avatar_url)
        em.set_footer(text=f"Made by {owner}", icon_url=owner.avatar_url)
        await ctx.send(embed=em)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def unspoiler(self, ctx, *, msg : str = None):
        if msg is None:
            if ctx.message.reference:
                text = ctx.message.reference.resolved.clean_content
        else:
            text = msg
        await ctx.reply(text.replace("|", ""), mention_author=False, allowed_mentions=discord.AllowedMentions.none())
    
    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def spoiler(self, ctx, *, msg : str = None):
        if msg is None:
            if ctx.message.reference:
                text = ctx.message.reference.resolved.clean_content
        else:
            text = msg
        await ctx.reply("".join(f"||{letter}||" for letter in text), mention_author=False, allowed_mentions=discord.AllowedMentions.none())
    
    @commands.command(aliases=["rp", "activity", "richpresence", "status"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def presence(self, ctx, member : discord.Member = None):
        if member is None:
            member = ctx.author
        em=discord.Embed(title=f"{member.name}'s activities", color=color(), timestamp=datetime.datetime.utcnow())
        for activity in member.activities:
            if isinstance(activity, discord.activity.Spotify):
                artists = ", ".join(artist for artist in activity.artists)
                duration = activity.duration
                days, seconds = duration.days, duration.seconds
                hours = days * 24 + seconds // 3600
                minutes = (seconds % 3600) // 60
                seconds = seconds % 60
                em.add_field(
                    name="Spotify",
                    value=f"""
Title: `{activity.title}`
Artists: `{artists}`
Album: `{activity.album}`
Album Cover: [url]({activity.album_cover_url})
Duration: `{hours}`h `{minutes}`m `{seconds}`s
""",
                    inline=False
                )
            elif isinstance(activity, discord.activity.CustomActivity):
                if activity.emoji != None:
                    emoji = f"[url]({activity.emoji.url})"
                    emojiName = f"`{activity.emoji.name}`"
                else:
                    emoji = "`None`"
                    emojiName = "`None`"
                em.add_field(
                    name="Custom",
                    value=f"""
Text: `{activity.name}`
Emoji Name: {emojiName}
Emoji: {emoji}
""",
                    inline=False
                )
            elif isinstance(activity, discord.activity.Game):
                em.add_field(
                    name="Game",
                    value=f"Name: `{activity.name}`",
                    inline=False
                )
            elif isinstance(activity, discord.activity.Streaming):
                em.add_field(
                    name="Stream",
                    value=f"""
Title: `{activity.name}`
Platform: `{activity.platform}`
URL: [{activity.url.split("/")[3]}]({activity.url})
""",
                    inline=False
                )
            else:
                try:
                    type = str(activity.type).lower().split("activitytype.")[1].title()
                except:
                    type = "None"
                em.add_field(
                    name="Unknown",
                    value=f"""
Name: `{activity.name}`
Details: `{activity.details}`
Emoji: `{activity.emoji}`
Type: `{type}`
""",
                    inline=False
                )
        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
        await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def snipe(self, ctx):
        try:
            msg = self.bot.message_cache[ctx.guild.id][ctx.channel.id]
        except KeyError:
            em=discord.Embed(description=f"There's no message to snipe", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"`{msg.content}`", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            em.set_author(name=f"{msg.author} ({msg.author.id})", icon_url=msg.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["ss"])
    @commands.is_nsfw()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def screenshot(self, ctx, website):
        async with ctx.typing():
            res = await self.bot.session.get(f"https://api.screenshotmachine.com?key={get_config('screenshot')}&url={website}&dimension=1280x720&user-agent=Mozilla/5.0 (Windows NT 10.0; rv:80.0) Gecko/20100101 Firefox/80.0")
            res = io.BytesIO(await res.read())
            em=discord.Embed(color=color(), timestamp=datetime.datetime.utcnow())
            em.set_image(url="attachment://screenshot.jpg")
            em.set_footer(text=f"Powered by screenshotapi.net • {ctx.author}", icon_url=ctx.author.avatar_url)
        msg = await ctx.reply(embed=em, file=discord.File(res, "screenshot.jpg"), mention_author=False)
        await msg.add_reaction("🚮")
        reaction, user = await self.bot.wait_for("reaction_add", check=lambda reaction, user: str(reaction.emoji) == "🚮" and reaction.message == msg and not user.bot)
        await msg.delete()
        em=discord.Embed(description=f"The screenshot has been deleted by {user.mention}", color=color(), timestamp=datetime.datetime.utcnow())
        await ctx.reply(embed=em, mention_author=False)


    @commands.command()
    @commands.cooldown(1,5, commands.BucketType.user)
    async def disabled(self, ctx):
        res = await self.bot.db.fetchrow("SELECT commands FROM commands WHERE guild = $1", ctx.guild.id)
        try:
            res["commands"]
        except TypeError:
            em=discord.Embed(description=f"There are no disabled commands", color=color())
            await ctx.reply(embed=em, mention_author=False)
        else:
            commands = res["commands"]
            commands = commands.split(",")
            if len(commands) != 0 and commands != ['']:
                em=discord.Embed(title="Disabled commands", description=", ".join(cmd for cmd in commands if cmd != ""), color=color())
                em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=em, mention_author=False)
            else:
                em=discord.Embed(description=f"There are no disabled commands", color=color())
                await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["rtfd"])
    @commands.cooldown(1,5,commands.BucketType.user)
    async def rtfm(self, ctx, query):
        async with ctx.typing():
            res = await self.bot.session.get(f"https://idevision.net/api/public/rtfm?query={query}&location=https://discordpy.readthedocs.io/en/latest&show-labels=false&label-labels=false")
            print(res.text)
            print(res.status)
            res = await res.json()
            nodes = res["nodes"]
        if nodes != {}:
            em=discord.Embed(description="\n".join(f"[`{e}`]({nodes[e]})" for e in nodes), color=color())
            em.set_footer(text=f"Powered by idevision.net • {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"No results found for `{query}`", color=color())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    @commands.cooldown(1,5,commands.BucketType.user)
    async def weather(self, ctx, state):
        state = state.replace(" ", "%20")
        async with ctx.typing():
            location = await self.bot.session.get(f"https://www.metaweather.com/api/location/search/?query={state}")
            location = await location.json()
            try:
                woeid = location[0]["woeid"]
            except:
                em=discord.Embed(description=f"I couldn't retrieve the weather for `{state}`", color=color())
                em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=em, mention_author=False)
            else:
                results = await google.search(location[0]["title"], safesearch=True)
                image = None
                for res in results:
                    if res.image_url.endswith("png") or res.image_url.endswith("jpg") or res.image_url.endswith("jpeg") or res.image_url.endswith("webp"):
                        image = res.image_url
                res = await self.bot.session.get(f"https://www.metaweather.com/api/location/{woeid}")
                res = await res.json()
                res = res["consolidated_weather"][0]
                em=discord.Embed(title=location[0]["title"], description=f"""
Type: `{res["weather_state_name"]}`
Wind Direction: `{res["wind_direction_compass"]}`
Temperature: `{round(int(res["the_temp"]), 1)}`
Minimum Temperature: `{round(int(res["min_temp"]), 1)}`
Maximum Temperature: `{round(int(res["max_temp"]), 1)}`
Wind Speed: `{round(int(res["wind_speed"]), 1)}`
Air Pressure: `{round(int(res["air_pressure"]), 1)}`
Humidity: `{res["humidity"]}`
Visibility: `{round(int(res["visibility"]), 1)}`
""", color=color())
                if image is not None:
                    em.set_thumbnail(url=image)
                em.set_footer(text=f"Powered by metaweather.com • {ctx.author}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=em, mention_author=False)

    @commands.command(aliases=["shard", "shards"])
    @commands.cooldown(1,15,commands.BucketType.user)
    async def shardinfo(self, ctx, shard : int = None):
        if shard is None:
            em=discord.Embed(title="Shards", color=color())
            for shard in list(self.bot.shards):
                shard = dict(self.bot.shards)[shard]
                em.add_field(
                    name=f"Shard {shard.id+1}",
                    value=f"""
Latency: `{round(shard.latency, 1)}`ms
Count: `{shard.shard_count}`
""", inline=True
                )
            await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def help(self, ctx, *, command : str = None):
        if command is None:
            em=discord.Embed(
                title="Help Page",
                description=f'''
```diff
- Type "{ctx.prefix}help [command]" or "{ctx.prefix}help [cog]" for more information about a command or cog
+ [argument] for an optional argument
+ <argument> for a required argument
```
[Developer](https://discord.com/users/{self.bot.ownersid}) | [Support]({self.bot.invite}) | [Invite](https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot)
''',
                timestamp=datetime.datetime.utcnow(),
                color=color()
            )
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            if ctx.guild is not None:
                disabled = await self.bot.db.fetchrow("SELECT commands FROM commands WHERE guild = $1", ctx.guild.id)
                try:
                    disabled = disabled["commands"]
                except:
                    pass
                else:
                    disabled = disabled.split(",")
            else:
                disabled = []
            cogs = []
            for cog in self.bot.cogs:
                cog = get_cog(self.bot, cog)
                if not cog.qualified_name.lower() in ["jishaku"]:
                    if is_mod(self.bot, ctx.author):
                        cmds = [cmd for cmd in cog.get_commands()]
                    else:
                        cmds = [cmd for cmd in cog.get_commands() if not cmd.hidden and not cmd.name in disabled]
                    if len(cmds) != 0 and cmds != []:
                        cogs.append(cog)
            em.add_field(
                name=f"Cogs [{len(cogs)}]",
                value="\n".join(f"`{cog.qualified_name}`" for cog in cogs),
                inline=True
            )
            operating_system=None
            if os.name == "nt":
                operating_system = "Windows"
            elif os.name == "posix":
                operating_system = "Linux"
            process = psutil.Process()
            delta_uptime = datetime.datetime.utcnow() - self.bot.uptime
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)
            em.add_field(
                name="Information",
                value=f"""
**Uptime**: `{days}d {hours}h {minutes}m {seconds}s`
**Commands**: `{len([cmd for cmd in self.bot.commands if not cmd.hidden])}`
**Shards**: `{len(list(self.bot.shards))}`
**Memory**: `{humanize.naturalsize(process.memory_full_info().rss)}`
""",
                inline=True
            )
            em.set_image(url=self.bot.banner)
            await ctx.reply(embed=em, mention_author=False)
        else:
            if self.bot.get_command(str(command)) is not None:
                given_command = self.bot.get_command(str(command))
                disabled = await self.bot.db.fetchrow("SELECT commands FROM commands WHERE guild = $1", ctx.guild.id)
                try:
                    disabled = disabled["commands"]
                except:
                    pass
                else:
                    disabled = disabled.split(",")
                if not given_command.hidden == True and not given_command.name in disabled or is_mod(self.bot, ctx.author):
                    #-------------------------------------
                    try:
                        command_subcommands = "> " + ", ".join(f"`{command.name}`" for command in given_command.commands if not command.hidden or not command.name in disabled)
                    except:
                        command_subcommands = "None"
                    #-------------------------------------
                    if given_command.usage:
                        command_usage = given_command.usage
                    else:
                        parameters = {}
                        for param in list(given_command.params):
                            if not param in ["self", "ctx"]:
                                parameter = dict(given_command.params)[str(param)]
                                if parameter.kind.name.lower() == "positional_or_keyword":
                                    parameters[str(param)] = "required"
                                else:
                                    parameters[str(param)] = "optional"
                        command_usage = " ".join(f"<{param}>" if dict(parameters)[param] == "required" else f"[{param}]" for param in list(parameters))
                    #---------------------------------------
                    em=discord.Embed(
                        title=given_command.name,
                        timestamp=datetime.datetime.utcnow(),
                        description=given_command.description,
                        color=color()
                    )
                    em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                    em.add_field(name="Usage", value=f"{ctx.prefix}{given_command.name} {command_usage}", inline=False)
                    if given_command.aliases:
                        em.add_field(name=f"Aliases [{len(given_command.aliases)}]", value="> " + ", ".join(f"`{alias}`" for alias in given_command.aliases), inline=False)
                    else:
                        em.add_field(name="Aliases [0]", value="None", inline=False)
                    try:
                        if is_mod(self.bot, ctx.author):
                            commands_ = [cmd for cmd in given_command.commands]
                        else:
                            commands_ = [cmd for cmd in given_command.commands if not cmd.hidden and not cmd.name in disabled]
                    except:
                        commands_ = "None"
                    try:
                        em.add_field(name=f"Subcommands [{len(commands_)}]", value=command_subcommands, inline=False)
                    except AttributeError:
                        em.add_field(name=f"Subcommands [0]", value="None", inline=False)
                    em.add_field(name="Category", value=given_command.cog_name, inline=False)
                    em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                    await ctx.reply(embed=em, mention_author=False)
                else:
                    em=discord.Embed(description=f"This command does not exist", color=color())
                    em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                    await ctx.reply(embed=em, mention_author=False)
            else:
                disabled = await self.bot.db.fetchrow("SELECT commands FROM commands WHERE guild = $1", ctx.guild.id)
                try:
                    disabled = disabled["commands"]
                except:
                    pass
                else:
                    disabled = disabled.split(",")
                given_cog = get_cog(self.bot, command)
                if given_cog is not None:
                    if is_mod(self.bot, ctx.author):
                        commands_ = [cmd for cmd in given_cog.walk_commands() if cmd.parent is None]
                    else:
                        commands_ = [cmd for cmd in given_cog.walk_commands() if not cmd.hidden and not cmd.name in disabled and cmd.parent is None]
                    if commands_ is not None and commands_ != []:
                        em=discord.Embed(title=f"{given_cog.qualified_name} commands [{len(commands_)}]", description=f"{given_cog.description}\n\n> "+", ".join(f"`{cmd.name}`" for cmd in commands_), color=color())
                        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                        em.set_image(url=self.bot.banner)
                        await ctx.reply(embed=em, mention_author=False)
                    else:
                        em=discord.Embed(description=f"There isn't a cog / command with the name `{command}`", color=color())
                        em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                        await ctx.reply(embed=em, mention_author=False)
                else:
                    em=discord.Embed(description=f"There isn't a cog / command with the name `{command}`", color=color())
                    em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                    await ctx.reply(embed=em, mention_author=False)

    @commands.group(invoke_without_command=True)
    @commands.cooldown(1,10,commands.BucketType.user)
    async def minecraft(self, ctx, username):
        uid = await self.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uid.status == 200:
            uid = await uid.json()
            name = uid["name"]
            uid = uid["id"]
            em=discord.Embed(title=name, description=f"""
Name: `{name}`
UID: `{uid}`
""", color=color(), timestamp=datetime.datetime.utcnow(), url=f"https://namemc.com/profile/{name}")
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            em.set_thumbnail(url=f"https://crafatar.com/avatars/{uid}?default=MHF_Steve&overlay&size=256")
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"I couldn't find a player with the name `{username}`", color=color(), timestamp=datetime.datetime.utcnow())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @minecraft.command()
    @commands.cooldown(1,10,commands.BucketType.user)
    async def avatar(self, ctx, username):
        uid = await self.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uid.status == 200:
            uid = await uid.json()
            name = uid["name"]
            uid = uid["id"]
            em=discord.Embed(title=f"{name}'s avatar", color=color(), timestamp=datetime.datetime.utcnow(), url=f"https://namemc.com/profile/{name}")
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            em.set_image(url=f"https://crafatar.com/avatars/{uid}?default=MHF_Steve&overlay&size128")
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"I couldn't find a player with the name `{username}`", color=color(), timestamp=datetime.datetime.utcnow())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @minecraft.command()
    @commands.cooldown(1,10,commands.BucketType.user)
    async def skin(self, ctx, username):
        uid = await self.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uid.status == 200:
            uid = await uid.json()
            name = uid["name"]
            uid = uid["id"]
            em=discord.Embed(title=f"{name}'s skin", color=color(), timestamp=datetime.datetime.utcnow(), url=f"https://namemc.com/profile/{name}")
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            em.set_image(url=f"https://crafatar.com/renders/body/{uid}?default=MHF_Steve&overlay&scale=5")
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"I couldn't find a player with the name `{username}`", color=color(), timestamp=datetime.datetime.utcnow())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @minecraft.command()
    @commands.cooldown(1,10,commands.BucketType.user)
    async def head(self, ctx, username):
        uid = await self.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uid.status == 200:
            uid = await uid.json()
            name = uid["name"]
            uid = uid["id"]
            em=discord.Embed(title=f"{name}'s head", color=color(), timestamp=datetime.datetime.utcnow(), url=f"https://namemc.com/profile/{name}")
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            em.set_image(url=f"https://crafatar.com/renders/head/{uid}?default=MHF_Steve&overlay&scale=5")
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"I couldn't find a player with the name `{username}`", color=color(), timestamp=datetime.datetime.utcnow())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @minecraft.command()
    @commands.cooldown(1,10,commands.BucketType.user)
    async def friends(self, ctx, username):
        uid = await self.bot.session.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")
        if uid.status == 200:
            uid = await uid.json()
            name = uid["name"]
            uid = uid["id"]
            res = await self.bot.session.get(f"https://api.namemc.com/profile/{uid}/friends")
            res = await res.json()
            if res != []:
                em=discord.Embed(title=f"{name}'s friends", color=color(), timestamp=datetime.datetime.utcnow(), url=f"https://namemc.com/profile/{name}")
                em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                for friend in list(res):
                    em.add_field(
                        name=friend["name"],
                        value=f"""
Name: `{friend['name']}`
UUID: `{friend['uuid']}`
[NameMC](https://namemc.com/profile/{friend['name']})
""",
                        inline=True
                    )
                await ctx.reply(embed=em, mention_author=False)
            else:
                em=discord.Embed(description=f"`{name}` has no friends on namemc.com", color=color(), timestamp=datetime.datetime.utcnow(), url=f"https://namemc.com/profile/{name}")
                em.set_thumbnail(url=f"https://crafatar.com/avatars/{uid}?default=MHF_Steve&overlay&size=256")
                em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
                await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"I couldn't find a player with the name `{username}`", color=color(), timestamp=datetime.datetime.utcnow())
            em.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        em=discord.Embed(color=color())
        dagpi_ping = round(await dagpi.image_ping(), 3) * 1000
        em.add_field(name="latency", value=f"""
- **Typing**: `pinging`
- **Bot**: `{round(self.bot.latency*1000)}`ms
- **Database**: `pinging`
- **Dagpi**: `{dagpi_ping}`ms""", inline=False)
        start=time.perf_counter()
        msg = await ctx.send(embed=em)
        end=time.perf_counter()
        final=end-start
        api_latency = round(final*1000)
        em=discord.Embed(color=color())
        poststart = time.perf_counter()
        await self.bot.db.fetch("SELECT 1")
        postduration = (time.perf_counter() - poststart) * 1000
        db_ping = round(postduration, 1)
        em.add_field(name="latency", value=f"""
- **Typing**: `{api_latency}`ms
- **Bot**: `{round(self.bot.latency*1000)}`ms
- **Database**: `{db_ping}`ms
- **Dagpi**: `{dagpi_ping}`ms""", inline=False)
        await msg.edit(embed=em)

    @commands.command()
    async def afk(self, ctx, *, reason : str = None):
        if reason is None:
            msg = f"Okay, I've marked you as afk"
        else:
            msg = f"Okay, I've marked you as afk for `{reason}`"
        em=discord.Embed(description=msg, color=color())
        await ctx.reply(embed=em, mention_author=False)
        await asyncio.sleep(3)
        self.bot.afks[ctx.author.id] = {"reason": reason}

    @commands.command()
    @commands.cooldown(1,10,commands.BucketType.user)
    async def ocr(self, ctx, member : discord.Member = None):
        if member is None:
            if ctx.message.attachments:
                if ctx.message.attachments[0].url.endswith("png") or ctx.message.attachments[0].url.endswith("jpg") or ctx.message.attachments[0].url.endswith("jpeg") or ctx.message.attachments[0].url.endswith("webp"):
                    url = ctx.message.attachments[0].proxy_url or ctx.message.attachments[0].url
                else:
                    url = ctx.author.avatar_url_as(format="png", size=1024)
            else:
                url = ctx.author.avatar_url_as(format="png", size=1024)
        else:
            url = member.avatar_url_as(format="png", size=1024)

        url = url.replace("cdn.discordapp.com", "media.discordapp.com")

        res = await self.bot.session.get(url)

        image = await res.read()

        if url.endswith("png"):
            filetype = "png"
        elif url.endswith("jpg"):
            filetype = "jpg"
        elif url.endswith("jpeg"):
            filetype = "jpeg"
        elif url.endswith("webp"):
            filetype = "webp"
        else:
            filetype = None
        
        async with ctx.typing():
            res = await idevisionn.ocr(image, filetype=filetype)

        if res != "":
            em=discord.Embed(description=f"`{res}`", color=color())
            em.set_footer(text=f"Powered by idevision.net • {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.reply(embed=em, mention_author=False)
        else:
            em=discord.Embed(description=f"I couldn't read what your image says", color=color())
            await ctx.reply(embed=em, mention_author=False)

def setup(bot):
    bot.add_cog(Utility(bot))