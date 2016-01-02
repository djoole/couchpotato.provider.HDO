# coding: utf8
from couchpotato.core.helpers.encoding import tryUrlencode
from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.media.movie.providers.base import MovieProvider
import traceback
import json
from HTMLParser import HTMLParser
import urllib2

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

        h = HTMLParser()

        index = self.getJsonData(self.urls['index'])
        authkey = index['response']['authkey']
        passkey = index['response']['passkey']

        if isinstance(title, str):
            title = title.decode('utf8')
        titles = [title]
        movieYear = str(movie['info']['year'])
        frTitle = self.getFrenchTitle(title, movieYear)

        log.debug('Searching HD-Only for ' + title)
        request = urllib2.quote(title.encode('iso-8859-1'))
        if (self.conf('ignoreyear')):
            searchUrl = self.urls['search'] % request
        else:
            searchUrl = (self.urls['search'] + '&year=%s') % (request, movieYear)
        data = self.getJsonData(searchUrl)
        #log.debug('******* data : ')
        #log.debug(data)

        if frTitle is not None:
            titles = [frTitle, title]
            #log.debug('******* titles : ')
            #log.debug(titles)
            log.debug('Searching HD-Only for ' + frTitle)
            request = urllib2.quote(frTitle.encode('iso-8859-1'))
            if (self.conf('ignoreyear')):
                searchUrl = self.urls['search'] % frTitle
            else:
                searchUrl = (self.urls['search'] + '&year=%s') % (frTitle, movieYear)
            frData = self.getJsonData(searchUrl)
            log.debug('******* searchUrl : ' + searchUrl)
            log.debug('******* frData : ')
            log.debug(frData)
            totalData = combine(frData, data)
            data = totalData
            #log.debug('***************************')
            #log.debug('******* totalData : ')
            #log.debug(data)

        try:
            if data['status'] == 'success':
                if not data['response']['results']:
                    log.debug('No result from HD-Only with %s or %s' % (frTitle, title))
                    return
                result = ''
                for res in data['response']['results']:
                    release_name = h.unescape(res['groupName']).lower().replace(':','').replace('  ',' ')
                    log.debug('release name reported by HD-Only : ' + release_name)
                    if release_name in titles:
                        log.debug('It\'s a match')
                        result = res
                        break
                    else:
                        log.debug('No match')
                if result != '':
                    for torrent in result['torrents']:
                        id = torrent['torrentId']
                        #name = release_name + '.' + str(result['groupYear']) + '.' + torrent['encoding'] + '.' + torrent['media'] + '.' + torrent['format']
                        url = self.urls['download'] % (torrent['torrentId'], authkey, passkey)
                        detail_url = self.urls['detail'] % id
                        size = tryInt(torrent['size']) / 1024 / 1024
                        seeders = tryInt(torrent['seeders'])
                        leechers = tryInt(torrent['leechers'])
                        if not self.getJsonData(detail_url)['response']['torrent']['filePath']:
                            detail = self.getJsonData(detail_url)['response']['torrent']['fileList'].lower()
                        else:
                            detail = self.getJsonData(detail_url)['response']['torrent']['filePath'].lower()
                        detail = h.unescape(detail)
                        name = detail
                        log.debug('Filename is %s' % detail)
                        if (seeders == 0):
                            log.debug('0 seeders, ignoring torrent %s' % id)
                            continue
                        if (self.conf('vf') and not (('vf' in detail.replace('vfq','')) or ('multi' in detail.replace('vfq',''))) and title != frTitle):
                            log.debug('VF mandatory checked, ignoring torrent %s' % id)
                            continue
                        if (self.conf('vfq') and ('vfq' not in detail) and title != frTitle):
                            log.debug('VFQ mandatory checked, ignoring torrent %s' % id)
                            continue
                        if (self.conf('vo') and (('vf' in detail) and not (('vo' in detail) or ('multi' in detail))) and title != frTitle):
                            log.debug('VO mandatory checked, ignoring torrent %s' % id)
                            continue
                        if (self.conf('multi') and ('multi' not in detail) and title != frTitle):
                            log.debug('MULTI mandatory checked, ignoring torrent %s' % id)
                            continue
                        if (self.conf('x265') and ('x265' not in detail)):
                            log.debug('x265 mandatory checked, ignoring torrent %s' % id)
                            continue
                        #if (self.conf('vf')):
                        #    log.debug('VF mandatory checked and french release found, adding french keyword to release name')
                        #    name = name + '.french'
                        #else:
                        #    name = replaceTitle(name, title, frTitle)
                        log.debug('Torrent added to results : id %s; name %s; detail_url %s; size %s; seeders %s; leechers %s' % (id, replaceTitle(name, title, frTitle), detail_url, size, 
seeders, leechers))
                        results.append({
                        'id': id,
                        'name': replaceTitle(name, title, frTitle),
                        'url': url,
                        'detail_url': detail_url,
                        'size': size,
                        'seeders': seeders,
                        'leechers': leechers
                        })
            return
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


    def getFrenchTitle(self, title, year):
        """
        This function uses TMDB API to get the French movie title of the given title.
        """

        url = "https://api.themoviedb.org/3/search/movie?api_key=0f3094295d96461eb7a672626c54574d&language=fr&query=%s" % title
        log.debug('Looking on TMDB for French title of : ' + title)
        #data = self.getJsonData(url, decode_from = 'utf8')
        data = self.getJsonData(url)
        try:
            if data['results'] != None:
                for res in data['results']:
                    yearI = res['release_date']
                    if year in yearI:
                        break
                #frTitle = res['title'].lower().replace(':','').replace('  ',' ').replace('-','')
                frTitle = res['title'].lower().replace(':','').replace('  ',' ')
                if frTitle == title:
                    log.debug('TMDB report identical FR and original title')
                    return None
                else:
                    log.debug(u'L\'API TMDB a trouvé un titre français => ' + frTitle)
                    return frTitle
            else:
                log.debug('TMDB could not find a movie corresponding to : ' + title)
                return None
        except:
            log.error('Failed to parse TMDB API: %s' % (traceback.format_exc()))

