"""
Analyse the parameter scan output
"""
import pandas as pd

from ..config import config_rand
from ..functions import PostProcess, get_PS_rand_str


def main(config):
    
    par_str = get_PS_rand_str(config)

    PP = PostProcess(par_str)

    PP.get_maximum_along_contour_df()
    
    PP.analyse_max_contour_df()

    PP.analyse_failed()
    
    PP.which_runs_worked_max_cont()

    PP.re_run_failures(NDoses=51, failed_run_indices=[12])
        
    # PP.check_high_or_low_dose()



if __name__=="__main__":
    main(config_rand)