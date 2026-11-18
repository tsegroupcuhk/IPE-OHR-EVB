import openmm as mm
import openmm.app as app

atom1 = 9
atom2 = 18
class SN2OffDiagGenerator:
    def __init__(self, hamiltonian):
        self.ff = hamiltonian
        self.params = {}
        self._jaxPotential = None
        self.types = []

    def registerPairType(self, bond):

        types = self.ff._findAtomTypes(bond, 2)
        self.types = types
        self.params['A1'] = float(bond['A1'])


        self.params['r1'] = float(bond['r1'])


        self.params['D1'] = float(bond['D1'])


    @staticmethod
    def parseElement(element, hamiltonian):
        generator = SN2OffDiagGenerator(hamiltonian)
        hamiltonian.registerGenerator(generator)
        for bondtype in element.findall("Pair"):
            generator.registerPairType(bondtype.attrib)

    def createForce(self, system, data, nonbondedMethod, nonbondedCutoff,
                    args):


        force = mm.CustomCompoundBondForce(
            2,
             "D1*exp(-A1*(d1-r1)^2); d1=distance(p1,p2)"

        )
        force.addPerBondParameter("D1")


        force.addPerBondParameter("A1")
        force.addPerBondParameter("r1")


        force.addBond([atom1, atom2], [
            self.params["D1"], self.params["A1"], self.params["r1"],


        ])
        system.addForce(force)


app.forcefield.parsers["SN2OffDiagForce"] = SN2OffDiagGenerator.parseElement
