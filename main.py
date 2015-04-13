from bs4 import BeautifulSoup
from couchpotato.core.helpers.encoding import tryUrlencode
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import traceback
import urlparse

log = CPLog(__name__)


class HDO(TorrentProvider, MovieProvider):

    urls = {
        'base' : 'https://hd-only.org/%s',
        'test' : 'https://hd-only.org',
        'login' : 'https://hd-only.org/login.php',
        'login_check': 'https://hd-only.org',
        'search': 'https://hd-only.org/torrents.php?searchstr=%s&searchsubmit=1',
    }

    http_time_between_calls = 1 #seconds
    cat_backup_id = None

    def _searchOnTitle(self, title, movie, quality, results):

        log.debug('Searching HD-Only for %s' % (title))

        url = self.urls['search'] % (title)
        data = self.getHTMLData(url)

        log.debug('Received data from HD-Only')
        if data:
            log.debug('Data is valid from HD-Only')
            html = BeautifulSoup(data)

            try:
                result_table = html.find('table', attrs = {'id':'torrent_table'})
                if not result_table:
                    log.debug('No table results from HD-Only')
                    return

                torrents = result_table.find('tbody').findAll('tr')
                for result in torrents:
                    href = result.findAll('td')[1].findAll('a')[0]['href']
                    log.debug('*** href = %s' % href)
                    idt = urlparse.urlparse_qs(href)['id'][0]
                    log.debug('*** idt = %s' % idt)
                    detail = result.findAll('td')[1].findAll('a')[2]['href']
                    log.debug('*** detail = %s' % detail)
                    release_name = result.findAll('td')[1].findAll('a')[2].text
                    log.debug('*** release_name = %s' % release_name)
                    lang = result.findAll('td')[1].findAll('div', attrs = {'class':'torrent_info'})
                    log.debug('*** lang = %s' % lang)
                    words = title.lower().replace(':',' ').split()
                    if self.conf('ignore_year'):
                        index = release_name.lower().find(words[-1] if words[-1] != 'the' else words[-2]) + len(words[-1] if words[-1] != 'the' else words[-2]) +1
                        index2 = index + 7
                        if not str(movie['info']['year']) in release_name[index:index2]:
                            release_name = release_name[0:index] + '(' + str(movie['info']['year']) + ').' + release_name[index:]
                    if 'the' not in release_name.lower() and (words[-1] == 'the' or words[0] == 'the'):
                        release_name = 'the.' + release_name
                    if (self.conf('vf') and ('VF' not in lang.replace('VFQ',''))):
                        release_name = ''
                    if (self.conf('vfq') and ('VFQ' not in lang)):
                        release_name = ''
                    if (self.conf('vo') and ('VO' not in lang)):
                        release_name = ''
                    results.append({
                        'id': idt,
                        'name': release_name,
                        'url': self.urls['base'] % href,
                        'detail_url': self.urls['base'] % detail,
                        'size': self.parseSize(str(result.findAll('td')[4].text)),
                        'seeders': result.findAll('td')[6].text,
                        'leechers': result.findAll('td')[7].text,
                    })
                    log.debug('details for found torrent :')
                    log.debug('Torrent ID : %s' % id)
                    log.debug('Release name : %s' % name)
                    log.debug('Download URL : %s' % url)
                    log.debug('Detail URL : %s' % detail_url)
                    log.debug('Torrent size : %s' % size)
                    log.debug('Seeders : %s' % seeders)
                    log.debug('Leechers : %s' % leechers)
            except:
                log.error('Failed to parse HD-Only: %s' % (traceback.format_exc()))

    def getLoginParams(self):
        log.debug('*** username = %s' % self.conf('vo'))
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

