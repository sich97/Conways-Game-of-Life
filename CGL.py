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
GET_USER_INPUT = False
DEFAULT_CANVAS_HEIGHT = 100
DEFAULT_CANVAS_WIDTH = DEFAULT_CANVAS_HEIGHT
DEFAULT_MAX_FRAMERATE = 60
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
    drawn_cells, pause_signal, top, canvas, restart_button, pause_button, current_seed, canvas_height_input,\
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
    :return: drawn_cells (dict), pause_signal (Signal), top (tkinter.Tk), canvas (tkinter.Canvas),
    button_new_sim (tkinter.Button), button_pause_sim (tkinter.Button), current_seed (list),
    canvas_height_input (tkinter.Entry), canvas_width_input (tkinter.Entry), next_frame_signal (Signal),
    next_frame_button (tkinter.Button), max_framerate (float), min_auto_seed_percent (float),
    max_auto_seed_percent (float)
    """
    drawn_cells = {}
    pause_signal = Signal("pause_signal", False)
    next_frame_signal = Signal("next_frame_signal", False)
    current_seed = []
    max_framerate = 1 / DEFAULT_MAX_FRAMERATE
    min_auto_seed_percent = DEFAULT_MIN_AUTO_SEED_PERCENT / 100
    max_auto_seed_percent = DEFAULT_MAX_AUTO_SEED_PERCENT / 100

    # Creates the graphical window
    top, canvas, button_new_sim, button_pause_sim, canvas_height_input,\
        canvas_width_input, next_frame_button = create_gui("Conway's Game of Life", pause_signal, min_auto_seed_percent,
                                                           max_auto_seed_percent, drawn_cells, max_framerate,
                                                           current_seed, next_frame_signal)

    return drawn_cells, pause_signal, top, canvas, button_new_sim, button_pause_sim, current_seed,\
        canvas_height_input, canvas_width_input, next_frame_signal, next_frame_button, max_framerate,\
        min_auto_seed_percent, max_auto_seed_percent


def game_loop(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, canvas, max_framerate, pause_signal,
              pause_button, mode, current_seed, canvas_height_input, canvas_width_input, next_frame_signal,
              next_frame_button):
    """
    Creates and runs a simulation
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: float
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: float
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param canvas: The instance of a tkinter canvas that visualizes the game
    :type canvas: tkinter.Canvas
    :param max_framerate: The maximum amount of times per second the program will run this loop
    :type max_framerate: float
    :param pause_signal: The signal which controls whether or not to pause the loop
    :type pause_signal: Signal
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
    :type next_frame_signal: Signal
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


