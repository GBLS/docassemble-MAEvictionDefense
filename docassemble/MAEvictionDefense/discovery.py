from docassemble.base.core import DAObject, DAList, DADict
from docassemble.base.util import path_and_mimetype
import csv, sys

class DiscoveryRequest(DAObject):
  """Discovery items should have a checked property."""
  def __str__(self):
      return self.description
  def __nonzero__(self):
    return self.checked

class DocumentRequest(DiscoveryRequest):
  pass

class Interrogatory(DiscoveryRequest):
  pass

class Admission(DiscoveryRequest):
  pass

class DiscoveryList(DAList):
  """Represents a list of Discovery Requests in a case.  The default object
  type for items in the list is DiscoveryRequest."""
  def init(self, *pargs, **kwargs):
    self.object_type = DiscoveryRequest
    return super(DiscoveryList, self).init(*pargs, **kwargs) 
#  def 
#  def checked_values(self):
#    return DiscoveryList(elements=[key for key,value in self.iteritems() if value.checked is True]})
#  def checked_values(self):


class DiscoveryDict(DADict):
  def init(self, *pargs, **kwargs):
    self.elements = dict()
    self.object_type = DiscoveryRequest
    if 'elements' in kwargs:
      self.elements.update(kwargs['elements'])
      self.gathered = True
      del kwargs['elements']
    return super(DiscoveryDict, self).init(*pargs, **kwargs) 
  def checked_values(self):
    return DAList(elements=[key for key,value in self.iteritems() if value.checked is True])
  def unchecked_values(self):
    return DAList(elements=[key for key,value in self.iteritems() if value.checked is False])
  def matches_category(self, category):
    return DAList(elements=[key for key,value in self.iteritems() if value.category == category])
  def any_in_category(self, category):
      for key in self.elements:
        if self.elements[key].checked and self.elements[key].category == category:
          return True
      return False
  def count_checked(self):
    i = 0
    for key in self.elements:
      if self.elements[key].checked: 
        i += 1
    return i
 

def load_from_csv(relative_path):
  """ Return a list containing a dictionary for each line of the CSV file at relative_path. Uses Docassemble path_and_mimetype to locate the path."""
  (path,mimetype) = path_and_mimetype(relative_path)
  reader = csv.DictReader(open(path,'r'))
  myList = []
  for line in reader:
    myList.append(line)
  del reader
  return myList