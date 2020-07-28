from docassemble.base.core import DAObject, DAList, DADict
from docassemble.base.util import path_and_mimetype, Address, LatitudeLongitude, DAStaticFile, text_type, PY2
from docassemble.base.legal import Court
import io, json, sys, requests, bs4, re, os #, cbor
from docassemble.webapp.playground import PlaygroundSection
import usaddress
from uszipcode import SearchEngine

# Needed for Boston Municipal Court
import geopandas as gpd
from shapely.geometry import Point

__all__= ['get_courts_from_massgov_url','save_courts_to_file','MACourt','MACourtList','PY2'] 

def get_courts_from_massgov_url(url, shim_ehc_middlesex=True, shim_nhc_woburn=True):
    searcher = SearchEngine(simple_zipcode=True)
    """Load specified court directory page on Mass.gov and returns an MACourtList
    Properties include name, phone, fax, address, description (usually includes cities or county served), latitude, longitude
    """
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    jstring = soup.find_all( attrs={"data-drupal-selector":"drupal-settings-json"} )[0].text # this is the element that has the JSON data as of 6/19/2018
    jdata = json.loads(jstring)
    markers = jdata['locations']['googleMap']['markers']

    courts = []

    # The address and description are in a different part of the JSON
    for marker in markers:
        html_name = marker['infoWindow']['name']
        for item in jdata['locations']['imagePromos']['items']:
            description = ''
            if item['title']['text'] in html_name:
                name = item['title']['text'].rstrip()
                description = item['description']['richText']['rteElements'][0]['data']['rawHtml']['content']['#context']['value']
                break

        address = Address()
        orig_address = marker['infoWindow']['address'] # The geolocate method does _not_ work with PO Boxes (silently discards)
        clean_address = re.sub(r' *PO Box .*?,',"",orig_address)
        clean_address = re.sub(r' *P.O. Box .*?,',"",orig_address)
        has_po_box = not clean_address == orig_address # We want to track if there was a PO Box where mail should be delivered
        address.address = orig_address

        # See: https://usaddress.readthedocs.io/en/latest/ which explains how the mapping below prevents a RepeatedLabelError.
        # Basically parsing into line 1, line 2, etc is good enough for our use case.
        tag_mapping={
            'Recipient': 'recipient',
            'AddressNumber': 'address',
            'AddressNumberPrefix': 'address',
            'AddressNumberSuffix': 'address',
            'StreetName': 'address',
            'StreetNamePreDirectional': 'address',
            'StreetNamePreModifier': 'address',
            'StreetNamePreType': 'address',
            'StreetNamePostDirectional': 'address',
            'StreetNamePostModifier': 'address',
            'StreetNamePostType': 'address',
            'CornerOf': 'address',
            'IntersectionSeparator': 'address',
            'LandmarkName': 'address',
            'USPSBoxGroupID': 'address',
            'USPSBoxGroupType': 'address',
            'USPSBoxID': 'address',
            'USPSBoxType': 'address',
            'BuildingName': 'unit',
            'OccupancyType': 'unit',
            'OccupancyIdentifier': 'unit',
            'SubaddressIdentifier': 'unit',
            'SubaddressType': 'unit',
            'PlaceName': 'city',
            'StateName': 'state',
            'ZipCode': 'zip',
            } 
        try:
            address_parts = usaddress.tag(orig_address, tag_mapping=tag_mapping) 
        except usaddress.RepeatedLabelError:
            address_parts = usaddress.tag(clean_address, tag_mapping=tag_mapping) # Discard the PO box entry if necessary - not a valid address

        try:
            if address_parts[1].lower() == 'street address':
                address.address = address_parts[0].get('address')
                if address_parts[0].get('unit'):
                    address.unit = address_parts[0].get('unit')
                address.city = address_parts[0].get('city')
                address.state = address_parts[0].get('state')
                address.zip = address_parts[0].get('zip')
                zipinfo = searcher.by_zipcode(address.zip)
                address.county = zipinfo.county
                del zipinfo
            else:
                raise Exception('We expected a Street Address.')
        except:
            address.address = orig_address
            #address.geolocate(self.elements.get('full_address',''))

        if not hasattr(address,'address'):
            address.address = ''
        if not hasattr(address, 'city'):
            address.city = ''
        if not hasattr(address, 'state'):
            address.state = ''
        if not hasattr(address, 'zip'):
            address.zip = ''
        if not hasattr(address, 'county'):
            address.county = ''
        #if not hasattr(address, 'unit'):
            #address.unit = ''                    

        # store the data in a serializable format. maybe could refactor to use object_hooks, but would need to go all the way down to DAObject?
        court = {
            'name': name,
            'description': description,
            'has_po_box' : has_po_box,
            'phone':marker['infoWindow']['phone'],
            'fax':marker['infoWindow']['fax'],
            'address': {
                'city': address.city,
                'address': address.address,
                'state': address.state,
                'zip': address.zip,
                'county': address.county,
                'orig_address':  orig_address # the one-line original address, which may include a PO Box
            },
            'location': {
                'latitude': marker['position']['lat'],
                'longitude': marker['position']['lng']
            }
        }
        if hasattr(address, 'unit'):
            court['address']['unit']= address.unit

        courts.append(court)
        
    if shim_ehc_middlesex and url == 'https://www.mass.gov/orgs/housing-court/locations':
        court = {
            'name': "Eastern Housing Court - Middlesex Session",
            'description': "The Middlesex Session of the Eastern Housing Court serves Arlington, Belmont, and Cambridge, Medford and Somerville",
            'has_po_box' : False,
            'phone': "(781) 306-2715",
            'fax':"",
            'address': {
                'city': "Medford",
                'address': "4040 Mystic Valley Parkway",
                'state': "MA",
                'zip': "02155",
                'county': "Middlesex County",
                'orig_address':  "4040 Mystic Valley Parkway, Medford, MA 02155"
            },
            'location': {
                'latitude': 42.4048336,
                'longitude': -71.0893853
            }
        }
        courts.append(court)

    if shim_nhc_woburn and url == 'https://www.mass.gov/orgs/housing-court/locations': 
        court = {
            'name': "Northeast Housing Court - Woburn Session",
            'description': "The Woburn session of the Northeast Housing Court serves Bedford, Burlington, Concord, Everett,Lexington, Lincoln, Malden, Melrose, North Reading, Reading, Stoneham, Wakefield, Waltham, Watertown, Weston, Wilmington, Winchester, and Woburn.",
            'has_po_box' : False,
            'phone': "(978) 689-7833",
            'fax':"",
            'address': {
                'city': "Woburn",
                'address': "200 Trade Center",
                'unit': "Courtroom 540 - 5th Floor",
                'state': "MA",
                'zip': "01801",
                'county': "Middlesex County",
                'orig_address':  "200 Trade Center, Courtroom 540 - 5th Floor, Woburn, MA 01801"
            },
            'location': {
                'latitude': 42.500543,
                'longitude': -71.1656604
            }
        }
        courts.append(court)

    courts.sort(key=lambda k: k['name']) # We want to sort within category of court

    return courts

