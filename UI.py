import pygame, sys
from pygame.locals import *
import npuzzle
import test
from multiprocessing import Process, Queue
import time

TILESIZE = 80
WINDOWWIDTH = 800
WINDOWHEIGHT = 640
FPS = 60
BLANK = None

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BRIGHTBLUE =    (  0,  50, 255)
LIGHTTURQUOISE = (  192,  240,  255)
GREEN =         (  0, 204,   0)
ASHBLUE =       (  72, 95, 122)
LIGHTBLUE =     ( 78, 147, 228)
BRIGHTPINK =    (255,  22,  93)

BGCOLOR = LIGHTTURQUOISE
TILECOLOR = WHITE
TEXTCOLOR = LIGHTBLUE
BORDERCOLOR = LIGHTBLUE
BASICFONTSIZE = 20

MESSAGECOLOR = LIGHTBLUE

UP = 'Up'
DOWN = 'Down'
LEFT = 'Left'
RIGHT = 'Right'


# Read the input (output) file and return the number of puzzles, size and initial state of each puzzle
def read_input_file(file_path):
    with open(file_path, 'r') as f:
        num_puzzles = int(f.readline().strip())
        puzzles = []
        for _ in range(num_puzzles):
            size = int(f.readline().strip())
            initial_state = [list(map(int, f.readline().strip().split())) for _ in range(size)]
            puzzles.append((size, initial_state))

    # print(puzzles) 
    return puzzles

# Read the output file and return the list of actions, number of explored nodes and runtime
def read_output_file(file_path):
    with open(file_path, 'r') as f:
        actions_line = f.readline().strip()
        actions = actions_line.replace("Action: ", "").strip("[]").replace("'", "").split(", ")

        nodes_line = f.readline().strip()
        num_explored_nodes = int(nodes_line.replace("Number of explored nodes is: ", ""))

        time_line = f.readline().strip()
        time_taken = float(time_line.replace("Time: ", "").replace(" second", ""))

    return actions, num_explored_nodes, time_taken

def get_initial_board(puzzles):
    # board = []
    # return the initial state of the first puzzle
    size, board = puzzles[0]
    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                board[row][col] = BLANK
    return board

# Return the x and y of board coordinates of the blank space
def get_blank_position(size, board):
    for x in range(size):
        for y in range(size):
            if board[x][y] == BLANK:
                return (x, y)

def make_move(board, move):
    blank_x, blank_y = get_blank_position(len(board), board)
    # print("makemove", blank_x, blank_y)

    if move == UP:
        board[blank_x][blank_y], board[blank_x + 1][blank_y] = board[blank_x + 1][blank_y], board[blank_x][blank_y]
    elif move == DOWN:
        board[blank_x][blank_y], board[blank_x - 1][blank_y] = board[blank_x - 1][blank_y], board[blank_x][blank_y]
    elif move == RIGHT:
        board[blank_x][blank_y], board[blank_x][blank_y - 1] = board[blank_x][blank_y -1], board[blank_x][blank_y]
    elif move == LEFT:
        board[blank_x][blank_y], board[blank_x][blank_y + 1] = board[blank_x][blank_y + 1], board[blank_x][blank_y]

    # print("mm", board)

def is_valid_move(board, move):
    blank_x, blank_y = get_blank_position(len(board), board)
    # print("isvalidmove", blank_x, blank_y)

    return (move == UP and blank_x != len(board[0]) - 1) or \
           (move == DOWN and blank_x != 0) or \
           (move == LEFT and blank_y != len(board) - 1) or \
           (move == RIGHT and blank_y != 0)

def get_left_top_of_tile(tile_x, tile_y):
    left = XMARGIN + (tile_x * TILESIZE) + (tile_x - 1)
    top = YMARGIN + (tile_y * TILESIZE) + (tile_y - 1)
    return left, top

def get_move_spot(board, x, y):
    for tile_x in range(len(board)):
        for tile_y in range(len(board[0])):
            left, top = get_left_top_of_tile(tile_x, tile_y)
            tile_rect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tile_rect.collidepoint(x, y):
                return tile_x, tile_y
    return None, None

