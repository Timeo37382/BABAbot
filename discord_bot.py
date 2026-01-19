import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from datetime import datetime

# ==============================
# Configuration bot
# ==============================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# IDs des salons (à remplacer par tes vrais IDs)
SALON_DEMANDES = 1234567890  # salon des nouvelles demandes
SALON_EN_COURS = 1234567891  # salon des demandes acceptées
SALON_TERMINEES = 1234567892 # salon des demandes terminées

# ==============================
# Classes Boutons
# ==============================
class BoutonAccepterRefuser(View):
    def __init__(self, embed_data):
        super().__init__(timeout=None)
        self.embed_data = embed_data

    @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.success, custom_id="accepter")
    async def accepter(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title=self.embed_data['title'],
            description=self.embed_data['description'],
            color=self.embed_data['color'],
            timestamp=datetime.now()
        )
        for field in self.embed_data['fields']:
            embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
        embed.set_footer(text=f"Accepté par {interaction.user.name}")

        salon_en_cours = bot.get_channel(SALON_EN_COURS)
        view_terminer = BoutonTerminer(self.embed_data)
        await salon_en_cours.send(embed=embed, view=view_terminer)

        await interaction.response.edit_message(
            content="✅ **Demande acceptée et transférée !**",
            embed=None,
            view=None
        )

    @discord.ui.button(label="❌ Refuser", style=discord.ButtonStyle.danger, custom_id="refuser")
    async def refuser(self, interaction: discord.Interaction, button: Button):
        await interaction.response.edit_message(
            content=f"❌ **Demande refusée par {interaction.user.name}**",
            embed=None,
            view=None
        )

class BoutonTerminer(View):
    def __init__(self, embed_data):
        super().__init__(timeout=None)
        self.embed_data = embed_data

    @discord.ui.button(label="🏁 Terminer", style=discord.ButtonStyle.primary, custom_id="terminer")
    async def terminer(self, interaction: discord.Interaction, button: Button):
        embed = discord.Embed(
            title=self.embed_data['title'],
            description=self.embed_data['description'],
            color=0x00ff00,
            timestamp=datetime.now()
        )
        for field in self.embed_data['fields']:
            embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
        embed.set_footer(text=f"Terminé par {interaction.user.name}")

        salon_terminees = bot.get_channel(SALON_TERMINEES)
        await salon_terminees.send(embed=embed)

        await interaction.response.edit_message(
            content="🏁 **Projet terminé et archivé !**",
            embed=None,
            view=None
        )

# ==============================
# Événements bot
# ==============================
@bot.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {bot.user}')
    print(f'🔗 Connecté à {len(bot.guilds)} serveur(s)')
    
    # Message de confirmation dans le salon des nouvelles demandes
    salon_demandes = bot.get_channel(SALON_DEMANDES)
    if salon_demandes:
        await salon_demandes.send("✅ **BABAbot est connecté et prêt !**")

    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} commande(s) synchronisée(s)')
    except Exception as e:
        print(f'❌ Erreur de synchronisation: {e}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.channel.id == SALON_DEMANDES and message.embeds:
        embed = message.embeds[0]
        embed_data = {
            'title': embed.title or "Nouvelle demande",
            'description': embed.description or "",
            'color': embed.color.value if embed.color else 0x3447003,
            'fields': []
        }
        for field in embed.fields:
            embed_data['fields'].append({
                'name': field.name,
                'value': field.value,
                'inline': field.inline
            })
        view = BoutonAccepterRefuser(embed_data)
        await message.reply("**🔔 Nouvelle demande détectée !**\nQue voulez-vous faire ?", view=view)

    # Traitement des commandes
    await bot.process_commands(message)

# ==============================
# Commandes slash
# ==============================
@bot.tree.command(name="test_demande", description="Créer une demande de test")
async def test_demande(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🏗️ Nouvelle demande - BUILD",
        description="**TestUser** vient de soumettre une demande",
        color=0x3447003,
        timestamp=datetime.now()
    )
    embed.add_field(name="🎮 Pseudo Minecraft", value="`TestPlayer`", inline=True)
    embed.add_field(name="💬 Discord", value="`@testuser`", inline=True)
    embed.add_field(name="📋 Type de demande", value="**Build**", inline=True)
    embed.add_field(name="📝 Description de la demande", value=">>> Ceci est une demande de test", inline=False)
    embed.set_footer(text="BabaBuild - Formulaire de demande")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="config", description="Afficher les IDs des salons configurés")
@commands.has_permissions(administrator=True)
async def config(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"**Configuration actuelle :**\n"
        f"📥 Salon demandes: `{SALON_DEMANDES}`\n"
        f"⏳ Salon en cours: `{SALON_EN_COURS}`\n"
        f"✅ Salon terminées: `{SALON_TERMINEES}`\n\n"
        f"Pour modifier, éditez les variables dans le code.",
        ephemeral=True
    )

# ==============================
# Lancer le bot
# ==============================
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')
    if not TOKEN:
        print("❌ ERREUR: Token Discord non trouvé! Définissez la variable DISCORD_TOKEN")
    else:
        bot.run(TOKEN)