def create_gui(title, pause_signal, min_auto_seed_percent, max_auto_seed_percent, drawn_cells, max_framerate,
               current_seed, next_frame_signal):
    """
    Uses tkinter to create a graphical user interface for visualizing the simulation and controlling the program.
    :param title: The window title
    :type title: string
    :param pause_signal: The signal which controls whether or not to pause the loop
    :type pause_signal: Signal
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: float
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: float
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param max_framerate: The maximum amount of times per second the program will run this loop
    :type max_framerate: float
    :param current_seed: The seed that determines which cells start as alive or note
    :type current_seed: list of lists
    :param next_frame_signal: The signal which controls whether or not to move to the next frame
    while the simulation is paused
    :type next_frame_signal: Signal
    :return: top (tkinter.Tk), canvas (tkinter.Canvas), button_new_sim (tkinter.Button),
    button_pause_sim (tkinter.Button), canvas_height_input (tkinter.Entry), canvas_width_input (tkinter.Entry)
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
    top = tkinter.Tk()
    top.minsize(height=canvas_height, width=canvas_width)
    top.title(title)

    # The canvas that the cells are drawn onto
    canvas = tkinter.Canvas(top, height=canvas_height, width=canvas_width, bg="black")

    # Create canvas_size inputs
    canvas_height_label, canvas_height_input, button_set_canvas_height, canvas_width_label,\
        canvas_width_input, button_set_canvas_width = create_canvas_size_inputs(top, canvas)

    # Button for pausing the simulation
    button_pause_sim = tkinter.Button(top, text="Pause", command=lambda: pause_signal.change_state())

    # Button for manually moving to the next frame while the simulation is paused
    next_frame_button = tkinter.Button(top, text="Next frame", command=lambda: next_frame_signal.change_state())

    # Button for replaying the current simulation
    button_replay_sim = create_sim_mode_buttons(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, top,
                                                canvas, max_framerate, pause_signal, button_pause_sim, "Replay",
                                                current_seed, canvas_height_input, canvas_width_input,
                                                next_frame_signal, next_frame_button)

    # Button for creating a new simulation
    button_new_sim = create_sim_mode_buttons(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, top,
                                             canvas, max_framerate, pause_signal, button_pause_sim, "New",
                                             current_seed, canvas_height_input, canvas_width_input, next_frame_signal,
                                             next_frame_button)

    # Button for loading an existing simulation
    button_load_sim = create_sim_mode_buttons(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, top,
                                              canvas, max_framerate, pause_signal, button_pause_sim, "Load",
                                              current_seed, canvas_height_input, canvas_width_input, next_frame_signal,
                                              next_frame_button)

    # Arrange the widgets on screen
    canvas.grid(row=0, column=1)
    button_pause_sim.grid(row=1, column=1)
    button_replay_sim.grid(row=2, column=0)
    button_new_sim.grid(row=2, column=1)
    button_load_sim.grid(row=2, column=2)
    canvas_height_label.grid(row=3, column=0)
    canvas_height_input.grid(row=3, column=1)
    button_set_canvas_height.grid(row=3, column=2)
    canvas_width_label.grid(row=4, column=0)
    canvas_width_input.grid(row=4, column=1)
    button_set_canvas_width.grid(row=4, column=2)

    canvas.update()

    if VERBOSE:
        print("Canvas created")

    return top, canvas, button_new_sim, button_pause_sim, canvas_height_input, canvas_width_input, next_frame_button


def create_sim_mode_buttons(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, top, canvas,
                            max_framerate, pause_signal, button_pause_sim, mode, current_seed, canvas_height_input,
                            canvas_width_input, next_frame_signal, next_frame_button):
    """
    Creates a button that will call the game loop function with a mode determined by the 'mode' parameter
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: float
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: float
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param top: The parent window
    :type top: tkinter.Tk
    :param canvas: The canvas where the cells will be drawn
    :type canvas: tkinter.Canvas
    :param max_framerate: The maximum amount of times per second the program will run this loop
    :type max_framerate: float
    :param pause_signal: The signal which controls whether or not to pause the loop
    :type pause_signal: Signal
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
    :type next_frame_signal: Signal
    :param next_frame_button: The button which changes the next_frame_signal
    :type next_frame_button: tkinter.Button
    :return: vars()[button_name] (tkinter.Button)
    """
    mode_lowercase = mode.lower()
    button_name = "button_" + mode_lowercase + "_sim"
    vars()[button_name] = tkinter.Button(top, text=mode, command=lambda: game_loop(min_auto_seed_percent,
                                                                                   max_auto_seed_percent, drawn_cells,
                                                                                   canvas, max_framerate, pause_signal,
                                                                                   button_pause_sim, mode_lowercase,
                                                                                   current_seed, canvas_height_input,
                                                                                   canvas_width_input,
                                                                                   next_frame_signal,
                                                                                   next_frame_button))

    return vars()[button_name]


def create_canvas_size_inputs(top, canvas):
    """
    Creates the labels, input fields and buttons for changing the canvas size through the GUI
    :param top: The parent graphical window container
    :type top: tkinter.Tk
    :param canvas: The part of the window that the cells are drawn on
    :type canvas: tkinter.Canvas
    :return: canvas_height_label (tkinter.Label), canvas_height_input (tkinter.Entry),
    button_set_canvas_height (tkinter.Button), canvas_width_label (tkinter.Label), canvas_width_input (tkinter.Label),
    button_set_canvas_width (tkinter.Button)
    """
    # Canvas height input
    canvas_height_label = tkinter.Label(top, text="Canvas height: ")
    canvas_height_input = tkinter.Entry(top)
    canvas_height_input.insert(0, DEFAULT_CANVAS_HEIGHT)
    button_set_canvas_height = tkinter.Button(top, text="Set canvas height",
                                              command=lambda: change_canvas_size("height", canvas, canvas_height_input))

    # Canvas width input
    canvas_width_label = tkinter.Label(top, text="Canvas width: ")
    canvas_width_input = tkinter.Entry(top)
    canvas_width_input.insert(0, DEFAULT_CANVAS_WIDTH)
    button_set_canvas_width = tkinter.Button(top, text="Set canvas width",
                                             command=lambda: change_canvas_size("width", canvas, canvas_width_input))

    return canvas_height_label, canvas_height_input, button_set_canvas_height, canvas_width_label, canvas_width_input,\
        button_set_canvas_width


def change_canvas_size(direction, canvas, entry_box):
    """
    Changes the size of the canvas in the given direction by the amount specified in the entry box
    :param direction: Whether or not the size shall be changed in height or width
    :type direction: str
    :param canvas: The part of the window that stuff is drawn on (?)
    :type canvas: tkinter.Canvas
    :param entry_box: The input field
    :type entry_box: tkinter.Entry
    :return: None
    """
    input_value = entry_box.get()
    if input_value is not None:
        try:
            int_value = int(input_value)
        except ValueError:
            print("You did not input an integer when setting canvas " + direction)
            if direction == "height":
                int_value = canvas.winfo_height() - 2
            else:
                int_value = canvas.winfo_width() - 2

        if direction == "height":
            canvas.config(height=int_value)
        elif direction == "width":
            canvas.config(width=int_value)


def create_simulation(min_auto_seed_percent, max_auto_seed_percent, drawn_cells, canvas, mode, current_seed,
                      canvas_height_input, canvas_width_input):
    """
    Resets necessary variables and generates new values for next simulation.
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: float
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: float
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
    :type min_auto_seed_percent: float
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: float
    :param current_seed: The seed that determines which cells start as alive or not
    :type current_seed: list of lists
    :return: None
    """
    # Prepares variables
    if VERBOSE:
        print("Preparing variables")

    current_seed.clear()
    min_alive_cells = int((canvas_height * canvas_width) * min_auto_seed_percent)
    max_alive_cells = int((canvas_height * canvas_width) * max_auto_seed_percent)
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
    :type max_framerate: float
    :param drawn_cells: The dictionary of already rendered pixels
    :type drawn_cells: dict
    :param pause_signal: The signal which controls whether or not to pause the loop
    :type pause_signal: Signal
    :param canvas: The instance of a tkinter canvas that visualizes the game
    :type canvas: tkinter.Canvas
    :param pause_button: The button which changes the pause_signal
    :type pause_button: tkinter.Button
    :param grid: The 2D list of cells
    :type grid: list of lists
    :param next_frame_signal: The signal which controls whether or not to move to the next frame
    while the simulation is paused
    :type next_frame_signal: Signal
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
        next_frame_signal.set_state(False)

        # If the pause button has been pressed
        if pause_signal.get_state():
            # Set the pause button's text to "Resume"
            pause_button.config(text="Resume")

            # Show the next_frame_button
            next_frame_button.grid(row=0, column=2)

            # Wait for pause_signal to be false, or next_frame_signal to be true
            while pause_signal.get_state() and not next_frame_signal.get_state():
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
        if not loop_time > max_framerate:
            time_to_sleep = max_framerate - loop_time

            if VERBOSE:
                print("Waiting " + str(time_to_sleep) + " seconds")

            time.sleep(time_to_sleep)


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


class Signal:
    """
    Mainly used to control and break loops
    """
    def __init__(self, name, initial_state):
        """
        Sets the signal to the desired initial state.
        Also stores the name of the object used to create the instance.
        :param name: The name of the object used when instantiating.
        :type name: string
        :param initial_state: The initial signal
        :type initial_state: bool
        """
        self.state = initial_state
        self.name = name

    def get_state(self):
        """
        Returns the current state of the signal
        :return: self.state (bool)
        """
        return self.state

    def set_state(self, new_state):
        """
        Sets the signal state to a desired truth value
        :param new_state: The new truth value
        :type new_state: bool
        :return: old_state (bool)
        """
        old_state = self.state
        self.state = new_state

        return old_state

    def change_state(self):
        """
        Changes the signal state to the opposite of what it currently is
        :return: self.state (bool)
        """
        if self.state:
            self.set_state(False)

        else:
            self.set_state(True)

        return self.state


if __name__ == '__main__':
    main()
