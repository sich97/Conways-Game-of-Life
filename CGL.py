"""
File: CGL.py
-------------------
Developed using python 3.8

I made this as a tribute to John Conway who recently passed away due to the COVID-19 pandemic.

Here is the description of the game from Wikipedia (https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life):
    The Game of Life, also known simply as Life, is a cellular automaton devised
    by the British mathematician John Horton Conway in 1970.
    It is a zero-player game, meaning that its evolution is determined by its initial state, requiring no further input.
    One interacts with the Game of Life by creating an initial configuration and observing how it evolves.
    It is Turing complete and can simulate a universal constructor or any other Turing machine.
"""
import tkinter
from tkinter import filedialog
import random
import time
from timeit import default_timer as timer
from datetime import datetime
import pathlib

VERBOSE = False
PRINT_INTRO = False
DEFAULT_CANVAS_HEIGHT = 100
DEFAULT_CANVAS_WIDTH = DEFAULT_CANVAS_HEIGHT
DEFAULT_MAX_FRAMERATE = 30
DEFAULT_MIN_AUTO_SEED_PERCENT = 5
DEFAULT_MAX_AUTO_SEED_PERCENT = 20


def main():
    """
    Initializes. Then starts the game loop, from within another game loop can be called.
    :return: None
    """
    # Intro message
    if PRINT_INTRO:
        print_intro()

    # Initialization
    if VERBOSE:
        print("Starting initialization")
    drawn_cells, pause_signal, canvas, restart_button, pause_button, current_seed, canvas_height_input,\
        canvas_width_input, next_frame_signal, next_frame_button, max_framerate, min_auto_seed_percent,\
        max_auto_seed_percent = initialize()
    if VERBOSE:
        print("Initialization done")

    # Game loop
    game_loop(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, canvas, max_framerate, pause_signal,
              pause_button, "new", current_seed, canvas_height_input, canvas_width_input, next_frame_signal,
              next_frame_button)


def print_intro():
    """
    Prints an intro message.
    :return: None
    """
    time.sleep(1)
    print("Welcome to an amateurs recreation of Conway's Game of Life!")
    time.sleep(2)
    print("John Conway invented this game, which is based on three simple rules:")
    time.sleep(2)
    print("\t1: Any living cell with less than 2 neighbouring cells dies of celibacy")
    time.sleep(2)
    print("\t2: Any living cell with more than 3 neighbouring cells dies of overpopulation")
    time.sleep(2)
    print("\t3: Any dead cell with exactly 3 neighbouring cells is reincarnated")
    time.sleep(3)
    print("Imagine being reincarnated as a pixel.")
    time.sleep(2)
    print("yikes..")
    time.sleep(2)
    print("Anyways. One could say John Conway passed away due to the rule of overpopulation.")
    time.sleep(4)
    print("He died of COVID-19 just recently. That's why I decided to recreate his game, in tribute.")
    time.sleep(4)
    print("DISCLAIMER: I am not to be held responsible for any existential crisis as a result of contemplating"
          " simulation theory.\nProceed at your own caution...")
    time.sleep(1)
    print("To disable this intro message, change the global variable PRINT_INTRO to False")


def initialize():
    """
    Instantiates a couple of variables which will be used later
    :return: drawn_cells (dict), pause_signal (Signal), canvas (tkinter.Canvas),
    button_new_sim (tkinter.Button), button_pause_sim (tkinter.Button), current_seed (list),
    canvas_height_input (tkinter.Entry), canvas_width_input (tkinter.Entry), next_frame_signal (Signal),
    next_frame_button (tkinter.Button), max_framerate (tkinter.IntVar), min_auto_seed_percent (tkinter.IntVar),
    max_auto_seed_percent (tkinter.IntVar)
    """
    drawn_cells = {}
    current_seed = []

    # Creates the graphical window
    canvas, button_new_sim, button_pause_sim, canvas_height_input,\
        canvas_width_input, next_frame_button, min_auto_seed_percent,\
        max_auto_seed_percent, max_framerate, pause_signal, next_frame_signal = create_gui("Conway's Game of Life",
                                                                                           drawn_cells, current_seed)

    return drawn_cells, pause_signal, canvas, button_new_sim, button_pause_sim, current_seed,\
        canvas_height_input, canvas_width_input, next_frame_signal, next_frame_button, max_framerate,\
        min_auto_seed_percent, max_auto_seed_percent


