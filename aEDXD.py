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

"""aEDXD.py:
   A GUI program for amorphous EDXD data analysis
"""

###############################################################################
#   v1.1.1:
#       1. Multi-file input at a 2Th angle is allowed
#   v1.1.2:
#       1. The spectrum normalization is done directly to be S(q),
#          not to be an I(q) profile, hence no I(q) data is saved.
#       2. Change the way to smooth the S(q) for UnivariateSpline parameter.
#          The sq_smoothing_factor is multiplied to the weight factor:
#          scipy.interploate.UnivariateSpline(x,y,w=sq_smoothing_factor*weight,
#          bbox=[None,None],k=3,s=None), where weight = 1/y_err.
#   v1.2a:
#       1. The version convention changed: Version.Revision+a:alphaa or b:beta    
#       2. Read aEDXD_input.cfg file: python dictionary syntax
#       3. aEDXD_class is separated from aEDXD_functions
#       4. Verbose analysis using aEDXD methods
#   v1.2b:
#       1. Automatically save the structure factor segments
#   v1.3:
#       1. Work with:
#               Python 2.7.9
#               Numpy 1.9.2
#               Scipy 0.15.1
#               matplotlib 1.4.3
#       2. Add new option to choose input file format
#       3. Fix a but that did not sum intensities from multiple input files
#   v1.9:  Author: R. Hrubiak, ANL
#       1. Upgraded to Python 3.7
#       2. Created a GUI based on PyQt5 and pyqtgraph
#       3. Visual peak removal via interactive plot
#       4. Improved interpolation under removed peaks 
#       4. GUI options editing / operation possible without a config file
#       6. Options/project saving  
#   v2.0:  Author: R. Hrubiak, ANL
#       1. Plotting of calculated uncertainties 
#       2. Invalid config file loading does not crash program
#       3. Drag-drop files
#       4. Automatic loading of 2theta from file.
#       5. Save and save-as options
#       6. Buttons to export data
#       7. In peak cut window only show one 2th at a time
#       8. Undo, reset functionality
#       9. Input/output directory saving to config file
#       10. Warn to save on exit
#       11. Save file-use tag
#       12. Periodic table atom picker
#       13. TODO sequence file loading 
#       14. TODO Hdf5 compatible, save datafiles in projext files, save parameters in exported files?
#       15. TODO better peak cutting based on background function, use LV bg function
#       16. TODO Integrate scanning data acquisition and data display
#       17. TODO improve autonaming of exported files, export all option
#       18. TODO Allow different E range for different segments 
#       19. TODO Optimal parameters not found when Emax 69.5, prorgram crashes
#       20. TODO integrate peak cutting screen tools with main view
#       21. TODO improve parameter entry, e.g. density should be more intuitive or offer more options
#       22. TODO self consistency of S(q) check
#       23. TODO expand number of available elements, look up scattering factors in lit
#       24. TODO Q scale for n spectrum view
#       25. 
#       
#        
###############################################################################


from axd import main

main()

