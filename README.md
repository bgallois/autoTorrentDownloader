# Automatic torrent downloader

This program allows to automatically find new episodes of your favorites TV show on ettv and downloads them.
It works on Linux by command lines: you can use it on a VPS.

## How it works?

1. Download the dist folder in the git archive.
2. Inside the folder dist/autoTorrentDownloader creates the file "series.txt".
3. In the file "series.txt" add the series that you want to follow following this convention:  
name of the serie one tabulation the format (720p or 480p) one tabulation number of episodes to download.* name of the serie: keyword for the name of the serie, if multiple series found the program will ask you to choose the right serie.  
* format: 720p or 480p, if the one you choose is not available it will download the other.
* number of episodes to download: the number of episodes to download starting from the last episode of the serie. For example 1 means download the last episode broadcasted, 0 means download all the episodes of all the seasons.
4. Then types ./start and the program will begin.
5. The downloaded file will be downloaded and can't be found in the folder dist/autoTorrentDownloader/series/.
6. A file dataBase.db is also created and it contains the list of all episodes already downloaded. If you want to reset the program (re-downloads a whole serie for example) you have to delete it.
