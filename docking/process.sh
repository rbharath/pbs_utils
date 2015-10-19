obabel -i sdf $CID.sdf -o pdbqt -O $CID.pdbqt
sed -i -e s/USER/REMARKS/ -e /TER/d $CID.pdbqt
sed -e "s/receptor =.*$/receptor = $PDB.pdbqt/" -e "s/ligand =.*$/ligand = $CID.pdbqt/" conf.txt > conf_$CID.txt
