"""
Featurize pdbbind molecules through pbs.
"""
import argparse
import os
import math
import subprocess

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--pdbbind-dir', required=1,
                      help='Directory containing pdbbind data.')
  parser.add_argument("--script-dir", required=1,
                      help="Directory to generate qsub scripts.")
  parser.add_argument("--script-template", default="script%d.pbs",
                      help="Template for script name. Must have one "
                      "string-substitutable entry for job number.")
  parser.add_argument("--num-jobs", required=1, type=int,
                      help='Number of PBS jobs to launch.')
  parser.add_argument('--pickle-dir', required=1,
                      help='Directory to output pickled featured vectors.')
  return parser.parse_args(input_args)

def featurize_pdbbind(pdbbind_dir, script_dir, script_template, num_jobs,
    pickle_dir):
  """Featurize all entries in pdbbind_dir and write features to pickle_out

  pdbbind_dir should be a dir, with K subdirs, one for each protein-ligand
  complex to be featurized. The ligand and receptor should each have a pdb
  and pdbqt file. The ligand files should end in '_ligand_hyd.${FILETYPE}'
  while the receptor files should end in '_protein_hyd.${FILETYPE}'

  pdbbind_dir: string
    Path to pdbbind directory.
  pickle_out: string
    Path to write pickle output.
  """
  assert os.path.isdir(pdbbind_dir)

  # Extract the subdirectories in pdbbind_dir
  subdirs = [d for d in os.listdir(pdbbind_dir) if
      os.path.isdir(os.path.join(pdbbind_dir, d))]

  num_per_job = int(math.ceil(len(subdirs)/float(num_jobs)))
  print "Number per job: %d" % num_per_job

  for job in range(num_jobs):
    job_dirs = subdirs[job*num_per_job:(job+1)*num_per_job]
    job_dirs = [os.path.join(pdbbind_dir, dirname) for dirname in job_dirs]
    print "About to process following subdirectories in job %d" % job
    print job_dirs

    # TODO(rbharath): This is horrible. Clean this script up...
    pickle_out = os.path.join(pickle_dir, "features%d.p" % job)
    command = " ".join(["python", "/home/rbharath/pbs_utils/featurize_pdbbind_pbs_job.py",
        "--pdb-directories"] + job_dirs + ["--pickle-out", pickle_out, "\n"])

    print "command: "
    print command
    script_loc = os.path.join(script_dir, script_template % job)
    print "script_loc: "
    print script_loc
    print "Writing script!"
    with open(script_loc, "w") as f:
      f.write(command)

    qsub_command = ["qsub", "-j", "oe", "-q", "MP", script_loc]
    print qsub_command
    print "launching job"
    subprocess.Popen(qsub_command)


if __name__ == '__main__':
  args = parse_args()
  featurize_pdbbind(args.pdbbind_dir, args.script_dir,
      args.script_template, args.num_jobs, args.pickle_dir)
