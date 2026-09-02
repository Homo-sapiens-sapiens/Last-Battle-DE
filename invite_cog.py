import sys
from types import SimpleNamespace

import discord
from discord.ext import commands
import invite_db


class InviteView(discord.ui.View):
    def __init__(self, invite_id: int, inviter: discord.Member, target: discord.Member):
        super().__init__(timeout=300)
        self.invite_id = invite_id
        self.inviter = inviter
        self.target = target
        self.message = None
        accept_button = discord.ui.Button(label="Принять", style=discord.ButtonStyle.green)
        decline_button = discord.ui.Button(label="Отклонить", style=discord.ButtonStyle.red)
        accept_button.callback = self.accept
        decline_button.callback = self.decline
        self.add_item(accept_button)
        self.add_item(decline_button)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in (self.target.id, self.inviter.id):
            await interaction.response.send_message("Это приглашение не для вас.", ephemeral=True)
            return False
        return True

    async def accept(self, interaction: discord.Interaction):
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("Вызов может принять исключительно приглашённый соперник.", ephemeral=True)
            return
        await invite_db.set_invite_status(self.invite_id, "accepted")
        self.disable_all_items()
        self.stop()
        await interaction.response.edit_message(
            content=f"Начинаю игру...",
            view=self,
        )
        last_battle = sys.modules["__main__"]
        try:
            player1 = await last_battle.MyUser.create(SimpleNamespace(author=self.inviter))
            player2 = await last_battle.MyUser.create(SimpleNamespace(author=self.target))
        except discord.Forbidden:
            await self.message.edit(
                content="Мне не удалось создать игру! Походу у одного из игроков закрыты личные сообщения.",
                view=None,
            )
            return
        game = last_battle.MyGame()
        await game.create(player1, player2)
        await self.message.delete()

    async def decline(self, interaction: discord.Interaction):
        status = "declined" if interaction.user.id == self.target.id else "cancelled"
        await invite_db.set_invite_status(self.invite_id, status)
        self.stop()
        await interaction.response.defer()
        try:
            await interaction.message.delete()
        except discord.HTTPException:
            pass

    async def on_timeout(self):
        await invite_db.set_invite_status(self.invite_id, "expired")
        if self.message:
            try:
                await self.message.delete()
            except discord.HTTPException:
                pass


class InviteCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_ready = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.db_ready:
            await invite_db.init_db()
            await invite_db.expire_all_pending()
            self.db_ready = True

    @commands.slash_command(name="battle_invite", description="Пригласить соперника в игру")
    async def battle_invite(
        self,
        ctx: discord.ApplicationContext,
        opponent: discord.Option(discord.Member, "Кого ты хочешь пригласить?"),
    ):
        if ctx.guild is None:
            await ctx.respond("Эта команда не доступна в личке.", ephemeral=True)
            return
        if opponent.id == ctx.author.id:
            await ctx.respond("Нельзя пригласить самого себя...", ephemeral=True)
            return
        if opponent.bot:
            await ctx.respond("Нельзя пригласить бота...", ephemeral=True)
            return
        if await invite_db.get_pending_by_inviter(ctx.author.id):
            await ctx.respond("У тебя уже есть активное приглашение. Дождись ответа или же отмени его.", ephemeral=True)
            return
        invite = await invite_db.create_invite(ctx.author.id, opponent.id)
        view = InviteView(invite.id, ctx.author, opponent)
        response = await ctx.respond(
            f"{opponent.mention}, тебя {ctx.author.mention} вызывает на дуэль!", view=view
        )
        if isinstance(response, discord.Interaction):
            view.message = await response.original_response()
        else:
            view.message = response
