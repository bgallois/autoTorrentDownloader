from bs4 import BeautifulSoup
import requests
import re
import sqlite3
import libtorrent as lt
import time
import os


class Scraper:
    ''' Simple class to scrape serie from ettv torrent, compare them to previously downloaded episodes and download the new episodes'''

    def __init__(self, query, quality):
        '''
        :param query: keywords for the serie to download
        :param quality: keywords to specified the quality, either 480p or 720p
        :type query: str
        :type quality: str
        '''

        # Format string for ettv scraping
        self.query = query.replace(' ', '+')
        self.quality = quality
        self.name = query.replace(' ', '')

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
        if len(s) > 1: # Severale series find
            print("Not specific enought")
            return None
        elif len(s) == 0: # Not serie found
            print("Can't find the serie")
            return None
        else:
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
            episodeMagnet.extend( [i.find(lambda tag:tag.name=="a" and self.quality in tag.text).get('href') for i in downloadBox])
        
        return list(zip(*[ seasonNumber, episodeNumber, episodeMagnet ]))

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
                    print('S' + episode[0] + 'E' + episode[1] + ' will be Downloaded')
                    self.download(episode[2])
                    query = 'INSERT INTO {} VALUES(?, ?)'.format(self.name)
                    self.c.execute(query, (int(episode[0]), int(episode[1])))
                    self.db.commit()
    
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
        while (not handle.has_metadata()): time.sleep(1)
        print('got metadata, starting torrent download...')
        while (handle.status().state != lt.torrent_status.seeding):
            print('%d %% done' % (handle.status().progress*100))
            time.sleep(1)


