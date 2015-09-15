"""
PBS interface for preprocessing DUD-E pdb files for docking.
"""
import argparse
import os
from vs_utils.utils.nnscore_utils import hydrogenate_and_compute_partial_charges

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument("--dude-dir", required=1,
      help="Directory containing DUD-E data.")
  parser.add_argument("--target", required=1,
                      help="Name of DUD-E target.")
  #parser.add_argument("--script-template", default="script%d.pbs",
  #                    help="Template for script name. Must have one "
  #                    "string-substitutable entry for job number.")
  #parser.add_argument("--num-jobs", required=1, type=int,
  #                    help='Number of PBS jobs to launch.')
  return parser.parse_args(input_args)

def preprocess_dude(dude_dir, target):
  """Preprocess dude compounds for docking."""
  target_dir = os.path.join(dude_dir, target)
  actives_dir = os.path.join(target_dir, "actives")
  decoys_dir = os.path.join(target_dir, "decoys")
  actives = [a for a in os.listdir(actives_dir)]
  decoys = [a for a in os.listdir(decoys_dir)]
  receptor = os.path.join(target_dir, "receptor.pdb")

  # Just for debugging purposes
  actives = actives[:1]
  decoys = decoys[:1]
  hydrogenate_and_compute_partial_charges(
      receptor, "pdb", target_dir)
  conf = """
  receptor = receptor_hyd.pdbqt
  ligand = %s 

  center_x = 0
  center_y = 0
  center_z = 0

  size_x = 63
  size_y = 63
  size_z = 63

  exhaustiveness = 30
  """
  for active in actives:
    active_file = os.path.join(actives_dir, active)
    print active_file
    hydrogenate_and_compute_partial_charges(
        active_file, "pdb", actives_dir, rigid=False)
    active_conf = conf % active_file
    print active_conf
  for decoy in decoys:
    decoy_file = os.path.join(decoys_dir, decoy)
    print decoy_file
    hydrogenate_and_compute_partial_charges(
        decoy_file, "pdb", decoys_dir, rigid=False)
    decoy_conf = conf % decoy_file
    print deocy_conf


if __name__ == '__main__':
  args = parse_args()
  preprocess_dude(args.dude_dir, args.target)
