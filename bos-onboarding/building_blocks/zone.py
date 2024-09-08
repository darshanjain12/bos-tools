"""
  Contains classes which are used to store data for a zone.

  Ready to use, or extend subclasses as required to fill cases where more 
  information needs to be stored.

  Call to_dictionary() to retrieve all the data.
"""

import abc

class Zone:
  
  class ZoneLink:

    def __init__(self, name, points):
      self._name = name
      self._points = points

    def to_dictionary(self):
      return {self._name: self._points}

  class ZoneConnection:

    def __init__(self, name, value):
      self._name = name
      self._value = value

    def to_dictionary(self):
      return {self._name: self._value}
  
  def __init__(self, zone_name, zone_type, zone_id):
    self._name = zone_name
    self._type = zone_type
    self._id = zone_id
    self._links = {}
    self._connections = {}

  def populate_links(self, name, points):
    self._links.update(self.ZoneLink(name, points).to_dictionary())

  def populate_connections(self, name, value):
    #Logic is added to handle multiple values passed when function called in zone_section.py
    ids=name.split(',')
    for i in ids:
      self._connections.update(self.ZoneConnection(i, value).to_dictionary())

  """
    Call this to retrieve a dictionary representing this data.

    If links are empty, don't add the link value to dictionary.
  """
  def to_dictionary(self):
    #Logic added for new key attribute code
    return_dictionary = {
      self._id: {
        "type": self._type
      }
    }

    if len(self._links) > 0:
      return_dictionary[self._id].update({
        "links": self._links
      })

    if len(self._connections) > 0:
      return_dictionary[self._id].update({
        "connections": self._connections
      })

    if len(self._name) > 0:
      #Logic added for new key attribute code
      return_dictionary[self._id].update({
        "code": self._name
      })

    return return_dictionary
