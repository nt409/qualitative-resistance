import plotly.colors as pltly_clrs

E_cols = pltly_clrs.n_colors("rgb(0,0,255)", "rgb(255,255,255)", 5, colortype="rgb")[:4]
        
I_cols = pltly_clrs.n_colors("rgb(255,0,0)", "rgb(255,255,255)", 5, colortype="rgb")[:4]


ATTRS_DICT = {
    'S': dict(color='limegreen', dash='solid', name='Susceptible', legendgrp="S"),
    'R': dict(color='rgb(100,100,100)', dash='solid', name='Removed', legendgrp="S"),
    
    'ERR': dict(color=E_cols[0], dash='dot', name='Exposed (<i>rr</i>)', legendgrp="E"),
    'ERS': dict(color=E_cols[1], dash='dash', name='Exposed (<i>rs</i>)', legendgrp="E"),
    'ESR': dict(color=E_cols[2], dash='dashdot', name='Exposed (<i>sr</i>)', legendgrp="E"),
    'ESS': dict(color=E_cols[3], dash='solid', name='Exposed (<i>ss</i>)', legendgrp="E"),

    'IRR': dict(color=I_cols[0], dash='dot', name='Infectious (<i>rr</i>)', legendgrp="I"),
    'IRS': dict(color=I_cols[1], dash='dash', name='Infectious (<i>rs</i>)', legendgrp="I"),
    'ISR': dict(color=I_cols[2], dash='dashdot', name='Infectious (<i>sr</i>)', legendgrp="I"),
    'ISS': dict(color=I_cols[3], dash='solid', name='Infectious (<i>ss</i>)', legendgrp="I"),

    'fung_1': dict(color='turquoise', dash='solid', name='Fungicide <i>A</i>', legendgrp="F"),
    'fung_2': dict(color='magenta', dash='dot', name='Fungicide <i>B</i>', legendgrp="F"),
}


LABEL_COLOR = "rgb(110,110,110)"
LIGHT_GREY_TEXT = "rgb(150,150,150)"
FADED_LINE_COLOR = "rgba(0,0,0,0.5)"


NULL_HEATMAP_COLOUR = "rgb(100, 100, 100)"

STRAIN_ATTRS = dict(SS=dict(color="rgb(34,140,34)", dash="dot", longname='Double sensitive', abbrv="SS"),
                RS=dict(color="rgb(20,20,200)", dash="dash", longname='Single resistant (RS)', abbrv="RS"),
                SR=dict(color="rgb(200,20,20)", dash="dashdot", longname='Single resistant (SR)', abbrv="SR"),
                RR=dict(color="rgb(50,50,50)", dash="solid", longname='Double resistant', abbrv="RR"),
                )

TITLE_MAP = dict(
    LTY = "Lifetime yield",
    TY = "Total yield",
    FY = "Effective life",
    econ = "Economic life",
    )


# default is half page
PLOT_WIDTH = 600
PLOT_HEIGHT = 400

FULL_PAGE_WIDTH = 800