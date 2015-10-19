"""
Extract the labels for pdbbind  data.
"""
import argparse
import csv
import os
import math
import subprocess
import cPickle as pickle

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--pdbbind-label-file', required=1,
                      help='Path to pdbbind labels file.')
  parser.add_argument("--feature-files", nargs="+", required=1,
                      help="List of pickles with features.")
  parser.add_argument("--out-csv", required=1,
                      help="File to write csv output to.")
  return parser.parse_args(input_args)

def extract_labels(pdbbind_label_file):
  """Extract labels from pdbbind label file."""
  assert os.path.isfile(pdbbind_label_file)
  labels = {}
  with open(pdbbind_label_file) as f:
    content = f.readlines()
    for line in content:
      if line[0] == "#":
        continue
      line = line.split()
      # lines in the label file have format
      # PDB-code Resolution Release-Year -logKd Kd reference ligand-name
      #print line[0], line[3]
      labels[line[0]] = line[3]
  return labels

def generate_dataset(pdbbind_label_file, feature_files, out_csv):
  labels = extract_labels(pdbbind_label_file)
  feature_dict = {}
  for feature_file in feature_files:
    with open(feature_file, "rb") as features:
      contents = pickle.load(features)
      for key, value in contents.iteritems():
        name = os.path.basename(key)
        feature_dict[name] = value
  # TODO(bharath): There's a discrepancy between the number of labels and
  # keys. However, I've verified that no ValueErrors are thrown. Understand
  # the cause of this discrepancy (10656 labels vs 10605 features)
  #assert len(labels.keys()) == len(feature_dict.keys())
  with open(out_csv, "wb") as csvfile:
    writer = csv.writer(csvfile, delimiter="\t")
    writer.writerow(["Smiles", "Sequence", "Label", "Features"])
    for key in feature_dict:
      label = labels[key]
      (features, smiles, seq) = feature_dict[key]
      writer.writerow([smiles, ",".join(seq), label, ",".join([str(elem) for elem in list(features)])])

if __name__ == '__main__':
  args = parse_args()
  generate_dataset(args.pdbbind_label_file, args.feature_files,
      args.out_csv)
