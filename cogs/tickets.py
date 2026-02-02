import discord, yaml, io
from discord.ext import commands

with open("config.yml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

def es_owner(member):
    return any(r.name == config["OwnerRole"] for r in member.roles)

class TicketSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Allies", emoji="🤝", value="allies"),
            discord.SelectOption(label="Support", emoji="🛠️", value="support"),
            discord.SelectOption(label="Replace", emoji="🔁", value="replace"),
            discord.SelectOption(label="Producto no entregado", emoji="📦", value="no_entregado")
        ]
        super().__init__(placeholder="Selecciona una opción para comenzar...", options=options)

    async def callback(self, interaction):
        guild = interaction.guild
        user = interaction.user

        cat = discord.utils.get(guild.categories, name=config["Tickets"]["Categoria"])
        if not cat:
            cat = await guild.create_category(config["Tickets"]["Categoria"])

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }

        owner_role = discord.utils.get(guild.roles, name=config["OwnerRole"])
        if owner_role:
            overwrites[owner_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        channel = await guild.create_text_channel(f"ticket-{user.name}", category=cat, overwrites=overwrites)
        await channel.send(f"{user.mention} ticket creado.", view=TicketControls())
        await interaction.response.send_message(f"✅ Ticket creado: {channel.mention}", ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketSelect())

class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Cerrar", emoji="🔒", style=discord.ButtonStyle.red)
    async def cerrar(self, interaction, button):
        if not es_owner(interaction.user):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)

        transcript = ""
        async for msg in interaction.channel.history(oldest_first=True):
            transcript += f"[{msg.created_at}] {msg.author}: {msg.content}\n"

        file = discord.File(io.StringIO(transcript), filename="transcript.txt")
        logs = interaction.guild.get_channel(config["Tickets"]["CanalLogs"])
        if logs:
            await logs.send(file=file)

        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @discord.app_commands.command(name="panel", description="Enviar panel de tickets")
    async def panel(self, interaction):
        if not es_owner(interaction.user):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)

        embed = discord.Embed(
            title="🎫 Iberic House | Customer Support",
            description=(
                "👋 **Bienvenido al sistema de soporte oficial de Iberic House**\n\n"
                "Selecciona el tipo de asistencia que necesitas en el menú inferior.\n"
                "Nuestro equipo revisará tu solicitud lo antes posible.\n\n"
                "⬇️ **Selecciona una opción para comenzar**"
            ),
            color=discord.Color.from_rgb(255,255,255)
        )

        embed.set_image(url="https://cdn.discordapp.com/attachments/1456619337627734130/1467978284334583992/ChatGPT_Image_Feb_2_2026_09_19_45_PM.png")
        embed.set_footer(text="Iberic House • Professional Customer Support")

        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("✅ Panel enviado correctamente.", ephemeral=True)

    @discord.app_commands.command(name="close", description="Cerrar ticket")
    async def close(self, interaction):
        if not es_owner(interaction.user):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        await interaction.channel.delete()

    @discord.app_commands.command(name="rename", description="Renombrar ticket")
    async def rename(self, interaction, nombre: str):
        if not es_owner(interaction.user):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        await interaction.channel.edit(name=nombre)
        await interaction.response.send_message("✅ Ticket renombrado.", ephemeral=True)

    @discord.app_commands.command(name="add", description="Añadir usuario al ticket")
    async def add(self, interaction, user: discord.Member):
        if not es_owner(interaction.user):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        await interaction.channel.set_permissions(user, view_channel=True, send_messages=True)
        await interaction.response.send_message("✅ Usuario añadido.", ephemeral=True)

    @discord.app_commands.command(name="remove", description="Quitar usuario del ticket")
    async def remove(self, interaction, user: discord.Member):
        if not es_owner(interaction.user):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message("❌ Usuario eliminado.", ephemeral=True)

    @discord.app_commands.command(name="alert", description="Alertar al owner")
    async def alert(self, interaction):
        if not es_owner(interaction.user):
            return await interaction.response.send_message("❌ Sin permisos.", ephemeral=True)
        owner_role = discord.utils.get(interaction.guild.roles, name=config["OwnerRole"])
        if owner_role:
            await interaction.channel.send(f"🚨 {owner_role.mention} ticket pendiente")
        await interaction.response.send_message("🚨 Owner alertado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
