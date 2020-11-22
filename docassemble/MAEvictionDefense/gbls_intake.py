from docassemble.base.util import Individual, Address
from docassemble.base.config import daconfig
from docassemble.base.util import task_performed,task_not_yet_performed,mark_task_as_performed,log
import requests
import json
from nameparser import HumanName


__all__ = ['in_service_area','ls_submit_online_intake','nameparts','address_to_json','address_to_dict']

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

def in_service_area(tenant):
    tenant.address.geolocate()
    if hasattr(tenant.address, 'norm_long'):
      address_to_compare = tenant.address.norm_long
    else:
      address_to_compare = tenant.address
    return address_to_compare.city.lower() in [
            "acton","harvard",	"randolph",
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