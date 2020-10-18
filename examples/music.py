from discord import utils
from discord import Embed
import discord
import lavalink
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.music = lavalink.Client(744351543146446961)
        self.bot.music.add_node(
            'localhost', 2333, '1234', 'hongkong', 'music-node')
        self.bot.add_listener(
            self.bot.music.voice_update_handler, 'on_socket_response')
        self.bot.music.add_event_hook(self.track_hook)

    @commands.command(name='join', aliases=['j'])
    async def _join(self, ctx):
        print('봇 채널 접속시도')
        vc = ctx.message.author.voice.channel
        player = self.bot.music.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region))
        if not player.is_connected:
            player.store('channel', ctx.channel.id)
            embed = Embed(title=f'♪ {vc.name} 채널로 입장합니다!',
                          color=0xf3bb76)
            await self.connect_to(ctx.guild.id, str(vc.id))
            print(f'채널 접속 : {vc.name}')
            await ctx.send(embed=embed)

        elif int(player.channel_id) == vc.id:
            embed = Embed(title=f'이미 음성 채널에 접속했습니다!',
                          color=0xf3bb76)
            await ctx.send(embed=embed)

        elif int(player.channel_id) != vc.id:
            player.store('channel', ctx.channel.id)
            embed = Embed(title=f'♪ {vc.name} 채널로 이동합니다!',
                          color=0xf3bb76)
            await self.connect_to(ctx.guild.id, str(vc.id))
            print(f'채널 이동 : {vc.name}')
            await ctx.send(embed=embed)

    @commands.command(name='play', aliases=['p'])
    async def play(self, ctx, *, query=None):
        try:
            player = self.bot.music.player_manager.get(ctx.guild.id)
            if not player.is_connected:
                embed = Embed(title='제가 음성채널에 없는 것 같아요!',
                              color=0xf3bb76)
                await ctx.send(embed=embed)
            query = f'ytsearch:{query}'
            results = await player.node.get_tracks(query)
            tracks = results['tracks'][0:5]
            i = 1
            embed = Embed(title='재생하실 노래를 선택하세요!',
                          description='$1~5가 아닌 1~5를 채팅창에 입력하세요.',
                          color=0xf3bb76)
            for track in tracks:
                embed.add_field(name=f'#{i}',
                                value=f"{track['info']['title']}",
                                inline=False)
                i += 1
            track_list = await ctx.send(embed=embed)

            def check(m):
                return m.author.id == ctx.author.id
            response = await self.bot.wait_for('message', check=check)
            track = tracks[int(response.content)-1]

            player.add(requester=ctx.author.id, track=track)
            await track_list.delete()
            if not player.is_playing:
                embed = Embed(title='♪ 노래가 재생됩니다!',
                              description=track['info']['title'],
                              color=0xf3bb76)
                await player.play()
                await ctx.send(embed=embed)
            elif player.is_playing:
                embed = Embed(title="♪ 노래가 재생중이므로 재생목록에 추가합니다!",
                              color=0xf3bb76)
                await ctx.send(embed=embed)
        except Exception as error:
            print(error)

    @commands.command(name='stop', aliases=['s'])
    async def stop(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if player.is_playing:
            embed = Embed(title='♪ 노래를 정지합니다!',
                          color=0xf3bb76)
            await player.stop()
            await ctx.send(embed=embed)

    @commands.command(name='leave', aliases=['l'])
    async def leave(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        if not player.is_connected:
            embed = Embed(title='제가 음성채널에 없는 것 같아요!',
                          color=0xf3bb76)
            await ctx.send(embed=embed)

        elif not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            embed = Embed(title='절 내보내려면 같은 음성채널에 있어야해요!',
                          color=0xf3bb76)
            await ctx.send(embed=embed)

        else:
            player.queue.clear()
            await player.stop()
            await self.connect_to(ctx.guild.id, None)
            embed = Embed(title='♪ 음성채널에서 나갑니다!',
                          description='재생목록 또한 초기화되었습니다!',
                          color=0xf3bb76)
            print('봇 음성채널에서 퇴장함')
            await ctx.send(embed=embed)

    @commands.command(name='queue', aliases=['q'])
    async def queue(self, ctx):
        player = self.bot.music.player_manager.get(ctx.guild.id)
        await ctx.send("test show queue")
        await ctx.send(player.queue)
        print(player.queue)

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            await self.connect_to(guild_id, None)

    async def connect_to(self, guild_id: int, channel_id: str):
        ws = self.bot._connection._get_websocket(guild_id)
        await ws.voice_state(str(guild_id), channel_id)


def setup(bot):
    bot.add_cog(Music(bot))