def combine(dict1, dict2):
    combdict = {}
    if (dict1['status'] == 'success') or (dict2['status'] == 'success'):
        combdict[u'status'] = u'success'
    else:
        combdict[u'status'] = u'failure'
    combdict[u'response'] = {}
    combdict[u'response'][u'results'] = []
    if 'response' in dict1:
        if dict1['response']['results']:
            combdict[u'response'][u'results'] = dict1['response']['results']
    if 'response' in dict2:
        if dict2['response']['results']:
            combdict[u'response'][u'results'] = combdict[u'response'][u'results'] + dict2['response']['results']
    #log.debug('combined dict is :')
    #log.debug(combdict)
    return combdict


def replaceTitle(releaseNameI, titleI, newTitleI):
    """
    This function is replacing the title in the release name by the old one,
    so that couchpotato recognise it as a valid release.
    """

    if newTitleI is None: # if the newTitle is empty, do nothing
        return releaseNameI
    else:
        # input as lower case
        releaseName = releaseNameI.lower()
        title = titleI.lower()
        newTitle = newTitleI.lower()
        separatedWords = []
        for s in releaseName.split(' '):
            separatedWords.extend(s.split('.'))
        # test how far the release name corresponds to the original title
        index = 0
        while separatedWords[index] in title.split(' '):
            index += 1
        # test how far the release name corresponds to the new title
        newIndex = 0
        while separatedWords[newIndex] in newTitle.split(' '):
            newIndex += 1
        # then determine if it correspoinds to the new title or old title
        if index >= newIndex:
            # the release name corresponds to the original title. SO no change needed
            log.debug('The release name is already corresponding. Changed nothing.')
            return releaseNameI
        else:
            # otherwise, we replace the french title by the original title
            finalName = [title]
            finalName.extend(separatedWords[newIndex:])
            newReleaseName = ' '.join(finalName)
            log.debug('The new release name is : ' + newReleaseName)
            return newReleaseName

