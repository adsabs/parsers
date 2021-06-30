"""
Test parsers
"""

import unittest
import filecmp
import sys
import os
import glob
import json
import shutil

import namedentities

from pyingest.parsers import iop
from pyingest.config import config
from pyingest.parsers.author_names import AuthorNames
from pyingest.parsers.affils import AffiliationParser

from pyingest.serializers import classic

if sys.version_info > (3,):
    open_mode = 'rb'
    open_mode_u = 'rb'
else:
    open_mode = 'r'
    open_mode_u = 'rU'

class TestIOP(unittest.TestCase):

    def setUp(self):
        stubdata_dir = os.path.join(os.path.dirname(__file__), 'data/stubdata/')
        self.inputdir = os.path.join(stubdata_dir, 'input')
        self.maxDiff = None

    # Test 15
    def test_iop_parser(self):
        test_infile = os.path.join(self.inputdir, 'iop_apj.xml')
        parser = iop.IOPJATSParser()
        with open(test_infile, open_mode_u) as fp:
            input_data = fp.read()
        test_data = parser.parse(input_data)

        # # save temporary copy of data structure
        # target_saved = test_infile.replace('input','parsed') + '.parsed.NEW'
        # with open(target_saved, 'w') as fp:
            # json.dump(test_data, fp, sort_keys=True, indent=4)
        output_bibcode = '2019ApJ...882...74H'
        output_pub = u'The Astrophysical Journal, Volume 882, Issue 2, id.74, <NUMPAGES>13</NUMPAGES> pp.'
        output_aff = [u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; Space Sciences Laboratory, 7 Gauss Way, University of California, Berkeley, CA 94720-7450, USA; <ID system="ORCID">0000-0002-8548-482X</ID> <EMAIL>jhare@berkeley.edu</EMAIL>', u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; <ID system="ORCID">0000-0002-6447-4251</ID>', u'Department of Astronomy & Astrophysics, Pennsylvania State University, 525 Davey Lab, University Park, PA 16802, USA; <ID system="ORCID">0000-0002-7481-5259</ID>', u'Department of Physics, The George Washington University, 725 21st St. NW, Washington, DC 20052, USA; The George Washington Astronomy, Physics, and Statistics Institute of Sciences (APSIS), The George Washington University, Washington, DC 20052, USA; <ID system="ORCID">0000-0001-7833-1043</ID>']
        self.assertEqual(test_data['bibcode'], output_bibcode)
        self.assertEqual(test_data['publication'], output_pub)
        self.assertEqual(test_data['affiliations'], output_aff)
        return

    # Test 15a
    def test_iop_entities(self):
        test_infile = os.path.join(self.inputdir, 'iop_aj_accentnames.xml')
        parser = iop.IOPJATSParser()
        with open(test_infile, open_mode_u) as fp:
            input_data = fp.read()
        # input_data = namedentities.unicode_entities(str(input_data))
        # input_data = bytes(input_data, encoding='utf-8')
        test_data = parser.parse(input_data)
        output_title = 'Meteoroid Stream of Comet C/1961 T1 (Seki) and Its Relation to the December &#961;-Virginids and &#947;-Sagittariids'
        output_authors = 'Neslu&#353;an, Lubo&#353;; Hajdukov&#225;, M&#225;ria'
        output_affiliations = ['Astronomical Institute, Slovak Academy of Science, 05960 Tatransk&#225; Lomnica, Slovakia; <ID system="ORCID">0000-0001-9758-1144</ID> <EMAIL>ne@ta3.sk</EMAIL>', 'Astronomical Institute, Slovak Academy of Science, D&#250;bravsk&#225; cesta 9, 84504 Bratislava, Slovakia; <ID system="ORCID">0000-0002-7837-2627</ID>']
        self.assertEqual(test_data['title'], output_title)
        self.assertEqual(test_data['authors'], output_authors)
        self.assertEqual(test_data['affiliations'], output_affiliations)
        return