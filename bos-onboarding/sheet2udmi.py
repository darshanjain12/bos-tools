#!/usr/bin/env python3

"""
  sheet2udmi.py

  [About]
  Convert an .xlsx file containing asset/topic data for multiple devices to 
  a UDMI site model folder containing subfolders for each device 
  included in the .xlsx file, generating a metadata.json file for each device.

  The output folder will have the structure:
  - dvices:
    - [Device name indicated in file]
      - metadata.json

  [Usage]
  python3 sheet2udmi.py [options] <sheet.xlsx>
"""

__author__ = "Francesco Anselmo, Edzel Monteverde"
__copyright__ = "Copyright 2021"
__credits__ = ["Francesco Anselmo"]
__license__ = "MIT"
__version__ = "0.1"
__maintainer__ = "Francesco Anselmo"
__email__ = "francesco.anselmo@gmail.com"
__status__ = "Dev"

import os
import sys
import json
import shutil
import pprint
import argparse
from pyfiglet import *
import pandas as pd
from pandas import DataFrame, ExcelFile, ExcelWriter, Series, read_excel


class SiteModel:

  class AssetColumns:
    
    # Used to create subfolders.
    DEVICE_OR_VIRTUAL = "dbo.devices_or_virtual_devices"
    NAME = "entity_instance_name"

    # Used to create the "system" and "physical tag" sections.
    VERSION = "udmi.version"
    #DEVICE_VERSION = "udmi.device_version"
    TIMESTAMP = "udmi.timestamp"
    LOCATION_SITE = "udmi.system.location.site"
    LOCATION_SECTION = "udmi.system.location.section"
    # These below fields are not required so we have commented
    #LOCATION_POSITION_X = "udmi.system.location.position.x"
    #LOCATION_POSITION_Y = "udmi.system.location.position.y"
    #LOCATION_POSITION_Z = "udmi.system.location.position.z"
    PHYSICAL_TAG_GUID = "udmi.physical_tag.asset.guid"
    PHYSICAL_TAG_SITE = "udmi.physical_tag.asset.site"
    PHYSICAL_TAG_NAME = "udmi.physical_tag.asset.name"

    # Used to create the "pointset" section.
    POINTSET_POINTS = "udmi.pointset.points"

    # Used to create the "cloud" section.
    CLOUD_AUTH_TYPE = "udmi.cloud.auth_type"
    # Column is added to check condition in cloud section
    CLOUD_CONNECTION_TYPE = "udmi.cloud.connection"

    # Used to create the "gateway" section.
    GATEWAY_ID = "udmi.gateway.gateway_id"
    GATEWAY_PROXY_ID = "udmi.gateway.proxy_ids"

    # Used to create the "Local Bacnet Address" section.
    BACNET_ADDR = "udmi.bacnet_addr"


 
  class PayloadTypeColumns:

    # Used to create the "pointset" section.
    POINTS_TYPE = "points_type"
    POINTSET_POINTS = "udmi.pointset.points"
    POINTSET_UNITS = "udmi.pointset.units"
    #Column added for ref - key attribute in poinset.point section
    POINTSET_REF="udmi.pointset.ref"
    # Added for Missing logic
    POINTSET_FLAG ="dbo.flag"

  """
    Returns the contents of the excel sheet as a dictionary of format:

    Cleans up the dataframe by:
    - Replacing "nan" values with empty space.
    - Removing trailing whitespace.

    Assumes that the dataframe has headers.

    Format of output dictionary will look like this:
    [
      { column1: value, ... columnN: value }  # Row 1
      ...
      { column1: value, ... columnN: value }  # Row N
    ]
  """
  def _get_sheet_dict(self, excel_file, sheet_name):
    dataframe = pd.read_excel(excel_file, sheet_name, dtype=str)

    # Replace "nan" values with empty whitespace.
    dataframe = dataframe.fillna("")

    # Remove all trailing whitespace.
    for column in dataframe.columns:
      dataframe[column] = dataframe[column].apply(
        lambda dataframe_column: dataframe_column.strip()
      )

    return dataframe.to_dict('records')

  def __init__(self, site_model_path):
    excel_file = ExcelFile(site_model_path)
    self.assets = self._get_sheet_dict(excel_file, "assets")
    self.payload_types = self._get_sheet_dict(excel_file, "device_entities")


