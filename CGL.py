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

I currently have these next features planned:
    Saving and loading load seeds from file
        Saving seeds should be possible after observing the simulation.

    Instant resetting
        A user should be able to reset a simulation using a new random seed at any time once the simulation has started.

    Zooming, panning and procedural generation
        This would require a substantial rewrite of most, if not all, of the code

    Better performance
        As of now, the code is fairly inefficient, limiting the window size if one wants a smooth animation.

        This ties nicely in with the previous planned feature.
        Procedural generation and "chunk loading" might improve performance.

        This also will require a substantial rewrite.
"""


import tkinter
import random
import time
from timeit import default_timer as timer

PRINT_INTRO = False
GET_USER_INPUT = True

DEFAULT_CANVAS_HEIGHT = 150
DEFAULT_MAX_FRAMERATE = 60
DEFAULT_MANUAL = False
DEFAULT_AUTO_SEED = True
DEFAULT_MIN_AUTO_SEED_PERCENT = 5
DEFAULT_MAX_AUTO_SEED_PERCENT = 20


def main():
    """
    Run game of life.
    :return: None
    """
    # Intro message
    if PRINT_INTRO:
        print_intro()

    # User preferences
    canvas_height, canvas_width, canvas_area, max_framerate, manual, \
        auto_seed, min_auto_seed_percent, max_auto_seed_percent = get_user_input()

    # Initialization
    if manual:
        print("Press any key to start initialization", end="")
        input()
    print("Starting initialization")
    canvas, grid, drawn_cells = initialize(canvas_width, canvas_height, canvas_area, manual,
                                           auto_seed, min_auto_seed_percent, max_auto_seed_percent)
    print("Initialization done")

    # Game loop
    if manual:
        print("Press any key to start game", end="")
        input()

    # Draws the first frame
    paint_canvas(canvas, grid, drawn_cells)
    canvas.update()

    # Game loop
    while True:
        # No need for timer if manual progression
        if not manual:
            start = timer()

        # If the user wants to move frames manually
        if manual:
            print("Press any key to move to next frame ...", end="")
            input()

        # Calculates the next generation
        print("Calculating next generation")
        cells_to_be_killed, cells_to_be_revived, living_cells_before_next_generation = calculate_next_generation(grid)
        print("Creating next generation")
        create_next_generation(grid, cells_to_be_killed, cells_to_be_revived)
        print("Next generation complete")
        cells_alive = living_cells_before_next_generation + len(cells_to_be_revived) - len(cells_to_be_killed)
        print("\tNumber of cells alive: " + str(cells_alive))

        # Visualize the simulation
        print("Updating visual representation")
        paint_canvas(canvas, grid, drawn_cells)
        canvas.update()
        print("Visual representation updated")

        # Limits automatic loop to max_framerate
        if not manual:
            end = timer()
            loop_time = end - start
            if not loop_time > max_framerate:
                time_to_sleep = max_framerate - loop_time
                print("Waiting " + str(time_to_sleep) + " seconds")
                time.sleep(time_to_sleep)


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


def get_user_input():
    """
    Asks the user for input in order to set preferences.
    :return: canvas_height (int), canvas_width (int), canvas_area (int), max_framerate (float), manual (bool),
    auto_seed (bool), min_auto_seed_percent (float), max_auto_seed_percent (float)
    """

    # Asks the user for input
    if GET_USER_INPUT:
        print("Now let's set some preferences."
              "\nTo disable asking for preferences, change the global variable GET_USER_INPUT to False")

        # Canvas measures
        print("Please input window height[" + str(DEFAULT_CANVAS_HEIGHT) + "]: ", end="")
        canvas_height = int(input() or DEFAULT_CANVAS_HEIGHT)
        canvas_width = int(canvas_height * 1.7778)
        canvas_area = canvas_height * canvas_width

        # Framerate
        print("Please input max framerate[" + str(DEFAULT_MAX_FRAMERATE) + "]: ", end="")
        max_framerate = 1 / int(input() or DEFAULT_MAX_FRAMERATE)

        # Whether or not the user wants to manually progress through the program and between frames
        print("Do you want manual progression? 1 for yes, 0 for no [", end="")

        if DEFAULT_MANUAL:
            print("1]: ", end="")
            temp_input = int(input() or 1)
            if temp_input == 0:
                manual = False
            else:
                manual = True
        else:
            print("0]: ", end="")
            temp_input = int(input() or 0)
            if temp_input == 1:
                manual = True
            else:
                manual = False

        # Whether or not the user wants the program to automatically generate a seed or not
        print("Do you want random seed generation? 1 for yes, 0 for no [", end="")
        if DEFAULT_AUTO_SEED:
            print("1]: ", end="")
            temp_input = int(input() or 1)
            if temp_input == 0:
                auto_seed = False
            else:
                auto_seed = True
        else:
            print("0]: ", end="")
            temp_input = int(input() or 0)
            if temp_input == 1:
                auto_seed = True
            else:
                auto_seed = False

        # If the user wants automatic seeding, ask the user for min and max percentages for seeding
        if auto_seed:
            # Get minimum seed percent
            print("Please input the minimum percent of the cells you want to start as alive["
                  + str(DEFAULT_MIN_AUTO_SEED_PERCENT) + "]: ", end="")
            temp_input = int(input() or DEFAULT_MIN_AUTO_SEED_PERCENT)
            min_auto_seed_percent = DEFAULT_MIN_AUTO_SEED_PERCENT / 100

            # Get maximum seed percent
            print("Please input the maximum percent of the cells you want to start as alive["
                  + str(DEFAULT_MAX_AUTO_SEED_PERCENT) + "]: ", end="")
            temp_input = int(input() or DEFAULT_MAX_AUTO_SEED_PERCENT)
            max_auto_seed_percent = DEFAULT_MAX_AUTO_SEED_PERCENT / 100

        # To avoid referencing variables before assignment
        else:
            min_auto_seed_percent = DEFAULT_MIN_AUTO_SEED_PERCENT / 100
            max_auto_seed_percent = DEFAULT_MAX_AUTO_SEED_PERCENT / 100

    # Sets preferences using default values in the case that GET_USER_INPUT is false
    else:
        canvas_height = DEFAULT_CANVAS_HEIGHT
        canvas_width = int(canvas_height * 1.7778)
        canvas_area = canvas_height * canvas_width
        max_framerate = 1 / DEFAULT_MAX_FRAMERATE
        manual = DEFAULT_MANUAL
        auto_seed = DEFAULT_AUTO_SEED
        min_auto_seed_percent = DEFAULT_MIN_AUTO_SEED_PERCENT / 100
        max_auto_seed_percent = DEFAULT_MAX_AUTO_SEED_PERCENT / 100

    return canvas_height, canvas_width, canvas_area, max_framerate, manual,\
           auto_seed, min_auto_seed_percent, max_auto_seed_percent


def initialize(canvas_width, canvas_height, canvas_area, manual,
               auto_seed, min_auto_seed_percent, max_auto_seed_percent):
    """
    Prepares the program by initializing variables and applying seed.
    :param canvas_width: The desired width of the canvas in pixels
    :type canvas_width: int
    :param canvas_height: The desired height of the canvas in pixels
    :type canvas_height: int
    :param canvas_area: The area of the canvas in pixels
    :type canvas_area: int
    :param manual: Whether or not the user will be asked to proceed
    :type manual: bool
    :param auto_seed: Whether or not the program will generate seed automatically
    :type auto_seed: bool
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: float
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: float
    :return: canvas (tkinter.Canvas), grid (2D list), drawn_cells (dict)
    """
    # Creates the graphical window
    if manual:
        print("Press any key to create canvas", end="")
        input()
    print("Creating canvas")
    canvas = make_canvas(canvas_width, canvas_height, "Conway's Game of Life")
    print("Canvas created")

    # Creates the list of cells
    if manual:
        print("Press any key to create list of cells", end="")
        input()
    print("Creating list of cells")
    grid = []
    for i in range(canvas_height):
        grid.append([0] * canvas_width)
    print("List of cells created")

    # Apply seed to the grid
    if manual:
        print("Press any key to seed initial conditions", end="")
        input()
    print("Seeding...")
    seed(grid, canvas_area, auto_seed, min_auto_seed_percent, max_auto_seed_percent)
    print("Seeding complete")

    # Instantiates the dictionary which will be used to keep track of already drawn pixels
    drawn_cells = {}

    return canvas, grid, drawn_cells


def make_canvas(width, height, title):
    """
    Uses tkinter to create an instance of a canvas to be used for visualizing the game.
    :param width: The width of the canvas in pixels
    :type width: int
    :param height: The height of the canvas in pixels
    :type height: int
    :param title: The window title
    :type title: string
    :return: canvas (tkinter.Canvas)
    """
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1)
    canvas.config(bg="black")
    canvas.pack()

    return canvas


def seed(grid, canvas_area, auto_seed, min_auto_seed_percent, max_auto_seed_percent):
    """
    In the case of auto_seed, random cells in the grid will become alive.
    Otherwise, a built-in static seed will be used to do the same.
    :param grid: The 2D list of cells
    :type grid: list of lists
    :param canvas_area: The area of the canvas in pixels
    :type canvas_area: int
    :param auto_seed:
    :type auto_seed: bool
    :param min_auto_seed_percent: The minimum percentage of the grid which will be alive initially
    :type min_auto_seed_percent: float
    :param max_auto_seed_percent: The maximum percentage of the grid which will be alive initially
    :type max_auto_seed_percent: float
    :return: None
    """
    # Randomly seeds the grid
    if auto_seed:
        min_alive_cells = int(canvas_area * min_auto_seed_percent)
        max_alive_cells = int(canvas_area * max_auto_seed_percent)
        amount_of_cells_to_seed = random.randint(min_alive_cells, max_alive_cells)
        print("There will be " + str(amount_of_cells_to_seed) + " living cells initially")

        for i in range(amount_of_cells_to_seed):
            # Picks out a random row in the grid
            y = random.randint(0, len(grid) - 1)

            # Picks out a random cell in the row and makes it alive
            x = random.randint(0, len(grid[y]) - 1)
            grid[y][x] = 1

    # Seeds the grid using built-in information, mainly used for testing and benchmarking purposes
    else:
        grid[0][2] = 1
        grid[0][3] = 1
        grid[0][4] = 1
        grid[1][1] = 1
        grid[1][5] = 1
        grid[0][0] = 1
        grid[0][6] = 1


def paint_canvas(canvas, grid, drawn_cells):
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

            # If this cell is not alice
            else:
                # But is drawn on canvas
                if exists:
                    # Destroy the corresponding instance of a pixel and remove it from the drawn_cells dictionary
                    canvas.delete(drawn_cells[rectangle_name])
                    drawn_cells.pop(rectangle_name)


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
    for cell in range(len(cells_to_be_killed)):
        y = cells_to_be_killed[cell][0]
        x = cells_to_be_killed[cell][1]
        grid[y][x] = 0

    for cell in range(len(cells_to_be_revived)):
        y = cells_to_be_revived[cell][0]
        x = cells_to_be_revived[cell][1]
        grid[y][x] = 1


if __name__ == '__main__':
    main()
