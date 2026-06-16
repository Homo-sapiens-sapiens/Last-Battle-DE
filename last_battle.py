from io import BytesIO
import os 
from dotenv import load_dotenv
load_dotenv()
import discord
from discord import (ApplicationContext, Bot, ButtonStyle,
    Color, File, Interaction, SeparatorSpacingSize, User)
from discord.ui import (ActionRow, Button, Container, DesignerView,
    MediaGallery, Section, Select, Separator, TextDisplay, Thumbnail, button)

users = {}

class MyRow(ActionRow):
    @button(label="Delete Thread", style=ButtonStyle.red, id=200)
    async def delete_button(self, button: Button, interaction: Interaction):
        await interaction.response.defer(invisible=True)
        await interaction.channel.delete()

class MyView(DesignerView):
    def __init__(self, user: User):
        super().__init__(timeout=30)
        text1 = TextDisplay("LAST BATTLE")
        text2 = TextDisplay(
            "This section is contained in a `Container`.\nTo the right, you can see a `Thumbnail`."
        )
        thumbnail = Thumbnail(user.display_avatar.url)

        section = Section(text1, text2, accessory=thumbnail)
        section.add_text("-# Small text")

        container = Container(
            section,
            TextDisplay("Another `TextDisplay` separate from the `Section`."),
            color=Color.blue(),
        )
        container.add_separator(divider=True, spacing=SeparatorSpacingSize.large)
        container.add_item(Separator())
        container.add_text("Above is two `Separator`s followed by a `File`.")

        gallery = MediaGallery()
        gallery.add_item(user.default_avatar.url)
        gallery.add_item(user.avatar.url)

        self.add_item(container)
        self.add_item(gallery)
        self.add_item(
            TextDisplay("Above is a `MediaGallery` containing two `MediaGalleryItem`s.")
        )
        row = MyRow()
        self.add_item(row)

class User:
    def __init__(self):
        self.id = None
        self.free = None
        self.thread = None
        self.name = None
        self.embed = None 
    @classmethod
    async def create(cls, ctx: discord.ApplicationContext):
        global users
        self = cls()
        self.name = ctx.author.name
        self.id = ctx.author.id
        self.thread = await ctx.channel.create_thread(name=f"{ctx.author.name}'s game",
                                                      type=discord.ChannelType.private_thread, invitable=False)
        await self.thread.add_user(ctx.author)
        await self.thread.send(f"The new game thread for {self.name} was created")
        f = await ctx.author.display_avatar.read()
        file = File(BytesIO(f), filename="all_green.png")
        await self.thread.send(view=MyView(ctx.author), files=[file])
        await ctx.send(f"{self.thread.mention} thread for {self.name} created")
        return self

bot = Bot()

@bot.event
async def on_ready():
    global events
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="start", description="start the game (not ready yet)")
async def new_game(ctx: discord.ApplicationContext):
    await ctx.respond("creating the thread...",ephemeral=True)
    global users
    user=await User.create(ctx)
    users[str(user.id)]=user

bot.run(os.getenv('TOKEN'))