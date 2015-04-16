from couchpotato.core.helpers.encoding import tryUrlencode
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import traceback
import json

log = CPLog(__name__)

class hdonly(TorrentProvider, MovieProvider):

    baseurl = 'https://hd-only.org/'
    urls = {
        'test' : baseurl,
        'login' : baseurl + 'login.php',
        'login_check' : baseurl,
        'index' : baseurl + 'ajax.php?action=index',
        'search' : baseurl + 'ajax.php?action=browse&searchstr=%s',
        'detail' : baseurl + 'ajax.php?action=torrent&id=%s',
        'download' : baseurl + 'torrents.php?action=download&id=%s&authkey=%s&torrent_pass=%s'
    }

    http_time_between_calls = 1 #seconds
    cat_backup_id = None

	
    def _searchOnTitle(self, title, movie, quality, results):

        log.debug('Searching HD-Only for %s' % (title))
        index = self.getJsonData(self.urls['index'])
        authkey = index['response']['authkey']
        passkey = index['response']['passkey']
        url = self.urls['search'] % title
        data = self.getJsonData(url)

        try:
            if data['status'] == 'success':
                splittedTitle = title.lower().replace(':',' ').split()
                if not data['response']['results']:
                    log.debug('No result from HD-Only with this title : %s' % title)
                    testthe = False
                    if (splittedTitle[-1] == 'the' or splittedTitle[0] == 'the'):
                        testthe = True
                        title = title.replace('the ','')
                        log.debug('Trying with this title now : %s' % title)
                        url = self.urls['search'] % title 
                        data = self.getJsonData(url)
                        if not data['response']['results']:
                            log.debug('No result from HD-Only with this title neither : %s' % title)
                            return
                    if not testthe:
                        return
                release_name = data['response']['results'][0]['groupName']
                if 'the' not in release_name.lower() and (splittedTitle[-1] == 'the' or splittedTitle[0] == 'the'):
                    release_name = 'the.' + release_name.lower().replace(' ','.')
                for torrent in data['response']['results'][0]['torrents']:
                    id = torrent['torrentId']
                    name = release_name + '.' + str(data['response']['results'][0]['groupYear']) + '.' + torrent['encoding'] + '.' +  torrent['media'] + '.' +  torrent['format']
                    url = self.urls['download'] % (torrent['torrentId'], authkey, passkey)
                    detail_url = self.urls['detail'] % id
                    size = tryInt(torrent['size']) / 1024 / 1024
                    seeders = tryInt(torrent['seeders'])
                    leechers = tryInt(torrent['leechers'])
                    detail = self.getJsonData(detail_url)['response']['torrent']['fileList'] + self.getJsonData(detail_url)['response']['torrent']['filePath']
                    if (self.conf('vf') and ('VF' not in detail.replace('VFQ',''))):
                        continue
                    if (self.conf('vfq') and ('VFQ' not in detail)):
                        continue
                    if (self.conf('vo') and ('VO' not in detail)):
                        continue
                    if (self.conf('x265') and ('x265' not in detail)):
                        continue
                    log.debug('Torrent added to results : id %s; name %s; url %s; detail_url %s; size %s; seeders %s; leechers %s' % (id, name, url, detail_url, size, seeders, leechers))
                    results.append({
                        'id': id,
                        'name': name,
                        'url': url,
                        'detail_url': detail_url,
                        'size': size,
                        'seeders': seeders,
                        'leechers': leechers
                        })
        except:
            log.error('Failed to parse HD-Only: %s' % (traceback.format_exc()))


    def getLoginParams(self):
        log.debug('Getting login params for HD-Only')
        return {
             'username': self.conf('username'),
             'password': self.conf('password'),
             'keeplogged': '1',
             'login': 'M\'identifier'
        }


    def loginSuccess(self, output):
        log.debug('Checking login success for HD-Only: %s' % ('True' if ('logout' in output.lower()) else 'False'))
        return 'logout' in output.lower()


    loginCheckSuccess = loginSuccess
