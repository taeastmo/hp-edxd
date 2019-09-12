
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import

from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

if __version__ == "0+unknown":
    __version__ = "0.2.0"

import sys
import os
import time

from qtpy import QtWidgets

resources_path = os.path.join(os.path.dirname(__file__), 'resources')
#calibrants_path = os.path.join(resources_path, 'calibrants')
icons_path = os.path.join(resources_path, 'icons')
#data_path = os.path.join(resources_path, 'data')
#style_path = os.path.join(resources_path, 'style')

from ._desktop_shortcuts import make_shortcut

from .widgets.UtilityWidgets import ErrorMessageBox





def excepthook(exc_type, exc_value, traceback_obj):
    """
    Global function to catch unhandled exceptions. This function will result in an error dialog which displays the
    error information.

    :param exc_type: exception type
    :param exc_value: exception value
    :param traceback_obj: traceback object
    :return:
    """
    separator = '-' * 80
    log_file = "error.log"
    notice = \
        """An unhandled exception occurred. Please report the bug under:\n """ \
        """\t%s\n""" \
        """or via email to:\n\t <%s>.\n\n""" \
        """A log has been written to "%s".\n\nError information:\n""" % \
        (" ",
         "hrubiak@anl.gov",
         os.path.join(os.path.dirname(__file__), log_file))
    version_info = '\n'.join((separator, "hpMCA Version: %s" % dioptas_version))
    time_string = time.strftime("%Y-%m-%d, %H:%M:%S")
    tb_info_file = StringIO()
    traceback.print_tb(traceback_obj, None, tb_info_file)
    tb_info_file.seek(0)
    tb_info = tb_info_file.read()
    errmsg = '%s: \n%s' % (str(exc_type), str(exc_value))
    sections = [separator, time_string, separator, errmsg, separator, tb_info]
    msg = '\n'.join(sections)
    try:
        f = open(log_file, "w")
        f.write(msg)
        f.write(version_info)
        f.close()
    except IOError:
        pass
    errorbox = ErrorMessageBox()
    errorbox.setText(str(notice) + str(msg) + str(version_info))
    errorbox.exec_()


def main():
    app = QtWidgets.QApplication([])

    from hpMCA.controllers.hpmca_controller import hpMCA
    app.aboutToQuit.connect(app.deleteLater)

    controller = hpMCA(app)
    controller.widget.show()

    # autoload a file, using for debugging
    controller.openFile(filename='resources/20181010-Au-wire-50um-15deg.hpmca')
    controller.phase_controller.add_btn_click_callback(filenames=['JCPDS/Metals/au.jcpds'])
    #controller.phase_controller.add_btn_click_callback(filenames=['JCPDS/Oxides/mgo.jcpds'])

    return app.exec_()