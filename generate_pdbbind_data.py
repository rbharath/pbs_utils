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
import pandas as pd
import multiprocessing as mp

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
  parser.add_argument("--parallel", default=False,
                      type=bool,
                      help="Do processing in parallel")
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
    # We use tab delimiter since features is a float array represented in the
    # form 3.5,4.3,etc.
    writer = csv.writer(csvfile, delimiter="\t")
    writer.writerow(["Smiles", "Sequence", "Label", "Features"])
    for key in feature_dict:
      label = labels[key]
      (features, smiles, seq) = feature_dict[key]
      features_str = ",".join([str(elem) for elem in list(features)])
      writer.writerow([smiles, ",".join(seq), label, features_str])

def write_pkl_gz(feature_dict, labels, out):
  """Write pkl.gz output."""
  with gzip.open(out, "wb") as f:
    outputs = []
    for key in feature_dict:
      labels_key = key.split("_")[0]
      label = labels[labels_key]
      features, smiles, sequence = feature_dict[key]
      outputs.append({"smiles": smiles, "sequence": sequence, "label": label, "features": features})
    df = pd.DataFrame(outputs)
    pickle.dump(df, f)

def read_feature_file(feature_file, feature_dict = {}):
  print("Currently reading %s" %feature_file)
  with gzip.open(feature_file, "rb") as features:
    contents = pickle.load(features)
    for index, (key, value) in enumerate(contents.iteritems()):
      name = os.path.basename(key)
      feature_dict[name] = value
  return(feature_dict)

'''
http://stackoverflow.com/questions/38987/how-can-i-merge-two-python-dictionaries-in-a-single-expression
'''
def merge_dicts(*dict_args):
    '''
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    '''
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def generate_dataset(pdbbind_label_file, feature_files, out, output_type, parallel):
  """Generate dataset file."""
  labels = extract_labels(pdbbind_label_file)
  if not parallel:
    feature_dict = {}
    for feature_file in feature_files:
      feature_dict = read_feature_file(feature_file, feature_dict)
  else:
    pool = mp.Pool(mp.cpu_count())
    feature_dicts = pool.map(read_feature_file, feature_files)
    feature_dict = merge_dicts(*feature_dicts)
    pool.terminate()
  if output_type == "csv":
    write_csv(feature_dict, labels, out)
  elif output_type == "pkl.gz":
    write_pkl_gz(feature_dict, labels, out)


if __name__ == '__main__':
  args = parse_args()
  generate_dataset(args.pdbbind_label_file, args.feature_files, args.out, args.output_type, args.parallel)
