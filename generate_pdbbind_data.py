"""
Extract the labels for pdbbind data and output in deep-chem readable format.
"""
import argparse
import csv
import os
import math
import subprocess
import cPickle as pickle
import gzip

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--pdbbind-label-file', required=1,
                      help='Path to pdbbind labels file.')
  parser.add_argument("--feature-files", nargs="+", required=1,
                      help="List of pickles with features.")
  parser.add_argument("--out", required=1,
                      help="File to write output to.")
  parser.add_argument("--output_type", default="csv",
                      choices=["csv", "pkl.gz"],
                      help="Type of output file.")
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

def write_csv(feature_dict, labels, out):
  """Write CSV output."""
  with open(out, "wb") as csvfile:
    writer = csv.writer(csvfile, delimiter="\t")
    writer.writerow(["Smiles", "Sequence", "Label", "Features"])
    for key in feature_dict:
      label = labels[key]
      (features, smiles, seq) = feature_dict[key]
      writer.writerow([smiles, ",".join(seq), label, ",".join([str(elem) for elem in list(features)])])

def write_pkl_gz(feature_dict, labels, out):
  """Write pkl.gz output."""
  with gzip.open(out, "wb") as f:
    outputs = []
    for key in feature_dict:
      label = labels[key]
      features = feature_dict[key]
      # TODO(rbharath): Once smiles/sequences are added into 3D grid data,
      # remove this line
      smiles, sequence = None, None
      outputs.append({"smiles": smiles, "sequence": sequence, "label": label, "features": features})
    pickle.dump(outputs, f)

def generate_dataset(pdbbind_label_file, feature_files, out, output_type):
  """Generate dataset file."""
  labels = extract_labels(pdbbind_label_file)
  feature_dict = {}
  for feature_file in feature_files:
    with open(feature_file, "rb") as features:
      contents = pickle.load(features)
      for key, value in contents.iteritems():
        name = os.path.basename(key)
        feature_dict[name] = value
  if output_type == "csv":
    write_csv(feature_dict, labels, out)
  elif output_type == "pkl.gz":
    write_pkl_gz(feature_dict, labels, out)


if __name__ == '__main__':
  args = parse_args()
  generate_dataset(args.pdbbind_label_file, args.feature_files, args.out, args.output_type)
