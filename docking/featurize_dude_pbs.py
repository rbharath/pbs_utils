"""
PBS interface for featurizing DUD-E docked poses.
"""
import argparse
import os

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
  #parser.add_argument("--num-jobs", required=1, type=int,
  #                    help='Number of PBS jobs to launch.')
  parser.add_argument('--pickle-dir', required=1,
                      help='Directory to output pickled featured vectors.')
  return parser.parse_args(input_args)

def featurize_dude(dude_dir, target, pickle_dir):
  """Featurize DUD-E docked poses and write features to pickle_out."""
  target_dir = os.path.join(dude_dir, target)
  actives_dir = os.path.join(target_dir, "actives")
  decoys_dir = os.path.join(target_dir, "decoys")
  actives = [a for a in os.listdir(actives_dir)]
  decoys = [a for a in os.listdir(decoys_dir)]
  receptor = os.path.join(target_dir, "receptor.pdb")
  # Just for debugging purposes
  actives = actives[:1]
  decoys = decoys[:1]
  for active in actives:
    active_pdbqt = active.split(".")[0] + "_hyd_out.pdbqt"
    active_pdbqt = os.path.join(actives_dir, active_pdbqt)
    active_pdb = active.split(".")[0] + "_hyd_out.pdb"
    active_pdb = os.path.join(actives_dir, active_pdb)
    print active_pdbqt
    print active_pdb

if __name__ == '__main__':
  args = parse_args()
  featurize_dude(args.dude_dir, args.target, args.pickle_dir)
