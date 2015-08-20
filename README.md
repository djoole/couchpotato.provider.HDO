#couchpotato.provider.HDO
HD-Only Torrent Provider integration into CouchPotato.

#How-to install

1. Go to your custom_plugins folder, which is located within your config folder.
See Settings->About->Directories (second folder is your config folder) for location.
2. Enter this command : *git clone https://github.com/djoole/couchpotato.provider.HDO.git .*

Or if you don't have git :
1. Make a folder named hdonly in your custom_plugins folder
2. Place the init.py and main.py file inside this hdonly folder.

#How-to use

Once installed as above, go about activating the provider as you would with any other provider in CouchPotato.

Options available :
- Download only torrents with at least a VO audio track
- Download only torrents with at least a VF audio track
- Download only torrents with at least a VFQ audio track
- Download only torrents with MULTI (VO and VF) audio tracks
- Download only torrents with x265 encoding

#Contribute/Issues

Use issue tracker or send PR.
