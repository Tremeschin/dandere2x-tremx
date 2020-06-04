"""
===============================================================================

Purpose: Qt GUI for Dandere2x made with Qt Designer, Python loads and configures

===============================================================================

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.

===============================================================================
"""

from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtCore import QThread
from PyQt5 import QtWidgets, uic
from dandere2x import Dandere2x
from functools import partial
import misc.greeter_message
from utils import Utils
import threading
import time
import sys
import os


# QT needs to know this is a QThread otherwise it'll hand main thread
class Dandere2xStarter(QThread):

    # QT needs to start the QThread
    def __init__(self, statslabel, progress_bar, stop_button):
        QThread.__init__(self)
        self.statslabel = statslabel
        self.progress_bar = progress_bar
        self.stop_button = stop_button

    # Load config and create Dandere2x() main thread
    def load_and_configure(self, config):
        self.config = config
        self.dandere2x = Dandere2x(self.config)

    # When main application quits
    def __del__(self):
        # Stop (resume session) and wait to be finished
        self.stop()
        self.wait()

    # Update the status label on the main window
    def keep_updating_status(self):
        while not self.dandere2x.controller.stop:
            # Get the stats text from main Dandere2x
            stats = "\n".join(self.dandere2x.controller.stats_list)

            # Set the label and progress bar accordinly
            self.statslabel.setText(stats)
            self.progress_bar.setValue(int(self.dandere2x.controller.percentage_completed))

            # Don't hang this thread with an stupid updates per second
            time.sleep(0.1)
        
        self.progress_bar.setEnabled(False)
        self.stop_button.setEnabled(False)

        # Controller says to stop, did we finish the upscale or was it stopped / crashed?
        if int(self.dandere2x.controller.percentage_completed) == 100:
            self.statslabel.setText("Upscale finished\nGoodbye Dandere!!\n")
        else:
            self.statslabel.setText("Upscale was stopped or crashed\nGoodbye Dandere!!\n")

    # Main routine on running Dandere2x
    def run(self):
        # Load required stuff
        self.dandere2x.load()
        self.dandere2x.setup()

        # Thread to update gui status label and progress bar
        threading.Thread(target=self.keep_updating_status).start()

        # Run a Dandere2x session (either new or resume)
        self.dandere2x.run()
    
    # Run controller.exit function to stop Dandere2x() and mark as resume session
    def stop(self):
        self.dandere2x.controller.exit()


