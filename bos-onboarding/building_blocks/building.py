"""
  Contains classes which are used to store data for a building.

  Ready to use, or extend subclasses as required to fill cases where more 
  information needs to be stored.

  Call to_dictionary() to retrieve all the data.
"""

import abc

class Building:
  
  def __init__(self, building_name, building_id):
    self._name = building_name
    """
    original code change for Building_Id as per requirement. Orginal code is commented. 
    """
    #self._id = "FACILITIES/{0}".format(building_id)
    self._id=building_id
  
  """
    Call this to retrieve a dictionary representing this dataset.
  """
  def to_dictionary(self):
    # Code key attribute is newly added.
    return {
      self._id: {
        "type": "FACILITIES/BUILDING",
        "code": self._name
      }
    }