def game_loop(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, canvas, max_framerate, pause_signal,
              pause_button, mode, current_seed, canvas_height_input, canvas_width_input, next_frame_signal,
              next_frame_button):
    """
    Creates and runs a simulation
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: tkinter.IntVar
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: tkinter.IntVar
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param canvas: The instance of a tkinter canvas that visualizes the game
    :type canvas: tkinter.Canvas
    :param max_framerate: The maximum amount of times per second the program will run this loop
    :type max_framerate: tkinter.IntVar
    :param pause_signal: The signal which controls whether or not to pause the loop
    :type pause_signal: tkinter.BooleanVar
    :param pause_button: The button which changes the pause_signal
    :type pause_button: tkinter.Button
    :param mode: Whether or not to create a new simulation, load existing one or simply replay the current one
    :type mode: str
    :param current_seed: The seed that determines which cells start as alive or not
    :type current_seed: list of lists
    :param canvas_height_input: The GUI input box for changing the canvas height
    :type canvas_height_input: tkinter.Entry
    :param canvas_width_input: The GUI input box for changing the canvas width
    :type canvas_width_input: tkinter.Entry
    :param next_frame_signal: The signal which controls whether or not to move to the next frame
    while the simulation is paused
    :type next_frame_signal: tkinter.BooleanVar
    :param next_frame_button: The button which changes the next_frame_signal
    :type next_frame_button: tkinter.Button
    :return: None
    """
    # Create new simulation
    grid = create_simulation(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, canvas, mode,
                             current_seed, canvas_height_input, canvas_width_input)

    # Run simulation
    run_simulation(max_framerate, drawn_cells, pause_signal, canvas, pause_button, grid, next_frame_signal,
                   next_frame_button)


def load_seed_from_file(current_seed):
    """
    Have the user choose a file to use as seed and then load it into memory.
    :param current_seed: The seed that determines which cells start as alive or not
    :type current_seed: list of lists
    :return: current_seed (list of lists), canvas_height (int), canvas_width (int)
    """
    # Create a new instance of tkinter
    root = tkinter.Tk()

    # Hide the tkinter window
    root.withdraw()

    # Then bring up the file dialog for the user to chose file to use as seed
    root.update()
    root.filename = filedialog.askopenfilename(initialdir="seeds/", title="Select file",
                                               filetypes=(("seed files", "*.seed"), ("all files", "*.*")))

    # Loads seed from file
    if VERBOSE:
        print("Parsing file")

    current_seed.clear()
    with open(root.filename, "r") as file:
        for line_number, line in enumerate(file):
            # Remove string characters
            cell = line.replace("'", "")
            cell = cell.replace("\n", "")
            cell = cell.replace("[", "")
            cell = cell.replace("]", "")
            cell = cell.replace(" ", "")

            # Turn it into a list
            cell = cell.split(",")
            y = int(cell[0])
            x = int(cell[1])

            # The first line tells us the canvas size used for the saved seed
            if line_number == 0:
                canvas_height = y
                canvas_width = x

            # Add the cell to the current seed
            else:
                cell = [y, x]
                current_seed.append(cell)

    if VERBOSE:
        print("Parsing complete")

    return canvas_height, canvas_width


