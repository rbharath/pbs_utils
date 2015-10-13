"""
Generate ligand pdb files for actives and decoys.
"""
import argparse
import gzip
import os
from rdkit import Chem

def parse_args(input_args=None):
  """Parse command-line arguments."""
  parser = argparse.ArgumentParser()
  parser.add_argument("--ligand-file", required=1,
      help="Path of sdf.gz file containing ligands.")
  parser.add_argument("--out-dir", required=1,
      help="Directory to write ligand pdb files.")
  parser.add_argument("--out-template", default="active-%d.pdb",
                      help="Template for output ligand pdbs. Must have one "
                      "int-substitutable entry for ligand id.")
  return parser.parse_args(input_args)

def generate_pdbs(ligand_file, out_dir, out_template):
  """Generate pdb files for ligands."""
  with gzip.open(ligand_file) as inf:
    gzsuppl = Chem.ForwardSDMolSupplier(inf)
    mols = [x for x in gzsuppl if x is not None]
    print "Number molecules: " + str(len(mols))
    for id, mol in enumerate(mols):
      ligand_pdb = os.path.join(out_dir, out_template % id)
      print "writing " + ligand_pdb
      w = Chem.PDBWriter(ligand_pdb)
      w.write(mol)

if __name__ == '__main__':
  args = parse_args()
  generate_pdbs(args.ligand_file, args.out_dir, args.out_template)
