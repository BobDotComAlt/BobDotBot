"""
MIT License

Copyright (c) 2020 BobDotCom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# import stuff
import discord
import aiohttp
from discord.ext import commands
from bs4 import BeautifulSoup

class GrowtopiaCog(commands.Cog, name = "Growtopia"):
    """Commands relating to the online sandbox game, Growtopia"""

    def __init__(self, client):
        self.client = client
        self.url = "https://growtopiagame.com"
        self.session = aiohttp.ClientSession()

    @commands.command(aliases=["rw", "render"])
    async def renderworld(self,ctx,world):
        """Get a render of a world in Growtopia"""
        async with ctx.typing():
            async with self.session.get(self.url+f'/worlds/{world.lower()}.png') as resp:
                if not resp.status == 200:
                    embed = discord.Embed(color=discord.Color.red(), timestamp=ctx.message.created_at, title=f"That world hasn't been rendered yet")
                    await ctx.send(embed=embed)
                    return
                embed = discord.Embed(title=f"Here is a render of the world: {world.upper()}")
                embed.set_image(url=self.url+f'/worlds/{world.lower()}.png') 
                await ctx.send(embed=embed)             
    @commands.command(aliases=["gt"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def online(self,ctx):
        """See how many people are playing the game right now"""
        async with self.session.get(self.url+'/detail') as resp:
              data = await resp.json(content_type="text/html")
              data = data["online_user"]
        embed = discord.Embed(timestamp=ctx.message.created_at, title=f"Growtopia stats", description=f"Players online: {data}")
        await ctx.send(embed=embed)
        
    @commands.command(aliases=["wiki","item"])
    @commands.cooldown(1, 1, commands.BucketType.channel)
    async def gt_wiki(self,ctx,*,item):
        """Search the wiki for an item"""
        async with ctx.typing():
            item = item.replace(" ","+")
            url = "https://growtopia.fandom.com/wiki/"
            search = "Special:Search?query=" + item
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url + search) as r:
                    html = await r.text()
            soup = BeautifulSoup(html, 'html.parser')
            article = ''
            content = soup.find('li', {"class": "unified-search__result"})
            for i in content.findAll('article'):
                article = article + ' ' +  i.text
            start = article.find("https://")
            items_link = article[start:].replace("\n","")
            async with aiohttp.ClientSession() as cs:
                async with cs.get(items_link) as r:
                    html = await r.text()
            soup1 = BeautifulSoup(html, 'html.parser')
            contents = soup1.find('div', {"class": "gtw-card item-card"})
            article,article1,article2 = '','',''
            for i in contents.findAll('div',"card-text"):
                article = article + ' ' +  i.text
            for i in contents.findAll('div',"card-header"):
                article1 = article1 + ' ' +  i.text
            for i in contents.findAll('table',"card-field"):
                article2 = article2 + ' ' +  i.text
            contents1 = soup1.find('span', {"class": "growsprite"})
            x = ''
            for i in contents1.findAll("img"):
                x = x + ' ' +  i["src"]
            class html:
                content = article.replace("None None Red Yellow Green Aqua Blue Purple Charcoal","")
                content = content.replace("None Red Yellow Green Aqua Blue Purple Charcoal","")
                content1 = article1
                thumbnail = x
                field = article2
                hits = article2.find("Hardness")
            embed = discord.Embed(title=article1,description=html.content,timestamp=ctx.message.created_at)
            embed.set_thumbnail(url=x)
            embed.add_field(name="Hits",value=f"Normal: {html.field[html.hits + 9:html.hits + 10]} \nWith pickaxe: {html.field[html.hits + 16:html.hits + 17]}")
            await ctx.send(embed=embed)
        
def setup(client):
    client.add_cog(GrowtopiaCog(client))
