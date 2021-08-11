import numpy as np
from math import ceil, floor
from scipy.integrate import simps, ode
import pickle
import os
import copy
from tqdm import tqdm
import itertools

from .params import PARAMS
from .utils import res_prop_calculator, yield_calculator, \
    SelectionFinder, FungicideStrategy, object_dump
from .ode_system import ODESystem
from .config_classes import SingleConfig
from .outputs import GridTacticOutput, SimOutput, SingleTacticOutput






class Simulator:
    def __init__(self, fungicide_params):
        self.ode_sys = ODESystem(fungicide_params)
        self.selection_finder = SelectionFinder
        self.res_prop_finder = res_prop_calculator
        self.yield_finder = yield_calculator


    def run(self, fung1_doses, fung2_doses, primary_inoc):

        self.primary_inoc = primary_inoc
        self.fung1_doses = fung1_doses
        self.fung2_doses = fung2_doses

        self.output = SimOutput(PARAMS)

        self._find_solution()
        
        
        final_res_dict, end_freqs = self.res_prop_finder(self.output.states)

        selection = self.selection_finder(self.primary_inoc, final_res_dict).sel

        self.output.final_res_vec_dict = final_res_dict
        self.output.end_freqs = end_freqs
        self.output.selection = selection
        
        self.output.delete_unnecessary_vars()

        return self.output



    def _find_solution(self):

        sol = ode(self.ode_sys.system).set_integrator('dopri5', nsteps=PARAMS.nstepz)
        
        self._solve_ode(sol)

        y_yield = self.output.y_yield
        t_yield = self.output.t_yield

        self.output.yield_val = self.yield_finder(y_yield, t_yield)




    def _solve_ode(self, sol):
        """
        Solves the ODE in 4 stages:
        
        - before first spray
        - spray 1
        - spray 2
        - yield period (end of season)

        """
        y0_new = None
        
        list_of_tvs = self.output.t_vecs
        segments = self.output.seg_names

        for time_vec, segment in zip(list_of_tvs, segments):

            y0_new = self._get_y0_this_segment(segment, sol)

            y_array = self._solve_for_y_this_segment(y0_new, sol, time_vec)

            if segment=="yield":
                # final segment - need to add final time
                # rather than leave it for start condition 
                # of next segment

                y_array[:,-1] = sol.y

                self.output.get_yield_contributing_y(y_array)

                y_out = y_array

            else:
                y_out = y_array[:,:-1]

            self.output.states.update_y(y_out)








    def _get_y0_this_segment(self, segment, sol):
        
        if segment=="start":
            PI = self.primary_inoc

            y0_new = [PARAMS.S_0] + [0]*9 + [PI['RR'], 
                                                PI['RS'],
                                                PI['SR'],
                                                PI['SS']] + [0]*2

        else:
            y0_new = sol.y

            if segment in ["spray_1", "spray_2"]:
                y0_new[PARAMS.fung_1_ind] = y0_new[PARAMS.fung_1_ind] + self.fung1_doses[segment]
                y0_new[PARAMS.fung_2_ind] = y0_new[PARAMS.fung_2_ind] + self.fung2_doses[segment]
        
        return y0_new
    
    
    
    @staticmethod
    def _solve_for_y_this_segment(y0_new, sol, time_vec):
        
        sol.set_initial_value(y0_new, time_vec[0])

        y_array = np.zeros((PARAMS.no_variables, len(time_vec)))

        for index, t in enumerate(time_vec[1:]):
            if sol.successful():
                y_array[:,index] = sol.y
                sol.integrate(t)
            else:
                raise RuntimeError('ode solver unsuccessful')
        
        return y_array







