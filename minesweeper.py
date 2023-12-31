import tkinter as tk
import random
import time

# Constants
WIDTH, HEIGHT = 10, 10
EASY_MINES = 5
HARD_MINES = 10

# Initialize the game board
board = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]
revealed = [[False for _ in range(WIDTH)] for _ in range(HEIGHT)]
mines = set()
mine_count = 0  # Store the current mine count

# Create the main game window
root = tk.Tk()
root.title("Minesweeper")

# Initialize timer variables
start_time = None
elapsed_time = 0

# Scoring variables
score = 0
bonus_score = 0

# High scores
high_scores = []

# Function to load high scores from a file
def load_high_scores():
    try:
        with open("high_scores.txt", "r") as file:
            high_scores.extend(file.read().splitlines())
    except FileNotFoundError:
        pass

# Function to save high scores to a file
def save_high_scores():
    with open("high_scores.txt", "w") as file:
        file.write("\n".join(high_scores))

# Load high scores at the start of the game
load_high_scores()

# Function to generate mines based on difficulty
def generate_mines(difficulty):
    global mines, mine_count
    mine_count = EASY_MINES if difficulty == "Easy" else HARD_MINES
    mines = set()
    while len(mines) < mine_count:
        x, y = random.randint(0, WIDTH-1), random.randint(0, HEIGHT-1)
        mines.add((x, y))

def count_adjacent_mines(x, y):
    count = 0
    for dx in range(-1, 2):
        for dy in range(-1, 2):
            if 0 <= x+dx < WIDTH and 0 <= y+dy < HEIGHT and (x+dx, y+dy) in mines:
                count += 1
    return count

def reveal(x, y):
    global score, bonus_score
    if not (0 <= x < WIDTH) or not (0 <= y < HEIGHT) or revealed[y][x]:
        return
    revealed[y][x] = True
    if (x, y) in mines:
        # Animate the mine cell briefly
        animate_mine(x, y)
        game_over()
    else:
        count = count_adjacent_mines(x, y)
        if count == 0:
            canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="lightgray")
            for dx in range(-1, 2):
                for dy in range(-1, 2):
                    reveal(x+dx, y+dy)
        else:
            canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="lightgray")
            canvas.create_text((x+0.5)*30, (y+0.5)*30, text=str(count))

        if mine_count == HARD_MINES:
            score += 200
        else:
            score += 100

        # Check for bonus score if all non-mine cells are revealed
        if all(revealed[y][x] or (x, y) in mines for x in range(WIDTH) for y in range(HEIGHT)):
            bonus_score = 200

        # Update the score label
        update_score_label()

def animate_mine(x, y):
    # Animate the color change of the clicked mine and then continue with the rest of the mines
    mine_list = list(mines)
    mine_list.remove((x, y))  # Remove the clicked mine from the list
    canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="red")
    root.update()
    time.sleep(0.2)
    canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="black")
    root.update()
    
    for (mine_x, mine_y) in mine_list:
        if not revealed[mine_y][mine_x]:
            canvas.create_rectangle(mine_x*30, mine_y*30, (mine_x+1)*30, (mine_y+1)*30, fill="red")
            root.update()
            time.sleep(0.2)
            canvas.create_rectangle(mine_x*30, mine_y*30, (mine_x+1)*30, (mine_y+1)*30, fill="black")
            root.update()



def game_over():
    global high_scores
    for x in range(WIDTH):
        for y in range(HEIGHT):
            if (x, y) in mines:
                canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="black")
    elapsed_seconds = round(elapsed_time, 2)
    if bonus_score == 200:
        canvas.create_text(WIDTH*15, HEIGHT*15, text="You Win!", font=("Helvetica", 24))
        # Save the score in the high scores list
        high_scores.append("Score: {} - Time: {} seconds".format(score + bonus_score, elapsed_seconds))
        # Sort high scores in descending order
        high_scores.sort(reverse=True, key=lambda x: int(x.split()[1]))
        # Limit to 5 high scores
        high_scores = high_scores[:5]
        # Save high scores to a file
        save_high_scores()
    else:
        canvas.create_text(WIDTH*15, HEIGHT*15, text="Game Over!", font=("Helvetica", 24))
    canvas.create_text(WIDTH*15, HEIGHT*45, text="Time: {} seconds".format(elapsed_seconds), font=("Helvetica", 16))
    update_score_label()

def left_click(event):
    global start_time, elapsed_time
    if start_time is None:
        start_time = time.time()
    x, y = event.x // 30, event.y // 30
    reveal(x, y)
    if (x, y) not in mines and all(revealed[y][x] or (x, y) in mines for x in range(WIDTH) for y in range(HEIGHT)):
        elapsed_time = time.time() - start_time
        game_over()

def right_click(event):
    x, y = event.x // 30, event.y // 30
    if not revealed[y][x]:
        canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="yellow")
    else:
        count = count_adjacent_mines(x, y)
        if count > 0:
            canvas.create_text((x+0.5)*30, (y+0.5)*30, text=str(count), font=("Helvetica", 16))

# Function to update the score label
def update_score_label():
    total_score = score + bonus_score
    score_label.config(text="Score: {}".format(total_score))

# Function to start the game based on difficulty
def start_game(difficulty):
    global mine_count, start_time, score, bonus_score
    generate_mines(difficulty)
    canvas.delete("all")
    for x in range(WIDTH):
        for y in range(HEIGHT):
            canvas.create_rectangle(x*30, y*30, (x+1)*30, (y+1)*30, fill="gray")
    start_time = None
    score = 0
    bonus_score = 0
    update_score_label()

# Function to open the high scores window
def open_high_scores_window():
    high_scores_window = tk.Toplevel(root)
    high_scores_window.title("High Scores")
    high_scores_label = tk.Label(high_scores_window, text="High Scores", font=("Helvetica", 18))
    high_scores_label.pack()
    for i, high_score in enumerate(high_scores):
        score_label = tk.Label(high_scores_window, text=f"{i + 1}. {high_score}", font=("Helvetica", 14))
        score_label.pack()

# Create buttons for selecting difficulty
easy_button = tk.Button(root, text="Easy", command=lambda: start_game("Easy"))
easy_button.pack(pady=10)
hard_button = tk.Button(root, text="Hard", command=lambda: start_game("Hard"))
hard_button.pack(pady=10)

# Button to view high scores
high_scores_button = tk.Button(root, text="High Scores", command=open_high_scores_window)
high_scores_button.pack(pady=10)

canvas = tk.Canvas(root, width=WIDTH*30, height=HEIGHT*30)
canvas.bind("<Button-1>", left_click)
canvas.bind("<Button-3>", right_click)
canvas.pack()

# Create a label for displaying the score
score_label = tk.Label(root, text="Score: 0", font=("Helvetica", 16))
score_label.pack()

root.mainloop()
