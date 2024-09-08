"""
  A collection of classes to represent the room section of the YAML.

  They are responsible for filling up the section with data.
  
  Holds logic for reading input files to retrieve the data for a room.
"""

import re
from building_blocks.room import Room, DBORoom
import sys

  
class DBORoomSection:

  def __init__(self, files):
    self._rooms = {}
    self._site_model_sheets = files.site_model_sheets
    self._site_model_columns = files.SiteModelColumns
    self._populate_rooms()

  def _create_room(self, row,b):
    #Handling multiple values coming from dbo.contains

    contains_value=[]
    conn_contains = row[self._site_model_columns.CONNECTIONS_CONTAINS].split(',')
    for j in conn_contains:
      j=j.strip()
      # Handling exception in values written in dbo.contains does not have value 
      if j in b :
        
        contains_value.append(b[j])

      elif len(j)==0:
        contains_value=j
        
      else:
        print('Value issue : Column value {0} in sheet db.connection.contains does not match with dbo.entity.name'.format(j))
        print('Please check value in db.connections.contains field')
        sys.exit()
                
    
    contains_val=','.join(contains_value)
    
    if row[self._site_model_columns.SECTION] == "Rooms":
      room_name = row[self._site_model_columns.ENTITY_NAME]
      room_id = row[self._site_model_columns.ID]
      room_type = row[self._site_model_columns.TYPE]
      #room_contains = row[self._site_model_columns.CONNECTIONS_CONTAINS]
      room_contains = contains_val
      room = DBORoom(room_name, room_id, room_type)
      room.populate_connections(room_contains)
      return room

  def _populate_rooms(self):
    #Creating seperate dictionary contains entity_name  as key and dbo.id as value
    b={}
    for i in self._site_model_sheets.LOCATIONS:
      b[i['dbo.entity_name']]=i['dbo.id']

    for row in self._site_model_sheets.LOCATIONS:
      room = self._create_room(row,b)
      if room is not None:
        self._rooms.update(room.to_dictionary())

  def to_dictionary(self):
    return self._rooms