def draw_tile(tile_x, tile_y, number, adjx=0, adjy=0):
    left, top = get_left_top_of_tile(tile_x, tile_y)
    pygame.draw.rect(DISPLAYSURF, TILECOLOR, (left + adjx, top + adjy, TILESIZE, TILESIZE))
    text_surf = BASICFONT.render(str(number), True, TEXTCOLOR)
    text_rect = text_surf.get_rect()
    text_rect.center = left + int(TILESIZE / 2) + adjx, top + int(TILESIZE / 2) + adjy
    DISPLAYSURF.blit(text_surf, text_rect)

def make_text(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)

def draw_board(board, message):
    DISPLAYSURF.fill(BGCOLOR)

    if message:
        text_surf, text_rect = make_text(message, MESSAGECOLOR, BGCOLOR, 5, 5)
        DISPLAYSURF.blit(text_surf, text_rect)
    
    for tile_y in range(len(board)):
        for tile_x in range(len(board[tile_y])):
            if board[tile_y][tile_x]:
                draw_tile(tile_x, tile_y, board[tile_y][tile_x])


    left, top = get_left_top_of_tile(0, 0)
    width = BOARDWIDTH * TILESIZE
    height = BOARDHEIGHT * TILESIZE
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (left - 5, top - 5, width + 11, height + 11), 4)

    DISPLAYSURF.blit(TIME_SURF, TIME_RECT)
    DISPLAYSURF.blit(NODES_SURF, NODES_RECT)
    DISPLAYSURF.blit(DFS_SURF, DFS_RECT)
    DISPLAYSURF.blit(IDS_SURF, IDS_RECT)
    DISPLAYSURF.blit(TIMER_SURF, TIMER_RECT)
    DISPLAYSURF.blit(RESET_SURF, RESET_RECT)
    DISPLAYSURF.blit(NEWGAME_SURF, NEWGAME_RECT)
    DISPLAYSURF.blit(STEP_SURF, STEP_RECT)

def slide_animation(board, direction, message, animationSpeed):
    # Note: This function does not check if the move is valid.

    blankx, blanky = get_blank_position(len(board), board)
    # print("slideanim", blankx, blanky)
    if direction == UP:
        movex = blankx + 1
        movey = blanky 
    elif direction == DOWN:
        movex = blankx - 1
        movey = blanky
    elif direction == LEFT:
        movex = blankx
        movey = blanky + 1
    elif direction == RIGHT:
        movex = blankx 
        movey = blanky - 1
    # print("mx, my", movex, movey)
    # prepare the base surface
    draw_board(board, message)
    baseSurf = DISPLAYSURF.copy()
    # draw a blank space over the moving tile on the baseSurf Surface.
    moveLeft, moveTop = get_left_top_of_tile(movey, movex)
    pygame.draw.rect(baseSurf, BGCOLOR, (moveLeft, moveTop, TILESIZE, TILESIZE))

    for i in range(0, TILESIZE, animationSpeed):
        # animate the tile sliding over
        check_for_quit()
        DISPLAYSURF.blit(baseSurf, (0, 0))
        if direction == DOWN:
            draw_tile(movey, movex, board[movex][movey], 0, i)
        if direction == UP:
            draw_tile(movey, movex, board[movex][movey], 0, -i)
        if direction == RIGHT:
            draw_tile(movey, movex, board[movex][movey], i, 0)
        if direction == LEFT:
            draw_tile(movey, movex, board[movex][movey], -i, 0)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

def get_spot_clicked(board, x, y):
    # from the x & y pixel coordinates, get the x & y board coordinates
    for tileX in range(len(board)):
        for tileY in range(len(board[0])):
            left, top = get_left_top_of_tile(tileX, tileY)
            tileRect = pygame.Rect(left, top, TILESIZE, TILESIZE)
            if tileRect.collidepoint(x, y):
                return (tileX, tileY)
    return (None, None)

def check_for_quit():
    for event in pygame.event.get(QUIT):
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)

def terminate():
    pygame.quit()
    sys.exit()

def reverse_directions(actions):
    reversed_actions = []
    for action in actions:
        if action == 'Left':
            reversed_actions.append('Right')
        elif action == 'Right':
            reversed_actions.append('Left')
        elif action == 'Up':
            reversed_actions.append('Down')
        elif action == 'Down':
            reversed_actions.append('Up')
    return reversed_actions