class UDMISiteModelGenerator:

  OUTPUT_PATH = "devices/"
  OUTPUT_PATH_TEMPLATE = "devices/{0}/"
  OUTPUT_FILE_TEMPLATE = "devices/{0}/metadata.json"

  def __init__(self, site_model, site_path):
    self._site_model = site_model
    self._asset_columns = site_model.AssetColumns
    self._payload_type_columns = site_model.PayloadTypeColumns
    self.SITE_PATH = site_path
    if site_path != '':
      self.OUTPUT_PATH = os.path.join(site_path, self.OUTPUT_PATH)
      self.OUTPUT_PATH_TEMPLATE = os.path.join(site_path, self.OUTPUT_PATH_TEMPLATE)
      self.OUTPUT_FILE_TEMPLATE = os.path.join(site_path, self.OUTPUT_FILE_TEMPLATE)

  def _cleanup_output(self):
    #logic added for cleanup of the files in respective folder to check
    if os.path.exists(self.OUTPUT_PATH):
      p=os.path.join(os.getcwd(),self.SITE_PATH)
      
      shutil.rmtree(self.OUTPUT_PATH)

  def _get_version_timestamp_section(self, device):
    # Device_version - key attribute is added as per requirement
    return {
      "version": device[self._asset_columns.VERSION],
      "timestamp": device[self._asset_columns.TIMESTAMP],
      
    }

  def _get_system_section(self, device):
    return {
      "system": {
        "location": {
          "site": device[self._asset_columns.LOCATION_SITE],
          "section": device[self._asset_columns.LOCATION_SECTION],
          #"position": {
            #"x": device[self._asset_columns.LOCATION_POSITION_X],
            #"y": device[self._asset_columns.LOCATION_POSITION_Y],
            #"z": device[self._asset_columns.LOCATION_POSITION_Z]
         # }
        },
        "physical_tag": {
          "asset": {
            "guid": "uuid://" + device[self._asset_columns.PHYSICAL_TAG_GUID],
            "site": device[self._asset_columns.PHYSICAL_TAG_SITE],
            "name": device[self._asset_columns.PHYSICAL_TAG_NAME]
          }
        }
      }
    }
  # Function added as per Gateway condition
  def _get_gateway_section(self, device):
    abc=device[self._asset_columns.GATEWAY_PROXY_ID].split(',')
    #abc='","'.join(abc)
    #print(abc)
    if device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='GATEWAY':
      
      return {
        "gateway": {
            #"gateway_id": device[self._asset_columns.GATEWAY_ID]
            #"proxy_ids": [device[self._asset_columns.GATEWAY_PROXY_ID]]
            "proxy_ids": abc
        
           }
       }
    elif device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='PROXIED':
      return {
        "gateway": {
            "gateway_id": device[self._asset_columns.GATEWAY_ID]
            #"proxy_ids": [device[self._asset_columns.GATEWAY_PROXY_ID]]
        
           }
       }
    else:
      return {}
    
  

  def split_string(self,ref):
    #Splitting alpha charachter and numbers
    alphabets = ""
    numbers = ""
    for char in ref:
      if char.isalpha():
        alphabets += char
      elif char.isdigit():
        numbers += char
    return alphabets, numbers
  
  def _get_pointset_section(self, device):
    points = {}

    for point in self._site_model.payload_types:
      
      payload_points_type = point[self._payload_type_columns.POINTS_TYPE]
      payload_point_name = point[self._payload_type_columns.POINTSET_POINTS]
      payload_pointset_units = point[self._payload_type_columns.POINTSET_UNITS]
      # New column added for change in logic for newly added key attribute ref
      payload_pointset_ref = point[self._payload_type_columns.POINTSET_REF]
      # New column added for pointset points condition
      payload_pointset_flag = point[self._payload_type_columns.POINTSET_FLAG]

      a,b=self.split_string(payload_pointset_ref)
      trans_str=a+':'+b+'.present_value'

      #pointset points condition
      if device[self._asset_columns.POINTSET_POINTS] == payload_points_type:
        if payload_pointset_flag == 'N':
          points.update({
            payload_point_name: {
            "ref": trans_str,
            "units": payload_pointset_units
            }
          })

    return {
      "pointset": {
        "points": points
      }
    }
  
  # Logic added for Proxied connection type
  def _get_cloud_section(self, device):
    if device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='PROXIED':
      return {
        "cloud": {
          #"auth_type": device[self._asset_columns.CLOUD_AUTH_TYPE],
          "connection_type": device[self._asset_columns.CLOUD_CONNECTION_TYPE],
          "config":{
            "static_file":"config.json"
          }
        }
      }
    else:
      return {
        "cloud": {
          "auth_type": device[self._asset_columns.CLOUD_AUTH_TYPE],
          "connection_type": device[self._asset_columns.CLOUD_CONNECTION_TYPE],
          "config":{
            "static_file":"config.json"
          }
        }
      }

  # Logic added for when connection type is Device
  def _get_bacnet_addr(self,device):
    return {
      "localnet":{
        "families":{
          "bacnet":{
          "addr": device[self._asset_columns.BACNET_ADDR]
          }
        }
      }
    }

  def _save_to_json(self, content, path):
    with open(path, "w") as output:
      json.dump(content, output, indent=2, separators=(",", ":"))

    '''with open(path, "r") as fout:
      st=fout.read()
      st=st.replace('\\',"")

    with open(path, 'w') as fout1:
      fout1.write(st)'''




  def generate(self):
    self._cleanup_output()

    if not os.path.exists(self.OUTPUT_PATH): 
      os.makedirs(self.SITE_PATH, exist_ok=True )
      os.makedirs(self.OUTPUT_PATH ,exist_ok=True)

    for device in self._site_model.assets:
      
      if device[self._asset_columns.DEVICE_OR_VIRTUAL] == "Device":
        
        metadata = {}
        name = device[self._asset_columns.NAME]
        
        metadata.update(self._get_version_timestamp_section(device))
        metadata.update(self._get_system_section(device))
        metadata.update(self._get_pointset_section(device))
        metadata.update(self._get_cloud_section(device))
        metadata.update(self._get_gateway_section(device))

        if device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='PROXIED':
          metadata.update(self._get_bacnet_addr(device))

        if device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='DEVICE':
          metadata.update(self._get_bacnet_addr(device))

        os.makedirs(self.OUTPUT_PATH_TEMPLATE.format(name), exist_ok=True)
        self._save_to_json(metadata, self.OUTPUT_FILE_TEMPLATE.format(name))


def show_title():
  """Show the program title
  """
  f1 = Figlet(font='standard')
  print(f1.renderText('sheet2UDMI'))

def main():
      
  show_title()

  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group()
  group.add_argument("-v", "--verbose", action="store_true", default=False, help="increase the verbosity level")
  parser.add_argument("-d", "--debug", action="store_true", default=False, help="print debug information")
  parser.add_argument("-i","--input", default="", help="input Excel sheet file name")
  parser.add_argument("-o","--output", default="udmi_site_model", help="output folder name")

  args = parser.parse_args()

  if args.verbose:
    print("program arguments:")
    print(args)

  if os.path.exists(args.input):
    print("Started UDMI site model generation ...")
    site_model = SiteModel(args.input)
    print("Creating UDMI site model ...")
    generator = UDMISiteModelGenerator(site_model, args.output)
    generator.generate()
    print("Done.")

  else:
    print("Please run ""%s -h"" to see the program options" % sys.argv[0])
  
  print()
    
if __name__ == "__main__":
  main()
