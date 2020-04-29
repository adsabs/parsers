import os
import re
import json
import urllib


def find(key, dictionary):
    for k, v in dictionary.iteritems():
        if k == key:
            yield v
        elif isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result


MONTH_TO_NUMBER = {'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                   'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11,
                   'dec': 12}

# APS Journal dictionary: used by parsers/aps.py to get the bibstem
APS_PUBLISHER_IDS = {'PRL': 'PhRvL', 'PRX': 'PhRvX', 'RMP': 'RvMP',
                     'PRA': 'PhRvA', 'PRB': 'PhRvB', 'PRC': 'PhRvC',
                     'PRD': 'PhRvD', 'PRE': 'PhRvE', 'PRAB': 'PhRvS',
                     'PRSTAB': 'PhRvS', 'PRAPPLIED': 'PhRvP',
                     'PRFLUIDS': 'PhRvF', 'PRMATERIALS': 'PhRvM',
                     'PRPER': 'PRPER', 'PRSTPER': 'PRSTP', 'PR': 'PhRv',
                     'PRI': 'PhRvI', 'PHYSICS': 'PhyOJ',
                     'PRResearch': 'PhRvR'}

IOP_PUBLISHER_IDS = {'apj': u'ApJ', 'jcap': u'JCAP', 'ejp': u'EJPh',
                     'raa': u'RAA', 'pmea': u'PhyM', 'd': u'JPhD',
                     'aj': u'AJ', 'apex': u'APExp', 'apjl': u'ApJL',
                     'apjs': u'ApJS', 'bb': u'BiBi', 'bf': u'BioFa',
                     'bmm': u'BioMa', 'cqg': u'CQGra', 'cpc': u'ChPhC',
                     'ctp': u'CoTPh', 'epl': u'EL', 'erc': u'ERCom',
                     'erx': u'ERExp', 'erl': u'ERL', 'est': u'EleSt',
                     'fcs': u'FCS', 'fdr': u'FlDyR', 'izv': u'IzMat',
                     'jbr': u'JBR', 'jopt': u'JOpt', 'cm': u'JPCM',
                     'jpenergy': u'JPEn', 'a': u'JPhA', 'b': u'JPhB',
                     'jpco': u'JPhCo', 'g': u'JPhG', 'jpmater': u'JPhM',
                     'jpphoton': u'JPhP', 'lpl': u'LaPhL', 'mrx': u'MRE',
                     'mst': u'MeScT', 'mfm': u'MuMat',
                     'njp': u'NJPh', 'nanof': u'NanoF', 'nano': u'Nanot',
                     'non': u'Nonli', 'pasp': u'PASP', 'met': u'Metro',
                     'pmb': u'PMB', 'ppcf': u'PPCF', 'prex': u'PRCom',
                     'ps': u'PhyS', 'ped': u'PhyEd',
                     'phu': u'PhyU', 'pst': u'PlST', 'prge': u'PrEne',
                     'rnaas': u'RNAAS', 'rop': u'RPPh', 'rms': u'RuMaS',
                     'sst': u'SeScT', 'sust': u'SuScT', 'tdm': u'TDM',
                     'rcr': u'RuCRv', 'nf': u'NucFu', 'jmm': u'JMiMi',
                     'cpl': u'ChPhL', 'ip': u'InvPr', 'jrp': u'JRP',
                     'psst': u'PSST', 'sms': u'SMaS', 'msms': u'MSMSE',
                     'qel': u'QuEle', 'msb': u'SbMat', 'jjap': u'JaJAP',
                     'ansn': u'ANSNN', 'maf': u'MApFl', 'stmp': u'SuTMP',
                     'qst': u'QS&T', 'ees': u'E&ES', 'mse': u'MS&E',
                     'pb': u'PhBio', 'lp': u'LaPhy', 'cpb': u'ChPhB',
                     'jos': u'JSemi', 'jne': u'JNEng', 'jge': u'JGE',
                     'jstat': u'JSMTE', 'jpcs': u'JPhCS', 'pw': u'PhyW',
                     'prv': u'PPS', 'c': 'JPhC', 'jphf': 'JPhF',
                     'jinst': u'JInst'}

IOP_JOURNAL_NAMES = {'rnaas': u'Research Notes of the American Astronomical Society'}

# IOP_SPECIAL_ID_HANDLING = ['PASP.','QuEle','JGE..','PhyU.','IzMat','SbMat',
#                            'RuMaS','RuCRv','EL...','Nonli','JRP..']
IOP_SPECIAL_ID_HANDLING = ['PASP.']

OUP_PUBLISHER_IDS = {'mnras': u'MNRAS', 'mnrasl': u'MNRAS',
                     'pasj': u'PASJ', 'ptep': u'PTEP', 'gji': u'GeoJI'}
