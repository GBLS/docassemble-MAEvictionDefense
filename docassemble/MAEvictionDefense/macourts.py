from docassemble.base.core import DAObject, DAList, DADict
from docassemble.base.util import path_and_mimetype, Address 
from docassemble.base.legal import Court
import io, json, sys, requests, bs4
# from pygeocoder import Geocoder

def get_courts_from_massgov_url(url):
    """Load specified court directory page on Mass.gov and return a list of dictionaries
    Properties include name, phone, fax, address, description (usually includes cities or county served), latitude, longitude
    """
    page = requests.get(url)
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    jstring = soup.find_all( attrs={"data-drupal-selector":"drupal-settings-json"} )[0].text # this is the element that has the JSON data as of 6/19/2018

    jdata = json.loads(jstring)

    markers = jdata['locations']['googleMap']['markers']

    courts = []


    for marker in markers:
        name = marker['infoWindow']['name']
        for item in jdata['locations']['imagePromos']['items']:
            description = ''
            if item['title']['text'] == name:
                description = item['description']['richText']['rteElements'][0]['data']['rawHtml']['content']['#context']['value']
                break

        address = Address()        
        address.address = marker['infoWindow']['address']
        address.geolocate()
        address.normalize()

        courts.append({
            'name': marker['infoWindow']['name'],
            'phone': marker['infoWindow']['phone'],
            'fax': marker['infoWindow']['fax'],
            'address': {
                'address': address.address,
                'city': address.city,
                'state': address.state,
                'zip': address.zip,
                'county': address.county
            },
            'description': description,
            'lat': marker['position']['lat'],
            'lng': marker['position']['lng']
        })

    return courts

def save_courts_to_file():
    ''' Writes district_court.json and housing_courts.json to current directory'''
    district_courts = get_courts_from_massgov_url('https://www.mass.gov/orgs/district-court/locations')
    with io.open('district_courts.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(district_courts, ensure_ascii=False))
    housing_courts = get_courts_from_massgov_url('https://www.mass.gov/orgs/housing-court/locations')
    with io.open('housing_courts.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(housing_courts, ensure_ascii=False))

class MACourt(Court):
    def init(self, *pargs, **kwargs):
        self.address = Address()
        if 'jurisdiction' not in kwargs:
            self.jurisdiction = list()
        return super(Court, self).init(*pargs, **kwargs)
    pass

def load_courts_from_file(json_path):
    new_courts = []

    (path,mimetype) = path_and_mimetype(json_path)

    with open(path) as courts_json:  
        courts = json.load(courts_json)

    for item in courts:
        # translate the JSON data into a DA Address types
        address = Address()
        address.address = item['address']['address']
        address.city = item['address']['city']
        address.state = item['address']['state']
        address.zip = item['address']['zip']
        address.county = item['address']['county']

        court = MACourt()
        court.name = item['name']
        court.phone = item['phone']
        court.fax = item['fax']
        court.address = address
        court.lat = item['lat']
        court.lng = item['lng']

        new_courts.append(court)
    
    return new_courts

def ma_courts():
    return load_courts_from_file('data/static/housing_courts.json') +  load_courts_from_file('data/static/district_courts.json')

def ma_courts_list():
    return [
        'Central Housing Court',
        'Eastern Housing Court',
        'Metro South Housing Court',
        'Northeast Housing Court',
        'Southeast Housing Court',
        'Western Housing Court',
        'Barnstable District Court',
        'Brighton Division Boston Municipal Court',
        'Brookline District Court',
        'Cambridge District Court',
        'Central Division Boston Municipal Court',
        'Charlestown Division Boston Municipal Court',
        'Chelsea District Court',
        'Concord District Court',
        'Dedham District Court',
        'Dorchester Division Boston Municipal Court',
        'East Boston Division Boston Municipal Court',
        'Falmouth District Court',
        'Framingham District Court',
        'Hingham District Court',
        'Lowell District Court',
        'Malden District Court',
        'Marlborough District Court',
        'Middlesex Superior Court',
        'Natick District Court',
        'Newton District Court',
        'Norfolk Superior Court',
        'Northern Berkshire District Court',
        'Orleans District Court',
        'Quincy District Court',
        'Roxbury Division Boston Municipal Court',
        'Somerville District Court',
        'South Boston Division Boston Municipal Court',
        'Stoughton District Court',
        'Suffolk Superior Court',
        'Waltham District Court',
        'West Roxbury Division Boston Municipal Court',
        'Woburn District Court',
        'Worcester District Court',
    ]