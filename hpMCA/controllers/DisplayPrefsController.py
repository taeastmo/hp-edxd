# -*- coding: utf8 -*-

# DISCLAIMER
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE 
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE 
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE 
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER 
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, 
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE 
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.




from utilities.hpMCAutilities import compare
from utilities.hpMCAutilities import Preferences
from hpMCA.widgets.DisplayPrefsWidget import DisplayPreferencesWidget
from PyQt5.QtCore import QObject
import json
from utilities.hpMCAutilities import displayErrorMessage, json_compatible_dict, readconfig


class DisplayPreferences(Preferences):
    def __init__(self, plot_widget):
        self.plot_widget = plot_widget
        self.colors = self.plot_widget.get_colors()

        self.config_file = 'hpMCA_color_settings.json'
        prefs, colors = opt_fields()
        

        self.widget = DisplayPreferencesWidget(prefs, 
                            title='Display preferences control')

        
        params = list(prefs.keys())
        '''
        ['plot_background_color',
                  'data_color',
                  'rois_color',
                  'roi_cursor_color'
                  ]
        '''

        super().__init__(params)
        self.name = "Display Preferences"
        self.note = ''
        self.make_connections()
        self.auto_process = True
        self.set_config(colors)
        

    def make_connections(self):
        self.widget.apply_clicked_signal.connect(self.apply_callback)

    def apply_callback(self, params):
        self.set_config(params)
        save_config(params, self.config_file)

    def update(self):
        updated_params = {}
        for c in self.config_modified:
            updated_params[c] = self.params[c]
        if len(updated_params):
            self.plot_widget.set_colors(updated_params)

    def show(self):
        prefs = self.plot_widget.get_colors()
        self.widget.set_params(prefs)
        self.widget.raise_widget()

    
        
def save_config(params, filename):
    options_out = json_compatible_dict(params)
    try:
        with open(filename, 'w') as outfile:
            json.dump(options_out, outfile,sort_keys=True, indent=4)
            outfile.close()
    except:
        pass


def opt_fields():

    colors = readconfig('hpMCA_color_settings.json')

    opts = {'display':
                   {'plot_background_color':
                    {'val': (255, 255, 255),
                     'desc': 'data binning for better statistics',
                     'label': 'Background'},
                    'data_color':
                        {'val': '#2F2F2F',
                            'desc': '',
                            'label': 'Plot foreground'},
                    'rois_color':
                        {'val': (0, 180, 255),
                            'desc': '',
                            'label': "ROIs highlight"},
                    'roi_cursor_color':
                        {'val': (255, 0, 0),
                            'desc': '',
                            'label': 'Selected ROI cursor'}

                    }
                   }


    prefs = opts['display']
    for c in colors:
        if c in prefs:
            prefs[c]['val']= colors[c]
    return prefs, colors
    
