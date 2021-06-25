
import discord
import asyncio
import os
from discord.ext import commands
import urllib
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
import re
import warnings
import requests
import time

token = ''

client = discord.Client()
def deleteTags(htmls):
    for a in range(len(htmls)):
        htmls[a] = re.sub('<.+?>','',str(htmls[a]),0).strip()
    return htmls

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game("%메이플 [닉네임]"))
    print("성공적으로 로그인이 되었습니다\n> {0.user}".format(client))

@client.event
async def on_message(message):
    print(message.content)
    if message.author == client.user:
        return

    if message.content.startswith('%메이플'):

        # Maplestroy base link
        mapleLink = "https://maplestory.nexon.com"
        # Maplestory character search base link
        mapleCharacterSearch = "https://maplestory.nexon.com/Ranking/World/Total?c="
        mapleUnionLevelSearch = "https://maplestory.nexon.com/Ranking/Union?c="


        playerNickname = ''.join((message.content).split(' ')[1:])
        html = urlopen(mapleCharacterSearch + quote(playerNickname))
        bs = BeautifulSoup(html, 'html.parser')

        html2 = urlopen(mapleUnionLevelSearch + quote(playerNickname))
        bs2 = BeautifulSoup(html2,'html.parser')

        if len(message.content.split(" ")) == 1:
            embed = discord.Embed(title="ERROR", description="", color=0xff7f00)
            embed.add_field(name="닉네임을 입력하지 않으셨습니다",
                            value="%메이플 [닉네임]", inline=False)
            await message.channel.send("", embed=embed)

        elif bs.find('tr', {'class': 'search_com_chk'}) == None:
            embed = discord.Embed(title="ERROR", description="", color=0xff7f00)
            embed.add_field(name="검색된 플레이어가 없습니다\n", 
                            value="에러의 원인으로는 다음과 같은 경우가 있습니다\n- 존재하지 않은 플레이어의 닉네임을 입력했을 경우\n- 캐릭터를 생성한 지 얼마 지나지 않았을 경우\n- 최근에 월드리프를 진행했을 경우", inline=False)
            await message.channel.send("", embed=embed)

        else:
            # Get to the character info page
            characterRankingLink = bs.find('tr', {'class': 'search_com_chk'}).find('a', {'href': re.compile('\/Common\/Character\/Detail\/[A-Za-z0-9%?=]*')})['href']
            # Parse Union Level
            characterUnionRanking = bs2.find('tr', {'class': 'search_com_chk'})
            if characterUnionRanking == None:
                pass
            else:
                characterUnionRanking = characterUnionRanking.findAll('td')[2].text
            html = urlopen(mapleLink + characterRankingLink)
            bs = BeautifulSoup(html, 'html.parser')

            # Find Ranking page and parse page
            personalRankingPageURL = bs.find('a', {'href': re.compile('\/Common\/Character\/Detail\/[A-Za-z0-9%?=]*\/Ranking\?p\=[A-Za-z0-9%?=]*')})['href']
            html = urlopen(mapleLink + personalRankingPageURL)
            bs = BeautifulSoup(html, 'html.parser')
            # Popularity

            popularityInfo = bs.find('span',{'class' : 'pop_data'}).text.strip()
            ''' Can't Embed Character's image. Gonna fix it after patch note
            #Character image
            getCharacterImage = bs.find('img',{'src': re.compile('https\:\/\/avatar\.maplestory\.nexon\.com\/Character\/[A-Za-z0-9%?=/]*')})['src']
            '''
            infoList = []
            # All Ranking information embeded in <dd> elements
            RankingInformation = bs.findAll('dd')  # [level,job,servericon,servername,'-',comprehensiveRanking,'-',WorldRanking,'-',JobRanking,'-',Popularity Ranking,'-',Maple Union Ranking,'-',Achivement Ranking]
            for inf in RankingInformation:
                infoList.append(inf.text)
            embed = discord.Embed(title="플레이어 [ " + playerNickname + " ] 검색 결과", description=infoList[0] + " | " +infoList[1] + " | " + "서버 : " + infoList[2], color=0xff7f00)
            embed.add_field(name="자세한 내용을 보려면 아래 링크를 클릭하세요", value = mapleLink + personalRankingPageURL, inline=False)
            embed.add_field(name="전체 랭킹",value=infoList[4], inline=True)
            embed.add_field(name="월드 랭킹", value=infoList[6], inline=True)
            embed.add_field(name="직업 랭킹", value=infoList[8], inline=True)
            embed.add_field(name="인기 랭킹", value=infoList[10] + " \n" +popularityInfo + "", inline=True)
            if characterUnionRanking == None:
                embed.add_field(name="유니온 랭킹", value=infoList[12],inline=True)
            else:
                embed.add_field(name="유니온 랭킹", value=infoList[12] + " \nLV." + characterUnionRanking + "", inline=True)
            embed.add_field(name="업적 랭킹", value=infoList[14], inline=True)
            embed.set_thumbnail(url='https://ssl.nx.com/s2/game/maplestory/renewal/common/logo.png')
            await message.channel.send("", embed=embed)
client.run('token')
# client.run(os.environ['token'])
