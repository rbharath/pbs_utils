"""
PBS interface for featurizing DUD-E docked poses.
"""
import argparse
import os
import gzip
import cPickle as pickle
import math
from vs_utils.features.nnscore import Binana
from vs_utils.utils.nnscore_pdb import PDB
from vs_utils.utils.nnscore_pdb import MultiStructure 
from vs_utils.utils.nnscore_utils import pdbqt_to_pdb

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--dude-dir', required=1,
                      help='Directory containing pdbbind data.')
  parser.add_argument("--target", required=1,
                      help="Name of DUD-E target.")
  #parser.add_argument("--script-dir", required=1,
  #                    help="Directory to generate qsub scripts.")
  #parser.add_argument("--script-template", default="script%d.pbs",
  #                    help="Template for script name. Must have one "
  #                    "string-substitutable entry for job number.")
  parser.add_argument("--num-jobs", required=1, type=int,
                      help='Number of PBS jobs to launch.')
  parser.add_argument('--pickle-dir', required=1,
                      help='Directory to output pickled featured vectors.')
  return parser.parse_args(input_args)

def featurize_dude(dude_dir, target, pickle_dir, num_jobs):
  """Featurize DUD-E docked poses and write features to pickle_out.
 
  Parameters
  ----------
  dude_dir: string
    Path to DUD-E directory
  target: string
    Name of DUD-E target.
  pickle_dir: string
    Path to directory to output pickles 
  """
  target_dir = os.path.join(dude_dir, target)
  actives_dir = os.path.join(target_dir, "actives")
  decoys_dir = os.path.join(target_dir, "decoys")
  actives = [a for a in os.listdir(actives_dir)]
  decoys = [a for a in os.listdir(decoys_dir)]
  receptor = os.path.join(target_dir, "receptor.pdb")
  pickle_out = os.path.join(target_dir, "out.pkl.gz")
  # Just for debugging purposes
  actives = actives[:1]

  num_per_job = int(math.ceil(len(actives)/float(num_jobs)))
  print "Number per job: %d" % num_per_job
  protein_pdb_path = "/home/rbharath/DUD-E/aa2ar/receptor_hyd.pdb"
  protein_pdbqt_path = "/home/rbharath/DUD-E/aa2ar/receptor_hyd.pdbqt"

  print "About to load protein from input files"
  protein_pdb_obj = PDB()
  protein_pdb_obj.load_from_files(protein_pdb_path, protein_pdbqt_path)

  binana = Binana()
  feature_len = binana.num_features()
  feature_vectors = {}
  for compound in actives:
    compound_name = compound.split(".")[0]
    compound_pdbqt = compound_name + "_hyd_out.pdbqt"
    compound_pdbqt = os.path.join(actives_dir, compound_pdbqt)

    # Convert the pdbqt to pdb
    pdbqt_to_pdb(compound_pdbqt, actives_dir)
    compound_pdb = compound_name + "_hyd_out.pdb"
    compound_pdb = os.path.join(actives_dir, compound_pdb)

    structures = MultiStructure()
    structures.load_from_files(compound_pdb, compound_pdbqt)

    vectors = []
    for key in sorted(structures.molecules.keys()):
      structure = structures.molecules[key]
      print "type(structure)"
      print type(structure)
      vectors.append(binana.compute_input_vector(structure,
          protein_pdb_obj))
    feature_vectors[compound_name] = vectors

  with gzip.open(pickle_out, "wb") as f:
    pickle.dump(feature_vectors, f)


  decoys = decoys[:1]

if __name__ == '__main__':
  args = parse_args()
  featurize_dude(args.dude_dir, args.target, args.pickle_dir, args.num_jobs)
