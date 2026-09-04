from docassemble.base.util import Individual, Address
from docassemble.base.config import daconfig
from docassemble.base.util import task_performed,task_not_yet_performed,mark_task_as_performed,log
import requests
import json
from nameparser import HumanName


__all__ = ['in_service_area','city_in_service_area','GBLS_SERVICE_AREA',
           'GBLS_ELDER_ONLY_SERVICE_AREA','ls_submit_online_intake','nameparts',
           'address_to_json','address_to_dict']

def nameparts(name):
    return HumanName(name)


def address_to_dict(address):
    addr = {
        "zip": address.zip,
        "address1": address.address,
        "address2": address.unit,
        "city":address.city,
        "state": address.state
    }
    return {key:value for (key,value) in addr.items() if not value is None}
  
def address_to_json(address): 
    """Returns a JSON string appropriate for Legal Server, given a Docassemble Address object"""
    addr = {
        "zip": address.zip,
        "address1": address.address,
        "address2": address.unit,
        "city":address.city,
        "state": address.state
    }
    addr = {key:value for (key,value) in addr.items() if not value is None}
    return json.dumps(addr)

# Communities GBLS serves regardless of the client's age.
GBLS_SERVICE_AREA = [
    "harvard",	"randolph",
    "arlington", "hingham", "reading",
    "bedford",	"holbrook",	"revere",
    "belmont",	"hull",	"scituate",
    "boston",	"lexington",	"somerville",
    "boxborough",	"lincoln",	"stoneham",
    "braintree",	"littleton",	"stow",
    "brookline",	"malden",	"wakefield",
    "burlington",	"maynard",	"waltham",
    "cambridge",	"medford",	"watertown",
    "canton",	"melrose",	"weymouth",
    "carlisle",	"milton",	"wilmington",
    "chelsea",	"newton",	"winchester",
    "cohasset",	"north reading",	"winthrop",
    "concord",	"norwell",	"woburn",
    "everett",	"quincy",'allston','back bay',
    'beacon hill','brighton','charlestown',
    'chinatown','dorchester','east boston',
    'fenway','kenmore','hyde park','jamaica plain',
    'mattapan','north end','roslindale','roxbury',
    'south boston','south end','west end','west roxbury'
]

# Communities GBLS serves only for elders. Non-elders here should be referred
# elsewhere rather than sent into GBLS intake.
GBLS_ELDER_ONLY_SERVICE_AREA = [
    "acton",
]


def city_in_service_area(city, is_elder=False):
    """Return whether GBLS covers this city, widening the area for elders."""
    if not city:
        return False
    normalized_city = city.strip().lower()
    if normalized_city in GBLS_SERVICE_AREA:
        return True
    return bool(is_elder) and normalized_city in GBLS_ELDER_ONLY_SERVICE_AREA


def in_service_area(tenant, is_elder=False):
    """Return whether GBLS can take this tenant, based on where they live.

    Some communities are within the service area only for elders, so pass
    is_elder for a household with someone over 60.
    """
    tenant.address.geolocate()
    if hasattr(tenant.address, 'norm_long'):
      address_to_compare = tenant.address.norm_long
    else:
      address_to_compare = tenant.address
    return city_in_service_area(address_to_compare.city, is_elder=is_elder)

def ls_submit_online_intake(params, task=None):
    """Looks in config for legal server key, subkeys servername, username, and password
    then calls _ls_submit_online_intake with those values"""
    servername = daconfig.get('legal server',{}).get('servername')
    username = daconfig.get('legal server',{}).get('username')
    password = daconfig.get('legal server',{}).get('password')
    return _ls_submit_online_intake(servername, username, password, params,task=task)

def _ls_submit_online_intake(servername, username, password, params, task=None):
    # remove any empty parameters
    params = {key:value for (key,value) in params.items() if not value is None}
    headers = {
      'Accept': "application/json"
    }
    try:
        r = requests.get(servername + "/matter/api/online_intake_import",auth=(username,password),params=params, headers=headers)
    except requests.exceptions.RequestException as e:
        return e
    if not task is None:
        mark_task_as_performed(task)
    log(r.request.url)
    return r