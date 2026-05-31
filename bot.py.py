import discord
from discord.ext import commands
from discord.ui import Button, View
import datetime
import os

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)

# --- SISTEMA DE TICKET ---
class CloseTicketView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Fechar Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket", emoji="🔒")
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Este ticket será fechado em alguns segundos...", ephemeral=True)
        await interaction.channel.delete(reason="Ticket fechado pelo usuário.")

class TicketPanelBackground(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Abrir Suporte", style=discord.ButtonStyle.success, custom_id="open_ticket", emoji="🎟️")
    async def ticket_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        channel_name = f"ticket-{member.name}".lower().replace(" ", "-")
        
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        if existing_channel:
            return await interaction.response.send_message(f"Você já possui um ticket aberto em {existing_channel.mention}!", ephemeral=True)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
        await interaction.response.send_message(f"Ticket criado com sucesso em {ticket_channel.mention}!", ephemeral=True)

        embed = discord.Embed(
            title="🎫 Atendimento Iniciado",
            description=f"Olá {member.mention}, seja bem-vindo ao seu suporte.\nExplique sua dúvida ou problema abaixo e aguarde a equipe.",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_footer(text="Painel de Tickets")
        await ticket_channel.send(content=f"{member.mention} | Equipe", embed=embed, view=CloseTicketView())

# --- EVENTOS ---
@bot.event
async def on_ready():
    bot.add_view(TicketPanelBackground())
    bot.add_view(CloseTicketView())
    print(f"🤖 Bot {bot.user.name} está online!")
    await bot.change_presence(activity=discord.Game(name="!ajuda para ver comandos"))

# --- COMANDOS GERAIS ---
@bot.command()
@commands.has_permissions(administrator=True)
async def criarticket(ctx):
    await ctx.message.delete()
    embed = discord.Embed(
        title="👋 Central de Atendimento",
        description="Precisa de ajuda, suporte ou tirar dúvidas?\n\n**Clique no botão abaixo** para abrir um ticket privado.",
        color=discord.Color.green()
    )
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    await ctx.send(embed=embed, view=TicketPanelBackground())

@bot.command()
async def ping(ctx):
    latencia = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong!", description=f"Minha latência é de `{latencia}ms`", color=discord.Color.green())
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"ℹ️ Informações de {guild.name}", color=discord.Color.blue())
    embed.add_field(name="Membros", value=f"`{guild.member_count}`", inline=True)
    embed.add_field(name="Canais", value=f"`{len(guild.channels)}`", inline=True)
    embed.add_field(name="Dono", value=guild.owner.mention, inline=True)
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)

# --- COMANDOS DE MODERAÇÃO ---
@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🗑️ `{amount}` mensagens deletadas por {ctx.author.mention}.", delete_after=5)

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, motivo="Não informado"):
    await member.kick(reason=motivo)
    embed = discord.Embed(title="👢 Membro Expulso", color=discord.Color.orange())
    embed.add_field(name="Usuário", value=member.mention)
    embed.add_field(name="Staff", value=ctx.author.mention)
    embed.add_field(name="Motivo", value=motivo)
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, motivo="Não informado"):
    await member.ban(reason=motivo)
    embed = discord.Embed(title="🔨 Membro Banido", color=discord.Color.red())
    embed.add_field(name="Usuário", value=member.mention)
    embed.add_field(name="Staff", value=ctx.author.mention)
    embed.add_field(name="Motivo", value=motivo)
    await ctx.send(embed=embed)

# --- AJUDA ---
@bot.command()
async def ajuda(ctx):
    embed = discord.Embed(title="📚 Painel de Comandos", color=discord.Color.purple())
    embed.add_field(name="🎟️ Suporte", value="`!criarticket` - Envia o painel de tickets.", inline=False)
    embed.add_field(name="⚙️ Utilidades", value="`!ping` - Mostra a latência.\n`!serverinfo` - Detalhes do servidor.", inline=False)
    embed.add_field(name="🛡️ Moderação", value="`!clear [nº]` - Limpa o chat.\n`!kick [@membro]` - Expulsa alguém.\n`!ban [@membro]` - Bane alguém.", inline=False)
    await ctx.send(embed=embed)

TOKEN = os.environ.get("DISCORD_TOKEN")
bot.run(TOKEN)