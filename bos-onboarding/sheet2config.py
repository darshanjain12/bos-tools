#!/usr/bin/env python3


# New file code changes ---
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
    DEVICE_VERSION = "udmi.device_version"
    TIMESTAMP = "udmi.timestamp"
    LOCATION_SITE = "udmi.system.location.site"
    LOCATION_SECTION = "udmi.system.location.section"
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
    POINTSET_REF="udmi.pointset.ref"
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
  OUTPUT_PATH_TEMPLATE = "devices/{0}/config/"
  OUTPUT_FILE_TEMPLATE = "devices/{0}/config/config.json"

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
    if os.path.exists(self.OUTPUT_PATH):
      p=os.path.join(os.getcwd(),self.SITE_PATH)
      #print(p)
      #print(self.SITE_PATH)
      #print(self.OUTPUT_PATH)
      shutil.rmtree(p)

  def _get_version_timestamp_section(self, device):
    return {
      "timestamp": device[self._asset_columns.TIMESTAMP],
      "version": device[self._asset_columns.VERSION]
    }

  def _get_system_section(self, device):
    return {
      "system": {
        "min_loglevel": 300,
        "metrics_rate_sec": 10,
        "operation": { }
          #"position": {
            #"x": device[self._asset_columns.LOCATION_POSITION_X],
            #"y": device[self._asset_columns.LOCATION_POSITION_Y],
            #"z": device[self._asset_columns.LOCATION_POSITION_Z]
         # }
        }   
    }

  def _get_gateway_section(self, device):
      
      abc=device[self._asset_columns.GATEWAY_PROXY_ID].split(',')
  
      #abc='","'.join(abc)
      #abc='"'+abc+'"'
      
      return {
        "gateway": {
            #"gateway_id": device[self._asset_columns.GATEWAY_ID]
            "proxy_ids": abc
           }
       }
  
  def split_string(self,ref):
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
      payload_pointset_ref = point[self._payload_type_columns.POINTSET_REF]
      payload_pointset_flag = point[self._payload_type_columns.POINTSET_FLAG]
      a,b=self.split_string(payload_pointset_ref)
      trans_str=a+':'+b+'.present_value'

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
        "points": points,
        "sample_rate_sec": 300
      }
    }
  
  
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
    cnt=json.dumps(content, indent=2, separators=(",", ":"), ensure_ascii=True)
    #print(cnt)

    with open(path, "w" , encoding='utf-8') as output:
      output.write(cnt)
    #new code
    '''with open(path, "r") as fout:
      st=fout.read()
      st=st.replace('\\',"")

    with open(path, 'w') as fout1:
      fout1.write(st)'''

      

  def generate(self):
    pass
    #self._cleanup_output()

    '''if not os.path.exists(self.OUTPUT_PATH): 
      os.makedirs(self.SITE_PATH , exist_ok=True)
      os.makedirs(self.OUTPUT_PATH , exist_ok=True)'''

    for device in self._site_model.assets:
      
      if device[self._asset_columns.DEVICE_OR_VIRTUAL] == "Device":
        metadata = {}
        name = device[self._asset_columns.NAME]
        #print(device)
        metadata.update(self._get_version_timestamp_section(device))
        metadata.update(self._get_system_section(device))
        metadata.update(self._get_pointset_section(device))
        if device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='GATEWAY':
            metadata.update(self._get_gateway_section(device))

        if device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='PROXIED':
          metadata.update(self._get_bacnet_addr(device))

        #if device[self._asset_columns.CLOUD_CONNECTION_TYPE]=='DEVICE':
          #metadata.update(self._get_bacnet_addr(device))

        


        #path=os.path.join(os.getcwd(),self.OUTPUT_PATH_TEMPLATE.format(name))
        #path=path.replace('','\\')
        os.makedirs(self.OUTPUT_PATH_TEMPLATE.format(name),exist_ok=True)
        
        self._save_to_json(metadata, self.OUTPUT_FILE_TEMPLATE.format(name))


def show_title():
  """Show the program title
  """
  f1 = Figlet(font='standard')
  print(f1.renderText('sheet2CONFIG'))

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
