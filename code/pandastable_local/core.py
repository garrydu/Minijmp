import os
#########################
from .core_orig import statusBar as SBar_orig
from .core_orig import Table as Table_orig
from . import config

themes = {
    'dark': {
        'cellbackgr': 'gray25',
        'grid_color': 'gray50',
        'textcolor': '#f2eeeb',
        'rowselectedcolor': '#ed9252',
        'colselectedcolor': '#3d65d4'},
    'bold': {
        'cellbackgr': 'white',
        'grid_color': 'gray50',
        'textcolor': 'black',
        'rowselectedcolor': 'yellow',
        'colselectedcolor': '#e4e3e4'},
    'default': {
        'cellbackgr': '#F4F4F3',
        'grid_color': '#ABB1AD',
        'textcolor': 'black',
        'rowselectedcolor': '#E4DED4',
        'colselectedcolor': '#e4e3e4'}}

loading_path = os.getcwd()
parent_path = os.path.dirname(loading_path)
config_path = os.path.join(parent_path, 'log')
logfile = os.path.join(config_path, 'error.log')
if not os.path.exists(config_path):
    os.mkdir(config_path)


class Table(Table_orig):
    def init_reserved(self):
        print("loading_path", os.getcwd())
        self.currentdir = os.path.join(parent_path, 'sample_data')
        print("current dir", self.currentdir)
        self.logfile = logfile
        return

    def loadPrefs(self, prefs=None):
        """Load preferences from defaults"""
        # Added to change default dir
        # This loadPrefs seems only be loaded when init
        self.init_reserved()
        ###
        options = config.load_options()
        config.apply_options(options, self)
        return


class statusBar(SBar_orig):
    """Status bar class"""
    pass
