import discord
from discord.ext import commands
from discord.ui import Button, View
import os
from datetime import datetime

# Configuration
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# IDs des salons (À REMPLACER PAR TES IDS)
SALON_DEMANDES = 1234567890  # Salon où arrivent les nouvelles demandes
SALON_EN_COURS = 1234567891  # Salon des demandes acceptées
SALON_TERMINEES = 1234567892 # Salon des demandes terminées

class BoutonAccepterRefuser(View):
    def __init__(self, embed_data):
        super().__init__(timeout=None)
        self.embed_data = embed_data
    
    @discord.ui.button(label="✅ Accepter", style=discord.ButtonStyle.success, custom_id="accepter")
    async def accepter(self, interaction: discord.Interaction, button: Button):
        # Créer l'embed pour le salon "en cours"
        embed = discord.Embed(
            title=self.embed_data['title'],
            description=self.embed_data['description'],
            color=self.embed_data['color'],
            timestamp=datetime.now()
        )
        
        for field in self.embed_data['fields']:
            embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
        
        embed.set_footer(text=f"Accepté par {interaction.user.name}")
        
        # Envoyer dans le salon "en cours" avec bouton "Terminer"
        salon_en_cours = bot.get_channel(SALON_EN_COURS)
        view_terminer = BoutonTerminer(self.embed_data)
        await salon_en_cours.send(embed=embed, view=view_terminer)
        
        # Modifier le message original
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
        # Créer l'embed pour le salon "terminées"
        embed = discord.Embed(
            title=self.embed_data['title'],
            description=self.embed_data['description'],
            color=0x00ff00,  # Vert pour terminé
            timestamp=datetime.now()
        )
        
        for field in self.embed_data['fields']:
            embed.add_field(name=field['name'], value=field['value'], inline=field['inline'])
        
        embed.set_footer(text=f"Terminé par {interaction.user.name}")
        
        # Envoyer dans le salon "terminées" SANS bouton
        salon_terminees = bot.get_channel(SALON_TERMINEES)
        await salon_terminees.send(embed=embed)
        
        # Modifier le message original
        await interaction.response.edit_message(
            content="🏁 **Projet terminé et archivé !**",
            embed=None,
            view=None
        )

@bot.event
async def on_ready():
    print(f'✅ Bot connecté en tant que {bot.user}')
    print(f'🔗 Connecté à {len(bot.guilds)} serveur(s)')
    
    # Synchroniser les commandes slash
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} commande(s) synchronisée(s)')
    except Exception as e:
        print(f'❌ Erreur de synchronisation: {e}')

@bot.event
async def on_message(message):
    # Ignorer les messages du bot
    if message.author == bot.user:
        return
    
    # Détecter les nouvelles demandes dans le salon spécifique
    if message.channel.id == SALON_DEMANDES and message.embeds:
        embed = message.embeds[0]
        
        # Extraire les données de l'embed
        embed_data = {
            'title': embed.title or "Nouvelle demande",
            'description': embed.description or "",
            'color': embed.color.value if embed.color else 0x3447003,
            'fields': []
        }
        
        # Extraire les champs
        for field in embed.fields:
            embed_data['fields'].append({
                'name': field.name,
                'value': field.value,
                'inline': field.inline
            })
        
        # Créer les boutons Accepter/Refuser
        view = BoutonAccepterRefuser(embed_data)
        
        # Répondre avec les boutons
        await message.reply(
            "**🔔 Nouvelle demande détectée !**\nQue voulez-vous faire ?",
            view=view
        )
    
    await bot.commands.process_commands(message)

# Commande pour tester le système
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

# Commande pour configurer les salons
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

# Lancer le bot
if __name__ == "__main__":
    TOKEN = os.getenv('DISCORD_TOKEN')  # Récupérer le token depuis les variables d'environnement
    
    if not TOKEN:
        print("❌ ERREUR: Token Discord non trouvé!")
        print("Définissez la variable d'environnement DISCORD_TOKEN")
    else:
        bot.run(TOKEN)