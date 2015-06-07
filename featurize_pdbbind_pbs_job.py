"""
One job invocation for prep-pdbbind.
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
  parser.add_argument('--pdb-directories', nargs="+", required=1,
                      help='List of directories containing pdbbind data.')
  parser.add_argument('--pickle-out', required=1,
                      help='Directory to output pickled featured vectors.')
  return parser.parse_args(input_args)

def featurize_job(pdb_directories, pickle_out):
  """Featurize all pdbs in provided directories."""
  # Instantiate copy of binana vector
  binana = Binana()
  num_atoms = len(Binana.atom_types)
  # See features/tests/nnscore_test.py:TestBinana.testComputeInputVector
  # for derivation.
  feature_len = (3*num_atoms*(num_atoms+1)/2 + num_atoms + 12 + 6 + 3 + 6 +
      3 + 6 + 3 + 1)
  feature_vectors = {}
  for count, dir in enumerate(pdb_directories):
    print "\nprocessing %d-th pdb %s" % (count, dir)

    print "About to extract ligand and protein input files"
    ligand_pdb, ligand_pdbqt = None, None
    protein_pdb, protein_pdbqt = None, None
    for f in os.listdir(dir):
      if re.search("_ligand_hyd.pdb$", f):
        ligand_pdb = f
      elif re.search("_ligand_hyd.pdbqt$", f):
        ligand_pdbqt = f
      elif re.search("_protein_hyd.pdb$", f):
        protein_pdb = f
      elif re.search("_protein_hyd.pdbqt$", f):
        protein_pdbqt = f

    print "Extracted Input Files:"
    print (ligand_pdb, ligand_pdbqt, protein_pdb, protein_pdbqt)
    if (not ligand_pdb or not ligand_pdbqt or not protein_pdb or not
        protein_pdbqt):
        raise ValueError("Required files not present for %s" % d)
    ligand_pdb_path = os.path.join(dir, ligand_pdb)
    ligand_pdbqt_path = os.path.join(dir, ligand_pdbqt)
    protein_pdb_path = os.path.join(dir, protein_pdb)
    protein_pdbqt_path = os.path.join(dir, protein_pdbqt)

    print "About to load ligand from input files"
    ligand_pdb_obj = PDB()
    ligand_pdb_obj.load_from_files(ligand_pdb_path, ligand_pdbqt_path)

    print "About to load protein from input files"
    protein_pdb_obj = PDB()
    protein_pdb_obj.load_from_files(protein_pdb_path, protein_pdbqt_path)

    print "About to generate feature vector."
    vector = binana.compute_input_vector(ligand_pdb_obj,
        protein_pdb_obj)
    feature_vectors[dir] = vector
    if len(vector) != feature_len:
      raise ValueError("Feature length incorrect on %s" % d)
    print "Feature vector generated correctly."

  with open(pickle_out, "wb") as f:
    pickle.dump(feature_vectors, f)

if __name__ == '__main__':
  args = parse_args()
  featurize_job(args.pdb_directories, args.pickle_out)