def IDS_solver_process(given_state, size, max_depth, solution_queue, metrics_queue):
    elapsed_time, nodes_visited, total_steps = npuzzle.IDS_with_steps(given_state, size, max_depth, solution_queue)
    metrics_queue.put((elapsed_time, nodes_visited, total_steps))  # Send time and node count to the main process

def DFS_solver_process(given_state, size, solution_queue, metrics_queue):
    elapsed_time, nodes_visited, total_steps = npuzzle.DFS_with_steps(given_state, size, solution_queue)
    metrics_queue.put((elapsed_time, nodes_visited, total_steps))  # Send time and node count to the main process

total_time = 60
last_update = pygame.time.get_ticks()

def update_timer():
    global total_time, last_update, TIMER_SURF, TIMER_RECT
    current_time = pygame.time.get_ticks()
    if current_time - last_update >= 1000 and total_time > 0:   # Update the timer every second (1000 milliseconds)
        total_time -= 1  # Decrement the countdown timer
        last_update = current_time  # Reset the last update time
        
        # Update the timer display
        TIMER_SURF, TIMER_RECT = make_text(
            f'Time left: {total_time} (s)', 
            TEXTCOLOR, TILECOLOR, 
            WINDOWWIDTH - 160, 5
        )

def convert_to_2D(given_state, size):
    board = []
    for i in range(size):
        row = given_state[i*size:(i+1)*size]
        board.append([tile if tile != 0 else None for tile in row])
    return board

def prompt_for_size():
    """Prompts user to enter the size (k) for a new puzzle."""
    size = input("Enter the size for a new puzzle (e.g., 3 for 3x3): ")
    try:
        return int(size)
    except ValueError:
        print("Invalid input. Please enter an integer greater than or equal to 2.")
        return None