# Main thread on QT GUI of Dandere2x
class Dandere2xQTUI(QtWidgets.QMainWindow):

    def __init__(self):
        
        # Qt stuff :v, no clue what "super" is
        super(Dandere2xQTUI, self).__init__()

        # Create the gui Utils class and get the root folder of where this script is
        self.utils = Utils()
        self.ROOT = self.utils.get_root()

        # Load the Qt gui file
        uic.loadUi(self.ROOT + os.path.sep + "data/dandere2x-qt-gui.ui", self)

        # # # # Get all widgets into internal variables, connect all of them to some function

        # Status label and progress bar
        self.label_stats = self.findChild(QtWidgets.QLabel, "stats")
        self.progress_bar = self.findChild(QtWidgets.QProgressBar, 'progress_bar') 

        # # # Basic configuration

        # # The sliders
        self.slider_upscale_ratio = self.findChild(QtWidgets.QSlider, 'upscale_ratio')
        self.slider_upscale_ratio.valueChanged.connect(partial(self.value_changed, self.slider_upscale_ratio))

        self.slider_denoise_level = self.findChild(QtWidgets.QSlider, 'denoise_level')        
        self.slider_denoise_level.valueChanged.connect(partial(self.value_changed, self.slider_denoise_level))       

        # Label of the sliders
        self.label_upscale_ratio = self.findChild(QtWidgets.QLabel, "upscale_label")
        self.label_denoise_level = self.findChild(QtWidgets.QLabel, "denoise_label")

        # # I/O push buttons to select input video or output video
        self.push_button_input = self.findChild(QtWidgets.QPushButton, 'select_input')
        self.push_button_input.clicked.connect(partial(self.select_file, self.push_button_input))

        self.push_button_output = self.findChild(QtWidgets.QPushButton, 'select_output')
        self.push_button_output.clicked.connect(partial(self.select_file, self.push_button_output))

        # Session controls
        self.push_button_load_session = self.findChild(QtWidgets.QPushButton, 'load_session')
        self.push_button_load_session.clicked.connect(partial(self.select_file, self.push_button_load_session))

        self.push_button_start_session = self.findChild(QtWidgets.QPushButton, 'start_session')
        self.push_button_start_session.clicked.connect(partial(self.value_changed, self.push_button_start_session))

        self.push_button_stop_session = self.findChild(QtWidgets.QPushButton, 'stop_session')
        self.push_button_stop_session.clicked.connect(partial(self.value_changed, self.push_button_stop_session))

        # Editable video text box that is a path
        self.line_input = self.findChild(QtWidgets.QLineEdit, 'input')
        self.line_output = self.findChild(QtWidgets.QLineEdit, 'output')

        self.combobox_upscaler = self.findChild(QtWidgets.QComboBox, 'upscaler')
        self.combobox_upscaler.currentTextChanged.connect(partial(self.value_changed, self.combobox_upscaler))

        # # Block matching options
        self.spinbox_block_size = self.findChild(QtWidgets.QSpinBox, 'block_size')
        self.spinbox_block_size.valueChanged.connect(partial(self.value_changed, self.spinbox_block_size))

        self.spinbox_bleed = self.findChild(QtWidgets.QSpinBox, 'bleed')
        self.spinbox_bleed.valueChanged.connect(partial(self.value_changed, self.spinbox_bleed))

        self.combobox_aggressiveness = self.findChild(QtWidgets.QComboBox, 'aggressiveness')
        self.combobox_aggressiveness.currentTextChanged.connect(partial(self.value_changed, self.combobox_aggressiveness))

        # # # Advanced configuration

        # # Block matching / Dandere2x C++

        # Dark / Bright thresholds
        self.doublespinbox_dark_threshold = self.findChild(QtWidgets.QDoubleSpinBox, 'dark_threshold')
        self.doublespinbox_dark_threshold.valueChanged.connect(partial(self.value_changed, self.doublespinbox_dark_threshold))
        
        self.doublespinbox_bright_threshold = self.findChild(QtWidgets.QDoubleSpinBox, 'bright_threshold')
        self.doublespinbox_bright_threshold.valueChanged.connect(partial(self.value_changed, self.doublespinbox_bright_threshold))

        # Full frame threshold
        self.doublespinbox_fullframe_threshold = self.findChild(QtWidgets.QDoubleSpinBox, 'fullframe_threshold')
        self.doublespinbox_fullframe_threshold.valueChanged.connect(partial(self.value_changed, self.doublespinbox_fullframe_threshold))

        # Check boxes

        # Force mode
        self.check_box_force = self.findChild(QtWidgets.QCheckBox, 'force')
        self.check_box_force.stateChanged.connect(partial(self.value_changed, self.check_box_force))

        # Only run Dandere2x C++
        self.check_box_only_run_dandere2x_cpp = self.findChild(QtWidgets.QCheckBox, 'only_run_dandere2x_cpp')
        self.check_box_only_run_dandere2x_cpp.stateChanged.connect(partial(self.value_changed, self.check_box_only_run_dandere2x_cpp))

        # Write debug video
        self.check_box_write_debug_video = self.findChild(QtWidgets.QCheckBox, 'write_debug_video')
        self.check_box_write_debug_video.stateChanged.connect(partial(self.value_changed, self.check_box_write_debug_video))

        # Show debug video realtime
        self.check_box_show_debug_video_realtime = self.findChild(QtWidgets.QCheckBox, 'show_debug_video_realtime')
        self.check_box_show_debug_video_realtime.stateChanged.connect(partial(self.value_changed, self.check_box_show_debug_video_realtime))

        # Show block matching stats
        self.check_box_show_block_matching_stats = self.findChild(QtWidgets.QCheckBox, 'show_block_matching_stats')
        self.check_box_show_block_matching_stats.stateChanged.connect(partial(self.value_changed, self.check_box_show_block_matching_stats))

        # # FFmpeg / libx264

        # Deblock filter
        self.combobox_deblock_filter = self.findChild(QtWidgets.QComboBox, 'deblock_filter')
        self.combobox_deblock_filter.currentTextChanged.connect(partial(self.value_changed, self.combobox_deblock_filter))

        # x264 preset
        self.combobox_x264_preset = self.findChild(QtWidgets.QComboBox, 'x264_preset')
        self.combobox_x264_preset.currentTextChanged.connect(partial(self.value_changed, self.combobox_x264_preset))

        # x264 tune
        self.combobox_x264_tune = self.findChild(QtWidgets.QComboBox, 'x264_tune')
        self.combobox_x264_tune.currentTextChanged.connect(partial(self.value_changed, self.combobox_x264_tune))

        # x264 CRF
        self.spinbox_x264_crf = self.findChild(QtWidgets.QSpinBox, 'x264_crf')
        self.spinbox_x264_crf.valueChanged.connect(partial(self.value_changed, self.spinbox_x264_crf))
        
        # # Upscaler

        # Tile size
        self.spinbox_tile_size = self.findChild(QtWidgets.QSpinBox, 'tile_size')
        self.spinbox_tile_size.valueChanged.connect(partial(self.value_changed, self.spinbox_tile_size))

        # Load proc save
        self.line_load_proc_save = self.findChild(QtWidgets.QLineEdit, 'load_proc_save')
        self.line_load_proc_save.textChanged.connect(partial(self.value_changed, self.line_load_proc_save))

        # # Linux

        # Use ACO (RADV_PERFTEST=aco)
        self.check_box_mesaaco = self.findChild(QtWidgets.QCheckBox, 'mesaaco')
        self.check_box_mesaaco.stateChanged.connect(partial(self.value_changed, self.check_box_mesaaco))

        # Default set to yn_moving_480 sample file
        self.line_input.setText(self.ROOT + os.path.sep + "samples" + os.path.sep + "yn_moving_480.mkv")
        self.auto_output()

        # Create Dandere2xStarter class and load config, set resume to False by default
        # Resuming is done via "load session" button or same input video filename as session=auto
        self.dandere2x = Dandere2xStarter(self.label_stats, self.progress_bar, self.push_button_stop_session)
        self.config = self.utils.load_yaml(self.utils.ROOT + os.path.sep + "settings.yaml", log=False)
        self.config["resume"] = False

        # Load default values the gui starts with
        # TODO: Remember last settings?
        self.get_values()
    
        # Stopping session / progress bar should be only active while a session is running
        self.togglewidget("progress_bar", False)
        self.togglewidget("push_button_stop_session", False)

    # Get and store values of everything
    def get_values(self, reload_compatible=True):

        # # # Get default values

        # # Basic config

        # Upscaler, block matching, I/O
        self.upscale_ratio = self.slider_upscale_ratio.value()
        self.denoise_level = self.slider_denoise_level.value()
        self.input = self.line_input.text()
        self.output = self.line_output.text()
        self.upscaler = self.combobox_upscaler.currentText()
        self.block_size = self.spinbox_block_size.value()
        self.bleed = self.spinbox_bleed.value()
        self.aggressiveness = self.combobox_aggressiveness.currentText()
        self.force = self.check_box_force.isChecked()

        # # Advanced config

        # Block matching / Dandere2x C++
        self.dark_threshold = self.doublespinbox_dark_threshold.value()
        self.bright_threshold = self.doublespinbox_bright_threshold.value()
        self.fullframe_threshold = self.doublespinbox_fullframe_threshold.value()
        self.only_run_dandere2x_cpp = self.check_box_only_run_dandere2x_cpp.isChecked()
        self.write_debug_video = self.check_box_write_debug_video.isChecked()
        self.show_debug_video = self.check_box_show_debug_video_realtime.isChecked()
        self.show_block_matching_stats = self.check_box_show_block_matching_stats.isChecked()

        # FFmpeg / libx264
        self.deblock_filter = self.combobox_deblock_filter.currentText()
        self.x264_preset = self.combobox_x264_preset.currentText()
        self.x264_tune = self.combobox_x264_tune.currentText()
        self.x264_crf = self.spinbox_x264_crf.value()

        # Upscaler
        self.tile_size = self.spinbox_tile_size.value()
        self.load_proc_save = self.line_load_proc_save.text()

        # # Linux

        # Use ACO (RADV_PERFTEST=aco)
        self.mesaaco = self.check_box_mesaaco.isChecked()

        # # # # Create a dictionary with the widgets name for easier handling

        self.widgets = {
            "slider_upscale_ratio": self.slider_upscale_ratio,
            "slider_denoise_level": self.slider_denoise_level,
            "progress_bar": self.progress_bar,
            "push_button_start_session": self.push_button_start_session,
            "push_button_stop_session": self.push_button_stop_session,
            "push_button_load_session": self.push_button_load_session,
            "line_input": self.line_input,
            "line_output": self.line_output,
            "combobox_upscaler": self.combobox_upscaler,
            "spinbox_block_size": self.spinbox_block_size,
            "spinbox_bleed": self.spinbox_bleed,
            "combobox_aggressiveness": self.combobox_aggressiveness,
            "check_box_force": self.check_box_force,
            "doublespinbox_dark_threshold": self.doublespinbox_dark_threshold,
            "doublespinbox_bright_threshold": self.doublespinbox_bright_threshold,
            "doublespinbox_fullframe_threshold": self.doublespinbox_fullframe_threshold,
            "check_box_only_run_dandere2x_cpp": self.check_box_only_run_dandere2x_cpp,
            "check_box_write_debug_video": self.check_box_write_debug_video,
            "check_box_show_debug_video_realtime": self.check_box_show_debug_video_realtime,
            "check_box_show_block_matching_stats": self.check_box_show_block_matching_stats,
            "combobox_deblock_filter": self.combobox_deblock_filter,
            "combobox_x264_preset": self.combobox_x264_preset,
            "combobox_x264_tune": self.combobox_x264_tune,
            "spinbox_x264_crf": self.spinbox_x264_crf,
            "spinbox_tile_size": self.spinbox_tile_size,
            "line_load_proc_save": self.line_load_proc_save,
            "check_box_mesaaco": self.check_box_mesaaco
        }

        self.compatibilize()

        # We potentially changed some minimum / maximum ranges so
        # let's get the values again without running this otherwise will infinte loop
        if reload_compatible:
            self.get_values(reload_compatible=False)
            return

        self.update_config()
        self.auto_output()

        self.show()

    # Some options are incompatible with some upscalers so we fix them here
    # Or put a mode like Upscale started and we lock everything
    def compatibilize(self, mode=None):

        # Realsr doesn't have a denoise
        action = (not self.upscaler == "realsr-ncnn-vulkan")
        self.togglewidget("slider_denoise_level", action)

        # # Check upscale ratios based on the upscalers

        compatible = {
            "waifu2x-ncnn-vulkan": [1, 2],
            "waifu2x-converter-cpp": [1, 2],
            "realsr-ncnn-vulkan": [4],
            "srmd-ncnn-vulkan": [2, 4],
            "fake": [1, 8]
        }

        possible = compatible[self.upscaler]

        self.set_maximum("slider_upscale_ratio", possible[-1])
        self.set_minimum("slider_upscale_ratio", possible[0])

        # # Check denoise level based on the upscalers
        
        compatible = {
            "waifu2x-ncnn-vulkan": [-1, 3],
            "waifu2x-converter-cpp": [0, 3],
            "realsr-ncnn-vulkan": [0],
            "srmd-ncnn-vulkan": [-1, 10],
            "fake": [0]
        }

        possible = compatible[self.upscaler]

        self.set_maximum("slider_denoise_level", possible[-1])
        self.set_minimum("slider_denoise_level", possible[0])

        # Thresholds can only be set if aggressiveness is "custom"
        action = (not self.aggressiveness in ["High", "Medium", "Low"])
        self.togglewidget("doublespinbox_dark_threshold", action)
        self.togglewidget("doublespinbox_bright_threshold", action)

        # Set aggressiveness if on the three presets
        if self.aggressiveness == "Low":
            self.dark_threshold = 0.025
            self.bright_threshold = 0.027

        elif self.aggressiveness == "Medium":
            self.dark_threshold = 0.01
            self.bright_threshold = 0.015

        elif self.aggressiveness == "High":
            self.dark_threshold = 0.0035
            self.bright_threshold = 0.0045

    # Changes the settings.yaml equivalent options based on the ones from this gui
    def update_config(self):

        # Upscaler related
        self.config["upscaler"]["type"] = self.upscaler
        self.config["upscaler"]["upscale_ratio"] = self.upscale_ratio
        self.config["upscaler"]["denoise_level"] = self.denoise_level
        self.config["upscaler"]["tile_size"] = self.tile_size
        self.config["upscaler"]["load:proc:save"] = self.load_proc_save
        self.config["upscaler"]["linux_enable_mesa_aco_upscaler"] = self.mesaaco

        # Basic settings
        self.config["basic"]["input_file"] = self.input
        self.config["basic"]["output_file"] = self.output

        # Force mode
        self.config["danger_zone"]["force"] = self.force
        
        # Block matching
        if self.block_size == 0:
            self.config["block_matching"]["bleed"] = "auto"
        else:
            self.config["block_matching"]["bleed"] = self.block_size

        self.config["block_matching"]["bleed"] = self.bleed
        self.config["block_matching"]["dark_threshold"] = self.dark_threshold
        self.config["block_matching"]["bright_threshold"] = self.bright_threshold
        self.config["block_matching"]["upscale_full_frame_threshold"] = self.fullframe_threshold

        # Dandere2x C++ settings
        self.config["dandere2x_cpp"]["only_run_dandere2x_cpp"] = self.only_run_dandere2x_cpp
        self.config["dandere2x_cpp"]["write_debug_video"] = self.write_debug_video
        self.config["dandere2x_cpp"]["show_debug_video_realtime"] = self.show_debug_video
        self.config["dandere2x_cpp"]["show_block_matching_stats"] = self.show_block_matching_stats

        self.config["ffmpeg"]["deblock_filter"] = self.deblock_filter
        self.config["ffmpeg"]["x264"]["preset"] = self.x264_preset
        self.config["ffmpeg"]["x264"]["tune"] = self.x264_tune
        self.config["ffmpeg"]["x264"]["crf"] = self.x264_crf        

    # Enable or disable widgets, who = to (T/F)
    def togglewidget(self, who, to):
        self.widgets[who].setEnabled(to)

    # Set the maximum value of a widget (slider)
    def set_maximum(self, who, to):
        self.widgets[who].setMaximum(to)

    # Set the minimum value of a widget (slider)    
    def set_minimum(self, who, to):
        self.widgets[who].setMinimum(to)

    # When a value of a widget changes, combobox, slider
    def value_changed(self, who):
        try:
            print(who.objectName(), who.currentText())
        except Exception:
            pass

        try:
            print(who.objectName(), who.value())
        except Exception:
            pass

        try:
            print(who.objectName(), who.text())
        except Exception:
            pass

        self.get_values()

        # Sliders we have to update a label saying their value
        if who == self.slider_denoise_level:
            value = self.slider_denoise_level.value()
            self.label_denoise_level.setText(f"x{value}")

        elif who == self.slider_upscale_ratio:
            value = self.slider_upscale_ratio.value()
            self.label_upscale_ratio.setText(f"x{value}")

        # Start an upscale
        elif who == self.push_button_start_session:
            self.dandere2x.load_and_configure(self.config)
            self.togglewidget("progress_bar", True)
            self.togglewidget("push_button_stop_session", True) 
            self.dandere2x.start()

        # Exit an upscale
        elif who == self.push_button_stop_session:
            self.togglewidget("progress_bar", False)   
            self.togglewidget("push_button_stop_session", False) 
            self.dandere2x.stop()

    # Sets a dynamic output filename for convenience
    def auto_output(self):
        auto_output = self.utils.auto_output_file(
                self.line_input.text(),
                self.slider_upscale_ratio.value(),
                self.combobox_upscaler.currentText()
            )
        self.line_output.setText(auto_output)

    # File chooser dialog
    def select_file(self, who):

        text = QFileDialog.getOpenFileName()
    
        # We got no file selected from the user, cancelled dialog
        if text == ('', ''):
            return
        
        # Some input file has been recieved
        if who == self.push_button_input:

            # Set the input on the editable line
            self.line_input.setText(text[0])

            # Set an suggested output file based on some session settings
            self.auto_output() 
        
        # User chose some output file PATH
        elif who == self.push_button_output:
            self.line_output.setText(text[0])

        # Resume session
        elif who == self.push_button_load_session:
            # Set the resume from vars file, Dandere2x should handle everything
            self.config["resume_session_context_vars_file"] = text[0]
            print("config[\"resume_session_context_vars_file\"] =", text[0])
            
            self.togglewidget("progress_bar", True)
            self.dandere2x.load_and_configure(self.config)
            self.dandere2x.start()

# Qt stuff
app = QtWidgets.QApplication(sys.argv)
window = Dandere2xQTUI()
app.exec_()
