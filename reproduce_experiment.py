# run this script file concurrently with 9 threads
from cmty import GN
from bhcd import BHCD
from experiment_two_level import evaluate, InfoClusterWrapper
import bhcd_parameter

import runner
runner.NUM_TIMES = 20

def reproduce_z_in_1(alg_list, metric):
    for alg in alg_list:
        runner.collect_z_in_1_evaluate(alg, 3, 1, 10, 15, metric)
        
def reproduce_z_in_2(alg_list, metric):
    for alg in alg_list:
        runner.collect_z_in_2_evaluate(alg, 13, 0.5, 2, 5, metric)
        
def reproduce_z_o(alg_list, metric):
    for alg in alg_list:
        runner.collect_z_o_evaluate(alg, 14, 3, 0.25, 2)

class BHCDWrapper(BHCD):
    def __init__(self):
        super().__init__(restart=bhcd_parameter.restart, 
            gamma=bhcd_parameter.gamma, _lambda=bhcd_parameter._lambda, delta=bhcd_parameter.delta)
            
if __name__ == '__main__':
    alg_list = [InfoClusterWrapper(), GN(), BHCDWrapper()]
    metric = 'norm_rf'
    reproduce_z_in_1(alg_list, metric)
    reproduce_z_in_2(alg_list, metric)
    reproduce_z_o(alg_list, metric)    