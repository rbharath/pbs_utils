"""
One job invocation for prep-pdbbind.
"""
import argparse
import os
import math
from vs_utils.utils.nnscore_utils import hydrogenate_and_compute_partial_charges

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--pdb-directories', nargs="+", required=1,
                      help='List of directories containing pdbbind data.')
  return parser.parse_args(input_args)

def pdbbind_job(pdb_directories):
  """Processes all pdbs in provided directories."""
  for count, dirname in enumerate(pdb_directories):
    print "Processing %d-th entry %s" % (count, dirname)
    ligand, protein = None, None
    for molfile in os.listdir(dirname):
      if "_ligand.mol2" in molfile:
        print "Input ligand: %s" % molfile 
        ligand = molfile 
      elif "_protein.pdb" in molfile:
        print "Input protein: %s" % molfile
        protein = molfile 
    if not ligand or not protein:
      raise ValueError("Ligand or Protein missing in %s" % dirname)
    ligand_file = os.path.join(dirname, ligand)
    protein_file = os.path.join(dirname, protein)

    print "About to preprocess ligand."
    hydrogenate_and_compute_partial_charges(ligand_file, "mol2", dirname)

    print "About to preprocess protein."
    hydrogenate_and_compute_partial_charges(protein_file, "pdb", dirname)

if __name__ == '__main__':
  args = parse_args()
  pdbbind_job(args.pdb_directories)
