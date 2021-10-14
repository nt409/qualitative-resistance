import numpy as np
from math import floor
from model.config_classes import SingleConfig

from model.params import PARAMS
from model.simulator import RunSingleTactic
from model.utils import get_rfd



def get_alt_scan_params(n_its, index):
    
    rfs = np.logspace(-10, -4, n_its)
    omegas = np.linspace(0.4, 1, n_its)
    thetas = np.linspace(4,  12, n_its)


    ii = int( floor(index/(n_its**2)) )
    jj = int( floor((index % 25)/(n_its)) )
    kk = int( index % n_its )

    rf1 = rfs[ii]
    rf2 = 1e-5
    om1 = omegas[jj]
    om2 = 1
    thet1 = thetas[kk]
    thet2 = 9.6

    rfd = get_rfd(rf1, rf2)
    
    primary_inoc = dict(RR=rfd, RS=rf1, SR=rf2, SS=1-rf1-rf2-rfd)

    fcide_parms = dict(
        omega_1 = om1,
        omega_2 = om2,
        theta_1 = thet1,
        theta_2 = thet2,
        delta_1 = PARAMS.delta_1,
        delta_2 = PARAMS.delta_2,
        )
    
    return primary_inoc, fcide_parms, ii, jj, kk


def get_alt_scan_params_rand(index):
    np.random.seed(index)
    is_invalid = True
    while is_invalid:
        rf1 = 10**(np.random.uniform(-10,-4))
        rf2 = 10**(np.random.uniform(-10,-4))
        rfd = 10**(np.random.uniform(-15,-4))
        
        om1 = np.random.uniform(0.4, 1)
        om2 = np.random.uniform(0.4, 1)
        thet1 = np.random.uniform(4, 12)
        thet2 = np.random.uniform(4, 12)
        delta_factor_1 = np.random.uniform(1/3,3)
        delta_factor_2 = np.random.uniform(1/3,3)

        primary_inoc = dict(RR=rfd, RS=rf1, SR=rf2, SS=1-rf1-rf2-rfd)

        fcide_parms = dict(
            omega_1 = om1,
            omega_2 = om2,
            theta_1 = thet1,
            theta_2 = thet2,
            delta_1 = PARAMS.delta_1*delta_factor_1,
            delta_2 = PARAMS.delta_2*delta_factor_2,
            )

        conf_a = SingleConfig(1, None, None, 1,1,1,1)
        conf_a.load_saved = False
        conf_a.primary_inoculum = primary_inoc
        conf_a.add_string()

        yld = RunSingleTactic(fcide_parms).run(conf_a).yield_vec[0]

        if yld>95:
            is_invalid = False 

    return primary_inoc, fcide_parms