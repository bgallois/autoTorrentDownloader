''' autoTorrentDownloader 
Copyright (C) 2018 Benjamin GALLOIS
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
'''


from bs4 import BeautifulSoup
import requests
import re
import sqlite3
import libtorrent as lt
import time
import os
import string


class Scraper:
    ''' Simple class to scrape serie from ettv torrent, compare them to previously downloaded episodes and download the new episodes'''

    def __init__(self, query, quality, number):
        '''
        :param query: keywords for the serie to download
        :param quality: keywords to specified the quality, either 480p or 720p
        :param number: keywords to specified the number of episodes from the last episode to download, 0 mean all the serie
        :type query: str
        :type quality: str
        '''

        # Format string for ettv scraping
        self.query = query.replace(' ', '+')
        self.quality = quality
        self.name = query.replace(' ', '')
        self.name = self.name.replace(':', '')
        self.number = number
        self.status = True

        # Create a directory to stock the file 
        self.dir = os.path.dirname('series/' + self.name + '/')
        if not os.path.exists(self.dir):
                os.makedirs(self.dir)
        

        # Create the database where previouly download episodes will be stored
        self.db = sqlite3.connect('dataBase.db')
        self.c = self.db.cursor()
        tableName = "CREATE TABLE IF NOT EXISTS {} (saison INT, episode INT)".format(self.name)
        self.c.execute(tableName)        
        
        # Scape, compare with database and download
        homePage = self.searchSerie()
        episodes = self.getEpisodes(homePage)
        self.lastEpisode(episodes)
        self.dataBaseUpdate(episodes)
        self.c.close()
        self.db.close()


    def searchSerie(self):
        '''
        :description: find the serie on ettv, if keyboard are not specific enought, nothing is returned and the user must add keyboard

        :return: web link to the ettv page of serie
        :rtype: str
        '''

        searchPage = requests.get('https://ettvtorrents.com/?s=' + self.query)
        soup = BeautifulSoup(searchPage.text, 'html.parser')
        searchResults = soup.find_all(class_ = 'link-image')

        s = [i.get('href') for i in searchResults]

        return s[0]

    def getEpisodes(self, homePage):
        '''
        :description: scrape ettv page and find the list of episodes available and the magnet link associated
        :param homePage: page of the serie on ettv
        :type: str
        return: list of episodes available and its magnet links
        rtype: list of tuples
        '''

        seriePage = requests.get(homePage)
        soup = BeautifulSoup(seriePage.text, 'html.parser')
        seasons = soup.find_all(id = 'tv-seasons')
        episodeNumber = []
        episodeMagnet = []
        seasonNumber = []
        for season in seasons:
            outBox = season.find_all(class_='row')
            seasonNumber.extend( [season.find(itemprop='seasonNumber').string for i in outBox])
            infoBox = [i.find(class_="col-xs-12 col-sm-6 col-md-9") for i in outBox]
            downloadBox = [i.find(class_="col-xs-12 col-sm-6 col-md-3") for i in outBox]
            episodeNumber.extend( [i.find(itemprop='episodeNumber').string for i in infoBox] )
            try:
                episodeMagnet.extend( [i.find(lambda tag:tag.name=="a" and self.quality in tag.text).get('href') for i in downloadBox])
            except: # If format doesn't exist
                if self.quality.find("480") != -1:
                    episodeMagnet.extend( [i.find(lambda tag:tag.name=="a" and "720p" in tag.text).get('href') for i in downloadBox])
                elif self.quality.find("720") != -1:
                    episodeMagnet.extend( [i.find(lambda tag:tag.name=="a" and "480p" in tag.text).get('href') for i in downloadBox])
        return list(zip(*[ seasonNumber, episodeNumber, episodeMagnet ]))

    def lastEpisode(self, episodes):
        '''
        :description: find the last season and the last episode of a tv show
        :param episodes: list of episodes available and its magnet links
        :type episodes: list of tuples
        '''

        self.lastSeason = 0
        self.lastEpisode = 0
        for season, __, __ in episodes:
            if self.lastSeason < int(season):
                self.lastSeason = int(season)
        for __, episode, __ in episodes:
            if self.lastEpisode < int(episode.string):
                self.lastEpisode = int(episode)
	
    def dataBaseUpdate(self, episodes):
        '''
        :description: compare the list of episodes find on ettv the database of previously downloaded episodes. Then downloaded new episodes and update the database
        :param episodes: list of episodes available and its magnet links
        :type episodes: list of tuples

        '''
        for episode in episodes:
            query = 'SELECT * FROM {} WHERE saison = ? AND episode = ?'.format(self.name)
            self.c.execute(query, (episode[0], episode[1]))
            data = self.c.fetchall()

            if not data: # Not existing in the database
                    if int(self.number) == 0: # Download all the serie
                        print('S' + episode[0] + 'E' + episode[1] + ' of ' + self.name + ' will be Downloaded')
                        self.download(episode[2])
                    elif int(self.number) != 0: # Download the last number of episodes
                        if int(episode[0]) == self.lastSeason and int(episode[1]) in range(self.lastEpisode - int(self.number) + 1, self.lastEpisode + 1):
                            print('S' + episode[0] + 'E' + episode[1] + ' of ' + self.name + ' will be Downloaded')
                            self.download(episode[2])
                    if self.status:
                        query = 'INSERT INTO {} VALUES(?, ?)'.format(self.name)
                        self.c.execute(query, (int(episode[0]), int(episode[1])))
                        self.db.commit()
                    elif not self.status:
                            print('S' + episode[0] + 'E' + episode[1] + ' of ' + self.name + ' download has failed')
    
    def download(self, link):
        '''
        :description: download a file from the torrent magnet
        :param link: torrent magnet
        :type link: str
        
        THE METADATA DOWNLOADING IS SOMETIME STUCK OR VERY LONG FIND THE BUG WITH LIBTORRENT OR ADD A TIMER TO RETRY THE DOWNLOADING IF STUCK
        '''

        ses = lt.session()
        params = { 'save_path': self.dir }
        handle = lt.add_magnet_uri(ses, link, params)
        print(link)
        print('downloading metadata...')
        start = time.time()
        self.status = True
        while (not handle.has_metadata()):
            time.sleep(1)
            if (time.time() - start > 20):
                self.status = False
                break
        print('got metadata, starting torrent download...')
        while (handle.status().state != lt.torrent_status.seeding) and (self.status == True):
            print('%d %% done' % (handle.status().progress*100))
            time.sleep(1)

