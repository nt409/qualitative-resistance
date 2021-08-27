from model.utils import Fungicide, growth, senescence
from model.params import PARAMS



class BaseSystem:
    def __init__(self, fungicide_params) -> None:
        if fungicide_params is None:
            omega_1 = PARAMS.omega_1
            omega_2 = PARAMS.omega_2
            
            theta_1 = PARAMS.theta_1
            theta_2 = PARAMS.theta_2

            delta_1 = PARAMS.delta_1
            delta_2 = PARAMS.delta_2

        else:
            omega_1 = fungicide_params['omega_1']
            omega_2 = fungicide_params['omega_2']
            
            theta_1 = fungicide_params['theta_1']
            theta_2 = fungicide_params['theta_2']

            delta_1 = fungicide_params['delta_1']
            delta_2 = fungicide_params['delta_2']

        self.fcide1 = Fungicide(omega_1, theta_1, delta_1)
        self.fcide2 = Fungicide(omega_2, theta_2, delta_2)

        self.growth_fn = growth
        self.senescence_fn = senescence
    


class ODESystem(BaseSystem):
    def __init__(self, fungicide_params) -> None:
        super().__init__(fungicide_params)


    def system(self, t, y):
        
        S,ER,ERS,ESR,ES,IR,IRS,ISR,IS,R,PR,PRS,PSR,PS,conc_1,conc_2 = y

        A = S + ER + ERS + ESR + ES + IR + IRS + ISR + IS + R

        dydt = [self.growth_fn(A,t)
             - (self.senescence_fn(t))*S
             -  S * (PARAMS.beta/A) * (
                  (IR + PR)
                + (IRS + PRS) * (self.fcide2.effect(conc_2))
                + (ISR + PSR) * (self.fcide1.effect(conc_1))
                + (IS  +  PS) * (self.fcide1.effect(conc_1)) * (self.fcide2.effect(conc_2))),
            
            S*(PARAMS.beta/A) * (IR + PR) - (self.senescence_fn(t)) * ER  - PARAMS.gamma * ER,
            S*(PARAMS.beta/A) * (IRS + PRS) * (self.fcide2.effect(conc_2)) - (self.senescence_fn(t)) * ERS - PARAMS.gamma * (self.fcide2.effect(conc_2)) * ERS,
            S*(PARAMS.beta/A) * (ISR + PSR) * (self.fcide1.effect(conc_1)) - (self.senescence_fn(t)) * ESR - PARAMS.gamma * (self.fcide1.effect(conc_1)) * ESR,
            S*(PARAMS.beta/A) * (IS  +  PS) * (self.fcide1.effect(conc_1)) * (self.fcide2.effect(conc_2)) - (self.senescence_fn(t)) * ES  - PARAMS.gamma * (self.fcide1.effect(conc_1))*(self.fcide2.effect(conc_2)) * ES,
            
            PARAMS.gamma * ER   -  PARAMS.mu * IR,
            PARAMS.gamma * (self.fcide2.effect(conc_2)) * ERS  -  PARAMS.mu * IRS,
            PARAMS.gamma * (self.fcide1.effect(conc_1)) * ESR  -  PARAMS.mu * ISR,
            PARAMS.gamma * (self.fcide1.effect(conc_1)) * (self.fcide2.effect(conc_2)) * ES   -  PARAMS.mu * IS,
            
            PARAMS.mu * (IR + IRS + ISR + IS)   +  (self.senescence_fn(t)) * (S + ER + ERS + ESR + ES),
            
            - PARAMS.nu * PR,
            - PARAMS.nu * PRS,
            - PARAMS.nu * PSR,
            - PARAMS.nu * PS,
            
            - self.fcide1.delta * conc_1,
            - self.fcide2.delta * conc_2
            ]

        return dydt
