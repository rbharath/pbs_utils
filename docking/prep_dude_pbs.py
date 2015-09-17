"""
PBS interface for preprocessing DUD-E pdb files for docking.
"""
import argparse
import os
import os.path
from vs_utils.utils.nnscore_utils import hydrogenate_and_compute_partial_charges

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument("--dude-dir", required=1,
      help="Directory containing DUD-E data.")
  parser.add_argument("--target", required=1,
                      help="Name of DUD-E target.")
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
  receptor_pdbqt = os.path.join(target_dir, "receptor_hyd.pdbqt")
  # TODO(rbharath): This is a bit of an ugly kludge.
  conf = """receptor = %s 
ligand = %s 

center_x = 0
center_y = 0
center_z = 0

size_x = 63
size_y = 63
size_z = 63

exhaustiveness = 30"""
  for active in actives:
    active_file = os.path.join(actives_dir, active)
    active_base = active.split(".")[0]
    active_output = os.path.join(actives_dir, "%s_hyd.pdbqt" %
        active_base)
    conf_active_file = os.path.join(actives_dir,
        "conf_%s.txt" % active_base)
    print active_file
    print active_output
    print conf_active_file
    hydrogenate_and_compute_partial_charges(
        active_file, "pdb", actives_dir, rigid=False)
    active_conf = conf % (receptor_pdbqt, active_output)
    with open(conf_active_file, "wb") as f:
      f.write(active_conf)
    print active_conf
  for decoy in decoys:
    decoy_file = os.path.join(decoys_dir, decoy)
    decoy_base = os.path.basename(decoy_file).split(".")[0]
    decoy_output = os.path.join(decoys_dir, "%s_hyd.pdbqt" %
        decoy_base)
    conf_decoy_file = os.path.join(decoys_dir,
        "conf_%s.txt" % decoy_base)
    print decoy_file
    print decoy_output
    print conf_decoy_file
    hydrogenate_and_compute_partial_charges(
        decoy_file, "pdb", decoys_dir, rigid=False)
    decoy_conf = conf % (receptor_pdbqt, decoy_output)
    with open(conf_decoy_file, "wb") as f:
      f.write(decoy_conf)
    print decoy_conf


if __name__ == '__main__':
  args = parse_args()
  preprocess_dude(args.dude_dir, args.target)