class SimulatorDiseaseFree:
    def __init__(self, fungicide_params):
        self.ode_sys = ODESystem(fungicide_params)
        self.yield_finder = yield_calculator
        



    def run(self):
        y0 = [PARAMS.S_0] + [0]*(PARAMS.no_variables-1)

        sol = ode(self.ode_sys.system).set_integrator('dopri5', nsteps=PARAMS.nstepz)
        
        t_not_yield, t_yield = self._get_dis_free_t_vecs()

        _ = self._solve_for_y_this_segment(y0, sol, t_not_yield)

        y_yield = self._solve_for_y_this_segment(sol.y, sol, t_yield)

        y_yield[:, -1] = sol.y

        dis_free_yield = yield_calculator(y_yield[0,:], t_yield)

        return dis_free_yield



    @staticmethod
    def _get_dis_free_t_vecs():
        t0 = PARAMS.T_emerge
        t1 = PARAMS.T_GS61
        t2 = PARAMS.T_GS87
        
        n1 = 1 + (t1-t0)/PARAMS.dt
        n2 = 1 + (t2-t1)/PARAMS.dt
        
        c1 = ceil(n1-0.5)
        c2 = ceil(n2-0.5)
        
        t_not_yield = np.linspace(t0,t1,c1)
        t_yield = np.linspace(t1,t2,c2)
        
        return t_not_yield, t_yield
   
    
    
    @staticmethod
    def _solve_for_y_this_segment(y0_new, sol, time_vec):
        
        sol.set_initial_value(y0_new, time_vec[0])

        y_array  = np.zeros((PARAMS.no_variables, len(time_vec)))

        for index, t in enumerate(time_vec[1:]):
            if sol.successful():
                y_array[:,index] = sol.y
                sol.integrate(t)
            else:
                raise RuntimeError('ode solver unsuccessful')
        
        return y_array







# * End of Sim cls











class RunSingleTactic:
    def __init__(self, fcide_parms=None):

        self.sim = Simulator(fcide_parms)
        
        df_sim = SimulatorDiseaseFree(fcide_parms)

        self.dis_free_yield = df_sim.run()

        self.yield_stopper = 95

        self.PATHOGEN_STRAIN_NAMES = ['RR', 'RS', 'SR', 'SS']




    def run(self, conf):
        """
        Run HRHR model for one strategy
        """
        
        self.filename = conf.config_string

        if conf.load_saved:
            loaded_run = self._load_single_tactic()
            if loaded_run is not None:
                return loaded_run


        self.n_years = len(conf.fung1_doses['spray_1'])

        self.output = SingleTacticOutput(PARAMS, conf,
                                            self.PATHOGEN_STRAIN_NAMES,
                                            self.n_years, self.dis_free_yield)

        self._set_first_year_start_freqs(conf)

        self._loop_over_years(conf)

        self.output.delete_unnecessary_vars()
        
        self._save_run_if_was_single()
        
        return self.output

    





    def _set_first_year_start_freqs(self, conf):
        primary_inoculum = conf.primary_inoculum
        
        if primary_inoculum is None:
            primary_inoculum = self._primary_calculator(conf,
                                                conf.res_props['f1'], 
                                                conf.res_props['f2'])

        self.output.update_start_freqs(primary_inoculum, 0)


    
    def _loop_over_years(self, conf):
        for yr in range(self.n_years):
            # stop the solver after we drop below threshold
            if not (yr>0 and self.output.yield_vec[yr-1]<self.yield_stopper):
                self._run_single_year(conf, yr)
        
        if min(self.output.yield_vec)>PARAMS.yield_threshold:
            self.output.failure_year = -1




    def _run_single_year(self, conf, yr):
        
        fung1_doses = self._get_dose_this_fung_this_yr(conf.fung1_doses, yr)
        fung2_doses = self._get_dose_this_fung_this_yr(conf.fung2_doses, yr)
        
        model_inoc_in = self._get_initial_density(yr)
        
        sim_out = self.sim.run(fung1_doses, fung2_doses, model_inoc_in)

        self.output.add_new_sim_output(sim_out, yr)

        self._set_next_year_start_freqs(conf, sim_out, yr+1)
    



    def _set_next_year_start_freqs(self, conf, sim_out, next_yr):

        freqs_out = sim_out.end_freqs

        # sex/asex after each season
        res_prop_1_end = freqs_out['RR'] + freqs_out['RS']
        res_prop_2_end = freqs_out['RR'] + freqs_out['SR']

        # get next year's primary inoc - including SR step
        next_year_vals = self._primary_calculator(conf,
                                                    res_prop_1_end,
                                                    res_prop_2_end,
                                                    freqs_out)

        self.output.update_start_freqs(next_year_vals, next_yr)







    @staticmethod
    def _get_dose_this_fung_this_yr(dose_vec, yr):
        return dict(spray_1 = dose_vec['spray_1'][yr],
                    spray_2 = dose_vec['spray_2'][yr])



    def _get_initial_density(self, yr):
        out = {}
        for key in self.PATHOGEN_STRAIN_NAMES:
            out[key] = PARAMS.init_den*self.output.start_freqs[key][yr]
        return out

    

    @staticmethod
    def _primary_calculator(
                conf,
                res_prop_1,
                res_prop_2,
                proportions=None,
                ):
        
        # is_mixed_sex = conf.is_mixed_sex
        sex_prop = conf.sex_prop

        sex = dict(
            RR = res_prop_1*res_prop_2,
            RS = res_prop_1*(1-res_prop_2),
            SR = (1-res_prop_1)*res_prop_2,
            SS = (1-res_prop_1)*(1-res_prop_2)
            )

        if proportions is None:
            return sex

        else:
            asex = proportions
            out = {}
            for key in sex.keys():
                out[key] = sex_prop*sex[key] + (1 - sex_prop)*asex[key]
            
            return out
    




    # load/save

    def _load_single_tactic(self):
        filename = self.filename
        
        if os.path.isfile(filename) and "single" in filename:
            loaded_run = pickle.load(open(filename, 'rb'))
            return loaded_run



    def _save_run_if_was_single(self):
        if "single" in self.filename:
            object_dump(self.filename, self.output)



