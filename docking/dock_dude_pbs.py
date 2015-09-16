"""
PBS interface for generating DUD-E docked poses.
"""
import argparse
import os
import gzip
import cPickle as pickle
import math
import subprocess
from vs_utils.features.nnscore import Binana

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--dude-dir', required=1,
                      help='Directory containing pdbbind data.')
  parser.add_argument("--target", required=1,
                      help="Name of DUD-E target.")
  parser.add_argument("--num-jobs", required=1, type=int,
                      help='Number of PBS jobs to launch.')
  return parser.parse_args(input_args)

def dock_dude(dude_dir, target, num_jobs):
  """Featurize DUD-E docked poses and write features to pickle_out.
 
  Parameters
  ----------
  dude_dir: string
    Path to DUD-E directory
  target: string
    Name of DUD-E target.
  """
  target_dir = os.path.join(dude_dir, target)
  actives_dir = os.path.join(target_dir, "actives")
  decoys_dir = os.path.join(target_dir, "decoys")
  actives = [a for a in os.listdir(actives_dir)]
  decoys = [a for a in os.listdir(decoys_dir)]
  receptor = os.path.join(target_dir, "receptor.pdb")

  # Just for debugging purposes
  actives = actives[:1]
  protein_pdb_path = "/home/rbharath/DUD-E/aa2ar/receptor_hyd.pdb"
  protein_pdbqt_path = "/home/rbharath/DUD-E/aa2ar/receptor_hyd.pdbqt"

  for active in actives:
    active_file = os.path.join(actives_dir, active)
    active_base = os.path.basename(active_file).split(".")[0]
    conf_active_file = os.path.join(actives_dir,
        "conf_%s.txt" % active_base)
    log_file = os.path.join(actives_dir,
        "log_%s.txt" % active_base)
    vina_command = ["vina", "--config", conf_active_file, "--log", log_file]
    subprocess.Popen(vina_command).wait()

if __name__ == '__main__':
  args = parse_args()
  dock_dude(args.dude_dir, args.target, args.num_jobs)
