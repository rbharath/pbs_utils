"""
Extract the labels for pdbbind  data.
"""
import argparse
import os
import math
import subprocess

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--pdbbind-label-file', required=1,
                      help='Path to pdbbind labels file.')
  return parser.parse_args(input_args)

def extract_labels(pdbbind_label_file):
  """Extract labels from pdbbind label file."""
  assert os.path.isfile(pdbbind_label_file)
  with open(pdbbind_label_file) as f:
    content = f.readlines()
    for line in content:
      if line[0] == "#":
        continue
      line = line.split()
      # lines in the label file have format
      # PDB-code Resolution Release-Year -logKd Kd reference ligand-name
      print line[0], line[3]

if __name__ == '__main__':
  args = parse_args()
  extract_labels(args.pdbbind_label_file)