def save_courts_to_file():
    ''' Writes all courts to .json files in Playground data sources folder'''
    courts = [
        [
            'juvenile_courts', 'https://www.mass.gov/orgs/juvenile-court/locations'
        ],
        [
            'probate_and_family_courts', 'https://www.mass.gov/orgs/probate-and-family-court/locations'
        ], 
        [
            'district_courts', 'https://www.mass.gov/orgs/district-court/locations'
        ],
        [
            'housing_courts', 'https://www.mass.gov/orgs/housing-court/locations'
        ],
        [
            'bmc', 'https://www.mass.gov/orgs/boston-municipal-court/locations'
        ],
        [
            'superior_courts', 'https://www.mass.gov/orgs/superior-court/locations'
        ],
        [
            'land_court', 'https://www.mass.gov/orgs/land-court/locations'
        ]
    ]
    sources = PlaygroundSection('sources')
    for court in courts:
        jdata = json.dumps(get_courts_from_massgov_url(court[1]))
        sources.write_file(court[0] + '.json', jdata, binary=True)
        
    # for court in courts: 
    #     #area = PlaygroundSection('sources').get_area()
    #     fpath = os.path.join(sources.directory, court[0] + '.json')
    #     jdata = text_type(json.dumps(get_courts_from_massgov_url(court[1])))
    #     f = open(fpath, 'w')
    #     f.write(jdata)
    #     f.close()
    #sources.finalize()

def test_write():
    area = PlaygroundSection('sources').get_area()
    fpath = os.path.join(area.directory, "test" + '.json')
    jdata = "test"
    f = open(fpath, 'w')
    f.write(jdata)
    f.close()
    area.finalize()
    return fpath

class MACourt(Court):
    """Object representing a court in Massachusetts.
    TODO: it could be interesting to store a jurisdiction on a court. But this is non-trivial. Should it be geo boundaries? 
    A list of cities? A list of counties? Instead, we use a function on the CourtList object that filters courts by
    address and can use any of those three features of the court to do the filtering."""
    def init(self, *pargs, **kwargs):
        super(MACourt, self).init(*pargs, **kwargs)
        if 'address' not in kwargs:
            self.initializeAttribute('address', Address)
        if 'jurisdiction' not in kwargs: # This attribute isn't used. Could be a better way to handle court locating
            self.jurisdiction = list()
        if 'location' not in kwargs:
            self.initializeAttribute('location', LatitudeLongitude)

    def __unicode__(self):
        return text_type(self.name)

    def __str__(self):
        return self.__unicode__().encode('utf-8') if PY2 else self.name     

