#!/usr/bin/env python3

#
# It checks mapping files, but going only through systems
# which have TPR in folders preloaded. That is required for
# debugging mappings code.
#

import os
import sys
import numpy as np
import json
import matplotlib.pyplot as plt
import MDAnalysis as mda
import urllib.request
import yaml

import urllib.request
from urllib.error import URLError,HTTPError,ContentTooShortError

# From time monitoring
from tqdm import tqdm

import socket

sys.path.insert(1, '../BuildDatabank/')
from databankLibrary import download_link, lipids_dict, databank

path = '../../Data/Simulations/'

db_data = databank(path)
systems = db_data.get_systems()

for system in systems:
#    trj_name = system['path'] + system['TRJ'][0][0]
    if 'TPR' not in system.keys():
        sys.stderr.write("Skipping "+system["SYSTEM"]+" because there is no TPR\n")
        continue
    tpr_name = os.path.join(path, system['path'], system['TPR'][0][0])
    if not os.path.exists(tpr_name):
        sys.stderr.write("Skipping "+system["SYSTEM"]+" because TPR is not downloaded\n")
        sys.stderr.write("==> "+tpr_name+"\n")
        continue
    print("Checking system "+system['path']+" ...")
    # opening Universe using TPR only
    tpars = mda.topology.TPRParser.TPRParser(tpr_name)
    tpl = tpars.parse()
    u = mda.Universe(tpl)
    for molecule in system['COMPOSITION']:
        errnum = 0
        m_file = system['COMPOSITION'][molecule]['MAPPING']
        # opening mapping-yaml
        mapping_dict = {}
        with open('./mapping_files/'+m_file, "r") as yaml_file:
            mapping_dict = yaml.load(yaml_file, Loader=yaml.FullLoader)
        # go over all records
        for mk in mapping_dict.keys():
                selection = 'resname ' + system['COMPOSITION'][molecule]['NAME'] + ' and name ' +  mapping_dict[mk]['ATOMNAME']
                NatomsFromMapping = len(u.select_atoms(selection))
                NatomsFromREADME = np.sum(system['COMPOSITION'][molecule]['COUNT'])
                if NatomsFromMapping !=  NatomsFromREADME and molecule not in lipids_dict:
                    print("""
Found problematic system: %s
Molecule named %s
MDA selection: "%s"
Atoms from mapping/in readme: %d / %d
""" %
     (system['SYSTEM'], system['COMPOSITION'][molecule]['NAME'], selection, 
     NatomsFromMapping, NatomsFromREADME) )
                    errnum += 1
                # end for
        print("Everything is OK for molecule %s!" % molecule)
