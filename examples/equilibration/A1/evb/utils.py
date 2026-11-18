import openmm as mm
import openmm.app as app


def create_Mysystem(psf,ff,box_wu,nbcut,switchdist,ewaldtol,isPBC,isNVE,isoff):
    if isPBC:
        psf.setBox(box_wu[0],box_wu[1],box_wu[2])
        system = ff.createSystem(psf.topology,nonbondedMethod=app.PME,nonbondedCutoff=nbcut,switchDistance=switchdist,ewaldErrorTolerance=ewaldtol,constraints=None,rigidWater=False)
        modify_nbfix(system, nbcut, switchdist)
        for i in range(system.getNumForces()):


            myforce = system.getForce(i)


    else:
        system = ff.createSystem(psf.topology,nonbondedMethod=app.NoCutoff,constraints=None,rigidWater=False)
    if isNVE and not isoff: add_drude(system, psf)
    return system


def add_drude(system, psf):
    hyper = mm.CustomBondForce('(step(r-rhyper)*(r-rhyper)*khyper)^powh')
    hyper.addGlobalParameter('khyper', 100.0)
    hyper.addGlobalParameter('rhyper', 0.020)
    hyper.addGlobalParameter('powh', 6)
    system.addForce(hyper)
    for d in psf.drudepair_list:
        hyper.addBond(d[0], d[1], [])

def modify_nbfix(system, nbcut, switchdist):
    nbfix = [
        system.getForce(i) for i in range(system.getNumForces())
        if isinstance(system.getForce(i), mm.CustomNonbondedForce)
    ][0]
    nbfix.setNonbondedMethod(mm.CustomNonbondedForce.CutoffPeriodic)
    nbfix.setCutoffDistance(nbcut)
    nbfix.setUseSwitchingFunction(True)
    nbfix.setSwitchingDistance(switchdist)


def forcegroupify(system):

    forcegroups = {}
    for i in range(system.getNumForces()):
        force = system.getForce(i)

        force.setForceGroup(i)
        forcegroups[force] = i
    return forcegroups


def getEnergyDecomp(context, forcegroups):
    energies = {}
    for f, i in forcegroups.items():
        energies[f] = context.getState(getEnergy=True,
                                       groups=1 << i).getPotentialEnergy()
    return energies