OUP_PDFDIR = 'https://academic.oup.com'

JATS_TAGS_DANGER = ['php', 'script', 'css']

JATS_TAGS_MATH = ['inline-formula',
                  'tex-math',
                  'sc',
                  'mml:math',
                  'mml:semantics',
                  'mml:mrow',
                  'mml:munder',
                  'mml:mo',
                  'mml:mi',
                  'mml:msub',
                  'mml:mover',
                  'mml:mn',
                  'mml:annotation'
                  ]

JATS_TAGS_HTML = ['sub', 'sup', 'a', 'astrobj']

JATS_TAGSET = {'title': JATS_TAGS_MATH + JATS_TAGS_HTML,
               'abstract': JATS_TAGS_MATH + JATS_TAGS_HTML + ['pre', 'br'],
               'comments': JATS_TAGS_MATH + JATS_TAGS_HTML + ['pre', 'br'],
               'affiliations': ['email', 'orcid'],
               'keywords': ['astrobj']
               }

# KEYWORDS

# Unified Astronomy Thesaurus
# retrieve current UAT from github
UAT_URL = 'https://raw.githubusercontent.com/astrothesaurus/UAT/master/UAT.json'
try:
    remote = urllib.urlopen(UAT_URL)
    UAT_json = json.loads(remote.read())
    UAT_ASTRO_KEYWORDS = list(find('name', UAT_json))
except Exception as e:
    print("Warning: could not load UAT from github!")
    UAT_ASTRO_KEYWORDS = []

# American Astronomical Society keywords (superseded June 2019 by UAT)
AAS_ASTRO_KEYWORDS_FILE = os.path.dirname(os.path.abspath(__file__)) + '/kw_aas_astro.dat'
AAS_ASTRO_KEYWORDS = []
try:
    with open (AAS_ASTRO_KEYWORDS_FILE, 'rU') as fk:
        for l in fk.readlines():
            AAS_ASTRO_KEYWORDS.append(l.strip())
except Exception as e:
    print("Error loading AAS Astro keywords: %s" % err)


# American Physical Society keywords
APS_ASTRO_KEYWORDS_FILE = os.path.dirname(os.path.abspath(__file__)) + '/kw_aps_astro.dat'
APS_ASTRO_KEYWORDS = []
try:
    with open (APS_ASTRO_KEYWORDS_FILE, 'rU') as fk:
        for l in fk.readlines():
            APS_ASTRO_KEYWORDS.append(l.strip())
except Exception as e:
    print("Error loading APS Astro keywords: %s" % err)


# REFERENCE SOURCE OUTPUT
REFERENCE_TOPDIR = '/proj/ads/references/sources/'

# AUTHOR ALIASES
AUTHOR_ALIAS_DIR = '/proj/ads/abstracts/config/Authors/'

# HTML_ENTITY_TABLE
HTML_ENTITY_TABLE = os.path.dirname(os.path.abspath(__file__)) + '/html5.dat'
ENTITY_DICTIONARY = dict()
try:
    with open(HTML_ENTITY_TABLE, 'rU') as fent:
        for l in fent.readlines():
            carr = l.rstrip().split('\t')

            uni_entity = None
            name_entity = None
            hex_entity = None
            dec_entity = None
            if len(carr) >= 4:
                uni_entity = carr[0]
                name_entity = carr[1]
                hex_entity = carr[2]
                dec_entity = carr[3]
                for c in name_entity.split():
                    try:
                        ENTITY_DICTIONARY[c] = dec_entity
                    except Exception, err:
                        print("Error splitting name_entity: '%s'" % name_entity)
                ENTITY_DICTIONARY[uni_entity] = dec_entity
            else:
                print("broken HTML entity:", l.rstrip())
                name_entity = "xxxxx"

except Exception, err:
    print("Problem in config:", err)

# ADS-specific translations
# have been added to html5.txt
ENTITY_DICTIONARY['&Tilde;'] = "~"
ENTITY_DICTIONARY['&rsquo;'] = "'"
ENTITY_DICTIONARY['&lsquo;'] = "'"
ENTITY_DICTIONARY['&nbsp;'] = " "
ENTITY_DICTIONARY['&mdash;'] = "-"
ENTITY_DICTIONARY['&ndash;'] = "-"
ENTITY_DICTIONARY['&rdquo;'] = '"'
ENTITY_DICTIONARY['&ldquo;'] = '"'
ENTITY_DICTIONARY['&minus;'] = "-"
ENTITY_DICTIONARY['&plus;'] = "+"
ENTITY_DICTIONARY['&thinsp;'] = " "
ENTITY_DICTIONARY['&hairsp;'] = " "
ENTITY_DICTIONARY['&ensp;'] = " "
ENTITY_DICTIONARY['&emsp;'] = " "
