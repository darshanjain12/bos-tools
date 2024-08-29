"""
  Contains classes which are used to store data for a device.

  Ready to use, or extend subclasses as required to fill cases where more 
  information needs to be stored.

  Call to_dictionary() to retrieve all the data.
"""

import abc

class Device:
  
  class Connection:

    def __init__(self, name, value):
      self._name = name
      
      self._value = value

    def to_dictionary(self):
      return {self._name: self._value}

  class Translation:

    def __init__(self, name, value):
      self._name = name
      self._value = value
      
    def to_dictionary(self):
      return {self._name: self._value}
    
  class Translation_m:

    def __init__(self, value):
      
      self._value = value
      
    def to_dictionary(self):
      return self._value

  class Link:

    def __init__(self, name, value):
      self._name = name
      self._value = value
      
    def to_dictionary(self):
      return {self._name: self._value}

  def __init__(self, device_name, device_type, device_id,device_location,cloud_device_id):
    self._name = device_name
    self._type = device_type
    self._id = device_id
    self._location = device_location
    self._cloud_device_id = cloud_device_id
    self._connections = {}
    self._translation = {}
    self._links = {}
  
  def populate_connections(self, name, value):
    #new code
    
    ids=name.split(',')
    for i in ids:
      self._connections.update(self.Connection(i, value).to_dictionary())

  def populate_translations(self, name, value):
    self._translation.update(self.Translation(name, value).to_dictionary())
  #new code
  def populate_translations_m(self, value):
    self._translation.update(self.Translation_m( value).to_dictionary())

  def populate_links(self, name, value):
    self._links.update(self.Link(name, value).to_dictionary())

  """
    Call this to retrieve a dictionary representing this data.

    If connections are empty, don't add the connection value to dictionary.

    If translations are empty, don't add the translation value to dictionary.

    If links are empty, don't add the link value to dictionary.
  """
  def to_dictionary(self):
    return_dictionary = {
      self._id: {
        "type": self._type,
        "cloud_device_id": self._cloud_device_id
        
      }
    }

    

    if len(self._translation) > 0:
      return_dictionary[self._id].update({
        "translation": self._translation
      })

    if len(self._connections) > 0:
      return_dictionary[self._id].update({
        "connections": self._connections
      })

    if len(self._links) > 0:
      return_dictionary[self._id].update({
        "links": self._links
      })

    if len(self._name)>0:
      return_dictionary[self._id].update({
        "code": self._name
      })

    return return_dictionary 
