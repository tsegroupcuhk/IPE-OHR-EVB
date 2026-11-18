import openmm as mm
import openmm.app as app
import openmm.unit as unit
import numpy as np
from datetime import datetime as dtt
import evb.utils as utils
from evb.evb import EVBSystem
from myreporter import RestartReporter


starttime = dtt.now()
print(starttime)


box=np.array([3.132, 3.132, 10.])
box_wu = box*unit.nanometer
nbcut = 1.56 * unit.nanometer
switchdist = 1.46 * unit.nanometer

path = "inits"
path_to_xml = "inits"
jobname = 'nvtrun'
prename = 'restart' 

vfile = open("%s/V.txt"%(path),"r")
vdata = vfile.readlines()
vfile.close()
V = float(vdata[0].split()[0])

temp = 300

timestep = 0.5 * unit.femtoseconds
ewaldtol = 1e-5
isNVE = False
isPBC = True
nprint_restart = 100000
nprint = 100
restart = True
nstep = int(5e6)


print("###reading topology###")
psf1 = app.CharmmPsfFile("./inits/m1.psf")
psf2 = app.CharmmPsfFile("./inits/m2.psf")
psf3 = app.CharmmPsfFile("./inits/off.psf")
ff1 = app.ForceField("%s/toppar.xml"%(path_to_xml))
ff2 = app.ForceField("%s/toppar.xml"%(path_to_xml))
ff3 = app.ForceField("%s/toppar.xml"%(path_to_xml), "%s/off.xml"%(path_to_xml))

sub1=utils.create_Mysystem(psf1,ff1,box_wu,nbcut,switchdist,ewaldtol,isPBC,isNVE,isoff=False)
sub2=utils.create_Mysystem(psf2,ff2,box_wu,nbcut,switchdist,ewaldtol,isPBC,isNVE,isoff=False)
suboff=utils.create_Mysystem(psf3,ff3,box_wu,nbcut,switchdist,ewaldtol,isPBC,isNVE,isoff=True)

print ("###create EVBsystem###")

evbsys = EVBSystem(sub1, sub2, suboff, True)
system = evbsys.mergeSystem(V)


print ("###Setting up integrator###")
if isNVE:
    integrator = mm.DrudeSCFIntegrator(timestep)
    integrator.setMinimizationErrorTolerance(1e-5)
else:
    integrator = mm.DrudeLangevinIntegrator(temp*unit.kelvin, 5/unit.picosecond, 1*unit.kelvin, 20/unit.picosecond, timestep)
    integrator.setMaxDrudeDistance(0.02)
    integrator.setConstraintTolerance(1e-06)


platname = 'CUDA'
platform = mm.Platform.getPlatformByName(platname)
prop = dict(CudaPrecision='mixed')


fgrps = utils.forcegroupify(system)

simulation = app.Simulation(psf2.topology, system, integrator, platform, prop)

crd = app.CharmmCrdFile('inits/m2.crd')
simulation.context.setPositions(crd.positions)

if not restart:
    simulation.minimizeEnergy()
    simulation.context.setVelocitiesToTemperature(temp*unit.kelvin)
    simulation.context.computeVirtualSites()    
else:

    print ('###reading restart file###')
    print('#Startting from restart.rst')
    simulation.loadState('restart.rst')
    simulation.context.setTime(0)

print ("######setting up reporters######")
dcd=app.DCDReporter(jobname+'.dcd', nprint)
simulation.reporters.append(dcd)
simulation.reporters.append(app.StateDataReporter(jobname+'.log',nprint,time=True, kineticEnergy=True, potentialEnergy=True,totalEnergy=True, temperature=True, speed=True, separator=','))
simulation.reporters.append(RestartReporter(nprint_restart,'./restart/' + jobname + '-restart.log',jobname))

print ("###initial energies###")
state = simulation.context.getState(getPositions=True,getEnergy=True)

print('PE', state.getPotentialEnergy().value_in_unit(unit.kilojoules_per_mole),'kJ/mol')

for k, v in utils.getEnergyDecomp(simulation.context, fgrps).items():
    print(k.__class__.__name__, v.value_in_unit(unit.kilojoules_per_mole),'kJ/mol')


simulation.step(nstep)

cvforce = [system.getForce(i) for i in range(system.getNumForces()) if isinstance(system.getForce(i), mm.CustomCVForce)][0]
cvvalues = cvforce.getCollectiveVariableValues(simulation.context)
E11= cvvalues[0];E22=cvvalues[1];E12=cvvalues[2]


print("E11 = " + str(E11))
print("E22 = " + str(E22))
print("E12 = " + str(E12))


state = simulation.context.getState(getPositions=True,getVelocities=True,getEnergy=True)
with open(prename+'-current.rst', 'w') as f:
    f.write(mm.XmlSerializer.serialize(state))

endtime = dtt.now()
print(endtime-starttime)