def create_gui(title, drawn_cells, current_seed):
    """
    Uses tkinter to create a graphical user interface for visualizing the simulation and controlling the program.
    :param title: The window title
    :type title: string
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param current_seed: The seed that determines which cells start as alive or note
    :type current_seed: list of lists
    :return: canvas (tkinter.Canvas), button_new_sim (tkinter.Button),
    button_pause_sim (tkinter.Button), canvas_height_input (tkinter.Entry), canvas_width_input (tkinter.Entry),
    min_seed_percent (tkinter.IntVar), max_seed_percent (tkinter.IntVar), max_framerate (tkinter.IntVar),
    pause_signal (tkinter.BooleanVar), next_frame_signal (tkinter.BooleanVar)
    """
    if VERBOSE:
        print("Creating canvas")

    # Sets default variables
    if DEFAULT_CANVAS_HEIGHT < 36:
        canvas_height = 36
    else:
        canvas_height = DEFAULT_CANVAS_HEIGHT

    if DEFAULT_CANVAS_WIDTH < 36:
        canvas_width = 36
    else:
        canvas_width = DEFAULT_CANVAS_WIDTH

    # Creating the main window
    window = tkinter.Tk()
    window.minsize(height=canvas_height, width=canvas_width)
    window.title(title)

    # Creating the settings frame
    settings_frame = tkinter.Frame(window)
    settings_frame.grid(row=0, column=0, padx=10, pady=10)

    # Creating the canvas frame
    canvas_frame = tkinter.Frame(window)
    canvas_frame.grid(row=0, column=1, padx=10, pady=10)

    # The canvas that the cells are drawn onto
    canvas = tkinter.Canvas(canvas_frame, height=canvas_height, width=canvas_width, bg="black")

    # Seed_percent inputs
    min_seed_percent, max_seed_percent, min_seed_percent_label, max_seed_percent_label,\
        min_seed_percent_input, max_seed_percent_input, min_seed_percent_input_status,\
        max_seed_percent_input_status = create_seed_percent_inputs(settings_frame)

    # Canvas_size inputs
    canvas_height_label, canvas_height_input, canvas_width_label, canvas_width_input, canvas_height_input_status,\
        canvas_width_input_status = create_canvas_size_inputs(settings_frame)

    # Max framerate inputs
    max_framerate_label, max_framerate_input, max_framerate,\
        max_framerate_input_status = create_max_framerate_inputs(settings_frame)

    # Load defaults button
    button_load_defaults = tkinter.Button(settings_frame, text="Load defaults",
                                          command=lambda: load_defaults(min_seed_percent_input, max_seed_percent_input,
                                                                        canvas_height_input, canvas_width_input,
                                                                        max_framerate_input))

    # Apply settings button
    button_apply_settings = tkinter.Button(settings_frame, text="Apply settings",
                                           command=lambda: apply_settings(canvas, canvas_height_input,
                                                                          canvas_width_input, min_seed_percent_input,
                                                                          max_seed_percent_input, min_seed_percent,
                                                                          max_seed_percent,
                                                                          min_seed_percent_input_status,
                                                                          max_seed_percent_input_status,
                                                                          canvas_height_input_status,
                                                                          canvas_width_input_status,
                                                                          max_framerate_input, max_framerate,
                                                                          max_framerate_input_status))

    # Button for pausing the simulation
    pause_signal = tkinter.BooleanVar(canvas_frame, False, "pause_signal")
    button_pause_sim = tkinter.Button(canvas_frame, text="Pause",
                                      command=lambda: pause_signal.set(get_opposite_boolean(pause_signal.get())))

    # Button for manually moving to the next frame while the simulation is paused
    next_frame_signal = tkinter.BooleanVar(canvas_frame, False, "next_frame_signal")
    next_frame_button = tkinter.Button(canvas_frame, text="Next frame",
                                       command=lambda: next_frame_signal.set(get_opposite_boolean(
                                           next_frame_signal.get())))

    # Button for replaying the current simulation
    button_replay_sim = create_sim_mode_buttons(min_seed_percent, max_seed_percent, drawn_cells,
                                                canvas_frame, canvas, max_framerate, pause_signal, button_pause_sim,
                                                "Replay", current_seed, canvas_height_input, canvas_width_input,
                                                next_frame_signal, next_frame_button)

    # Button for creating a new simulation
    button_new_sim = create_sim_mode_buttons(min_seed_percent, max_seed_percent, drawn_cells, canvas_frame,
                                             canvas, max_framerate, pause_signal, button_pause_sim, "New",
                                             current_seed, canvas_height_input, canvas_width_input, next_frame_signal,
                                             next_frame_button)

    # Button for loading an existing simulation
    button_load_sim = create_sim_mode_buttons(min_seed_percent, max_seed_percent, drawn_cells, canvas_frame,
                                              canvas, max_framerate, pause_signal, button_pause_sim, "Load",
                                              current_seed, canvas_height_input, canvas_width_input, next_frame_signal,
                                              next_frame_button)

    # Arrange the widgets on screen
    # Settings frame
    button_load_defaults.grid(row=0, column=1)
    min_seed_percent_label.grid(row=1, column=0)
    min_seed_percent_input.grid(row=1, column=1)
    min_seed_percent_input_status.grid(row=1, column=2)
    max_seed_percent_label.grid(row=2, column=0)
    max_seed_percent_input.grid(row=2, column=1)
    max_seed_percent_input_status.grid(row=2, column=2)
    canvas_height_label.grid(row=3, column=0)
    canvas_height_input.grid(row=3, column=1)
    canvas_height_input_status.grid(row=3, column=2)
    canvas_width_label.grid(row=4, column=0)
    canvas_width_input.grid(row=4, column=1)
    canvas_width_input_status.grid(row=4, column=2)
    max_framerate_label.grid(row=5, column=0)
    max_framerate_input.grid(row=5, column=1)
    max_framerate_input_status.grid(row=5, column=2)
    button_apply_settings.grid(row=6, column=1)

    # Canvas frame
    canvas.grid(row=0, column=1)
    button_pause_sim.grid(row=1, column=1)
    button_new_sim.grid(row=2, column=0)
    button_replay_sim.grid(row=2, column=1)
    button_load_sim.grid(row=2, column=2)

    canvas.update()

    if VERBOSE:
        print("Canvas created")

    return canvas, button_new_sim, button_pause_sim, canvas_height_input, canvas_width_input, next_frame_button,\
        min_seed_percent, max_seed_percent, max_framerate, pause_signal, next_frame_signal


def get_opposite_boolean(boolean):
    if boolean:
        return False
    else:
        return True


def create_max_framerate_inputs(settings_frame):
    """
    Instantiates the labels, inputs and variables for controlling the max framerate
    :param settings_frame: The frame in which these widgets will be drawn
    :type settings_frame: tkinter.Frame
    :return: max_framerate_label (tkinter.Label), max_framerate_input (tkinter.Entry), max_framerate (tkinter.IntVar),
    max_framerate_input_status (tkinter.Label)
    """
    max_framerate = tkinter.IntVar(settings_frame, DEFAULT_MAX_FRAMERATE)
    max_framerate_label = tkinter.Label(settings_frame, text="Max framerate: ")
    max_framerate_input = tkinter.Entry(settings_frame)
    max_framerate_input.insert(0, max_framerate.get())
    max_framerate_input_status = tkinter.Label(settings_frame, text="Default value")

    return max_framerate_label, max_framerate_input, max_framerate, max_framerate_input_status


