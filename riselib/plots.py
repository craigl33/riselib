"""General math functions."""
import numpy as np


from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt

from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib import colors

CM_FROM_IN = 1/2.54


from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
import matplotlib.ticker as ticker


def apply_iea_style(ax, tick_spacing=20):
    ### Remove frame
    sns.despine(ax=ax, left=True, top=True, bottom= True, right=True)

    plt.rcParams['axes.labelsize'] = 10
    plt.rcParams['axes.titlesize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['legend.title_fontsize'] = 10
    plt.rcParams['font.family'] = 'Arial'

    
    ## Add gridlines
    plot_ax = ax.get_figure().get_axes()[0]
    plot_ax.grid(False)
    # plot_ax.grid(b=False, axis='y')
    plot_ax.grid(clip_on=False)

    ## Force y-axis tick spacing to each 20deg
#     ax.yaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    
#     plot_ax.set_yticklabels(['{}\xb0 N'.format(int(y)) if y > 0 else '{}\xb0 S'.format(int(abs(y))) if y < 0 
#                                  else '{}\xb0'.format(int(y)) for y in plot_ax.get_yticks()])


    ## Hide x-axis
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    ## Plot gridlines etc below the map
    ax.set_axisbelow(True)
    

def hex_to_rgb(value):
    '''
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values'''
    value = value.strip("#") # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_dec(value):
    '''
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values'''
    return [v/256 for v in value]

def get_continuous_cmap(hex_list, float_list=None):
    ''' creates and returns a color map that can be used in heat map figures.
        If float_list is not provided, colour map graduates linearly between each color in hex_list.
        If float_list is provided, each color in hex_list is mapped to the respective location in float_list. 
        
        Parameters
        ----------
        hex_list: list of hex code strings
        float_list: list of floats between 0 and 1, same length as hex_list. Must start with 0 and end with 1.
        
        Returns
        ----------
        colour map'''
    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    if float_list:
        pass
    else:
        float_list = list(np.linspace(0,1,len(rgb_list)))
        
    cdict = dict()
    for num, col in enumerate(['red', 'green', 'blue']):
        col_list = [[float_list[i], rgb_list[i][num], rgb_list[i][num]] for i in range(len(float_list))]
        cdict[col] = col_list
    cmp = plt.matplotlib.colors.LinearSegmentedColormap('my_cmp', segmentdata=cdict, N=256)
    return cmp


