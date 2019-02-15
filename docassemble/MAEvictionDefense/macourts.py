from docassemble.base.core import DAObject, DAList, DADict
from docassemble.base.util import path_and_mimetype, Address, LatitudeLongitude, DAStaticFile, text_type
from docassemble.base.legal import Court
import io, json, sys, requests, bs4, re, os #, cbor
# from operator import itemgetter
# from docassemble.base.logger import logmessage
from docassemble.webapp.playground import PlaygroundSection

def get_courts_from_massgov_url(url, shim_ehc_middlesex=True, shim_nhc_woburn=True):
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
                name = item['title']['text']
                description = item['description']['richText']['rteElements'][0]['data']['rawHtml']['content']['#context']['value']
                break

        address = Address()
        orig_address = marker['infoWindow']['address'] # The geolocate method does _not_ work with PO Boxes (silently discards)
        clean_address = re.sub(r' *PO Box .*?,',"",orig_address)
        has_po_box = not clean_address == orig_address # We want to track if there was a PO Box where mail should be delivered
        address.address = orig_address

        if address.address == '':
            address.city = ''
            address.state = ''
            address.zip = ''
            address.county = ''
            address.unit = ''
        else:
            address.geolocate(clean_address)
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
                'county': "Middlesex",
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
                'county': "Middlesex",
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
            'land_courts', 'https://www.mass.gov/orgs/land-court/locations'
        ],
        [
            'juvenile_courts', 'https://www.mass.gov/orgs/juvenile-court/locations'
        ],
        [
            'probate_and_family_courts', 'https://www.mass.gov/orgs/probate-and-family-court/locations'
        ] 
    ]

    try:
        for court in courts: 
            area = PlaygroundSection('sources').get_area()
            fpath = os.path.join(area.directory, court[0] + '.json')
            jdata = text_type(json.dumps(get_courts_from_massgov_url(court[1])))
            f = open(fpath, 'w')
            f.write(jdata)
            f.close()
            area.finalize()
    except:
        e = sys.exc_info()[0]
        return e
    else:
        return "Finished saving courts"

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
    def init(self, *pargs, **kwargs):
        super(MACourt, self).init(*pargs, **kwargs)
        if 'address' not in kwargs:
            self.initializeAttribute('address', Address)
        if 'jurisdiction' not in kwargs:
            self.jurisdiction = list()
        if 'location' not in kwargs:
            self.initializeAttribute('location', LatitudeLongitude)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.__unicode__        

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

    def load_courts(self, courts=['housing_courts','bmc','district_courts','superior_courts'], data_path='docassemble.MACourts:data/sources/'):
        """Load a set of courts into the MACourtList. Courts should be a list of names of JSON files in the data/sources directory.
        Will fall back on loading default set of courts from Mass.gov. Default set of courts is applicable to housing cases"""
        try:
            for court in courts:
                self.load_courts_from_file(court, data_path=data_path)
        except IOError:
            if courts == ['housing_courts','bmc','district_courts','superior_courts']:
                self.load_from_massgov()
            else:
                self.load_from_massgov(housing_only=False)

    def load_from_massgov(self, housing_only=True):
        """Load courts directly from Mass.gov: fallback if cached files don't exist. URLs hardcoded."""
        if housing_only:
            urls = ['https://www.mass.gov/orgs/housing-court/locations',
                    'https://www.mass.gov/orgs/boston-municipal-court/locations',
                    'https://www.mass.gov/orgs/district-court/locations',
                    'https://www.mass.gov/orgs/superior-court/locations']
        else:
            urls = ['https://www.mass.gov/orgs/district-court/locations',
                    'https://www.mass.gov/orgs/housing-court/locations',
                    'https://www.mass.gov/orgs/boston-municipal-court/locations',
                    'https://www.mass.gov/orgs/superior-court/locations',
                    'https://www.mass.gov/orgs/land-court/locations',
                    'https://www.mass.gov/orgs/juvenile-court/locations',
                    'https://www.mass.gov/orgs/probate-and-family-court/locations']
        for url in urls:
            courts = get_courts_from_massgov_url(url)
            
            for item in courts:
                # translate the dictionary data into an MACourtList
                court = self.appendObject()
                court.name = item['name']
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

    def load_courts_from_file(self, json_path, data_path='docassemble.MACourts:data/sources/'):
        """Add the list of courts at the specified JSON file into the current list"""

        path = path_and_mimetype(os.path.join(data_path,json_path+'.json'))[0]

        with open(path) as courts_json:
            courts = json.load(courts_json)

        for item in courts:
            # translate the dictionary data into an MACourtList

            court = self.appendObject()
            court.name = item['name']
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

    def matching_housing_court(self, address):
        """Return the MACourt representing the Housing Court serving the given address""" 
        court_name = self.matching_housing_court_name(address)
        return next ((court for court in self.elements if court.name == court_name), None)

    def matching_housing_court_name(self,address):
        """Returns the name of the MACourt representing the housing court that covers the specified address.
        Harcoded and must be updated if court jurisdictions or names change."""
        if (address.county == "Suffolk County") or (address.city in ["Newton","Brookline"]):
            local_housing_court = "Eastern Housing Court"
        elif address.city in ["Arlington","Belmont","Cambridge","Medford","Somerville"]:
            local_housing_court = "Eastern Housing Court - Middlesex Session"
        elif address.city in ["Ashfield", "Bernardston", "Buckland", "Charlemont", "Colrain", "Conway", "Deerfield", "Erving", "Gill", "Greenfield", "Hawley", "Heath", "Leverett", "Leyden", "Monroe", "Montague", "New Salem", "Northfield", "Orange", "Rowe", "Shelburne", "Shutesbury", "Sunderland", "Warwick", "Wendell", "Whately"]:
            local_housing_court = "Western Housing Court - Greenfield Session"
        elif address.city in ['Amherst', 'Belchertown', 'Chesterfield', 'Cummington', 'Easthampton', 'Goshen', 'Granby', 'Hadley', 'Hatfield', 'Huntington', 'Middlefield', 'Northampton', 'Pelham', 'Plainfield', 'South Hadley', 'Southampton', 'Ware', 'Westhampton', 'Williamsburg','Worthington']:
            local_housing_court = "Western Housing Court - Hadley Session"
        elif address.county == "Berkshire":
            local_housing_court = "Western Housing Court - Pittsfield Session"
        elif address.city in ['Agawam', 'Blandford', 'Brimfield', 'Chester', 'Chicopee', 'East Longmeadow', 'Granville', 'Hampden', 'Holland', 'Holyoke', 'Longmeadow', 'Ludlow', 'Monson', 'Montgomery', 'Palmer', 'Russell', 'Southwick', 'Springfield', 'Tolland', 'Wales', 'West Springfield', 'Westfield','Wilbraham']:
            local_housing_court = "Western Housing Court - Springfield Session"
        elif address.city in ['Charlton', 'Dudley', 'Oxford', 'Southbridge', 'Sturbridge', 'Webster']:
            local_housing_court ="Central Housing Court - Dudley Session"
        elif address.city in ['Ashburnham', 'Athol', 'Fitchburg', 'Gardner', 'Holden', 'Hubbardston', 'Leominster', 'Lunenberg', 'Petersham', 'Phillipston', 'Princeton', 'Royalston', 'Templeton', 'Westminster', 'Winchendon']:
            local_housing_court = "Central Housing Court - Leominster Session"
        elif address.city in ['Ashland', 'Berlin', 'Bolton', 'Framingham', 'Harvard', 'Holliston', 'Hopkinton', 'Hudson', 'Marlborough', 'Natick', 'Northborough', 'Sherborn', 'Southborough', 'Sudbury', 'Wayland', 'Westborough']:
            local_housing_court = "Central Housing Court - Marlborough Session"
        elif address.city in ['Auburn', 'Barre', 'Bellingham', 'Blackstone', 'Boylston', 'Brookfield', 'Clinton', 'Douglas', 'East Brookfield', 'Grafton', 'Hardwick', 'Hopedale', 'Lancaster', 'Leicester', 'Mendon', 'Milford', 'Millbury', 'Millville', 'New Braintree', 'Northbridge', 'North Brookfield', 'Oakham', 'Oxford', 'Paxton', 'Rutland', 'Shrewsbury', 'Spencer', 'Sterling', 'Sutton', 'Upton', 'Uxbridge', 'Warren', 'West Boylston', 'Worcester']:
            local_housing_court = "Central Housing Court - Worcester Session"
        elif address.city in ['Abington', 'Avon', 'Bellingham', 'Braintree', 'Bridgewater', 'Brockton', 'Canton', 'Cohasset', 'Dedham', 'Dover', 'East Bridgewater', 'Eastham', 'Foxborough', 'Franklin', 'Holbrook', 'Medfield', 'Medway', 'Millis', 'Milton', 'Needham', 'Norfolk', 'Norwood', 'Plainville', 'Quincy', 'Randolph', 'Sharon', 'Stoughton', 'Walpole', 'Wellesley', 'West Bridgewater', 'Westwood', 'Weymouth', 'Whitman', 'Wrentham']:
            local_housing_court = "Metro South Housing Court - Brockton Session"
        elif address.county == "Norfolk County" and not address.city in ["Newton","Brookline"]:
            local_housing_court = "Metro South Housing Court - Canton Session"
        elif address.city in ['Amesbury', 'Andover', 'Boxford', 'Georgetown', 'Groveland', 'Haverhill', 'Lawrence', 'Merrimac', 'Methuen', 'Newbury', 'Newburyport', 'North Andover', 'Rowley', 'Salisbury', 'West Newbury']:
            local_housing_court =  "Northeast Housing Court - Lawrence Session"
        elif address.city in ['Acton', 'Ashby', 'Ayer', 'Billerica', 'Boxborough', 'Carlisle', 'Chelmsford', 'Devens', 'Dracut', 'Dunstable', 'Groton', 'Littleton', 'Lowell', 'Maynard', 'Pepperell', 'Shirley', 'Stow', 'Tewksbury', 'Townsend', 'Tyngsborough', 'Westford']:
            local_housing_court = "Northeast Housing Court - Lowell Session"
        elif address.city in ['Lynn', 'Nahant', 'Saugus']:
            local_housing_court = "Northeast Housing Court - Lynn Session"
        elif address.city in ['Beverly', 'Danvers', 'Essex', 'Gloucester', 'Hamilton', 'Ipswich', 'Lynnfield', 'Manchester-by-The-Sea', 'Marblehead', 'Middleton', 'Peabody', 'Rockport', 'Salem', 'Swampscott', 'Topsfield', 'Wenham']:
            local_housing_court = "Northeast Housing Court - Salem Session"
        elif address.city in ['Bedford', 'Burlington', 'Concord', 'Everett','Lexington', 'Lincoln', 'Malden', 'Melrose', 'North Reading', 'Reading', 'Stoneham', 'Wakefield', 'Waltham', 'Watertown', 'Weston', 'Wilmington', 'Winchester', 'Woburn']:
            local_housing_court = "Northeast Housing Court - Woburn Session"
        elif address.city in ['Freetown', 'Westport', 'Fall River', 'Somerset','Swansea']:
            local_housing_court = "Southeast Housing Court - Fall River Session"
        elif address.city in ['Acushnet', 'Dartmouth', 'Fairhaven', 'Freetown', 'New Bedford','Westport']:
            local_housing_court = "Southeast Housing Court - New Bedford Session"
        elif address.city in ['Aquinnah', 'Barnstable', 'Bourne', 'Brewster', 'Carver', 'Chatham', 'Chilmark', 'Dennis', 'Duxbury', 'Edgartown', 'Falmouth', 'Halifax', 'Hanson', 'Harwich', 'Kingston', 'Lakeville', 'Marion', 'Marshfield', 'Mashpee', 'Mattapoisett', 'Middleborough', 'Nantucket', 'Oak Bluffs', 'Pembroke', 'Plymouth', 'Plympton', 'Provincetown', 'Rochester', 'Sandwich', 'and Wareham.Beginning on August 6', 'the Plymouth session of the Southeast Housing Court will also serve Accord', 'Assinippi', 'Hanover', 'Hingham', 'Hull', 'Humarock', 'Norwell', 'Rockland', 'Scituate']:
            local_housing_court = "Southeast Housing Court - Plymouth Session"
        elif address.city in ['Attleboro', 'Berkley', 'Dighton', 'Easton', 'Mansfield', 'North Attleborough', 'Norton', 'Raynham', 'Rehoboth', 'Seekonk','Taunton']:
            local_housing_court = "Southeast Housing Court - Taunton Session"
        else:
            local_housing_court = ""
        return local_housing_court



if __name__ == '__main__':
    import pprint
    courts = get_courts_from_massgov_url('https://www.mass.gov/orgs/district-court/locations')
    pprint.pprint(courts)