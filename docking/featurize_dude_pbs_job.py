"""
One job invocation for prepping DUD-E docking.
"""
import argparse
import os
import re
import cPickle as pickle
from vs_utils.features.nnscore import Binana
from vs_utils.utils.nnscore_pdb import PDB

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--docked_compounds', nargs="+", required=1,
                      help='List of docked output pdbs output by autodock')
  parser.add_argument('--pickle-out', required=1,
                      help='Directory to output pickled featured vectors.')
  return parser.parse_args(input_args)

def featurize_job(docked_compounds):
  """Featurize all docked structures."""
  # Instantiate copy of binana vector
  binana = Binana()
  feature_len = binana_num_features()
  feature_vectors = {}
  for count, compound in enumerate(docked_compounds):
    print "\nprocessing %d-th docked pdb %s" % (count, compound)
