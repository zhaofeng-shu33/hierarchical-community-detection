# run this script file concurrently with 9 threads
from cmty import GN
from bhcd import BHCD
from experiment_two_level import evaluate, InfoClusterWrapper
import bhcd_parameter

import runner
runner.NUM_TIMES = 20
METRIC = 'dendrogram_purity'

def initialize_alg(alg_name):
    if(alg_name == 'info-clustering'):
        return InfoClusterWrapper()
    elif(alg_name == 'gn'):
        return GN()
    elif(alg_name == 'bhcd'):
        return BHCDWrapper()
    else:
        raise NotImplementedError(alg_name + ' not found')

def reproduce_z_in_1(alg_name_list, metric):
    Z_IN_2 = 3
    Z_O = 1
    Z_IN_1_MIN = 10
    Z_IN_1_MAX = 15

    for alg_name in alg_name_list:
        alg = initialize_alg(alg_name)
        report_list = runner.collect_z_in_1_evaluate(alg, Z_IN_2, Z_O, Z_IN_1_MIN, Z_IN_1_MAX, metric)
        runner.save_to_file(report_list, 'z_in_1', runner.NUM_TIMES, alg_name, Z_IN_2, Z_O, Z_IN_1_MIN, Z_IN_1_MAX)

def reproduce_z_in_2(alg_name_list, metric):
    Z_IN_1 = 13
    Z_O = 0.5
    Z_IN_2_MIN = 2
    Z_IN_2_MAX = 5
    for alg_name in alg_name_list:
        alg = initialize_alg(alg_name)
        report_list = runner.collect_z_in_2_evaluate(alg, Z_IN_1, Z_O, Z_IN_2_MIN, Z_IN_2_MAX, metric)
        runner.save_to_file(report_list, 'z_in_2', runner.NUM_TIMES, alg_name, Z_IN_1, Z_O, Z_IN_2_MIN, Z_IN_2_MAX)

def reproduce_z_o(alg_name_list, metric):
    Z_IN_1 = 14
    Z_IN_2 = 3
    Z_O_MIN = 0.25
    Z_O_MAX = 2
    for alg_name in alg_name_list:
        alg = initialize_alg(alg_name)
        report_list = runner.collect_z_o_evaluate(alg, Z_IN_1, Z_IN_2, Z_O_MIN, Z_O_MAX, metric)
        runner.save_to_file(report_list, 'z_o', runner.NUM_TIMES, alg_name, Z_IN_1, Z_IN_2, Z_O_MIN, Z_O_MAX)

class BHCDWrapper(BHCD):
    def __init__(self):
        super().__init__(restart=bhcd_parameter.restart, 
            gamma=bhcd_parameter.gamma, _lambda=bhcd_parameter._lambda, delta=bhcd_parameter.delta)
            
if __name__ == '__main__':
    alg_list = ['info-clustering']
    reproduce_z_in_1(alg_list, METRIC)
    reproduce_z_in_2(alg_list, METRIC)
    reproduce_z_o(alg_list, METRIC)    
