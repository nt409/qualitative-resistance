from model.utils import Fungicide, growth, senescence
from model.params import PARAMS



class BaseSystem:
    def __init__(self, fungicide_params) -> None:
        self.pars = PARAMS

        if fungicide_params is None:
            omega_1 = self.pars.omega_1
            omega_2 = self.pars.omega_2
            
            theta_1 = self.pars.theta_1
            theta_2 = self.pars.theta_2

            delta_1 = self.pars.delta_1
            delta_2 = self.pars.delta_2

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

        pars = self.pars

        S,ER,ERS,ESR,ES,IR,IRS,ISR,IS,R,PR,PRS,PSR,PS,conc_1,conc_2 = y

        A = S + ER + ERS + ESR + ES + IR + IRS + ISR + IS + R

        dydt = [self.growth_fn(A,t)
             - (self.senescence_fn(t))*S
             -  S * (pars.beta/A) * (
                  (IR + PR)
                + (IRS + PRS) * (self.fcide2.effect(conc_2))
                + (ISR + PSR) * (self.fcide1.effect(conc_1))
                + (IS  +  PS) * (self.fcide1.effect(conc_1)) * (self.fcide2.effect(conc_2))),
            
            S*(pars.beta/A) * (IR + PR) - (self.senescence_fn(t)) * ER  - pars.gamma * ER,
            S*(pars.beta/A) * (IRS + PRS) * (self.fcide2.effect(conc_2)) - (self.senescence_fn(t)) * ERS - pars.gamma * (self.fcide2.effect(conc_2)) * ERS,
            S*(pars.beta/A) * (ISR + PSR) * (self.fcide1.effect(conc_1)) - (self.senescence_fn(t)) * ESR - pars.gamma * (self.fcide1.effect(conc_1)) * ESR,
            S*(pars.beta/A) * (IS  +  PS) * (self.fcide1.effect(conc_1)) * (self.fcide2.effect(conc_2)) - (self.senescence_fn(t)) * ES  - pars.gamma * (self.fcide1.effect(conc_1))*(self.fcide2.effect(conc_2)) * ES,
            
            pars.gamma * ER   -  pars.mu * IR,
            pars.gamma * (self.fcide2.effect(conc_2)) * ERS  -  pars.mu * IRS,
            pars.gamma * (self.fcide1.effect(conc_1)) * ESR  -  pars.mu * ISR,
            pars.gamma * (self.fcide1.effect(conc_1)) * (self.fcide2.effect(conc_2)) * ES   -  pars.mu * IS,
            
            pars.mu * (IR + IRS + ISR + IS)   +  (self.senescence_fn(t)) * (S + ER + ERS + ESR + ES),
            
            - pars.nu * PR,
            - pars.nu * PRS,
            - pars.nu * PSR,
            - pars.nu * PS,
            
            - self.fcide1.delta * conc_1,
            - self.fcide2.delta * conc_2
            ]

        return dydt
