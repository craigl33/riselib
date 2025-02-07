"""
Palette file and other plot constants

"""

from matplotlib import colors
from riselib.plots import get_continuous_cmap


IEA_PALETTE_DICT = {'grey5': '#f2f2f2','grey10':'#e6e6e6','pl':'#b187ef', 'bl':'#49d3ff', 'tl':'#00e0e0', 'gl':'#68f394', 'yl':'#fff45a',
               'ol':'#ffb743', 'rl':'#ff684d', 'gl':'#68f394', 'yl':'#fff45a','grey40':'#949494','grey50':'#6f6f6f',
               'p':'#af6ab1', 'b':'#3e7ad3', 't':'#00ada1', 'g':'#1dbe62', 'y':'#fed324',
               'o':'#f1a800', 'r':'#e34946', 'grey20':'#afafaf', 'grey40':'949494', 'grey50':'#6f6f6f', 'black':'#000000', 'white':'#ffffff', 'iea_b':'#0044ff', 
               'iea_b50':'#80a2ff'}

IEA_PALETTE_L8 = ['rl', 'ol', 'gl', 'bl', 'pl', 'grey10', 'yl', 'tl'] ### got rid of light yellow as its a poor choice for plots.
IEA_PALETTE_D8 = ['r', 'o', 'y', 'g', 't', 'b', 'p', 'grey50']
IEA_PALETTE_16 = IEA_PALETTE_L8 + IEA_PALETTE_D8
IEA_PALETTE_14 = ['rl', 'ol', 'bl', 'gl', 'pl', 'grey10', 'y', 'tl',  'g', 't', 'b', 'grey50', 'yl', 'r', 'p']

IEA_CMAP_L8 = colors.ListedColormap([ IEA_PALETTE_DICT[c] for c in IEA_PALETTE_L8])
IEA_CMAP_D8 = colors.ListedColormap([ IEA_PALETTE_DICT[c] for c in IEA_PALETTE_D8])
IEA_CMAP_16 = colors.ListedColormap([ IEA_PALETTE_DICT[c] for c in IEA_PALETTE_16])
IEA_CMAP_14 = colors.ListedColormap([ IEA_PALETTE_DICT[c] for c in IEA_PALETTE_14])

IEA_CMAP_RdYlGn_rl = get_continuous_cmap([IEA_PALETTE_DICT['gl'], IEA_PALETTE_DICT['yl'], IEA_PALETTE_DICT['rl']])
IEA_CMAP_RdYlGn_rd = get_continuous_cmap([IEA_PALETTE_DICT['g'], IEA_PALETTE_DICT['y'], IEA_PALETTE_DICT['r']])
IEA_CMAP_RdYlGn_l = get_continuous_cmap([IEA_PALETTE_DICT['rl'], IEA_PALETTE_DICT['yl'], IEA_PALETTE_DICT['gl']])
IEA_CMAP_RdYlGn_d = get_continuous_cmap([IEA_PALETTE_DICT['r'], IEA_PALETTE_DICT['y'], IEA_PALETTE_DICT['g']])

IEA_CMAP_BlGnYlRd = get_continuous_cmap([IEA_PALETTE_DICT['bl'], IEA_PALETTE_DICT['gl'], IEA_PALETTE_DICT['yl'], IEA_PALETTE_DICT['rl']])
IEA_CMAP_BlGnYlRd_d = get_continuous_cmap([IEA_PALETTE_DICT['b'], IEA_PALETTE_DICT['g'], IEA_PALETTE_DICT['y'], IEA_PALETTE_DICT['r']])

IEA_CMAP_BlGnYlRdPu = get_continuous_cmap([IEA_PALETTE_DICT['bl'], IEA_PALETTE_DICT['gl'], IEA_PALETTE_DICT['yl'], IEA_PALETTE_DICT['rl'],  IEA_PALETTE_DICT['pl']])
IEA_CMAP_BlGnYlRdPu_d = get_continuous_cmap([IEA_PALETTE_DICT['b'], IEA_PALETTE_DICT['g'], IEA_PALETTE_DICT['y'], IEA_PALETTE_DICT['r'],  IEA_PALETTE_DICT['p']])

IEA_CMAP_YlGnBl = get_continuous_cmap([IEA_PALETTE_DICT['yl'], IEA_PALETTE_DICT['gl'], IEA_PALETTE_DICT['bl']])
IEA_CMAP_YlGnBl_d = get_continuous_cmap([IEA_PALETTE_DICT['y'], IEA_PALETTE_DICT['g'], IEA_PALETTE_DICT['b']])

IEA_CMAP_coolwarm_l = get_continuous_cmap([IEA_PALETTE_DICT['rl'], IEA_PALETTE_DICT['grey10'], IEA_PALETTE_DICT['bl']])
IEA_CMAP_coolwarm_d = get_continuous_cmap([IEA_PALETTE_DICT['r'], IEA_PALETTE_DICT['grey10'], IEA_PALETTE_DICT['b']])