def apply_settings(canvas, canvas_height_input, canvas_width_input, min_seed_percent_input, max_seed_percent_input,
                   min_seed_percent, max_seed_percent, min_seed_percent_input_status, max_seed_percent_input_status,
                   canvas_height_input_status, canvas_width_input_status, max_framerate_input, max_framerate,
                   max_framerate_input_status):
    """
    Applies the settings in the settings frame
    :param canvas: The canvas that the cells are drawn onto
    :type canvas: tkinter.Canvas
    :param canvas_height_input: The input field for the canvas height
    :type canvas_height_input: tkinter.Entry
    :param canvas_width_input:  The input field for the canvas width
    :type canvas_width_input: tkinter.Entry
    :param min_seed_percent_input: The input field for the minimum seed percentage
    :type min_seed_percent_input: tkinter.Entry
    :param max_seed_percent_input: The input field for the maximum seed percentage
    :type max_seed_percent_input: tkinter.Entry
    :param min_seed_percent: The variable for the minimum seed percentage
    :type min_seed_percent: tkinter.IntVar
    :param max_seed_percent: The variable for the maximum seed percentage
    :type max_seed_percent: tkinter.IntVar
    :param min_seed_percent_input_status: Outputs to the user the status of the input
    :type min_seed_percent_input_status: tkinter.Label
    :param max_seed_percent_input_status: Outputs to the user the status of the input
    :type max_seed_percent_input_status: tkinter.Label
    :param canvas_height_input_status: Outputs to the user the status of the input
    :type canvas_height_input_status: tkinter.Label
    :param canvas_width_input_status: Outputs to the user the status of the input
    :type canvas_width_input_status: tkinter.Label
    :param max_framerate_input: The input field for the max framerate
    :type max_framerate_input: tkinter.Entry
    :param max_framerate: The variable for the maximum framerate
    :type max_framerate: tkinter.IntVar
    :param max_framerate_input_status: Outputs to the user the status of the input
    :type max_framerate_input_status: tkinter.Label
    :return: None
    """
    # Apply canvas size settings
    new_height = canvas_height_input.get()
    new_width = canvas_width_input.get()

    if new_height != "":
        try:
            new_height = int(new_height)
            canvas_height_input_status.config(text="OK")
        except ValueError:
            canvas_height_input_status.config(text="ERROR: Not an integer!")
            new_height = canvas.winfo_height() - 2

        canvas.config(height=new_height)

    else:
        canvas_height_input_status.config(text="ERROR: No input!")

    if new_width != "":
        try:
            new_width = int(new_width)
            canvas_width_input_status.config(text="OK")
        except ValueError:
            canvas_width_input_status.config(text="ERROR: Not an integer!")
            new_width = canvas.winfo_width() - 2

        canvas.config(width=new_width)

    else:
        canvas_width_input_status.config(text="ERROR: No input!")

    # Apply seed settings
    new_min_seed_percent = min_seed_percent_input.get()
    new_max_seed_percent = max_seed_percent_input.get()

    if new_min_seed_percent != "":
        try:
            new_min_seed_percent = int(new_min_seed_percent)
            min_seed_percent_input_status.config(text="OK")
        except ValueError:
            min_seed_percent_input_status.config(text="ERROR: Not an integer!")
            new_min_seed_percent = min_seed_percent.get()

        min_seed_percent.set(new_min_seed_percent)

    else:
        min_seed_percent_input_status.config(text="ERROR: No input!")

    if new_max_seed_percent != "":
        try:
            new_max_seed_percent = int(new_max_seed_percent)
            max_seed_percent_input_status.config(text="OK")
        except ValueError:
            max_seed_percent_input_status.config(text="ERROR: Not an integer!")
            new_max_seed_percent = max_seed_percent.get()

        max_seed_percent.set(new_max_seed_percent)

    else:
        max_seed_percent_input_status.config(text="ERROR: No input!")

    # Apply max framerate settings
    new_max_framerate = max_framerate_input.get()

    if new_max_framerate != "":
        try:
            new_max_framerate = int(new_max_framerate)
            max_framerate_input_status.config(text="OK")
        except ValueError:
            max_framerate_input_status.config(text="ERROR: Not an integer!")
            new_max_framerate = max_framerate.get()

        max_framerate.set(new_max_framerate)

    else:
        max_framerate_input_status.config(text="ERROR: No input!")


def load_defaults(min_seed_percent_input, max_seed_percent_input, canvas_height_input, canvas_width_input,
                  max_framerate_input):
    """
    Sets all the input fields and their corresponding status label to the defaults
    :param min_seed_percent_input: The input field for the minimum seed percentage
    :type min_seed_percent_input: tkinter.Entry
    :param max_seed_percent_input: The input field for the maximum seed percentage
    :type max_seed_percent_input: tkinter.Entry
    :param canvas_height_input: The input field for the canvas height
    :type canvas_height_input: tkinter.Entry
    :param canvas_width_input: The input field for the canvas width
    :type canvas_width_input: tkinter.Entry
    :param max_framerate_input: The input field for the max framerate
    :type max_framerate_input: tkinter.Entry
    :return:
    """
    # Seed percent inputs
    min_seed_percent_input.delete(0, tkinter.END)
    min_seed_percent_input.insert(0, DEFAULT_MIN_AUTO_SEED_PERCENT)

    max_seed_percent_input.delete(0, tkinter.END)
    max_seed_percent_input.insert(0, DEFAULT_MAX_AUTO_SEED_PERCENT)

    # Canvas size inputs
    canvas_height_input.delete(0, tkinter.END)
    canvas_height_input.insert(0, DEFAULT_CANVAS_HEIGHT)

    canvas_width_input.delete(0, tkinter.END)
    canvas_width_input.insert(0, DEFAULT_CANVAS_WIDTH)

    # Max framerate input
    max_framerate_input.delete(0, tkinter.END)
    max_framerate_input.insert(0, DEFAULT_MAX_FRAMERATE)