# * End of RunSingleTactic





















class RunGrid:
    def __init__(self, fcide_parms=None):
        self.sing_tact = RunSingleTactic(fcide_parms)
        self.fung_strat = FungicideStrategy



    def run(self, Conf):

        self.filename = Conf.config_string
        
        if Conf.load_saved:
            loaded_run = self._load_multi_tactic(self.filename)
            if loaded_run is not None:
                return loaded_run

        self.output = GridTacticOutput(Conf.n_doses, Conf.n_years)

        self._run_the_grid(Conf)

        self._save_grid()

        return self.output



    def _run_the_grid(self, Conf):
        fs = self.fung_strat(Conf.strategy, Conf.n_years)
        
        for f1_ind in tqdm(range(Conf.n_doses)):
            for f2_ind in range(Conf.n_doses):

                Conf.fung1_doses, Conf.fung2_doses = fs.get_grid_doses(f1_ind,
                                                        f2_ind, Conf.n_doses)

                one_tact_output =  self.sing_tact.run(Conf)
                
                self._post_process_multi(one_tact_output, f1_ind, f2_ind, Conf)





    
    def _post_process_multi(self, data_this_dose, f1_ind, f2_ind, Conf):

        self.output.LTY[f1_ind,f2_ind] = self._lifetime_yield(data_this_dose.yield_vec, data_this_dose.failure_year)

        self.output.TY[f1_ind,f2_ind] = self._total_yield(data_this_dose.yield_vec)

        self.output.FY[f1_ind,f2_ind] = data_this_dose.failure_year

        self.output.yield_array[f1_ind,f2_ind,:] = data_this_dose.yield_vec


        self.output.update_dicts_of_arrays(data_this_dose, f1_ind, f2_ind)

        



    @staticmethod
    def _lifetime_yield(Y_vec, F_y):
        return sum(Y_vec[:(F_y+1)])/100




    @staticmethod
    def _total_yield(Y_vec):
        return sum(Y_vec)/100





    @staticmethod
    def _load_multi_tactic(filename):
        if os.path.isfile(filename):
            loaded_run = pickle.load(open(filename, 'rb'))
            return loaded_run
        else:
            return None



    def _save_grid(self):
        object_dump(self.filename, self.output)




# End of RunGrid class










# # * changing doses fns

def get_SR_by_doses(doses, freqs):
    outputs = {}
    for dose, rf in itertools.product(doses, freqs):
        ConfigSingleRun = SingleConfig(1, rf, rf, dose, dose, dose, dose)
        output = RunSingleTactic().run(ConfigSingleRun)
        outputs[f"dose={dose},rf={rf}"] = output


    conf_str = ConfigSingleRun.config_string_img
    str_freqs = [str(round(f,2)) for f in freqs]
    str_doses = [str(round(d,2)) for d in doses]

    middle_string = ("=" + ",_".join(str_freqs) +
                "_doses=" + ",_".join(str_doses))
    middle_string = middle_string.replace(".", ",")

    conf_str = ("=".join(conf_str.split("=")[0:2]) + 
            middle_string + conf_str.split("=")[-1])

    
    return outputs, conf_str

# * End of changing doses fns
