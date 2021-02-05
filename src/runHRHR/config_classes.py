class BaselineConfig:
    def __init__(self, n_years, rp1, rp2, primary_inoculum, within_season_before):

        self.load_saved = True

        self.folder_save_run = '../outputs/saved_runs/'
        
        self.n_years = n_years

        self.res_props = dict(
            f1 = rp1,
            f2 = rp2
            )

        self.primary_inoculum = primary_inoculum

        self.within_season_before = within_season_before

        self.save_string = f"n_y={n_years}_rps={rp1},{rp2}_{str(primary_inoculum)[0]}_{str(within_season_before)[0]}"



class SingleConfig(BaselineConfig):
    def __init__(self,
                n_years,
                rp1,
                rp2,
                d11,
                d12,
                d21,
                d22,
                primary_inoculum=None,
                within_season_before=True
                ):
        
        super().__init__(n_years, rp1, rp2, primary_inoculum, within_season_before)
        
        self.fung1_doses = dict(
            spray_1 = [d11]*n_years,
            spray_2 = [d12]*n_years
            )

        self.fung2_doses = dict(
            spray_1 = [d21]*n_years,
            spray_2 = [d22]*n_years
            )
        
        self.add_string()

    def add_string(self):
        d11 = self.fung1_doses['spray_1'][0]
        d12 = self.fung1_doses['spray_2'][0]
        d21 = self.fung2_doses['spray_1'][0]
        d22 = self.fung2_doses['spray_2'][0]

        filename = f"single/{self.save_string}_doses={d11},{d12},{d21},{d22}"
        self.config_string = self.folder_save_run + filename.replace(".", ",") + ".pickle"



class GridConfig(BaselineConfig):
    def __init__(self,
            n_years,
            rp1,
            rp2,
            n_doses,
            primary_inoculum=None,
            within_season_before=True
            ):

        super().__init__(n_years, rp1, rp2, primary_inoculum, within_season_before)
        
        self.strategy = 'mix'

        self.n_doses = n_doses

        self.add_string()

    def add_string(self):
        filename = f"grid/{self.save_string}_n_d={self.n_doses},{self.strategy}"
        self.config_string = self.folder_save_run + filename.replace(".", ",") + ".pickle"