def create_seed_percent_inputs(settings_frame):
    """
    Instantiates the labels, inputs and variables for controlling the seed percentages
    :param settings_frame: The frame in which these widgets will be drawn
    :type settings_frame: tkinter.Frame
    :return: min_seed_percent (tkinter.IntVar), max_seed_percent (tkinter.IntVar),
    min_seed_percent_label (tkinter.Label), max_seed_percent_label (tkinter.Label),
    min_seed_percent_input (tkinter.Entry), max_seed_percent_input (tkinter.Entry),
    min_seed_percent_input_status (tkinter.Label), max_seed_percent_input_status (tkinter.Label)
    """
    min_seed_percent = tkinter.IntVar(settings_frame, DEFAULT_MIN_AUTO_SEED_PERCENT)
    max_seed_percent = tkinter.IntVar(settings_frame, DEFAULT_MAX_AUTO_SEED_PERCENT)
    min_seed_percent_label = tkinter.Label(settings_frame, text="Minimum seed percentage: ")
    max_seed_percent_label = tkinter.Label(settings_frame, text="Maximum seed percentage: ")
    min_seed_percent_input = tkinter.Entry(settings_frame)
    max_seed_percent_input = tkinter.Entry(settings_frame)
    min_seed_percent_input.insert(0, min_seed_percent.get())
    max_seed_percent_input.insert(0, max_seed_percent.get())
    min_seed_percent_input_status = tkinter.Label(settings_frame, text="Default value")
    max_seed_percent_input_status = tkinter.Label(settings_frame, text="Default value")

    return min_seed_percent, max_seed_percent, min_seed_percent_label, max_seed_percent_label,\
        min_seed_percent_input, max_seed_percent_input, min_seed_percent_input_status, max_seed_percent_input_status


def create_sim_mode_buttons(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, canvas_frame, canvas,
                            max_framerate, pause_signal, button_pause_sim, mode, current_seed, canvas_height_input,
                            canvas_width_input, next_frame_signal, next_frame_button):
    """
    Creates a button that will call the game loop function with a mode determined by the 'mode' parameter
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: tkinter.IntVar
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: tkinter.IntVar
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param canvas_frame: The parent window
    :type canvas_frame: tkinter.Frame
    :param canvas: The canvas where the cells will be drawn
    :type canvas: tkinter.Canvas
    :param max_framerate: The maximum amount of times per second the program will run this loop
    :type max_framerate: tkinter.IntVar
    :param pause_signal: The signal which controls whether or not to pause the loop
    :type pause_signal: tkinter.BooleanVar
    :param button_pause_sim: The button which controls the pause signal
    :type button_pause_sim: tkinter.Button
    :param mode: Which mode the new simulation will be (replay of the current one, create a new one
    or load an existing one)
    :type mode: str
    :param current_seed: The seed that determines which cells start as alive or note
    :type current_seed: list of lists
    :param canvas_height_input: The GUI input box for changing the canvas height
    :type canvas_height_input: tkinter.Entry
    :param canvas_width_input: The GUI input box for changing the canvas width
    :type canvas_width_input: tkinter.Entry
    :param next_frame_signal: The signal which controls whether or not to move to the next frame
    while the simulation is paused
    :type next_frame_signal: tkinter.BooleanVar
    :param next_frame_button: The button which changes the next_frame_signal
    :type next_frame_button: tkinter.Button
    :return: vars()[button_name] (tkinter.Button)
    """
    mode_lowercase = mode.lower()
    button_name = "button_" + mode_lowercase + "_sim"
    vars()[button_name] = tkinter.Button(canvas_frame, text=mode, command=lambda: game_loop(min_auto_seed_percent,
                                                                                            max_auto_seed_percent,
                                                                                            drawn_cells,
                                                                                            canvas, max_framerate,
                                                                                            pause_signal,
                                                                                            button_pause_sim,
                                                                                            mode_lowercase,
                                                                                            current_seed,
                                                                                            canvas_height_input,
                                                                                            canvas_width_input,
                                                                                            next_frame_signal,
                                                                                            next_frame_button))

    return vars()[button_name]


def create_canvas_size_inputs(settings_frame):
    """
    Creates the labels, input fields and buttons for changing the canvas size through the GUI
    :param settings_frame: The parent graphical window container
    :type settings_frame: tkinter.Frame
    :return: canvas_height_label (tkinter.Label), canvas_height_input (tkinter.Entry),
    canvas_width_label (tkinter.Label), canvas_width_input (tkinter.Label)
    """
    # Canvas height input
    canvas_height_label = tkinter.Label(settings_frame, text="Canvas height: ")
    canvas_height_input = tkinter.Entry(settings_frame)
    canvas_height_input.insert(0, DEFAULT_CANVAS_HEIGHT)
    canvas_height_input_status = tkinter.Label(settings_frame, text="Default value")

    # Canvas width input
    canvas_width_label = tkinter.Label(settings_frame, text="Canvas width: ")
    canvas_width_input = tkinter.Entry(settings_frame)
    canvas_width_input.insert(0, DEFAULT_CANVAS_WIDTH)
    canvas_width_input_status = tkinter.Label(settings_frame, text="Default value")

    return canvas_height_label, canvas_height_input, canvas_width_label, canvas_width_input,\
        canvas_height_input_status, canvas_width_input_status


