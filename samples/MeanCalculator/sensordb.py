import hashlib
import logging
import gupt

from datadriver.csvdriver import CSVDriver
from computedriver.computedriver import GuptComputeDriver

# Data Provider Code
def ART_filter(records):
    if records and records[0].find('ART') != -1:
        return True
    return False

def ART_transformer(records):
    return [int(hashlib.sha1(records[0]).hexdigest(), 16)] + map(float, records[1:])


def get_reader():
    reader = CSVDriver(filter=ART_filter, transformer=ART_transformer, delimiter=' ')
    reader.set_data_source('sensordb.txt')
    reader.set_input_bounds([[0, 0], [0, 1]])
    reader.set_sensitiveness([False, True])
    return reader

# Compute Provider Code
class MeanComputer(gupt.GuptComputeDriver):
    def initialize(self):
        self.total = 0
        self.num_records = 0

    def execute(self, record):
        if not record or len(record) != 2:
            return

        self.total += record[1]
        self.num_records += 1

    def finalize(self):
        return self.total / self.num_records

    def get_output_bounds(self, first_quartile=None, third_quartile=None):
        if not first_quartile or not third_quartile:
            return [0], [1]
        return [first_quartile[1]], [third_quartile[1]]


def run_expt(epsilon, gamma):
    for blocker in gupt.GuptRunTime.get_data_blockers():
        reader = get_reader()
        runtime = gupt.GuptRunTime(MeanComputer, reader, float(epsilon), blocker_name=blocker, blocker_args=gamma)
        print runtime.start()
        
        reader = get_reader()
        runtime = gupt.GuptRunTime(MeanComputer, reader, float(epsilon), blocker_name=blocker, blocker_args=gamma)
        print runtime.start_windsorized()

if __name__ == '__main__':
    epsilon_vals = [1, 5]
    gamma_vals = range(1, 10)
    REPETITIONS = 20

    for epsilon in epsilon_vals:
        for gamma in gamma_vals:
            for index in range(REPETITIONS):
                run_expt(epsilon, gamma)

    reader = get_reader()
    runtime = gupt.GuptRunTime(MeanComputer, reader, 1.0)
    print runtime.start_nonprivate()
    del runtime
    del reader
    
