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
  parser.add_argument("--tmp-dir", required=1, type=str,
                      help="Directory to save intermediate files.")
  parser.add_argument("--script-template", default="script%d.pbs",
                      help="Template for script name. Must have one "
                      "string-substitutable entry for job number.")
  parser.add_argument("--num-jobs", required=1, type=int,
                      help='Number of PBS jobs to launch.')
  parser.add_argument('--pickle-dir', required=1, type=str,
                      help='Directory to output pickled featured vectors.')
  parser.add_argument('--queue-system', required=1,
                      help='Choose slurm or pbs')
  parser.add_argument('--featurization-type', required=1,
                      help='Choose fingerprint or 3d_grid')
  parser.add_argument('--box-width', required=0, default=str(16.0),
                      help='Input box width in Angstroms, default=16.0')
  parser.add_argument('--voxel-width', required=0, default=str(0.5),
                      help='Input voxel width in Angstroms, default=0.5')
  parser.add_argument('--nb-rotations', required=0, default=str(0),
                      help='Number of times to rotate grid, integer')
  parser.add_argument('--nb-reflections', required=0, default=str(0),
                      help='Number of times to reflect grid, integer')
  parser.add_argument('--save-intermediates', action='store_true',
                      help="Save intermediate files.")
  parser.add_argument('--grid-featurization-type', required=0, default="ecfp",
                      type=str, help="Which type of 3d_grid? options: ecfp, splif")
  parser.add_argument('--fingerprint-bit-size', required=0, default=str(10),
                      help="Choose n in 2^n to define number of bits for ECFP fingerprint array")
  parser.add_argument('--fingerprint-degree', required=0, default=str(2),
                      help="Choose degree to which fingerprints are computed, i.e. ECFP2 vs ECFP4")
  parser.add_argument('--ligand-only', action='store_true',
                      help="Featurize only the ligands?")
  return parser.parse_args(input_args)

def featurize_pdbbind(pdbbind_dir, tmp_dir, script_template, num_jobs,
    pickle_dir, queue_system, featurization_type, box_width, voxel_width, nb_rotations, nb_reflections,
    save_intermediates, grid_featurization_type, fingerprint_bit_size, fingerprint_degree, ligand_only):
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
  if not os.path.exists(tmp_dir): os.makedirs(tmp_dir) 
  if not os.path.exists(pickle_dir): os.makedirs(pickle_dir)

  assert os.path.isdir(pdbbind_dir)

  # Extract the subdirectories in pdbbind_dir
  subdirs = [d for d in os.listdir(pdbbind_dir) if
      os.path.isdir(os.path.join(pdbbind_dir, d))]

  num_per_job = int(math.ceil(len(subdirs)/float(num_jobs)))
  print "Number per job: %d" % num_per_job

  for i, job in enumerate(range(num_jobs)):
    job_dirs = subdirs[job*num_per_job:(job+1)*num_per_job]
    job_dirs = [os.path.join(pdbbind_dir, dirname) for dirname in job_dirs]
    print "About to process following subdirectories in job %d" % job
    print job_dirs

    # TODO(rbharath): This is horrible. Clean this script up...
    pickle_out = os.path.join(pickle_dir, "features%d.pkl.gz" % job)
    #TODO(enf): the path needs to be user-independent 
    
    command = " ".join(["python", "/scratch/users/enf/deep-docking/cluster_utils/featurize_pdbbind_cluster_job.py",
        "--pdb-directories"] + job_dirs + ["--featurization-type", featurization_type] 
        + ["--box-width", box_width] + ["--voxel-width", voxel_width] + ["--nb-rotations", nb_rotations]
        + ["--nb-reflections", nb_reflections] + (["--save-intermediates"] if save_intermediates else []) + ["--grid-featurization-type", grid_featurization_type]
        + ["--fingerprint-bit-size", fingerprint_bit_size] + ["--fingerprint-degree", fingerprint_degree] + (["--ligand-only"] if ligand_only else [])
        + ["--tmp-dir", tmp_dir] + ["--pickle-out", pickle_out, "\n"])
    
    print "command: "
    print command

    script_loc = os.path.join(tmp_dir, script_template % job)
    print "script_loc: "
    print script_loc
    

    if queue_system == "pbs":
      print "Writing pbs script!"
      with open(script_loc, "w") as f:
        f.write(command)
      qsub_command = ["qsub", "-j", "oe", "-q", "MP", "-l", "nodes=1:ppn=1", script_loc]
      print qsub_command
      print "launching job"
      subprocess.Popen(qsub_command)
    elif queue_system == "slurm":
      print "Writing SLURM script!"
      with open(script_loc, "w") as f:
        f.write("#!/bin/bash\n")
        f.write("#SBATCH --output=out%d.out\n" %i)
        f.write("#SBATCH --error=out%d.err\n" %i)
        f.write("#SBATCH  -p normal\n")
        f.write("#SBATCH --mail-type=ALL")
        f.write("#SBATCH --mail=enf@stanford.edu")
        f.write("#SBATCH --job-name=deep%d\n" %i)
        f.write("#SBATCH -n 1\n")
        f.write("#SBATCH --time=12:00:00\n")
        f.write("##SBATCH --qos=normal\n")
        f.write(command)
        slurm_command = ["sbatch", script_loc]
        print slurm_command
        print "launching job"
        subprocess.Popen(slurm_command)




if __name__ == '__main__':
  args = parse_args()
  featurize_pdbbind(args.pdbbind_dir, args.tmp_dir, args.script_template, args.num_jobs, 
    args.pickle_dir, args.queue_system, args.featurization_type, args.box_width, args.voxel_width, args.nb_rotations, args.nb_reflections, 
    args.save_intermediates, args.grid_featurization_type, args.fingerprint_bit_size, args.fingerprint_degree, args.ligand_only)