class MACourtList(DAList):
    """Represents a list of courts in Massachusetts. Package includes a cached list that is scraped from mass.gov"""
    def init(self, *pargs, **kwargs):
        super(MACourtList, self).init(*pargs, **kwargs)
        self.auto_gather = False
        self.gathered = True
        self.object_type = MACourt
        if hasattr(self,'courts'):
            if isinstance(self.courts, list):
                self.load_courts(courts=self.courts)
            elif self.courts is True:
                self.load_courts()

    def filter_courts(self, court_types):
        """Return the list of courts matching the specified department(s). E.g., Housing Court. court_types may be list or single court department."""
        if isinstance(court_types, str):
            return self.filter(department=court_types)
        elif isinstance(court_types, list):
            return [court for court in self.elements if court.department in court_types]
        else:
            return None

    def matching_courts(self, address, court_types=None):
        """Return a list of courts serving the specified address. Optionally limit to one or more types of courts
        TODO: Alter this so it works with a list of addresses, and flattens a list of results from a single function."""
        court_type_map = {
            'Housing Court': self.matching_housing_court,
            'District Court': self.matching_district_court,
            'Boston Municipal Court': self.matching_bmc,
            'Juvenile Court': self.matching_juvenile_court,
            'Land Court': self.matching_land_court,
            'Probate and Family Court': self.matching_probate_and_family_court,
            'Superior Court': self.matching_superior_court,
        }

        if isinstance(court_types, str):
            return court_type_map[court_types](address)
        elif isinstance(court_types, list):
            matches = []
            for court_type in court_types:
                matches.append(court_type_map[court_type](address))
        else:
            # Return all of the courts if court_types is not filtering the results
            matches = []
            for key in court_type_map:
                matches.append(court_type_map[key](address))
        
        return matches

    def load_courts(self, courts=['housing_courts','bmc','district_courts','superior_courts'], data_path='docassemble.MACourts:data/sources/'):
        """Load a set of courts into the MACourtList. Courts should be a list of names of JSON files in the data/sources directory.
        Will fall back on loading courts directly from MassGov if the cached file doesn't exist. Available courts: district_courts, housing_courts,bmc,superior_courts,land_court,juvenile_courts,probate_and_family_courts"""
        try:
            for court in courts:
                self.load_courts_from_file(court, data_path=data_path)
        except IOError:
            for court in courts:
                self.load_courts_from_massgov_by_filename(court)

    def load_courts_from_massgov_by_filename(self, court_name):
        """Loads the specified court from Mass.gov, assuming website format hasn't changed. It has an embedded JSON we parse"""
        urls = {
            'district_courts': 'https://www.mass.gov/orgs/district-court/locations',
            'housing_courts': 'https://www.mass.gov/orgs/housing-court/locations',
            'bmc': 'https://www.mass.gov/orgs/boston-municipal-court/locations',
            'superior_courts': 'https://www.mass.gov/orgs/superior-court/locations',
            'land_court': 'https://www.mass.gov/orgs/land-court/locations',
            'juvenile_courts': 'https://www.mass.gov/orgs/juvenile-court/locations',
            'probate_and_family_courts': 'https://www.mass.gov/orgs/probate-and-family-court/locations'
            }
        filename = court_name

        courts = get_courts_from_massgov_url(urls[filename])

        # 'housing_courts','bmc','district_courts','superior_courts'
        if court_name == 'housing_courts':
            court_department = 'Housing Court'
        elif court_name == 'bmc':
            court_department = 'Boston Municipal Court'
        elif court_name == 'district_courts':
            court_department = 'District Court'
        elif court_name == 'superior_courts':
            court_department = 'Superior Court'
        elif court_name == 'juvenile_courts':
            court_department = 'Juvenile Court'
        elif court_name in ['land_courts', 'land_court']:
            court_department = 'Land Court'
        elif court_name == 'probate_and_family_courts':
            court_department = 'Probate and Family Court'
        
        for item in courts:
            # translate the dictionary data into an MACourt
            court = self.appendObject()
            court.name = item['name']
            court.department = court_department
            court.division = parse_division_from_name(item['name'])
            court.phone = item['phone']
            court.fax = item['fax']
            court.location.latitude = item['location']['latitude']
            court.location.longitude = item['location']['longitude']
            court.has_po_box = item.get('has_po_box')
            court.description = item.get('description')

            court.address.address = item['address']['address']
            court.address.city = item['address']['city']
            court.address.state = item['address']['state']
            court.address.zip = item['address']['zip']
            court.address.county = item['address']['county']
            court.address.orig_address = item['address'].get('orig_address')            
        
    def load_courts_from_file(self, court_name, data_path='docassemble.MACourts:data/sources/'):
        """Add the list of courts at the specified JSON file into the current list"""

        json_path = court_name

        # 'housing_courts','bmc','district_courts','superior_courts'
        if court_name == 'housing_courts':
            court_department = 'Housing Court'
        elif court_name == 'bmc':
            court_department = 'Boston Municipal Court'
        elif court_name == 'district_courts':
            court_department = 'District Court'
        elif court_name == 'superior_courts':
            court_department = 'Superior Court'
        elif court_name == 'juvenile_courts':
            court_department = 'Juvenile Court'
        elif court_name in ['land_courts', 'land_court']:
            court_department = 'Land Court'
        elif court_name == 'probate_and_family_courts':
            court_department = 'Probate and Family Court'

        path = path_and_mimetype(os.path.join(data_path,json_path+'.json'))[0]

        with open(path) as courts_json:
            courts = json.load(courts_json)

        for item in courts:
            # translate the dictionary data into an MACourtList
            court = self.appendObject()
            court.name = item['name']
            court.department = court_department
            court.division = parse_division_from_name(item['name'])
            court.phone = item['phone']
            court.fax = item['fax']
            court.location.latitude = item['location']['latitude']
            court.location.longitude = item['location']['longitude']
            court.has_po_box = item.get('has_po_box')
            court.description = item.get('description')

            court.address.address = item['address']['address']
            court.address.city = item['address']['city']
            court.address.state = item['address']['state']
            court.address.zip = item['address']['zip']
            court.address.county = item['address']['county']
            court.address.orig_address = item['address'].get('orig_address')

    def matching_juvenile_court(self, address):
        return None
    
    def matching_probate_and_family_court(self, address):
        return None
    
    def matching_superior_court(self, address):
        return None

    def matching_land_court(self, address):
        """There's currently only one Land Court"""
        return next((court for court in self.elements if court.name.rstrip().lower() == 'Land Court'),None)

    def matching_district_court(self, address):
        """Return the MACourt representing the District Court serving the given address""" 
        court_name = self.matching_district_court_name(address)
        return next ((court for court in self.elements if court.name.rstrip().lower() == court_name.lower()), None)

    def matching_district_court_name(self, address):
        """Returns the name of the MACourt representing the district court that covers the specified address.
        Harcoded and must be updated if court jurisdictions or names change. Address must specify county attribute"""
        if (not hasattr(address, 'county')) or (address.county.lower().strip() == ''):
            return ''
        if hasattr(address, 'norm') and hasattr(address.norm, 'city') and hasattr(address.norm, 'county'):
            address_to_compare = address.norm
        else:
            address_to_compare = address
        if (address_to_compare.county.lower() == "dukes county") or (address_to_compare.city.lower() in ["edgartown", "oak bluffs", "tisbury", "west tisbury", "chilmark", "aquinnah", "gosnold", "elizabeth islands"]):
            local_district_court = "Edgartown District Court"
        elif (address_to_compare.county.lower() == "nantucket county") or (address_to_compare.city.lower() in ["nantucket"]):
            local_district_court = "Nantucket District Court"
        elif address_to_compare.city.lower() in ["barnstable", "yarmouth", "sandwich"]:
            local_district_court = "Barnstable District Court"
        elif address_to_compare.city.lower() in ["attleboro", "mansfield", "north attleboro", "norton"]:
            local_district_court = "Attleboro District Court"
        elif address_to_compare.city.lower() in ["ashby", "ayer", "boxborough", "dunstable", "groton", "littleton", "pepperell", "shirley", "townsend", "westford", "devens","devens regional enterprise zone"]:
            local_district_court = "Ayer District Court"
        elif address_to_compare.city.lower() in ["abington", "bridgewater", "brockton", "east bridgewater", "west bridgewater", "whitman"]:
            local_district_court = "Brockton District Court"
        elif address_to_compare.city.lower() in ["brookline"]:
            local_district_court = "Brookline District Court"
        elif address_to_compare.city.lower() in ["cambridge", "arlington", "belmont"]:
            local_district_court = "Cambridge District Court"
        elif address_to_compare.city.lower() in ["chelsea", "revere"]:
            local_district_court = "Chelsea District Court"
        elif address_to_compare.city.lower() in ["chicopee"]:
            local_district_court = "Chicopee District Court"
        elif address_to_compare.city.lower() in ["berlin", "bolton", "boylston", "clinton", "harvard", "lancaster", "sterling", "west boylston"]:
            local_district_court = "Clinton District Court"
        elif address_to_compare.city.lower() in ["concord", "carlisle", "lincoln", "lexington", "bedford", "acton", "maynard", "stow"]:
            local_district_court = "Concord District Court"
        elif address_to_compare.city.lower() in ["dedham", "dover", "medfield", "needham", "norwood", "wellesley", "westwood"]:
            local_district_court = "Dedham District Court"
        elif address_to_compare.city.lower() in ["charlton", "dudley", "oxford", "southbridge", "sturbridge", "webster"]:
            local_district_court = "Dudley District Court"
        elif address_to_compare.city.lower() in ["barre", "brookfield", "east brookfield", "hardwick", "leicester", "new braintree", "north brookfield", "oakham", "paxton", "rutland", "spencer", "warren", "west brookfield"]:
            local_district_court = "East Brookfield District Court"
        elif address_to_compare.city.lower() in ["amherst", "belchertown", "granby", "hadley", "pelham", "south hadley", "ware", "m.d.c. quabbin reservoir", "watershed area"]:
            local_district_court = "Eastern Hampshire District Court"
        elif address_to_compare.city.lower() in ["fall river", "freetown", "somerset", "swansea", "westport"]:
            local_district_court = "Fall River District Court"
        elif address_to_compare.city.lower() in ["bourne", "falmouth", "mashpee"]:
            local_district_court = "Falmouth District Court"
        elif address_to_compare.city.lower() in ["fitchburg", "lunenburg"]:
            local_district_court = "Fitchburg District Court"
        elif address_to_compare.city.lower() in ["ashland", "framingham", "holliston", "hopkinton", "sudbury", "wayland"]:
            local_district_court = "Framingham District Court"
        elif address_to_compare.city.lower() in ["gardner", "hubbardston", "petersham", "westminster"]:
            local_district_court = "Gardner District Court"
        elif address_to_compare.city.lower() in ["essex", "gloucester", "rockport"]:
            local_district_court = "Gloucester District Court"
        elif address_to_compare.city.lower() in ["ashfield", "bernardston", "buckland", "charlemont", "colrain", "conway", "deerfield", "gill", "greenfield", "hawley", "heath", "leyden", "monroe", "montague", "northfield", "rowe", "shelburne", "sunderland", "whately"]:
            local_district_court = "Greenfield District Court"
        elif address_to_compare.city.lower() in ["boxford", "bradford", "georgetown", "groveland", "haverhill"]:
            local_district_court = "Haverhill District Court"
        elif address_to_compare.city.lower() in ["hanover", "hingham", "hull", "norwell", "rockland", "scituate"]:
            local_district_court = "Hingham District Court"
        elif address_to_compare.city.lower() in ["holyoke"]:
            local_district_court = "Holyoke District Court"
        elif address_to_compare.city.lower() in ["ipswich", "hamilton", "wenham", "topsfield"]:
            local_district_court = "Ipswich District Court"
        elif address_to_compare.city.lower() in ["andover", "lawrence", "methuen", "north andover"]:
            local_district_court = "Lawrence District Court"
        elif address_to_compare.city.lower() in ["holden", "princeton", "leominster"]:
            local_district_court = "Leominster District Court"
        elif address_to_compare.city.lower() in ["billerica", "chelmsford", "dracut", "lowell", "tewksbury", "tyngsboro"]:
            local_district_court = "Lowell District Court"
        elif address_to_compare.city.lower() in ["lynn", "marblehead", "nahant", "saugus", "swampscott"]:
            local_district_court = "Lynn District Court"
        elif address_to_compare.city.lower() in ["malden", "melrose", "everett", "wakefield"]:
            local_district_court = "Malden District Court"
        elif address_to_compare.city.lower() in ["marlborough", "hudson"]:
            local_district_court = "Marlborough District Court"
        elif address_to_compare.city.lower() in ["mendon", "upton", "hopedale", "milford", "bellingham"]:
            local_district_court = "Milford District Court"
        elif address_to_compare.city.lower() in ["acushnet", "dartmouth", "fairhaven", "freetown", "new bedford", "westport"]:
            local_district_court = "New Bedford District Court"
        elif address_to_compare.city.lower() in ["amesbury", "merrimac", "newbury", "newburyport", "rowley", "salisbury", "west newbury"]:
            local_district_court = "Newburyport District Court"
        elif address_to_compare.city.lower() in ["newton"]:
            local_district_court = "Newton District Court"
        elif address_to_compare.city.lower() in ["chesterfield", "cummington", "easthampton", "goshen", "hatfield", "huntington", "middlefield", "northampton", "plainfield", "southampton", "westhampton", "williamsburg", "worthington"]:
            local_district_court = "Northampton District Court"
        elif address_to_compare.city.lower() in ["adams", "cheshire", "clarksburg", "florida", "hancock", "new ashford", "north adams", "savoy", "williamstown", "windsor"]:
            local_district_court = "Northern Berkshire District Court"
        elif address_to_compare.city.lower() in ["athol", "erving", "leverett", "new salem", "orange", "shutesbury", "warwick", "wendell"]:
            local_district_court = "Orange District Court"
        elif address_to_compare.city.lower() in ["brewster", "chatham", "dennis", "eastham", "orleans", "harwich", "truro", "wellfleet", "provincetown"]:
            local_district_court = "Orleans District Court"
        elif address_to_compare.city.lower() in ["brimfield", "east longmeadow", "hampden", "holland", "ludlow", "monson", "palmer", "wales", "wilbraham"]:
            local_district_court = "Palmer District Court"
        elif address_to_compare.city.lower() in ["lynnfield", "peabody"]:
            local_district_court = "Peabody District Court"
        elif address_to_compare.city.lower() in ["becket", "dalton", "hancock", "hinsdale", "lanesborough", "lenox", "peru", "pittsfield", "richmond", "washington", "windsor"]:
            local_district_court = "Pittsfield District Court"
        elif address_to_compare.city.lower() in ["duxbury", "halifax", "hanson", "kingston", "marshfield", "pembroke", "plymouth", "plympton"]:
            local_district_court = "Plymouth District Court"
        elif address_to_compare.city.lower() in ["braintree", "cohasset", "holbrook", "milton", "quincy", "randolph", "weymouth"]:
            local_district_court = "Quincy District Court"
        elif address_to_compare.city.lower() in ["beverly", "danvers", "manchester by the sea", "middleton", "salem"]:
            local_district_court = "Salem District Court"
        elif address_to_compare.city.lower() in ["medford", "somerville"]:
            local_district_court = "Somerville District Court"
        elif address_to_compare.city.lower() in ["alford", "becket", "egremont", "great barrington", "lee", "lenox", "monterey", "mt. washington", "new marlborough", "otis", "sandisfield", "sheffield", "stockbridge", "tyringham", "west stockbridge"]:
            local_district_court = "Southern Berkshire District Court"
        elif address_to_compare.city.lower() in ["longmeadow", "springfield", "west springfield"]:
            local_district_court = "Springfield District Court"
        elif address_to_compare.city.lower() in ["avon", "canton", "sharon", "stoughton"]:
            local_district_court = "Stoughton District Court"
        elif address_to_compare.city.lower() in ["berkley", "dighton", "easton", "raynham", "rehoboth", "seekonk", "taunton"]:
            local_district_court = "Taunton District Court"
        elif address_to_compare.city.lower() in ["blackstone", "douglas", "millville", "northbridge", "sutton", "uxbridge"]:
            local_district_court = "Uxbridge District Court"
        elif address_to_compare.city.lower() in ["waltham", "watertown", "weston"]:
            local_district_court = "Waltham District Court"
        elif address_to_compare.city.lower() in ["carver", "lakeville", "mattapoisett", "middleboro", "rochester", "wareham"]:
            local_district_court = "Wareham District Court"
        elif address_to_compare.city.lower() in ["grafton", "northborough", "shrewsbury", "southborough", "westborough"]:
            local_district_court = "Westborough District Court"
        elif address_to_compare.city.lower() in ["agawam", "blandford", "chester", "granville", "montgomery", "russell", "southwick", "tolland", "westfield"]:
            local_district_court = "Westfield District Court"
        elif address_to_compare.city.lower() in ["ashburnham", "phillipston", "royalston", "templeton", "winchendon"]:
            local_district_court = "Winchendon District Court"
        elif address_to_compare.city.lower() in ["burlington", "north reading", "reading", "stoneham", "wilmington", "winchester", "woburn"]:
            local_district_court = "Woburn District Court"
        elif address_to_compare.city.lower() in ["auburn", "millbury", "worcester"]:
            local_district_court = "Worcester District Court"
        elif address_to_compare.city.lower() in ["foxborough", "franklin", "medway", "millis", "norfolk", "plainville", "walpole", "wrentham"]:
            local_district_court = "Wrentham District Court"
        else:
            local_district_court = ""            
        return local_district_court

    def matching_housing_court(self, address):
        """Return the MACourt representing the Housing Court serving the given address""" 
        court_name = self.matching_housing_court_name(address)
        return next ((court for court in self.elements if court.name.rstrip().lower() == court_name.lower()), None)

    def matching_housing_court_name(self,address):
        """Returns the name of the MACourt representing the housing court that covers the specified address.
        Harcoded and must be updated if court jurisdictions or names change. Address must specify county attribute"""
        if (not hasattr(address, 'county')) or (address.county.lower().strip() == ''):
            return ''
        if hasattr(address, 'norm') and hasattr(address.norm, 'city') and hasattr(address.norm, 'county'):
            address_to_compare = address.norm
        else:
            address_to_compare = address
        if (address_to_compare.county.lower() == "suffolk county") or (address_to_compare.city.lower() in ["newton","brookline"]):
            local_housing_court = "Eastern Housing Court"
        elif address_to_compare.city.lower() in ["arlington","belmont","cambridge","medford","somerville"]:
            local_housing_court = "Eastern Housing Court - Middlesex Session"
        elif address_to_compare.city.lower() in ["ashfield", "bernardston", "buckland", "charlemont", "colrain", "conway", "deerfield", "erving", "gill", "greenfield", "hawley", "heath", "leverett", "leyden", "monroe", "montague", "new salem", "northfield", "orange", "rowe", "shelburne", "shutesbury", "sunderland", "warwick", "wendell", "whately"]:
            local_housing_court = "Western Housing Court - Greenfield Session"
        elif address_to_compare.city.lower() in ['amherst', 'belchertown', 'chesterfield', 'cummington', 'easthampton', 'goshen', 'granby', 'hadley', 'hatfield', 'huntington', 'middlefield', 'northampton', 'pelham', 'plainfield', 'south hadley', 'southampton', 'ware', 'westhampton', 'williamsburg','worthington']:
            local_housing_court = "Western Housing Court - Hadley Session"
        elif address_to_compare.county.lower() == "berkshire":
            local_housing_court = "Western Housing Court - Pittsfield Session"
        elif address_to_compare.city.lower() in ['agawam', 'blandford', 'brimfield', 'chester', 'chicopee', 'east longmeadow', 'granville', 'hampden', 'holland', 'holyoke', 'longmeadow', 'ludlow', 'monson', 'montgomery', 'palmer', 'russell', 'southwick', 'springfield', 'tolland', 'wales', 'west springfield', 'westfield','wilbraham']:
            local_housing_court = "Western Housing Court - Springfield Session"
        elif address_to_compare.city.lower() in ['charlton', 'dudley', 'oxford', 'southbridge', 'sturbridge', 'webster']:
            local_housing_court ="Central Housing Court - Dudley Session"
        elif address_to_compare.city.lower() in ['ashburnham', 'athol', 'fitchburg', 'gardner', 'holden', 'hubbardston', 'leominster', 'lunenberg', 'petersham', 'phillipston', 'princeton', 'royalston', 'templeton', 'westminster', 'winchendon']:
            local_housing_court = "Central Housing Court - Leominster Session"
        elif address_to_compare.city.lower() in ['ashland', 'berlin', 'bolton', 'framingham', 'harvard', 'holliston', 'hopkinton', 'hudson', 'marlborough', 'natick', 'northborough', 'sherborn', 'southborough', 'sudbury', 'wayland', 'westborough']:
            local_housing_court = "Central Housing Court - Marlborough Session"
        elif address_to_compare.city.lower() in ['auburn', 'barre', 'bellingham', 'blackstone', 'boylston', 'brookfield', 'clinton', 'douglas', 'east brookfield', 'grafton', 'hardwick', 'hopedale', 'lancaster', 'leicester', 'mendon', 'milford', 'millbury', 'millville', 'new braintree', 'northbridge', 'north brookfield', 'oakham', 'oxford', 'paxton', 'rutland', 'shrewsbury', 'spencer', 'sterling', 'sutton', 'upton', 'uxbridge', 'warren', 'west boylston', 'worcester']:
            local_housing_court = "Central Housing Court - Worcester Session"
        elif address_to_compare.city.lower() in ['abington', 'avon', 'bellingham', 'braintree', 'bridgewater', 'brockton', 'canton', 'cohasset', 'dedham', 'dover', 'east bridgewater', 'eastham', 'foxborough', 'franklin', 'holbrook', 'medfield', 'medway', 'millis', 'milton', 'needham', 'norfolk', 'norwood', 'plainville', 'quincy', 'randolph', 'sharon', 'stoughton', 'walpole', 'wellesley', 'west bridgewater', 'westwood', 'weymouth', 'whitman', 'wrentham']:
            local_housing_court = "Metro South Housing Court - Brockton Session"
        elif address_to_compare.county.lower() == "norfolk county" and not address_to_compare.city.lower() in ["newton","brookline"]:
            local_housing_court = "Metro South Housing Court - Canton Session"
        elif address_to_compare.city.lower() in ['amesbury', 'andover', 'boxford', 'georgetown', 'groveland', 'haverhill', 'lawrence', 'merrimac', 'methuen', 'newbury', 'newburyport', 'north andover', 'rowley', 'salisbury', 'west newbury']:
            local_housing_court =  "Northeast Housing Court - Lawrence Session"
        elif address_to_compare.city.lower() in ['acton', 'ashby', 'ayer', 'billerica', 'boxborough', 'carlisle', 'chelmsford', 'devens', 'dracut', 'dunstable', 'groton', 'littleton', 'lowell', 'maynard', 'pepperell', 'shirley', 'stow', 'tewksbury', 'townsend', 'tyngsborough', 'westford']:
            local_housing_court = "Northeast Housing Court - Lowell Session"
        elif address_to_compare.city.lower() in ['lynn', 'nahant', 'saugus']:
            local_housing_court = "Northeast Housing Court - Lynn Session"
        elif address_to_compare.city.lower() in ['beverly', 'danvers', 'essex', 'gloucester', 'hamilton', 'ipswich', 'lynnfield', 'manchester-by-the-sea', 'marblehead', 'middleton', 'peabody', 'rockport', 'salem', 'swampscott', 'topsfield', 'wenham']:
            local_housing_court = "Northeast Housing Court - Salem Session"
        elif address_to_compare.city.lower() in ['bedford', 'burlington', 'concord', 'everett','lexington', 'lincoln', 'malden', 'melrose', 'north reading', 'reading', 'stoneham', 'wakefield', 'waltham', 'watertown', 'weston', 'wilmington', 'winchester', 'woburn']:
            local_housing_court = "Northeast Housing Court - Woburn Session"
        elif address_to_compare.city.lower() in ['freetown', 'westport', 'fall river', 'somerset','swansea']:
            local_housing_court = "Southeast Housing Court - Fall River Session"
        elif address_to_compare.city.lower() in ['acushnet', 'dartmouth', 'fairhaven', 'freetown', 'new bedford','westport']:
            local_housing_court = "Southeast Housing Court - New Bedford Session"
        elif address_to_compare.city.lower() in ['aquinnah', 'barnstable', 'bourne', 'brewster', 'carver', 'chatham', 'chilmark', 'dennis', 'duxbury', 'edgartown', 'falmouth', 'halifax', 'hanson', 'harwich', 'kingston', 'lakeville', 'marion', 'marshfield', 'mashpee', 'mattapoisett', 'middleborough', 'nantucket', 'oak bluffs', 'pembroke', 'plymouth', 'plympton', 'provincetown', 'rochester', 'sandwich', 'and wareham.beginning on august 6', 'the plymouth session of the southeast housing court will also serve accord', 'assinippi', 'hanover', 'hingham', 'hull', 'humarock', 'norwell', 'rockland', 'scituate']:
            local_housing_court = "Southeast Housing Court - Plymouth Session"
        elif address_to_compare.city.lower() in ['attleboro', 'berkley', 'dighton', 'easton', 'mansfield', 'north attleborough', 'norton', 'raynham', 'rehoboth', 'seekonk','taunton']:
            local_housing_court = "Southeast Housing Court - Taunton Session"
        else:
            local_housing_court = ""
        return local_housing_court
    
    def matching_bmc(self, address):
        try:
            court_name = self.get_boston_ward_number(address)[1] + ' Division, Boston Municipal Court'
        except:
            return None
        return next ((court for court in self.elements if court.name.rstrip().lower() == court_name.lower()), None)

    def load_boston_wards_from_file(self, json_path, data_path='docassemble.MACourts:data/sources/'):
        """load geojson file for boston wards"""
        path = path_and_mimetype(os.path.join(data_path,json_path+'.geojson'))[0]
        wards = gpd.read_file(path)
        return wards
    
    def get_boston_ward_number(self, address):
        """
        This function takes an address object as input,
        filters a geojson file to only include the ward
        that contains the address, and returns the
        ward number and name of the courthouse.

        Dependencies:
        1.Geopandas for loading the geojson file
        2.Raw geojson from github. Right now, this is referencing Calvin Metclaf's own repository. 
            We may want to host this geojson file under the GBLS/docassemble-MACourts repo
        """

        #if location data is not in address object, return empty string
        if (not hasattr(address, 'location')):
            return '',''

        else:
            #load geojson Boston Ward map
            boston_wards = self.load_boston_wards_from_file(json_path = "boston_wards")

            #construct point from address_object to use for lookup
            p1 = Point(address.location.longitude, address.location.latitude)

            #filter wards list to only include 
            #the ward containing the address
            ward = boston_wards[[p1.within(boston_wards.geometry[i]) for i in range(len(boston_wards))]]

            ward_number = ward.iloc[0].Ward_Num
            courthouse_name = ward.iloc[0].courthouse

            #return ward number and courthouse name
            return ward_number, courthouse_name

def parse_division_from_name(court_name):
    rules = {
        "District Court": r'(.*)( District Court)',
        "Boston Municipal Court": r"(.*)(, Boston Municipal Court)",
        "Housing Court": r"(.*)( Housing Court)",
        "Superior Court": r"(.*)( Superior Court)",
        "Juvenile Court": r"(.*)( Juvenile Court)",
        "Land Court": r"(Land Court)",
        "Probate and Family": r"(.*)( Probate and Family Court)",}
    for key in rules:
        match = re.match(rules[key], court_name)
        if match:
            return match[1] # We need to make sure the regex has a group though
            # if len(match) > 1:
            #     return match[1]
            # else:
            #     return match[0]
    # court.department = item['name']
    return court_name

if __name__ == '__main__':
    import pprint
    courts = get_courts_from_massgov_url('https://www.mass.gov/orgs/district-court/locations')
    pprint.pprint(courts)