def main():
    input_file_path = "input.txt"

    puzzles = npuzzle.readInput(input_file_path)
    if not puzzles:
        print("Không có bài toán nào để giải.")
        return

    size, given_state = puzzles[0]

    # Convert initial_state to a 2D board
    board = convert_to_2D(given_state, size)

    solution_queue = Queue()
    metrics_queue = Queue()

    # Define the solver processes
    IDS_solver = Process(target=IDS_solver_process, args=(given_state, size, 80, solution_queue, metrics_queue))
    DFS_solver = Process(target=DFS_solver_process, args=(given_state, size, solution_queue, metrics_queue))

    # Initialize Pygame
    pygame.init()
    global FPSCLOCK, DISPLAYSURF, BASICFONT, TIME_SURF, TIME_RECT, NODES_SURF, NODES_RECT, TIMER_SURF, TIMER_RECT, DFS_SURF, DFS_RECT, IDS_SURF, IDS_RECT, BOARDHEIGHT, BOARDWIDTH, XMARGIN, YMARGIN, RESET_SURF, RESET_RECT, total_time, last_update, NEWGAME_SURF, NEWGAME_RECT, STEP_SURF, STEP_RECT
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('n-puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    BOARDHEIGHT = size
    BOARDWIDTH = size
    XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
    YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)

    # Variables to track solution progress and metrics
    all_moves = []
    is_solving = False
    elapsed_time = None
    nodes_visited = None
    total_moves = None
    start_time = time.time()
    timeout_reached = False
    status_message = "Choose an algorithm to solve the puzzle!"
    start_timer = False

    # Buttons and text for the UI
    TIME_SURF, TIME_RECT = make_text('Time: ' + str(elapsed_time) + ' (s)', TEXTCOLOR, TILECOLOR, 5, 30)
    NODES_SURF, NODES_RECT = make_text('Nodes visited: ' + str(nodes_visited), TEXTCOLOR, TILECOLOR, 5, 60)
    STEP_SURF, STEP_RECT = make_text('Total steps: ' + str(total_moves), TEXTCOLOR, TILECOLOR, 5, 90)
    TIMER_SURF, TIMER_RECT = make_text('Time left: ' + str(total_time) + ' (s)', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 160, 5)
    DFS_SURF, DFS_RECT = make_text('DFS', TEXTCOLOR, TILECOLOR, 480, 570)
    IDS_SURF, IDS_RECT = make_text('IDS', TEXTCOLOR, TILECOLOR, 480, 600)
    RESET_SURF, RESET_RECT = make_text('Reset Puzzle', TEXTCOLOR,TILECOLOR, 240, 570)
    NEWGAME_SURF, NEWGAME_RECT = make_text('New Puzzle', TEXTCOLOR, TILECOLOR, 240, 600)

    while True:
        check_for_quit()
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == MOUSEBUTTONUP:
                spot_x, spot_y = get_spot_clicked(board, event.pos[0], event.pos[1])
                if (spot_x, spot_y) == (None, None):
                    # Start DFS solver
                    if DFS_RECT.collidepoint(event.pos):
                        if not DFS_solver.is_alive():
                            start_timer = True
                            DFS_solver = Process(target=DFS_solver_process, args=(given_state, size, solution_queue, metrics_queue))
                            DFS_solver.start()
                            is_solving = True
                            print("DFS started")
                            start_time = time.time()
                            timeout_reached = False
                            if metrics_queue.qsize() > 0 and elapsed_time is None:
                                elapsed_time, nodes_visited, total_moves = metrics_queue.get()
                    # Start IDS solver
                    elif IDS_RECT.collidepoint(event.pos):
                        if not IDS_solver.is_alive():
                            start_timer = True
                            IDS_solver = Process(target=IDS_solver_process, args=(given_state, size, 80, solution_queue, metrics_queue))
                            IDS_solver.start()
                            is_solving = True
                            print("IDS started")
                            start_time = time.time()
                            timeout_reached = False
                            if metrics_queue.qsize() > 0 and elapsed_time is None:
                                elapsed_time, nodes_visited, total_moves = metrics_queue.get()
                    if RESET_RECT.collidepoint(event.pos):
                        board = convert_to_2D(given_state, size)
                        all_moves = []
                        is_solving = False
                        elapsed_time = None
                        nodes_visited = None
                        total_moves = None
                        start_timer = False
                        timeout_reached = False
                        total_time = 60
                        status_message = "Choose an algorithm to solve the puzzle!"
                        start_time = time.time()
                        if DFS_solver.is_alive():
                            DFS_solver.terminate()
                        if IDS_solver.is_alive():
                            IDS_solver.terminate()
                        TIME_SURF, TIME_RECT = make_text('Time: ' + str(elapsed_time) + ' (s)', TEXTCOLOR, TILECOLOR, 5, 30)
                        NODES_SURF, NODES_RECT = make_text('Nodes visited: ' + str(nodes_visited), TEXTCOLOR, TILECOLOR, 5, 60)
                        STEP_SURF, STEP_RECT = make_text('Total steps: ' + str(total_moves), TEXTCOLOR, TILECOLOR, 5, 90)
                        TIMER_SURF, TIMER_RECT = make_text('Time left: ' + str(total_time) + ' (s)', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 160, 5)
                        DFS_SURF, DFS_RECT = make_text('DFS', TEXTCOLOR, TILECOLOR, 480, 570)
                        IDS_SURF, IDS_RECT = make_text('IDS', TEXTCOLOR, TILECOLOR, 480, 600)
                        RESET_SURF, RESET_RECT = make_text('Reset Puzzle', TEXTCOLOR,TILECOLOR, 240, 570)
                        NEWGAME_SURF, NEWGAME_RECT = make_text('New Puzzle', TEXTCOLOR, TILECOLOR, 240, 600)
                    if NEWGAME_RECT.collidepoint(event.pos):
                        k = prompt_for_size()
                        if k is not None and k >= 2:
                            new_puzzle = test.generate_puzzle(k)
                            test.write_puzzle_to_file(new_puzzle, k)
                            BOARDHEIGHT = k
                            BOARDWIDTH = k
                            XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) / 2)
                            YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) / 2)
                            print(f"New {k}x{k} puzzle generated and loaded.")
                        puzzles = npuzzle.readInput(input_file_path)                        
                        size, given_state = puzzles[0]
                        board = convert_to_2D(given_state, size)
                        all_moves = []
                        is_solving = False
                        elapsed_time = None
                        nodes_visited = None
                        total_moves = None
                        start_timer = False
                        timeout_reached = False
                        total_time = 60
                        status_message = "Choose an algorithm to solve the puzzle!"
                        start_time = time.time()
                        if DFS_solver.is_alive():
                            DFS_solver.terminate()
                        if IDS_solver.is_alive():
                            IDS_solver.terminate()
                        TIME_SURF, TIME_RECT = make_text('Time: ' + str(elapsed_time) + ' (s)', TEXTCOLOR, TILECOLOR, 5, 30)
                        NODES_SURF, NODES_RECT = make_text('Nodes visited: ' + str(nodes_visited), TEXTCOLOR, TILECOLOR, 5, 60)
                        STEP_SURF, STEP_RECT = make_text('Total steps: ' + str(total_moves), TEXTCOLOR, TILECOLOR, 5, 90)
                        TIMER_SURF, TIMER_RECT = make_text('Time left: ' + str(total_time) + ' (s)', TEXTCOLOR, TILECOLOR, WINDOWWIDTH - 160, 5)
                        DFS_SURF, DFS_RECT = make_text('DFS', TEXTCOLOR, TILECOLOR, 480, 570)
                        IDS_SURF, IDS_RECT = make_text('IDS', TEXTCOLOR, TILECOLOR, 480, 600)
                        RESET_SURF, RESET_RECT = make_text('Reset Puzzle', TEXTCOLOR,TILECOLOR, 240, 570)
                        NEWGAME_SURF, NEWGAME_RECT = make_text('New Puzzle', TEXTCOLOR, TILECOLOR, 240, 600)

        # Check if the 60-second limit has been reached
        DISPLAYSURF.blit(TIMER_SURF, TIMER_RECT)
        if start_timer and is_solving:
            update_timer()
        
        # Check if solution is completed by the solver
        if start_time and (time.time() - start_time > 60) and not timeout_reached:
            timeout_reached = True
            is_solving = False
            start_timer = False

            # Terminate the solver processes
            if DFS_solver.is_alive():
                DFS_solver.terminate()
                start_timer = False
                print("DFS took too long to solve...")
            if IDS_solver.is_alive():
                IDS_solver.terminate()
                start_timer = False
                print("IDS took too long to solve...")

            if metrics_queue.qsize() > 0 and elapsed_time is None:
                elapsed_time, nodes_visited, total_moves = metrics_queue.get()

        if metrics_queue.qsize() > 0 and elapsed_time is None:
            elapsed_time, nodes_visited, total_moves = metrics_queue.get()

        # Read moves from solution_queue if time has not run out
        if not timeout_reached:
            while not solution_queue.empty():
                move = solution_queue.get()
                if move == "DONE":
                    is_solving = False
                    print("Giải thuật đã hoàn tất!")
                    break
                all_moves.append(move)

        # Prepare reversed moves for animation
        reversed_moves = reverse_directions(all_moves)
        
        # Draw the current board and status
        draw_board(board, status_message)
        if is_solving:
            status_message = "Solving the puzzle..."
        elif not is_solving and elapsed_time is not None:
            if not timeout_reached and elapsed_time is not None:
                status_message = "Solved!"
            elif timeout_reached and elapsed_time is None:
                status_message = "Took too long to solve!"
        draw_board(board, status_message)

        if elapsed_time is not None or nodes_visited is not None:
            TIME_SURF, TIME_RECT = make_text('Time: ' + str(elapsed_time) + ' (s)', TEXTCOLOR, TILECOLOR, 5, 30)
            NODES_SURF, NODES_RECT = make_text('Nodes visited: ' + str(nodes_visited), TEXTCOLOR, TILECOLOR, 5, 60)
            STEP_SURF, STEP_RECT = make_text('Total steps: ' + str(total_moves), TEXTCOLOR, TILECOLOR, 5, 90)
        DISPLAYSURF.blit(TIME_SURF, TIME_RECT)
        DISPLAYSURF.blit(NODES_SURF, NODES_RECT)

        # Perform the moves animation
        if reversed_moves:
            move = reversed_moves.pop(0)
            all_moves.pop(0)
            if is_valid_move(board, move):
                slide_animation(board, move, "Simulating the solution...", 10)
                make_move(board, move)
                pygame.display.update()
                FPSCLOCK.tick(FPS)

        pygame.display.update()
        FPSCLOCK.tick(FPS)

    IDS_solver.join()
    DFS_solver.join()


if __name__ == '__main__':
    main()