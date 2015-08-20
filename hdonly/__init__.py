from .main import hdonly

def autoload():
    return hdonly()

config = [{
    'name': 'hdonly',
    'groups': [
        {
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'HD-Only',
            'description': 'See <a href="https://hd-only.org/">HD-Only.org</a>',
            'wizard': True,
            'options': [
                {
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': 0,
                },
                {
                    'name': 'username',
                    'default': '',
                },
                {
                    'name': 'password',
                    'default': '',
                    'type': 'password',
                },
                {
                    'name': 'ignoreyear',
                    'label': 'Ignore Year',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Won\'t use the release year to narrow the search if checked',
                },
                {
                    'name': 'vo',
                    'label': 'VO mandatory',
                    'default': 1,
                    'type': 'bool',
                    'description': 'Check this if you want to download results with VO audio track',
                },
                {
                    'name': 'vf',
                    'label': 'VF mandatory',
                    'default': 0,
                    'type': 'bool',                 
                    'description': 'Check this if you want to download results with VF/VFF/VFI/TrueFrench audio track',
                },
                {
                    'name': 'vfq',
                    'label': 'VFQ mandatory',
                    'default': 0,
                    'type': 'bool',                 
                    'description': 'Check this if you want to download results with VFQ audio track',
                },
                {
                    'name': 'multi',
                    'label': 'MULTI mandatory',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Check this if you want to download results with MULTI audio tracks (VO and VF)',
                },
                {
                    'name': 'x265',
                    'label': 'x265 mandatory',
                    'default': 0,
                    'type': 'bool',
                    'description': 'Will ignore results not encoded with x265 if checked',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 80,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met (72 hours is tracker rules minimum).',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 20,
                    'description': 'Starting score for each release found via this provider.',
                }
            ],
        },
    ],
}]