def create_simulation(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, canvas, mode, current_seed,
                      canvas_height_input, canvas_width_input):
    """
    Resets necessary variables and generates new values for next simulation.
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: tkinter.IntVar
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: tkinter.IntVar
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param canvas: The instance of a tkinter canvas that visualizes the game
    :type canvas: tkinter.Canvas
    :param mode: Whether or not to create a new simulation, load an existing one or simply replay the current one
    :type mode: str
    :param current_seed: The seed that determines which cells start as alive or not
    :type current_seed: list of lists
    :param canvas_height_input: The GUI input box for changing the canvas height
    :type canvas_height_input: tkinter.Entry
    :param canvas_width_input: The GUI input box for changing the canvas width
    :type canvas_width_input: tkinter.Entry
    :return: grid (list of lists)
    """
    # Reset
    if VERBOSE:
        print("Resetting variables")

    grid = []
    for rectangle_name in drawn_cells:
        canvas.delete(drawn_cells[rectangle_name])

    canvas_height = 0
    canvas_width = 0
    if not mode == "load":
        canvas_height = canvas.winfo_height() - 2
        canvas_width = canvas.winfo_width() - 2

    if VERBOSE:
        print("Variables reset")

    # If generating new seed
    if mode == "new":
        generate_seed(canvas_height, canvas_width, min_auto_seed_percent, max_auto_seed_percent, current_seed)

    # If loading seed from file
    elif mode == "load":
        canvas_height, canvas_width = load_seed_from_file(current_seed)

        # Set the entry boxes for changing canvas sizes to the newly loaded sizes
        canvas_height_input.delete(0, tkinter.END)
        canvas_height_input.insert(0, canvas_height)
        canvas_width_input.delete(0, tkinter.END)
        canvas_width_input.insert(0, canvas_width)

    # Resize canvas
    if VERBOSE:
        print("Resizing canvas")

    canvas.config(height=canvas_height, width=canvas_width)

    if VERBOSE:
        print("Canvas resized")

    # Creates the list of cells
    if VERBOSE:
        print("Creating list of cells")
    for i in range(canvas_height):
        grid.append([0] * canvas_width)
    if VERBOSE:
        print("List of cells created")

    # Seed
    apply_seed(grid, current_seed)

    return grid


def generate_seed(canvas_height, canvas_width, min_auto_seed_percent, max_auto_seed_percent, current_seed):
    """
    Generates a list of cells that will be alive initially.
    :param canvas_height: The height of the canvas in pixels
    :type canvas_height: int
    :param canvas_width: The width of the canvas in pixels
    :type canvas_width: int
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: tkinter.IntVar
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: tkinter.IntVar
    :param current_seed: The seed that determines which cells start as alive or not
    :type current_seed: list of lists
    :return: None
    """
    # Prepares variables
    if VERBOSE:
        print("Preparing variables")

    current_seed.clear()
    min_alive_cells = int((canvas_height * canvas_width) * (min_auto_seed_percent.get() / 100))
    max_alive_cells = int((canvas_height * canvas_width) * (max_auto_seed_percent.get() / 100))
    amount_of_cells_to_seed = random.randint(min_alive_cells, max_alive_cells)

    if VERBOSE:
        print("Variables prepared")
        print("There will be " + str(amount_of_cells_to_seed) + " living cells initially")

    # Generates random seed
    if VERBOSE:
        print("Generating random seed")

    for i in range(amount_of_cells_to_seed):
        # Picks out a random row in the grid
        y = random.randint(0, canvas_height - 1)

        # Picks out a random cell in the row and makes it alive
        x = random.randint(0, canvas_width - 1)

        # Add it to current_seed to allow for saving the seed to file and / or resetting simulation with same seed
        current_seed.append([y, x])

    if VERBOSE:
        print("Random seed generated")

    # Save seed to file, named with date and time (.seed extension)
    if VERBOSE:
        print("Saving seed")

    saved_seed_file_path = save_seed_to_file(current_seed, canvas_height, canvas_width)

    if VERBOSE:
        print("Seed saved to: " + str(saved_seed_file_path))

    return current_seed


def save_seed_to_file(current_seed, canvas_height, canvas_width):
    """
    Saves the current seed as a file.
    Location: seeds/
    Filename: yyyy.mm.dd.HH.MM.SS
    File extension: .seed
    :param current_seed: A list of lists containing y, x coordinates of cells that start as alive
    :type current_seed: list of lists
    :param canvas_height: The height of the canvas in pixels
    :type canvas_height: int
    :param canvas_width: The width of the canvas in pixels
    :type canvas_width: int
    :return: filename
    """
    # Determines filename including path
    if VERBOSE:
        print("Determine filename and path")

    now = datetime.now()
    filename = now.strftime("%Y.%m.%d.%H.%M.%S") + ".seed"
    seed_dir = pathlib.Path("seeds/")
    seed_dir.mkdir(parents=True, exist_ok=True)
    file_path = pathlib.Path("seeds/" + filename)

    if VERBOSE:
        print("Filename and path determined")

    # Stores seed in file, one line per cell that starts as alive
    if VERBOSE:
        print("Writing seed to file")

    with file_path.open('w') as file:
        file.write("[" + str(canvas_height) + ", " + str(canvas_width) + "]\n")
        for cell in current_seed:
            file.write("%s\n" % cell)

    if VERBOSE:
        print("Seed written to file")

    return file_path


