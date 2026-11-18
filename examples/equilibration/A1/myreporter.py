import openmm as mm
import openmm.unit as unit
import os


class RestartReporter(object):
    def __init__(self, reportInterval, fname, jobname):
        self._reportInterval = reportInterval
        os.makedirs("./restart", exist_ok=True)
        self.file = open(fname, "w")
        self.nrestart = 0
        self.jobname = jobname

    def __del__(self):
        self.file.close()

    def describeNextReport(self, simulation):
        steps = self._reportInterval - simulation.currentStep%self._reportInterval
        return (steps, True, True, False, True, False)

    def report(self, simulation, state):
        self.nrestart += 1
        time = state.getTime()
        with open('./restart/' + self.jobname + '-' + '%d'%(self.nrestart) + '.rst', 'w') as f:
            f.write(mm.XmlSerializer.serialize(state))
        self.file.write("%f %s \n"%(time.value_in_unit(unit.picosecond), './restart/' + self.jobname + '-' + '%d'%(self.nrestart) + '.rst'))
        self.file.flush()
