#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    streetaddress.streetaddress
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: (c) 2012 by PN.
    :license: MIT, see LICENSE for more details.
"""

import re
import six

########################################################################
# StreetAddressParser
########################################################################

class StreetAddressParser():
    def __init__(self):
        abbrev_suffix_map = get_abbrev_suffix_dict()
        self.street_type_set = set(abbrev_suffix_map.keys()) | set(abbrev_suffix_map.values())

        self.text2num_dict = get_text2num_dict()
        self.suite_type_set = set([
            'suite', 'ste', 'apt','apartment', 
            'room', 'rm', '#',
            ])
        self.rec_st_nd_rd_th = re.compile(r'^\d+(st|nd|rd|th)$', flags=re.I|re.U)
        self.rec_house_number = re.compile(r'^\d\S*$', flags=re.I|re.U)

    def parse(self, addr_str, skip_house=False):
        addr_str = addr_str.strip()
        res = {
                'house' : None,
                'street_name' : None,
                'street_type' : None,
                'street_full' : None,
                'suite_num' : None,
                'suite_type' : None,
                'other' : None,
                }

        tokens = addr_str.split()
        start_idx = 0

        if len(tokens) == 0:
            return res

        if skip_house:
            start_idx = 0
        else:
            if tokens[0].lower() in self.text2num_dict:
                res['house'] = six.text_type(self.text2num_dict[tokens[0].lower()])
                start_idx = 1
            elif self.rec_st_nd_rd_th.search(tokens[0]):
                #first token is actually a street number (not house)
                start_idx = 0 
            elif self.rec_house_number.search(tokens[0]):
                res['house'] = tokens[0] 
                start_idx = 1
            else:
                #no house number
                start_idx = 0

            if res['house'] and len(tokens) >= 2 and tokens[1] == '1/2':
                res['house'] += ' ' + tokens[1] 
                start_idx = 2

        street_accum = []
        other_accum = []
        is_in_state = 'street' #can be 'street', 'suite', 'other'

        for i in range(start_idx, len(tokens)):
            word = tokens[i]
            #word = re.sub(r'[\.\,]+$', '', word, flags=re.I|re.U) 
            while len(word) > 0 and (word[-1] == '.' or word[-1] == ','):
                #truncate the trailing dot (for abbrev)
                word = word[:-1]
            word_lw = word.lower()

            if word_lw in self.street_type_set and len(street_accum) > 0:
                res['street_type'] = word
                is_in_state = 'other'
            elif word_lw in self.suite_type_set:
                res['suite_type'] = word
                is_in_state = 'suite'
            elif len(word_lw) > 0 and word_lw[0] == '#' and res['suite_num'] is not None:
                res['suite_type'] = '#'
                res['suite_num'] = word[1:]
                is_in_state = 'other'
            elif is_in_state == 'street':
                street_accum.append(word)
            elif is_in_state == 'suite':
                res['suite_num'] = word
                is_in_state = 'other'
            elif is_in_state == 'other': 
                other_accum.append(word)
            else:
                raise Exception('this state should never be reached')

        # TODO PO Box handling
        #acronym = lambda s : Regex(r"\.?\s*".join(s)+r"\.?")
        #poBoxRef = ((acronym("po") | acronym("apo") | acronym("afp")) + 
        #            Optional(CaselessLiteral("BOX"))) + Word(alphanums)("boxnumber")

        if street_accum:
            res['street_name'] = ' ' . join(street_accum)
        if other_accum:
            res['other'] = ' ' . join(other_accum)

        if res['street_name'] and res['street_type']:
            res['street_full'] = res['street_name'] + ' ' + res['street_type']
        elif res['street_name']:
            res['street_full'] = res['street_name'] 
        elif res['street_type']:
            res['street_full'] = res['street_type'] 

        return res

def get_abbrev_suffix_dict():
    return {
            # 'avenue' : 'ave',
            # 'street' : 'st',
            # 'boulevard': 'blvd',
            # 'parkway': 'pkwy',
            # 'highway': 'hwy',
            # 'drive': 'dr',
            # 'place': 'pl',
            # 'expressway': 'expy',
            # 'heights': 'hts',
            # 'junction' : 'jct',
            # 'center': 'ctr',
            # 'circle' : 'cir',
            # 'cove' : 'cv',
            # 'lane' : 'ln',
            # 'road' : 'rd',
            # 'court' : 'ct',
            # 'square' : 'sq',
            # 'loop' : 'lp',
            # # new abbrev
            'allee': 'aly',
            'alley': 'aly',
            'ally': 'aly',
            'aly': 'aly',
            'anex': 'anx',
            'annex': 'anx',
            'annx': 'anx',
            'anx': 'anx',
            'arc': 'arc',
            'arcade': 'arc',
            'av': 'ave',
            'ave': 'ave',
            'aven': 'ave',
            'avenu': 'ave',
            'avenue': 'ave',
            'avn': 'ave',
            'avnue': 'ave',
            'bayoo': 'byu',
            'bayou': 'byu',
            'bch': 'bch',
            'beach': 'bch',
            'bend': 'bnd',
            'bnd': 'bnd',
            'blf': 'blf',
            'bluf': 'blf',
            'bluff': 'blf',
            'bluffs': 'blfs',
            'bot': 'btm',
            'btm': 'btm',
            'bottm': 'btm',
            'bottom': 'btm',
            'blvd': 'blvd',
            'boul': 'blvd',
            'boulevard': 'blvd',
            'boulv': 'blvd',
            'br': 'br',
            'brnch': 'br',
            'branch': 'br',
            'brdge': 'brg',
            'brg': 'brg',
            'bridge': 'brg',
            'brk': 'brk',
            'brook': 'brk',
            'brooks': 'brks',
            'burg': 'bg',
            'burgs': 'bgs',
            'byp': 'byp',
            'bypa': 'byp',
            'bypas': 'byp',
            'bypass': 'byp',
            'byps': 'byp',
            'camp': 'cp',
            'cp': 'cp',
            'cmp': 'cp',
            'canyn': 'cyn',
            'canyon': 'cyn',
            'cnyn': 'cyn',
            'cape': 'cpe',
            'cpe': 'cpe',
            'causeway': 'cswy',
            'causwa': 'cswy',
            'cswy': 'cswy',
            'cen': 'ctr',
            'cent': 'ctr',
            'center': 'ctr',
            'centr': 'ctr',
            'centre': 'ctr',
            'cnter': 'ctr',
            'cntr': 'ctr',
            'ctr': 'ctr',
            'centers': 'ctrs',
            'cir': 'cir',
            'circ': 'cir',
            'circl': 'cir',
            'circle': 'cir',
            'crcl': 'cir',
            'crcle': 'cir',
            'circles': 'cirs',
            'clf': 'clf',
            'cliff': 'clf',
            'clfs': 'clfs',
            'cliffs': 'clfs',
            'clb': 'clb',
            'club': 'clb',
            'common': 'cmn',
            'commons': 'cmns',
            'cor': 'cor',
            'corner': 'cor',
            'corners': 'cors',
            'cors': 'cors',
            'course': 'crse',
            'crse': 'crse',
            'court': 'ct',
            'ct': 'ct',
            'courts': 'cts',
            'cts': 'cts',
            'cove': 'cv',
            'cv': 'cv',
            'coves': 'cvs',
            'creek': 'crk',
            'crk': 'crk',
            'crescent': 'cres',
            'cres': 'cres',
            'crsent': 'cres',
            'crsnt': 'cres',
            'crest': 'crst',
            'crossing': 'xing',
            'crssng': 'xing',
            'xing': 'xing',
            'crossroad': 'xrd',
            'crossroads': 'xrds',
            'curve': 'curv',
            'dale': 'dl',
            'dl': 'dl',
            'dam': 'dm',
            'dm': 'dm',
            'div': 'dv',
            'divide': 'dv',
            'dv': 'dv',
            'dvd': 'dv',
            'dr': 'dr',
            'driv': 'dr',
            'drive': 'dr',
            'drv': 'dr',
            'drives': 'drs',
            'est': 'est',
            'estate': 'est',
            'estates': 'ests',
            'ests': 'ests',
            'exp': 'expy',
            'expr': 'expy',
            'express': 'expy',
            'expressway': 'expy',
            'expw': 'expy',
            'expy': 'expy',
            'ext': 'ext',
            'extension': 'ext',
            'extn': 'ext',
            'extnsn': 'ext',
            'exts': 'exts',
            'fall': 'fall',
            'falls': 'fls',
            'fls': 'fls',
            'ferry': 'fry',
            'frry': 'fry',
            'fry': 'fry',
            'field': 'fld',
            'fld': 'fld',
            'fields': 'flds',
            'flds': 'flds',
            'flat': 'flt',
            'flt': 'flt',
            'flats': 'flts',
            'flts': 'flts',
            'ford': 'frd',
            'frd': 'frd',
            'fords': 'frds',
            'forest': 'frst',
            'forests': 'frst',
            'frst': 'frst',
            'forg': 'frg',
            'forge': 'frg',
            'frg': 'frg',
            'forges': 'frgs',
            'fork': 'frk',
            'frk': 'frk',
            'forks': 'frks',
            'frks': 'frks',
            'fort': 'ft',
            'frt': 'ft',
            'ft': 'ft',
            'freeway': 'fwy',
            'freewy': 'fwy',
            'frway': 'fwy',
            'frwy': 'fwy',
            'fwy': 'fwy',
            'garden': 'gdn',
            'gardn': 'gdn',
            'grden': 'gdn',
            'grdn': 'gdn',
            'gardens': 'gdns',
            'gdns': 'gdns',
            'grdns': 'gdns',
            'gateway': 'gtwy',
            'gatewy': 'gtwy',
            'gatway': 'gtwy',
            'gtway': 'gtwy',
            'gtwy': 'gtwy',
            'glen': 'gln',
            'gln': 'gln',
            'glens': 'glns',
            'green': 'grn',
            'grn': 'grn',
            'greens': 'grns',
            'grov': 'grv',
            'grove': 'grv',
            'grv': 'grv',
            'groves': 'grvs',
            'harb': 'hbr',
            'harbor': 'hbr',
            'harbr': 'hbr',
            'hbr': 'hbr',
            'hrbor': 'hbr',
            'harbors': 'hbrs',
            'haven': 'hvn',
            'hvn': 'hvn',
            'ht': 'hts',
            'hts': 'hts',
            'highway': 'hwy',
            'highwy': 'hwy',
            'hiway': 'hwy',
            'hiwy': 'hwy',
            'hway': 'hwy',
            'hwy': 'hwy',
            'hill': 'hl',
            'hl': 'hl',
            'hills': 'hls',
            'hls': '',
            'hllw': 'holw',
            'hollow': 'holw',
            'hollows': 'holw',
            'holw': 'holw',
            'holws': 'holw',
            'inlt': 'inlt',
            'is': 'is',
            'island': 'is',
            'islnd': 'is',
            'islands': 'iss',
            'islnds': 'iss',
            'iss': 'iss',
            'isle': 'isle',
            'isles': 'isle',
            'jct': 'jct',
            'jction': 'jct',
            'jctn': 'jct',
            'junction': 'jct',
            'junctn': 'jct',
            'juncton': 'jct',
            'jctns': 'jcts',
            'jcts': 'jcts',
            'junctions': 'jcts',
            'key': 'ky',
            'ky': 'ky',
            'keys': 'kys',
            'kys': 'kys',
            'knl': 'knl',
            'knol': 'knl',
            'knoll': 'knl',
            'knls': 'knls',
            'knolls': 'knls',
            'lk': 'lk',
            'lake': 'lk',
            'lks': 'lks',
            'lakes': 'lks',
            'land': 'land',
            'landing': 'lndg',
            'lndg': 'lndg',
            'lndng': 'lndg',
            'lane': 'ln',
            'ln': 'ln',
            'lgt': 'lgt',
            'light': 'lgt',
            'lights': 'lgts',
            'lf': 'lf',
            'loaf': 'lf',
            'lck': 'lck',
            'lock': 'lck',
            'lcks': 'lcks',
            'locks': 'lcks',
            'ldg': 'ldg',
            'ldge': 'ldg',
            'lodg': 'ldg',
            'lodge': 'ldg',
            'loop': 'loop',
            'loops': 'loop',
            'mall': 'mall',
            'mnr': 'mnr',
            'manor': 'mnr',
            'manors': 'mnrs',
            'mnrs': 'mnrs',
            'meadow': 'mdw',
            'mdw': 'mdws',
            'mdws': 'mdws',
            'meadows': 'mdws',
            'medows': 'mdws',
            'mews': 'mews',
            'mill': 'ml',
            'mills': 'mls',
            'missn': 'msn',
            'mssn': 'msn',
            'motorway': 'mtwy',
            'mnt': 'mt',
            'mt': 'mt',
            'mount': 'mt',
            'mntain': 'mtn',
            'mntn': 'mtn',
            'mountain': 'mtn',
            'mountin': 'mtn',
            'mtin': 'mtn',
            'mtn': 'mtn',
            'mntns': 'mtns',
            'mountains': 'mtns',
            'nck': 'nck',
            'neck': 'nck',
            'orch': 'orch',
            'orchard': 'orch',
            'orchrd': 'orch',
            'oval': 'oval',
            'ovl': 'oval',
            'overpass': 'opas',
            'park': 'park',
            'prk': 'park',
            'parks': 'park',
            'parkway': 'pkwy',
            'parkwy': 'pkwy',
            'pkway': 'pkwy',
            'pkwy': 'pkwy',
            'pky': 'pkwy',
            'parkways': 'pkwy',
            'pkwys': 'pkwy',
            'pass': 'pass',
            'passage': 'psge',
            'path': 'path',
            'paths': 'path',
            'pike': 'pike',
            'pikes': 'pike',
            'pine': 'pne',
            'pines': 'pnes',
            'pnes': 'pnes',
            'pl': 'pl',
            'plain': 'pln',
            'pln': 'pln',
            'plains': 'plns',
            'plns': 'plns',
            'plaza': 'plz',
            'plz': 'plz',
            'plza': 'plz',
            'point': 'pt',
            'pt': 'pt',
            'points': 'pts',
            'pts': 'pts',
            'port': 'prt',
            'prt': 'prt',
            'ports': 'prts',
            'prts': 'prts',
            'pr': 'pr',
            'prairie': 'pr',
            'prr': 'pr',
            'rad': 'radl',
            'radial': 'radl',
            'radiel': 'radl',
            'radl': 'radl',
            'ramp': 'ramp',
            'ranch': 'rnch',
            'ranches': 'rnch',
            'rnch': 'rnch',
            'rnchs': 'rnch',
            'rapid': 'rpd',
            'rpd': 'rpd',
            'rapids': 'rpds',
            'rpds': 'rpds',
            'rest': 'rst',
            'rst': 'rst',
            'rdg': 'rdg',
            'rdge': 'rdg',
            'ridge': 'rdg',
            'rdgs': 'rdgs',
            'ridges': 'rdgs',
            'riv': 'riv',
            'river': 'riv',
            'rvr': 'riv',
            'rivr': 'riv',
            'rd': 'rd',
            'road': 'rd',
            'roads': 'rds',
            'rds': 'rds',
            'route': 'rte',
            'row': 'row',
            'rue': 'rue',
            'run': 'run',
            'shl': 'shl',
            'shoal': 'shl',
            'shls': 'shls',
            'shoals': 'shls',
            'shoar': 'shr',
            'shore': 'shr',
            'shr': 'shr',
            'shoars': 'shrs',
            'shores': 'shrs',
            'shrs': 'shrs',
            'skyway': 'skwy',
            'spg': 'spg',
            'spng': 'spg',
            'spring': 'spg',
            'sprng': 'spg',
            'spgs': 'spgs',
            'spngs': 'spgs',
            'springs': 'spgs',
            'sprngs': 'spgs',
            'spur': 'spur',
            'spurs': 'spur',
            'sq': 'sq',
            'sqr': 'sq',
            'sqre': 'sq',
            'squ': 'sq',
            'square': 'sq',
            'sqrs': 'sqs',
            'squares': 'sqs',
            'sta': 'sta',
            'station': 'sta',
            'statn': 'sta',
            'stn': 'sta',
            'stra': 'stra',
            'strav': 'stra',
            'straven': 'stra',
            'stravenue': 'stra',
            'stravn': 'stra',
            'strvn': 'stra',
            'strvnue': 'stra',
            'stream': 'strm',
            'streme': 'strm',
            'strm': 'strm',
            'street': 'st',
            'strt': 'st',
            'st': 'st',
            'str': 'st',
            'streets': 'sts',
            'smt': 'smt',
            'sumit': 'smt',
            'sumitt': 'smt',
            'summit': 'smt',
            'ter': 'ter',
            'terr': 'ter',
            'terrace': 'ter',
            'throughway': 'trwy',
            'trace': 'trce',
            'traces': 'trce',
            'trce': 'trce',
            'track': 'trak',
            'tracks': 'trak',
            'trak': 'trak',
            'trk': 'trak',
            'trks': 'trak',
            'trafficway': 'trfy',
            'trail': 'trl',
            'trails': 'trl',
            'trl': 'trl',
            'trls': 'trl',
            'trailer': 'trlr',
            'trlr': 'trlr',
            'trlrs': 'trlr',
            'tunel': 'tunl',
            'tunl': 'tunl',
            'tunls': 'tunl',
            'tunnel': 'tunl',
            'tunnels': 'tunl',
            'tunnl': 'tunl',
            'trnpk': 'tpke',
            'turnpike': 'tpke',
            'turnpk': 'tpke',
            'underpass': 'upas',
            'un': 'un',
            'union': 'un',
            'unions': 'uns',
            'valley': 'vly',
            'vally': 'vly',
            'vlly': 'vly',
            'vly': 'vly',
            'valleys': 'vlys',
            'vlys': 'vlys',
            'vdct': 'via',
            'via': 'via',
            'viadct': 'via',
            'viaduct': 'via',
            'view': 'vw',
            'vw': 'vw',
            'views': 'vws',
            'vws': 'vws',
            'vill': 'vlg',
            'villag': 'vlg',
            'village': 'vlg',
            'villg': 'vlg',
            'villiage': 'vlg',
            'vlg': 'vlg',
            'villages': 'vlgs',
            'vlgs': 'vlgs',
            'ville': 'vl',
            'vl': 'vl',
            'vis': 'vis',
            'vist': 'vis',
            'vista': 'vis',
            'vst': 'vis',
            'vsta': 'vis',
            'walk': 'walk',
            'walks': 'walk',
            'wall': 'wall',
            'wy': 'way',
            'way': 'way',
            'ways': 'ways',
            'well': 'wl',
            'wells': 'wls',
            'wls': 'wls'

    }



def get_text2num_dict():
    return  {
        'zero': 0,
        'one': 1,
        'two': 2,
        'three': 3,
        'four': 4,
        'five': 5,
        'six': 6,
        'seven': 7,
        'eight': 8,
        'nine': 9,
        'ten': 10,
        'eleven': 11,
        'twelve': 12,
        'thirteen': 13,
        'fourteen': 14,
        'fifteen': 15,
        'sixteen': 16,
        'seventeen': 17,
        'eighteen': 18,
        'nineteen': 19,
        'twenty': 20,
        'thirty': 30,
        'forty': 40,
        'fifty': 50,
        'sixty': 60,
        'seventy': 70,
        'eighty': 80,
        'ninety': 90,
        } 


########################################################################
# StreetAddressFormatter
########################################################################
class StreetAddressFormatter():
    def __init__(self):
        #abbreviate west, east, north, south?
        self.abbrev_suffix_map = get_abbrev_suffix_dict()
        self.street_type_set = set(self.abbrev_suffix_map.keys()) | set(self.abbrev_suffix_map.values())
        self.abbrev_direction_map = {
            'east' : 'E',
            'west' : 'W', 
            'north' : 'N',
            'south' : 'S',
            }

        for k,v in self.abbrev_suffix_map.items():
            self.abbrev_suffix_map[k] = v.title()

        TH_or_str = '|' . join(self.street_type_set)
        self.re_TH= re.compile(r'\b(\d+)\s+(%s)\.?$' % TH_or_str, flags=re.I|re.U)

    def st_nd_th_convert(self, num_str):
        if len(num_str) >= 2 and (num_str[-2:] =='11' or num_str[-2:] =='12'):
            return num_str + 'th'
        elif num_str[-1] == '1':
            return num_str + 'st'
        elif num_str[-1] == '2':
            return num_str + 'nd'
        elif num_str[-1] == '3':
            return num_str + 'rd'
        else:
            return num_str + 'th'

    def append_TH_to_street(self, addr):
        #street,avenue needs to be the last word
        addr = addr.strip()
        match = self.re_TH.search(addr)
        if match:
            repl = '%s %s' % (self.st_nd_th_convert(match.group(1)), match.group(2))
            addr = addr.replace(match.group(0), repl)
        return addr

    def abbrev_direction(self, addr):
        word_lst = addr.split()
        if len(word_lst) == 0:
            return addr

        for i in range(len(word_lst) - 1):
            word = word_lst[i].lower() 
            #should have a digit after direction, e.g. "West 23rd" 
            if word in self.abbrev_direction_map and word_lst[i+1][0].isdigit():
                word_lst[i] = self.abbrev_direction_map[word]
        addr = ' ' . join(word_lst)
        return addr

    def abbrev_street_avenue_etc(self, addr, abbrev_only_last_token=True):
        word_lst = addr.split()
        if len(word_lst) == 0:
            return addr

        if abbrev_only_last_token:
            pos_lst = [-1]
        else:
            pos_lst = range(len(word_lst))

        for p in pos_lst:
            word = re.sub(r'\.$', '', word_lst[p]).lower() #get rid of trailing period
            if word in self.abbrev_suffix_map:
                word_lst[p] = self.abbrev_suffix_map[word]
        addr = ' ' . join(word_lst)
        return addr