def apply_seed(grid, seed):
    """
    For every cell listed in seed, make the corresponding cell in grid alive
    :param grid: The 2D list of cells
    :type grid: list of lists
    :param seed: A list of lists containing coordinates to cells which will shall start as alive
    :type seed: list of lists
    :return: None
    """
    if VERBOSE:
        print("Applying seed")

    for cell in seed:
        y = cell[0]
        x = cell[1]
        grid[y][x] = 1

    if VERBOSE:
        print("Seed applied")


def run_simulation(max_framerate, drawn_cells, pause_signal, canvas, pause_button, grid, next_frame_signal,
                   next_frame_button):
    """
    Generates new generations, draws them on screen, then repeats.
    :param max_framerate: The maximum amount of times per second the program will run this loop
    :type max_framerate: tkinter.IntVar
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param pause_signal: The signal which controls whether or not to pause the loop
    :type pause_signal: tkinter.BooleanVar
    :param canvas: The instance of a tkinter canvas that visualizes the game
    :type canvas: tkinter.Canvas
    :param pause_button: The button which changes the pause_signal
    :type pause_button: tkinter.Button
    :param grid: The 2D list of cells
    :type grid: list of lists
    :param next_frame_signal: The signal which controls whether or not to move to the next frame
    while the simulation is paused
    :type next_frame_signal: tkinter.BooleanVar
    :param next_frame_button: The button which changes the next_frame_signal
    :type next_frame_button: tkinter.Button
    :return: None
    """

    # Draws the first frame
    if VERBOSE:
        print("Drawing first frame")

    draw_canvas(canvas, grid, drawn_cells)
    canvas.update()

    if VERBOSE:
        print("First frame drawn")

    while True:
        # Start measuring time
        start = timer()

        # Reset
        pause_button.config(text="Pause")
        next_frame_button.grid_remove()
        next_frame_signal.set(False)

        # If the pause button has been pressed
        if pause_signal.get():
            # Set the pause button's text to "Resume"
            pause_button.config(text="Resume")

            # Show the next_frame_button
            next_frame_button.grid(row=0, column=2)

            # Wait for pause_signal to be false, or next_frame_signal to be true
            while pause_signal.get() and not next_frame_signal.get():
                canvas.update()
                time.sleep(0.01)

        # Calculates the next generation
        if VERBOSE:
            print("Calculating next generation")
        cells_to_be_killed, cells_to_be_revived,\
            living_cells_before_next_generation = calculate_next_generation(grid)
        if VERBOSE:
            print("Creating next generation")
        create_next_generation(grid, cells_to_be_killed, cells_to_be_revived)
        if VERBOSE:
            print("Next generation complete")
        cells_alive = living_cells_before_next_generation + len(cells_to_be_revived) - len(cells_to_be_killed)
        if VERBOSE:
            print("\tNumber of cells alive: " + str(cells_alive))

        # Visualize the simulation
        if VERBOSE:
            print("Updating visual representation")

        draw_canvas(canvas, grid, drawn_cells)
        canvas.update()

        if VERBOSE:
            print("Visual representation updated")

        # Limits automatic loop to max_framerate
        end = timer()
        loop_time = end - start
        max_framerate_calculated = 1 / max_framerate.get()
        while loop_time < max_framerate_calculated:
            if VERBOSE:
                print("Held by max framerate")

            end = timer()
            loop_time = end - start
            canvas.update()
            time.sleep(0.01)


def draw_canvas(canvas, grid, drawn_cells):
    """
    If a cell is alive, make it white, if not then make it black.
    :param canvas: The instance of a tkinter canvas that visualizes the game
    :type canvas: tkinter.Canvas
    :param grid: The 2D list of cells
    :type grid: list of lists
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :return: None
    """
    if VERBOSE:
        print("Drawing canvas")

    # For every row in the grid
    for y in range(len(grid)):
        # For every cell in the row
        for x in range(len(grid[y])):
            # Create a name which will be the name of the object when instantiating the pixel, corresponds with y, x
            rectangle_name = str(y) + "_" + str(x)

            # Is this cell already drawn on canvas?
            exists = is_drawn_before(rectangle_name, drawn_cells)

            # If this cell is alive
            if grid[y][x] == 1:
                # And is not already drawn on canvas
                if not exists:
                    # Create a new instance of a pixel and register it in drawn_cells with object name as rectangle_name
                    vars()[rectangle_name] = canvas.create_rectangle(x, y, x, y, fill="green", outline="")
                    drawn_cells[rectangle_name] = vars()[rectangle_name]

            # If this cell is not alive
            else:
                # But is drawn on canvas
                if exists:
                    # Destroy the corresponding instance of a pixel and remove it from the drawn_cells dictionary
                    canvas.delete(drawn_cells[rectangle_name])
                    drawn_cells.pop(rectangle_name)

    if VERBOSE:
        print("Canvas drawn")


