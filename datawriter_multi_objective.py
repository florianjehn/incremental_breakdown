# coding: utf-8

import spotpy
import datetime
import os
class DataWriter(spotpy.database.database):
    """
    Class to write the data in csv-files
    Writes all parameter sets with their efficieny but saves only those
    time series where the efficieny is above simthreshold (default 0.0)
    """
    def __init__(self, prefix, params, begin, end, simthreshold_NS = 0.5, 
                 simthreshold_pbias = 25., simthreshold_rsr = 0.7, 
                 with_valid_data = False, shift_one_day = False):
        """
        Opens the files for the output and writes the headers
        
        simthreshold - Model effiency that must be reached so that the they 
                    are saved    
        with_calib_data: if True also the data from the validation period is 
                        written in the file. The validation time period is not
                        evaluated. The values of the objective function in the file 
                        are purely calculated from the calibration timeperiod
        """
        self.simthreshold_NS = simthreshold_NS
        self.simthreshold_pbias = simthreshold_pbias
        self.simthreshold_rsr = simthreshold_rsr
        self.with_valid_data = with_valid_data
        self.shift_one_day = shift_one_day
        # Open the simulation file
        try:
            task_id = int(os.environ.get('SGE_TASK_ID',0))
        except:
            task_id = 0
        postfix = '.%04i' % task_id if task_id else ''
        self.outfile_sim = open(prefix + '-simulation.csv' + postfix,'w')
        # Open the parameter file
        self.outfile_param = open(prefix + '-parameters.csv' + postfix,'w')
        # Make the header
        if task_id<2:
            header = 'logNS,' + "pbias," + "rsr," + ','.join(p.name for p in params)
            self.outfile_param.write(header + '\n')
            # Prolong the header with the data
            t = begin
            # add the validation period if wanted
            if self.with_valid_data:
                end = datetime.datetime(1988,12,31)
            # if the whole timeseries is shifted add one day to the header
            if self.shift_one_day:
                end = datetime.datetime(1989,1,1)
            while t <= end:
                header += ', ' + datetime.datetime.strftime(t,'%Y-%m-%d')
                t += datetime.timedelta(days=1)
            self.outfile_sim.write(header + '\n')

    def save(self, objectivefunctions, parameter, simulations):
        """
        Part of the spotpy interface
        Saves the simulation line
        """
        # Save the effiency and the parameters in outfile_param
        line=str(objectivefunctions[0])+ "," + str(objectivefunctions[1])+ "," +str(objectivefunctions[2])+ ','+str(list(parameter)).strip('[]')
        self.outfile_param.write(line+'\n')
        self.outfile_param.flush()
        # If the model run is ok save the results in outfile_sim
        if objectivefunctions[0] > self.simthreshold_NS and abs(objectivefunctions[1]) <= self.simthreshold_pbias and objectivefunctions[2] <= self.simthreshold_rsr:
            # shift the whole timeseries by one day to hit peaks better
            if self.shift_one_day:
                self.outfile_sim.write(line + "," + ',' + str(list(simulations)).strip('[]')+'\n')
                self.outfile_sim.flush()                
            else:
                self.outfile_sim.write(line + ',' + str(list(simulations)).strip('[]')+'\n')
                self.outfile_sim.flush()
            
    def finalize(self):
        """
        Part of the spotpy datawriter Interface
        """
        self.outfile_param.close()
        self.outfile_sim.close()
        
