from respyte.molecule import *
from respyte.readinp_resp import Input
from respyte.molecule_resp import *
from respyte.select_grid import *
from respyte.resp_unit import *

def main():
    cwd = os.getcwd()
    # check if the current working idr contains input folder
    print('\n')
    print('---------------------------------------------------------')
    print(' 1. Reading  input files and folders.                    ')
    print('---------------------------------------------------------')
    if os.path.isdir("%s/input" % cwd):
        print(' Found the input folder. Now read input/respyte.yml')
    else:
        print(' Failed to find input folder. Should have input(folder) containing input.yml and molecules(folder)')
    # read respyte.yml
    inp = Input('%s/input/respyte.yml' % (cwd))

    # Create molecule object
    if inp.cheminformatics == 'openeye':
        molecule = Molecule_OEMol()
    elif inp.cheminformatics == 'rdkit':
        molecule = Molecule_RDMol()
    else:
        print(' Not using Cheminformatics?')
        molecule = Molecule_respyte()

    molecule.addInp(inp)

    for idx, i in enumerate(inp.nmols):
        molN = 'mol%d' % (idx+1)
        wkd = '%s/input/molecules/%s' % (cwd, molN)
        coordfilepath = []
        espffilepath = []
        listofselectedPts = []
        for j in range(i):
            confN = 'conf%d' % (j+1)
            path = wkd + '/%s' % (confN)
            pdbfile = path + '/%s_%s.pdb' % (molN, confN)
            mol2file = path + '/%s_%s.mol2' % (molN, confN)
            xyzfile = path + '/%s_%s.xyz' % (molN, confN)
            if os.path.isfile(pdbfile):
                coordpath = pdbfile
                coordfilepath.append(coordpath)
            elif os.path.isfile(mol2file):
                coordpath = mol2file
                coordfilepath.append(coordpath)
            elif os.path.isfile(xyzfile):
                coordpath = xyzfile
                coordfilepath.append(coordpath)
                print(' This folder doesn not contain pdb or mol2 file format. ')
            else:
                raise RuntimeError(" Coordinate file should have pdb or mol2 file format! ")

            espfpath = path + '/%s_%s.espf' %(molN, confN)
            if not os.path.isfile(espfpath):
                raise RuntimeError(' %s file doesnt exist!!! '% espfpath)
            else:
                espffilepath.append(espfpath)

            if 'boundary_select' in inp.gridinfo:
                radii = inp.gridinfo['boundary_select']['radii']
                inner = inp.gridinfo['boundary_select']['inner']
                outer = inp.gridinfo['boundary_select']['outer']
                tmpmol = Molecule(coordpath)
                pts = []
                with open(espfpath, 'r') as espff:
                    for i, line in enumerate(espff):
                        fields = line.strip().split()
                        numbers = [float(field) for field in fields]
                        if (len(numbers)==4):
                            xyz = [x for x in numbers[0:3]]
                            pts.append(xyz)
                selectedPtsIdx, selectedPts = SelectGridPts(tmpmol,inner,outer,pts, radii )
            else:
                selectedPtsIdx = None
            listofselectedPts.append(selectedPtsIdx)
        molecule.addCoordFiles(*coordfilepath)
        molecule.addEspf(*espffilepath, selectedPts = listofselectedPts)
    print('---------------------------------------------------------')
    print(' 2. Charge fitting to QM data                            ')
    print('---------------------------------------------------------')
    os.chdir(cwd)
    cal = Respyte_Optimizer()
    cal.addInp(inp)
    cal.addMolecule(molecule)
    if inp.restraintinfo:
        if inp.restraintinfo['penalty'] == 'model2':
            aval = inp.restraintinfo['a']
            cal.Model2qpot(aval)
        elif inp.restraintinfo['penalty'] == 'model3':
            aval = inp.restraintinfo['a']
            bval = inp.restraintinfo['b']
            cal.Model3qpot(aval, bval)
        elif inp.restraintinfo['penalty'] == 'model4':
            a1val = inp.restraintinfo['a1']
            a2val = inp.restraintinfo['a2']
            bval = inp.restraintinfo['b']
            cal.Model4qpot(a1val, a2val, bval)
        elif inp.restraintinfo['penalty'] == 'model5':
            a1val = inp.restraintinfo['a1']
            a2val = inp.restraintinfo['a2']
            bval = inp.restraintinfo['b']
            cal.Model5qpot(a1val, a2val, bval)
        elif inp.restraintinfo['penalty'] == 'model6':
            aval = inp.restraintinfo['a']
            bval = inp.restraintinfo['b']
            cal.Model6qpot(aval, bval)
        elif inp.restraintinfo['penalty'] == '2-stg-fit':
            a1val = inp.restraintinfo['a1']
            a2val = inp.restraintinfo['a2']
            bval = inp.restraintinfo['b']
            cal.twoStageFit(a1val, a2val, bval)
        elif inp.restraintinfo['penalty'] == '2-stg-fit(6)':
            aval = inp.restraintinfo['a']
            bval = inp.restraintinfo['b']
            cal.twoStageFit_Model6(aval, bval)

if __name__ == '__main__':
    main()
