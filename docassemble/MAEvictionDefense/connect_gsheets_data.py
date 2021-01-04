import gspread
import json
from docassemble.base.util import get_config
from oauth2client.service_account import ServiceAccountCredentials
credential_info = json.loads(get_config('google').get('service account credentials'), strict=False)
scope = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']
import usaddress
import nameparser

__all__ = ['read_sheet','map_address','map_name','map_attorney_info']

def read_sheet(sheet_name, worksheet_title):
  creds = ServiceAccountCredentials.from_json_keyfile_dict(credential_info, scope)
  client = gspread.authorize(creds)
  sheet = client.open(sheet_name).worksheet(worksheet_title)
  return sheet.get_all_records()

def map_attorney_info(attorney_row, attorney_object):
    map_name(attorney_row.get('Attorney Name'), attorney_object.name)
    attorney_object.office = attorney_row.get('Office Name','')
    attorney_object.email = attorney_row.get('Email Address','')
    map_address(attorney_row.get('Street Address') + ', ' + attorney_row.get('City State and Zip'), attorney_object.address)
    attorney_object.bbo = attorney_row.get('BBO Number','')
    attorney_object.phone_number = attorney_row.get('Phone Number','')
    attorney_object.fax_number = attorney_row.get('Fax Number','') 

def map_address(oneline_address, address_object):
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
    address_parts = usaddress.tag(oneline_address, tag_mapping=tag_mapping) 
    
    if address_parts[1].lower() == 'street address':
      address_object.address = address_parts[0].get('address')
      if address_parts[0].get('unit'):
          address_object.unit = address_parts[0].get('unit')
      address_object.city = address_parts[0].get('city')
      address_object.state = address_parts[0].get('state')
      address_object.zip = address_parts[0].get('zip')
    else:
      address_object.address = oneline_address

  except:
    address_object.address = oneline_address

  if not hasattr(address_object,'address'):
    address_object.address = ''
  if not hasattr(address_object, 'city'):
    address_object.city = ''
  if not hasattr(address_object, 'state'):
    address_object.state = ''
  if not hasattr(address_object, 'zip'):
    address_object.zip = ''
    
def map_name(oneline_name, name_object):
  name = nameparser.HumanName(str(oneline_name))
  name_object.first = name['first']
  if name['middle']:
    name_object.middle = name['middle']
  name_object.last = name['last']
  if name['suffix']:
    name_object.suffix = name['suffix']