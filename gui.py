"""
===============================================================================

    THIS NEEDS HEAVY REWRITING

Purpose: Load up and get options from a GTK GUI, execute Dandere2x with them

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

from dandere2x import Dandere2x
from playsound import playsound
from gi.repository import Gtk, GObject
from color import rgb
import multiprocessing
import webbrowser
import threading
import datetime
import random
import shutil
import time
import yaml
import os
import gi

gi.require_version('Gtk', '3.0')

GObject.threads_init()

ROOT = os.path.dirname(os.path.abspath(__file__))
color = rgb(200, 120, 255)

dandere2x = None
dandere2x_thread = None
dandere2x_start_thread = False

def progressbar_thread():
    global window

    while True:
        # Wait until frame count and current frame exists
        try:
            last_processing_frame = window.dandere2x.context.last_processing_frame
        except Exception:
            time.sleep(1)
            # dandere2x.utils.log(color, debug_prefix, "Waiting for frame count to exist")

    for x in range(window.dandere2x.context.last_processing_frame - 1):

        # Wait until merged_count changes
        while (x >= window.dandere2x.context.signal_merged_count):
            time.sleep(1/30) # 30 Fps

        # Update progress bar
        window.update_progress_bar(x+1, last_processing_frame)




def play_sound_threaded(audio):
    playsound(ROOT + os.path.sep + "data" + os.path.sep + audio + ".wav")


def thread_d2x():
    global dandere2x, dandere2x_thread, dandere2x_start_thread

    while True:
        if dandere2x_start_thread == True:
            print("breaking")
            break
        time.sleep(0.2)
        print("keeping")

    print("Running d2x")

    dandere2x.run()

    dandere2x_start_thread = False

threading.Thread(target=progressbar_thread).start()
threading.Thread(target=thread_d2x).start()

def sound(audio):
    # Gotta thread of GUI hangs
    threading.Thread(target=play_sound_threaded, args=(audio, )).start()


class DandereGTK():
    global dandere2x, dandere2x_thread, dandere2x_start_thread

    def __init__(self, windowfile):
        global dandere2x, dandere2x_thread, dandere2x_start_thread

        # More verbosely print stuff that is happening, might leave on?
        self.debug = True

        dandere2x = Dandere2x({"force": False})
        dandere2x.load()

        # The builder object from GTK as for adding the gui .glade file
        self.builder = Gtk.Builder()
        self.builder.add_from_file(windowfile)

        self.status("Setting up handlers")

        # The handlers are defined in the GLADE file on the Signals tab
        self.handlers = {
            "action_buttons": self.action_buttons,
            "slider_changed": self.slider_changed,
            "switch_changed": self.switch_changed,
            "update_waifu_type": self.update_waifu_type,
            "file_clicked": self.file_clicked,

            "load_session": self.point_to_session_for_resume,

            "resources": self.resources,

            "quit": Gtk.main_quit  # TODO: does not quit python?
        }

        # Connect the handlers to Python functions
        self.builder.connect_signals(self.handlers)

        # Declare all the varables in their default values

        # Sliders
        self.scale_factor = 2
        self.denoise_level = 3
        self.block_size = "20"

        # Switches
        self.minimal_disk = True
        self.resume = False

        # Files
        self.input_file = ""
        self.output_file = ""
        self.session_name = "auto"

        # Progress bar and averages
        self.progressbar = self.builder.get_object("progressbar")
        self.average = self.builder.get_object("averages")
        self.tcc = self.builder.get_object("tcc")
        self.n_frames_average = 120  # MUST BE GREATER OR EQUAL TO 10
        self.last_frame_time_completed = 0  # for calculating the TCC correctly
        self.gui_round_numbers_decimals = 2

        # Waifu2x
        self.current_mode = "stopped"
        self.waifu2x_type = "vulkan"

        # Internals
        self.can_toggle = True
        self.time_start = None
        self.time_took_frames = [0 for _ in range(self.n_frames_average)]

        self.can_change_options = False

        if self.n_frames_average < 10:
            self.n_frames_average = 10

        self.status("Enabling widgets")
        self.toggle_gui_options()

        self.status("Waiting user input...", True)

        # Only after the first smart message box that greets the user
        # if never executed before.
        self.smart_messagebox("greetings")

        # Get and show main window
        self.window = self.builder.get_object("mainwindow")
        self.window.show_all()

        debug_prefix = "[DandereGTK.__init__]"

        dandere2x.utils.log(color, debug_prefix, "Init done")


    # Calls the GTK MessageDialog
    def message_box(self, title, content):

        # Create the GTK object dialog with the title
        dialog = Gtk.MessageDialog(None, None, Gtk.MessageType.QUESTION,
                                   Gtk.ButtonsType.OK, title)

        # Add the content of it
        dialog.format_secondary_text(content)

        # Run and destroy it after being closed (runned)
        response = dialog.run()
        dialog.destroy()


    # (/s) Smartly chooses which dialog message to call the MessageDialog
    def smart_messagebox(self, message_type=""):

        # Get the path for the gui_stuff.yaml
        configfile = ROOT + os.path.sep + "gui" + os.path.sep + "gui_stuff.yaml"

        # Load it
        with open(configfile, "r") as read_file:
            config = yaml.safe_load(read_file)

        # This section checks which message_type is being requested and
        # calls the message_box modular function to show up the dialog

        if config["gtk_gui"]["first_time_%s" % message_type]:

            message = config["gtk_gui"]["messages"][message_type]
            config["gtk_gui"]["first_time_%s" % message_type] = False

            #sound("pop")
            self.message_box(message[0], message[1])


        # Save everything we just changed (if we were greeted first time,
        # or clicked the advanced options first time as well)
        with open(configfile, 'w') as outfile:
            yaml.dump(config, outfile, default_flow_style=False)



    # This function toggles the user-interactible widgets but the upscale and stop button
    def toggle_gui_options(self, to=None):

        # List the widgets IDs we gonna disable
        option_widgets_ids = ["block_size", "waifutype", "scale_factor",
                              "denoise_level", "minimal_disk",
                              "output", "input", "suspendbutton"]

        if to == None:
            # T-FLIP-FLOP the can_change_options
            self.can_change_options = not self.can_change_options
        else:
            self.can_change_options = to

        for widget in option_widgets_ids:
            # Set the widget sensitive or insensitive (enabled/disabled)
            self.builder.get_object(widget).set_sensitive(self.can_change_options)


    # Change the status label at bottom left of the GUI, the spinner button
    # is off by default and can be called if True is set as a second argument
    def status(self, new_status, spin = False):

        debug_prefix = "[DandereGTK.status]"

        # Get the builder object of the status label and set the new status
        self.builder.get_object("status").set_label(new_status)

        # Enable/disable the spinner
        if spin:
            self.builder.get_object("spinner").start()
        else:
            self.builder.get_object("spinner").stop()

        if self.debug:
            dandere2x.utils.log(color, debug_prefix, new_status)



    # Get the value of the combobox and update the waifu2x type var
    def update_waifu_type(self, data):
        self.waifu2x_type = self.builder.get_object("waifutype").get_active_text()

        equivalents = {
            "Vulkan Legacy (SNAP)": "vulkan_legacy",
            "CPP": "converter_cpp",
            "Vulkan": "vulkan",
            "Caffe": "caffe"
        }

        for key in equivalents.keys():
            self.waifu2x_type = self.waifu2x_type.replace(key, equivalents[key])

        self.status("Waifu2x type changed to " + self.waifu2x_type)



    def action_buttons(self, data):

        debug_prefix = "[DandereGTK.action_buttons]"

        # Alternate between upscale and stop, the two toggle buttons

        upscalebutton = self.builder.get_object("upscalebutton")
        suspendbutton = self.builder.get_object("suspendbutton")

        who = Gtk.Buildable.get_name(data)

        # Avoid infinite loops
        if self.can_toggle:

            # DISCLAIMER: This just works, little tricky to code though

            if who == "upscalebutton":

                # It's already toggled, do nothing
                if upscalebutton.get_active() == False:
                    self.can_toggle = False
                    upscalebutton.set_active(True)

                # Not toggled so we change the current mode
                elif upscalebutton.get_active() == True:

                    if self.test_good_to_go() == True:

                        if not upscalebutton.get_label() == "Resume Session":
                            sound("start")
                        else:
                            sound("resume")

                        self.can_toggle = False  # Avoid infinite loop
                        self.current_mode = "upscale"

                        suspendbutton.set_label("Suspend Session")
                        upscalebutton.set_label("Upscaling in Process...")

                        self.time_start = time.time()
                        self.last_frame_time_completed = time.time()
                        self.toggle_gui_options(False)
                        self.upscale()

                        dandere2x.utils.log(color, debug_prefix, "Upscale button clicked")

                    else:
                        sound("error")
                        self.can_toggle = False
                        upscalebutton.set_active(False)
                        dandere2x.utils.log(color, debug_prefix, "Couldn't start upscale, not good to go")


            if who == "suspendbutton":

                # It's already toggled, do nothing
                if suspendbutton.get_active() == False:
                    self.can_toggle = False
                    suspendbutton.set_active(True)

                # Not toggled so we change the current mode
                elif suspendbutton.get_active() == True:

                    sound("stop")

                    self.can_toggle = False # Avoid infinite loop
                    upscalebutton.set_active(False)
                    self.current_mode = "stopped"
                    dandere2x.controller.exit()
                    suspendbutton.set_label("Session Suspended")
                    upscalebutton.set_label("Resume Session")
                    dandere2x.utils.log(color, debug_prefix, "Stop session button clicked")

        else:
            self.can_toggle = True


    # Test if input file is file and output file not empty
    # TODO: check if valid directory set for the outfile?
    # TODO: LINUX DOES NOT SUPPORT CAFFE

    def test_good_to_go(self):

        if self.resume:
            return True

        self.status("Testing good to go options...", True)

        # Input file exists
        if not os.path.isfile(self.input_file):
            self.status("Input file is not file: " + self.input_file)
            return False

        # Output file not empty
        if self.output_file == "":
            self.status("Output file is empty")
            return False

        self.status("Good to go!!")

        return True


    # Core functionality of this gui, calling Dandere2x.start() method
    def upscale(self):

        self.status("Upscale function called")


        self.status("Loading config YAML file", True)

        # Get the YAML config file based on OS
        configfile = ROOT + os.path.sep + "settings.yaml"

        with open(configfile, "r") as read_file:
            self.config = yaml.safe_load(read_file)


        # Change values based on GUI ones

        self.status("Changing configs accordinly to GUI", True)

        self.config['processing']['block_size'] = self.block_size
        self.config['waifu2x']['denoise_level'] = self.denoise_level

        self.config['basic']['input_file'] = self.input_file
        self.config['basic']['output_file'] = self.output_file

        self.config['waifu2x_type'] = self.waifu2x_type

        self.config['mindisk'] = self.minimal_disk
        self.config['session_name'] = self.session_name


        #self.config['scale_factor'] = self.scale_factor

        print(self.config)

        self.status("Running Dandere2x setup() function...", True)

        dandere2x.setup()

        self.status("Threading-start Dandere2x run() function...", True)

        dandere2x_start_thread = True

        self.status("Dandere2x run() called")

        self.status("Upscaling...", True)



    # Lazy math, bruh
    def proportion(self, a, b, c):
        # a is to b
        # c is to what
        # what = b*c/a
        return b*c/a



    # This needs to be called outside of this class preferably in a separate thread
    def update_progress_bar(self, currentframe, totalframes):

        # Limit progress bar updats in frames per second    vvvv
        if (time.time() - self.last_frame_time_completed) > 1/60:

            # For calculating global averages
            time_took_until_now = time.time() - self.time_start

            # Proportion completed
            frac = self.proportion(totalframes, 1, currentframe + 1)

            # The text to set the progressbar to
            progress_bar_text = "Progress: Frame [%s/%s] - %s %% " % (currentframe+1, totalframes, round(frac*100, 1))

            self.progressbar.set_fraction(frac)
            self.progressbar.set_text(progress_bar_text)



            # Put the values it took to go to the next frame based on the
            # difference of last item to the current one, that's being looped
            # by the modulo operation since it's the remainder of smth
            self.time_took_frames[ currentframe % self.n_frames_average ] = time.time() - self.last_frame_time_completed
            self.last_frame_time_completed = time.time()


            #    AVERAGES

            # Get the 10 last items by "biasing" the currentframe, sum those numbers and divide by 10
            # do not consider those who are zero otherwise wrong average value
            average_10_list = self.time_took_frames[ (currentframe - 10) % self.n_frames_average : currentframe % self.n_frames_average ]
            average_last_10 =  sum(average_10_list)/(10 - average_10_list.count(0))

            # Just sum it up and divide by n_frames_average
            average_last_n = sum(self.time_took_frames) / (self.n_frames_average - self.time_took_frames.count(0))

            # Self explanatory I guess?
            average_all = time_took_until_now / currentframe

            # The text to set the widget to
            average_text = "Average last N frames:   [10 :  %s sec/frame]    [%s : %s sec/frame]    [ALL : %s sec/frame]" % ( \
                            round(average_last_10, self.gui_round_numbers_decimals),
                            round(self.n_frames_average, self.gui_round_numbers_decimals),
                            round(average_last_n, self.gui_round_numbers_decimals),
                            round(average_all, self.gui_round_numbers_decimals))

            self.average.set_text(average_text)


            #   ETA

            # Basic proportion on how much time left until completion

            #tcc_time = self.proportion(currentframe, time_took_until_now, totalframes - currentframe)
            tcc_time_number = average_all*(totalframes-currentframe)
            tcc_time = str(datetime.timedelta(seconds=round(tcc_time_number, 2)))[:-7]

            tt_time = time_took_until_now
            tt_time = str(datetime.timedelta(seconds=round(time_took_until_now,2)))[:-5]

            now_plus_tcc = str(datetime.datetime.now() + datetime.timedelta(seconds = tcc_time_number))[:-7]


            tcc_text = "Total Time: [%s]    Time to Completion: [%s EST]  -->  Date will be [%s]" % (tt_time, tcc_time, now_plus_tcc)
            self.tcc.set_text(tcc_text)




    # Moved the Scale Factor slider so updating variables
    def switch_changed(self, *data):

        # Get what slider were changed
        who = Gtk.Buildable.get_name(data[0])
        newvalue = data[1]

        # As it is just a boolean, no need for checking, just update
        self.status(who + " changed to " + str(newvalue))
        exec("self.%s = %s" % (who, newvalue))

        self.smart_messagebox(who)



    # Moved the Scale Factor slider so updating variables
    def slider_changed(self, *data):

        # Get what slider were changed
        who = Gtk.Buildable.get_name(data[0])



        # Check if the new value is different from the old one
        if not who == "block_size":

            # Round to the nearest integer number the new decimal value.
            newvalue = int(round(data[0].get_value()))

            if not newvalue == eval("self." + who):
                self.status(who + " changed to " + str(newvalue))
                exec("self.%s = %s" % (who, newvalue))

        else:
            newvalue = round(float(data[0].get_value()), 4)
            self.status(who + " changed to " + str(newvalue) + "%")
            exec("self.%s = \"%s%%\"" % (who, newvalue))


    # Self explanatory
    def save_dialog(self):

        self.status("Select output video file", True)

        dialog = Gtk.FileChooserDialog(
            'Load file', None,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            self.output_file =  dialog.get_filename()
            dialog.destroy()
            self.status("Output file selected")
            return True

        self.status("No output file selected")
        dialog.destroy()
        return False


    # Self explanatory
    def open_dialog(self):

        self.status("Select input video file", True)

        dialog = Gtk.FileChooserDialog(
            'Load file', None,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            self.input_file =  dialog.get_filename()
            dialog.destroy()
            self.status("Input file selected")
            return True

        self.status("No input file selected")
        dialog.destroy()
        return False


    # If file input or output has changed
    def file_clicked(self, *data):

        # Get what slider were changed
        who = Gtk.Buildable.get_name(data[0])
        text = data[0].get_text()

        # Check if we need to call the open or save dialog as the file were not set
        if text == "":
            if who == "output":
                if self.save_dialog():
                    self.builder.get_object(who).set_text(self.output_file)
                    sound("output_file")

            elif who == "input":
                if self.open_dialog():
                    self.builder.get_object(who).set_text(self.input_file)
                    sound("input_file")

                    # Set an auto output value
                    auto_out = os.path.split(self.input_file)
                    auto_out = auto_out[0] + os.path.sep + "2x_" + auto_out[1]
                    self.builder.get_object("output").set_text(auto_out)
                    self.output_file = auto_out


    # Self explanatory
    def point_to_session_for_resume(self, *data):

        self.status("Select the session folder you want to resume", True)

        dialog = Gtk.FileChooserDialog(
            'Select the session', None,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

        if dialog.run() == Gtk.ResponseType.OK:
            self.session_to_resume = dialog.get_filename()
            self.status("Input file selected")

            session_name = os.path.basename(self.session_to_resume)

            upscalebutton = self.builder.get_object("upscalebutton")
            upscalebutton.set_label("Resume session")

            self.session_name = session_name
            dialog.destroy()
            self.resume = True
            self.toggle_gui_options(False)

            return 0

        self.resume = False
        self.status("No resume session folder selected")
        dialog.destroy()
        return 0



    # Collections of links to Dandere2x related places
    def resources(self, *data):

        debug_prefix = "[DandereGTK.resources]"

        # Get id of button in the toolbar
        who = Gtk.Buildable.get_name(data[0])
        dandere2x.utils.log(color, debug_prefix, "Open link:", who)

        links = {
            "docs": "https://dandere2x.readthedocs.io/en/latest/",
            "reddit": "https://www.reddit.com/r/Dandere2x/",
            "telegram": "https://t.me/joinchat/KTRznBIPPNCbHkUqnwT8pA",
            "howitworks": "https://github.com/aka-katto/dandere2x/wiki/How-Dandere2x-Works",
            "github": "https://github.com/aka-katto/dandere2x",
        }

        # Open the link on webbrowser
        webbrowser.open(links[who], new=0)

        self.status("Open link in default browser: " + links[who])


# Get the .glade file
window = DandereGTK(ROOT + os.path.sep + "gui" + os.path.sep + "gtk_dandere2x_gui.glade")

Gtk.main()
