"""
One job invocation for prep-pdbbind.
"""
import argparse
import os
import re
import cPickle as pickle
import mdtraj as md
from vs_utils.features.nnscore import Binana
from vs_utils.utils.nnscore_pdb import PDB
from vs_utils.utils.PDBTransformer import PDBTransformer
from vs_utils.utils.grid_factory import GridGenerator
from rdkit import Chem

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--pdb-directories', nargs="+", required=1,
                      help='List of directories containing pdbbind data.')
  parser.add_argument('--pickle-out', required=1,
                      help='Directory to output pickled featured vectors.')
  parser.add_argument('--featurization-type', required=1,
                      help='Choose fingerprint or 3d_grid')
  parser.add_argument('--box-width', required=1,
                      help='Input box width in Angstroms, default=16')
  parser.add_argument('--voxel-width', required=1,
                      help='Input voxel width in Angstroms, default=0.5')
  parser.add_argument('--tmp-dir', required=1,
                      help='Directory for saving all intermediate files')
  return parser.parse_args(input_args)

def featurize_fingerprint(pdb_directories, pickle_out):
  """Featurize all pdbs in provided directories."""
  # Instantiate copy of binana vector
  binana = Binana()
  # See features/tests/nnscore_test.py:TestBinana.testComputeInputVector
  # for derivation.
  feature_len = binana.num_features()
  feature_vectors = {}
  for count, pdb_dir in enumerate(pdb_directories):
    print "\nprocessing %d-th pdb %s" % (count, dir)

    print "About to extract ligand and protein input files"
    ligand_pdb, ligand_pdbqt = None, None
    protein_pdb, protein_pdbqt = None, None
    for f in os.listdir(pdb_dir):
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
        raise ValueError("Required files not present for %s" % pdb_dir)

    ligand_pdb_path = os.path.join(pdb_dir, ligand_pdb)
    ligand_pdbqt_path = os.path.join(pdb_dir, ligand_pdbqt)
    protein_pdb_path = os.path.join(pdb_dir, protein_pdb)
    protein_pdbqt_path = os.path.join(pdb_dir, protein_pdbqt)

    print "About to load ligand from input files"
    ligand_pdb_obj = PDB()
    ligand_pdb_obj.load_from_files(ligand_pdb_path, ligand_pdbqt_path)

    print "About to load protein from input files"
    protein_pdb_obj = PDB()
    protein_pdb_obj.load_from_files(protein_pdb_path, protein_pdbqt_path)

    print "About to generate feature vector."
    features = binana.compute_input_vector(ligand_pdb_obj,
        protein_pdb_obj)
    if len(features) != feature_len:
      raise ValueError("Feature length incorrect on %s" % pdb_dir)
    print "Feature vector generated correctly."

    print "About to compute ligand smiles string."
    ligand_mol = Chem.MolFromPDBFile(ligand_pdb_path)
    # TODO(rbharath): Why does this fail sometimes?
    if ligand_mol is None:
      continue
    smiles = Chem.MolToSmiles(ligand_mol)

    print "About to compute sequence."
    protein = md.load(protein_pdb_path)
    seq = [r.name for r in protein.top.residues] 

    # Write the computed quantities
    feature_vectors[pdb_dir] = (features, smiles, seq)
  print "About to write pickle to " + pickle_out
  with open(pickle_out, "wb") as f:
    pickle.dump(feature_vectors, f)

def featurize_3d_grid(pdb_directories, pickle_out, box_width, voxel_width, tmp_dir):
  feature_vectors = {}
  for count, pdb_dir in enumerate(pdb_directories):
    
    #TODO(evanfeinberg): Re-factor common code between two featurization functions into a 
      #separate function
    print "\nprocessing %d-th pdb %s" % (count, pdb_dir)

    print "About to extract ligand and protein input files"
    ligand_pdb, ligand_pdbqt = None, None
    protein_pdb, protein_pdbqt = None, None
    for f in os.listdir(pdb_dir):
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
        raise ValueError("Required files not present for %s" % pdb_dir)

    ligand_pdb_path = os.path.join(pdb_dir, ligand_pdb)
    ligand_pdbqt_path = os.path.join(pdb_dir, ligand_pdbqt)
    protein_pdb_path = os.path.join(pdb_dir, protein_pdb)
    protein_pdbqt_path = os.path.join(pdb_dir, protein_pdbqt)

    tmp_dir = os.path.join(tmp_dir, protein_pdb)
    if not os.path.exists(tmp_dir): os.makedirs(tmp_dir)
    system_pdb = os.path.join(tmp_dir, "system.pdb")
    box_pdb = os.path.join(tmp_dir, "box.pdb")
    box_pickle = os.path.join(tmp_dir, "box.pickle")
    grid_pickle = os.path.join(tmp_dir, "grid.pickle")

    p = PDBTransformer()
    p.transform(protein_pdb_path, protein_pdbqt_path, ligand_pdb_path, ligand_pdbqt_path, 
                system_pdb, box_pdb, box_pickle, box_x = box_width, box_y = box_width, box_z = box_width)

    g = GridGenerator()
    grid = g.transform(box_pickle, box_width, box_width, box_width, voxel_width, grid_pickle, num_features=3)

    print "About to compute sequence."
    protein = md.load(protein_pdb_path)
    seq = [r.name for r in protein.top.residues] 

    print "About to compute ligand smiles string."
    ligand_mol = Chem.MolFromPDBFile(ligand_pdb_path)
    # TODO(rbharath): Why does this fail sometimes?
    if ligand_mol is None:
      continue
    smiles = Chem.MolToSmiles(ligand_mol)

    feature_vectors[pdb_dir] = (grid, smiles, seq)
  print "About to write pickle to " + pickle_out
  with open(pickle_out, "wb") as f:
    pickle.dump(feature_vectors, f)


def featurize_job(pdb_directories, pickle_out, featurization_type, box_width, voxel_width, tmp_dir):
  if featurization_type=="fingerprint":
    featurize_fingerprint(pdb_directories, pickle_out)
  elif featurization_type=="3d_grid":
    featurize_3d_grid(pdb_directories, pickle_out, box_width, voxel_width, tmp_dir)
  else:
    print("Didn't understand featurization type. options are fingerprint or 3d_grid")
 

if __name__ == '__main__':
  args = parse_args()
  featurize_job(args.pdb_directories, args.pickle_out, args.featurization_type, args.box_width, args.voxel_width, args.tmp_dir)
