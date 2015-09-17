"""
PBS interface for preprocessing DUD-E pdb files for docking.
"""
import argparse
import os
import os.path
from vs_utils.utils.nnscore_utils import hydrogenate_and_compute_partial_charges

def launch_jobs(num_jobs):
  """First attempt to factor out job launching code."""
  # Launch jobs
  command_list = ["python", "/home/rbharath/pbs_utils/prep_dude_pdbs.py"]
  for job in range(num_jobs):
    job_compounds = compounds[job*num_per_job:(job+1)*num_per_job]
    command = " ".join(command_list + ["--compounds"] + job_compounds + ["\n"])
    script_loc = os.path.join(script_dir, script_template % job)
    with open(script_loc, "w") as f:
      f.write(command)
    qsub_command = ["qsub", "-j", "oe", "-q", "MP", "-l", "nodes=1:ppn=1", script_loc]
    subprocess.Popen(qsub_command)

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument("--dude-dir", required=1,
      help="Directory containing DUD-E data.")
  parser.add_argument("--target", required=1,
                      help="Name of DUD-E target.")
  parser.add_argument("--script-dir", required=1,
                      help="Directory to generate qsub scripts.")
  parser.add_argument("--script-template", default="prep_dude_script%d.pbs",
                      help="Template for script name. Must have one "
                      "string-substitutable entry for job number.")
  parser.add_argument("--conf-template", required=1,
                      help="Template for configuration file. Must have two"
                      "string-substitutable entries for receptor and ligand.")
  parser.add_argument("--num-jobs", required=1, type=int,
                      help="Number of PBS jobs to launch.")
  parser.add_argument("--mode", required=1, type=string,
                      help="Either 'launcher' or 'job'")
  parser.add_argument('--compounds', nargs="+", required=1,
                      help='List of dude compounds to process.')
  return parser.parse_args(input_args)

def launch_preprocessing_jobs(dude_dir, script_dir,
    script_template, num_jobs):
  """Launch jobs to perform required preprocessing jobs."""
  assert os.path.isdir(dude_dir)
  target_dir = os.path.join(dude_dir, target)

  # Extract list of actives and decoys
  actives_dir = os.path.join(target_dir, "actives")
  decoys_dir = os.path.join(target_dir, "decoys")
  actives = [a for a in os.listdir(actives_dir)]
  decoys = [a for a in os.listdir(decoys_dir)]
  # Just for debugging purposes
  actives = actives[:1]
  decoys = decoys[:1]

  # Hydrogenate and process the receptor
  receptor = os.path.join(target_dir, "receptor.pdb")
  hydrogenate_and_compute_partial_charges(
      receptor, "pdb", target_dir)
  receptor_pdbqt = os.path.join(target_dir, "receptor_hyd.pdbqt")

  # Compute work per job
  sources = ["active"] * len(actives) + ["decoy"] * len(decoys)
  compounds = actives + decoys
  num_per_job = int(math.ceil(len(compounds)/float(num_jobs)))
  print "Number per job: %d" % num_per_job


def preprocess_dude(compounds):
  """Preprocess dude compounds for docking."""
  with open(conf_template, "rb") as f:
    conf = f.read()
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