def is_drawn_before(rectangle_name, drawn_cells):
    """
    Checks if a specific canvas widget's reference exists in the dictionary of already rendered widgets.
    :param rectangle_name: The object name to check
    :type rectangle_name: string
    :param drawn_cells: The dictionary of already rendered widgets (pixels in this case)
    :type drawn_cells: dict
    :return: bool
    """
    if rectangle_name in drawn_cells:
        return True
    else:
        return False


def calculate_next_generation(grid):
    """
    Determines which cells will live or die based on the three fundamental rules of the game.
    :param grid: The 2D list of cells
    :type grid: list of lists
    :return: cells_to_be_killed (2D list), cells_to_be_revived (2D list), living_cells_before_next_generation (int)
    """
    if VERBOSE:
        print("Calculating next generation")

    # Instantiates variables
    cells_to_be_killed = []
    cells_to_be_revived = []
    living_cells_before_next_generation = 0

    # For every row in the grid
    for y in range(len(grid)):
        # For every cell in the row
        for x in range(len(grid[y])):
            # Reset variable
            living_neighbours = 0

            # For every possible neighbour (those outside of scope are accounted for in the check_neighbour function)
            for i in range(8):
                # Add 1 to living_neighbours if the neighbour exists and is alive
                neighbour = check_neighbour(y, x, i, grid)
                living_neighbours += neighbour

            # Determine the state of this cell in the next generation based on the amount of living neighbours

            # If currently alive
            if grid[y][x] == 1:
                # To keep track of total amount of living cells in each generation
                living_cells_before_next_generation += 1

                # Rule of starvation and overpopulation
                if living_neighbours < 2 or living_neighbours > 3:
                    # Dies in next generation
                    cells_to_be_killed.append([y, x])

            # If currently dead
            else:
                # Rule of reproduction
                if living_neighbours == 3:
                    # Resurrects in next generation
                    cells_to_be_revived.append([y, x])

    if VERBOSE:
        print("Generation calculated")

    return cells_to_be_killed, cells_to_be_revived, living_cells_before_next_generation


def check_neighbour(y, x, i, grid):
    """
    Checks the state of a neighbour in i direction of the cell at y, x.
    The direction corresponds with cardinal directions like this: 0 being north, 2 being east, 7 being north-west.
    :param y: The y coordinate the origin cell has in the list of cells
    :type y: int
    :param x: The x coordinate the origin cell has in the list of cells
    :type x: int
    :param i: The direction in which to check the neighbour's state
    :type i: int
    :param grid: The 2D list of cells
    :type grid: list of lists
    :return: neighbour_state (int, 0 or 1)
    """
    # North neighbour
    if i == 0:
        try:
            neighbour_state = grid[y - 1][x]
        except IndexError:
            neighbour_state = 0
        return neighbour_state

    # North-east neighbour
    if i == 1:
        try:
            neighbour_state = grid[y - 1][x + 1]
        except IndexError:
            neighbour_state = 0
        return neighbour_state

    # East neighbour
    if i == 2:
        try:
            neighbour_state = grid[y][x + 1]
        except IndexError:
            neighbour_state = 0
        return neighbour_state

    # South-east neighbour
    if i == 3:
        try:
            neighbour_state = grid[y + 1][x + 1]
        except IndexError:
            neighbour_state = 0
        return neighbour_state

    # South neighbour
    if i == 4:
        try:
            neighbour_state = grid[y + 1][x]
        except IndexError:
            neighbour_state = 0
        return neighbour_state

    # South-west neighbour
    if i == 5:
        try:
            neighbour_state = grid[y + 1][x - 1]
        except IndexError:
            neighbour_state = 0
        return neighbour_state

    # West neighbour
    if i == 6:
        try:
            neighbour_state = grid[y][x - 1]
        except IndexError:
            neighbour_state = 0
        return neighbour_state

    # North-west neighbour
    if i == 7:
        try:
            neighbour_state = grid[y - 1][x - 1]
        except IndexError:
            neighbour_state = 0
        return neighbour_state


def create_next_generation(grid, cells_to_be_killed, cells_to_be_revived):
    """
    Kills and revives cells.
    :param grid: The 2D list of cells
    :type grid: list of lists
    :param cells_to_be_killed: A list of lists containing y and x coordinates of cells that will be killed
    :type cells_to_be_killed: list of lists
    :param cells_to_be_revived: A list of lists containing y and x coordinates of cells that will be killed
    :type cells_to_be_revived: list of lists
    :return: None
    """
    if VERBOSE:
        print("Creating next generation")

    # Kill cells
    if VERBOSE:
        print("Killing cells")

    for cell in range(len(cells_to_be_killed)):
        y = cells_to_be_killed[cell][0]
        x = cells_to_be_killed[cell][1]
        grid[y][x] = 0

    if VERBOSE:
        print("Cells killed")

    # Revive cells
    if VERBOSE:
        print("Reviving cells")

    for cell in range(len(cells_to_be_revived)):
        y = cells_to_be_revived[cell][0]
        x = cells_to_be_revived[cell][1]
        grid[y][x] = 1

    if VERBOSE:
        print("Cells revived")

    if VERBOSE:
        print("Next generation created")


if __name__ == '__main__':
    main()
