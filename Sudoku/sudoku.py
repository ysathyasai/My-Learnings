import random
import os
import time
import json
import pickle
from typing import List, Set, Tuple, Optional
from colorama import init, Fore, Back, Style
from datetime import datetime

# Initialize colorama for cross-platform color support
init(autoreset=True)

# Constants
SAVE_FILE = "sudoku_save.pkl"
HIGH_SCORES_FILE = "high_scores.json"
ACHIEVEMENTS_FILE = "achievements.json"

class Achievement:
    def __init__(self, name: str, description: str, condition: str):
        self.name = name
        self.description = description
        self.condition = condition
        self.earned = False
        self.earned_date = None

class Move:
    def __init__(self, row: int, col: int, old_value: int, new_value: int, 
                 old_notes: Set[int], new_notes: Set[int]):
        self.row = row
        self.col = col
        self.old_value = old_value
        self.new_value = new_value
        self.old_notes = old_notes.copy()
        self.new_notes = new_notes.copy()

class Cell:
    def __init__(self):
        self.value = 0
        self.notes = set()
        self.original = False
        self.has_conflict = False
        self.highlighted = False

class SudokuGame:
    def __init__(self):
        self.board = [[Cell() for _ in range(9)] for _ in range(9)]
        self.selected_cell = (0, 0)
        self.mistakes = 0
        self.hint_count = 3
        self.start_time = None
        self.pause_time = 0
        self.is_paused = False
        self.moves_history = []
        self.redo_stack = []
        self.score = 0
        self.difficulty = 1
        self.achievements = self._init_achievements()
        self.auto_check = True
        
    def _init_achievements(self):
        return {
            "speed_demon": Achievement("Speed Demon", "Complete Easy puzzle under 5 minutes", "time < 300"),
            "no_mistakes": Achievement("Perfect Game", "Complete puzzle with no mistakes", "mistakes == 0"),
            "hard_victory": Achievement("Master", "Complete Hard puzzle", "difficulty == 3"),
            "note_master": Achievement("Note Master", "Use notes 20 times", "notes_used >= 20"),
            "marathon": Achievement("Marathon", "Play for 1 hour total", "total_time >= 3600")
        }

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def generate_puzzle(self, difficulty: int):
        self._generate_solved()
        cells_to_remove = {
            1: 41,  # Easy: 40 hints
            2: 51,  # Medium: 30 hints
            3: 56   # Hard: 25 hints
        }.get(difficulty, 41)

        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)

        for i, j in positions[:cells_to_remove]:
            self.board[i][j].value = 0
            self.board[i][j].original = False

        self.start_time = time.time()

    def _generate_solved(self):
        for i in range(9):
            for j in range(9):
                self.board[i][j] = Cell()

        self.board[0][0].value = random.randint(1, 9)
        self.board[0][0].original = True

        if self._solve():
            for i in range(9):
                for j in range(9):
                    self.board[i][j].original = True
            return True
        return False

    def _solve(self) -> bool:
        row, col = self._find_empty()
        if row is None:
            return True

        numbers = list(range(1, 10))
        random.shuffle(numbers)

        for num in numbers:
            if self._is_valid((row, col), num):
                self.board[row][col].value = num
                if self._solve():
                    return True
                self.board[row][col].value = 0

        return False

    def _find_empty(self) -> Tuple[Optional[int], Optional[int]]:
        for i in range(9):
            for j in range(9):
                if self.board[i][j].value == 0:
                    return i, j
        return None, None

    def _is_valid(self, pos: Tuple[int, int], num: int) -> bool:
        row, col = pos
        for j in range(9):
            if j != col and self.board[row][j].value == num:
                return False
        for i in range(9):
            if i != row and self.board[i][col].value == num:
                return False
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if (i != row or j != col) and self.board[i][j].value == num:
                    return False
        return True

    def print_board(self):
        self.clear_screen()
        print(f"\n{Fore.CYAN}╔════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}                    S U D O K U            {Fore.CYAN} ║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}")

        # Controls section
        print("\nControls:")
        print("WASD: Move | 1-9: Number | Space: Notes | Tab: Auto-check")
        print("n: Notes | h: Hint | u: Undo | r: Redo | s: Save | l: Load")
        print("p: Pause | q: Quit")

        # Status section
        difficulty_names = ["Easy", "Medium", "Hard"]
        print(f"\nDifficulty: {difficulty_names[self.difficulty-1]}")
        print(f"Mistakes: {'❌' * self.mistakes}")
        print(f"Hints: {'💡' * self.hint_count}")
        
        if self.start_time:
            elapsed = self.get_elapsed_time()
            status = f"{Fore.YELLOW}[PAUSED]{Style.RESET_ALL}" if self.is_paused else ""
            print(f"Time: {elapsed//60:02d}:{elapsed%60:02d} {status}")
        
        print(f"Score: {self.score}")

        # Board section
        print(f"\n    {Fore.CYAN}1 2 3   4 5 6   7 8 9{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}┌───────┬───────┬───────┐{Style.RESET_ALL}")
        
        for i in range(9):
            print(f"{Fore.CYAN}{i + 1}{Style.RESET_ALL} │", end=" ")
            for j in range(9):
                cell = self.board[i][j]
                
                # Cell background
                bg_color = Back.WHITE if (i, j) == self.selected_cell else \
                          Back.LIGHTBLACK_EX if cell.highlighted else Back.RESET

                # Cell foreground
                if cell.has_conflict:
                    fg_color = Fore.RED
                elif cell.original:
                    fg_color = Fore.BLUE
                else:
                    fg_color = Fore.GREEN

                # Cell content
                if cell.value != 0:
                    print(f"{bg_color}{fg_color}{cell.value}{Style.RESET_ALL}", end=" ")
                else:
                    notes_str = "·" if cell.notes else "·"
                    color = Fore.YELLOW if cell.notes else Fore.WHITE
                    print(f"{bg_color}{color}{notes_str}{Style.RESET_ALL}", end=" ")
                
                if j in {2, 5}:
                    print(f"{Fore.CYAN}│{Style.RESET_ALL}", end=" ")
            print(f"{Fore.CYAN}│{Style.RESET_ALL}")
            if i in {2, 5}:
                print(f"  {Fore.CYAN}├───────┼───────┼───────┤{Style.RESET_ALL}")
        print(f"  {Fore.CYAN}└───────┴───────┴───────┘{Style.RESET_ALL}")

        # Notes for selected cell
        cell = self.board[self.selected_cell[0]][self.selected_cell[1]]
        if cell.notes:
            notes_list = sorted(cell.notes)
            print(f"\nNotes: {', '.join(map(str, notes_list))}")

        print(f"\nAuto-check: {'ON' if self.auto_check else 'OFF'}")

    def make_move(self, row: int, col: int, num: int, note_mode: bool = False) -> bool:
        if self.board[row][col].original:
            return False

        if note_mode:
            if num in self.board[row][col].notes:
                self.board[row][col].notes.remove(num)
            else:
                self.board[row][col].notes.add(num)
            return True

        if not self._is_valid((row, col), num):
            self.mistakes += 1
            return False

        self.board[row][col].value = num
        self.board[row][col].notes.clear()
        return True

    def use_hint(self) -> bool:
        if self.hint_count <= 0:
            return False

        row, col = self.selected_cell
        if self.board[row][col].original or self.board[row][col].value != 0:
            return False

        temp_board = [[self.board[i][j].value for j in range(9)] for i in range(9)]
        temp_game = SudokuGame()
        temp_game.board = [[Cell() for _ in range(9)] for _ in range(9)]
        for i in range(9):
            for j in range(9):
                temp_game.board[i][j].value = temp_board[i][j]

        if temp_game._solve():
            self.board[row][col].value = temp_game.board[row][col].value
            self.board[row][col].original = True
            self.hint_count -= 1
            return True
        return False

    def is_complete(self) -> bool:
        for i in range(9):
            for j in range(9):
                if self.board[i][j].value == 0:
                    return False
        return True

    def save_game(self):
        game_state = {
            'board': self.board,
            'mistakes': self.mistakes,
            'hint_count': self.hint_count,
            'start_time': self.start_time,
            'pause_time': self.pause_time,
            'score': self.score,
            'difficulty': self.difficulty,
            'achievements': self.achievements
        }
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(game_state, f)

    def load_game(self) -> bool:
        try:
            with open(SAVE_FILE, 'rb') as f:
                game_state = pickle.load(f)
                self.board = game_state['board']
                self.mistakes = game_state['mistakes']
                self.hint_count = game_state['hint_count']
                self.start_time = game_state['start_time']
                self.pause_time = game_state['pause_time']
                self.score = game_state['score']
                self.difficulty = game_state['difficulty']
                self.achievements = game_state.get('achievements', self._init_achievements())
                return True
        except:
            return False

    def update_high_scores(self):
        scores = []
        try:
            with open(HIGH_SCORES_FILE, 'r') as f:
                scores = json.load(f)
        except:
            scores = []

        elapsed = self.get_elapsed_time()
        new_score = {
            'difficulty': self.difficulty,
            'time': elapsed,
            'mistakes': self.mistakes,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'score': self.calculate_score()
        }
        scores.append(new_score)
        scores.sort(key=lambda x: (-x['difficulty'], x['time'], x['mistakes']))
        scores = scores[:10]  # Keep top 10

        with open(HIGH_SCORES_FILE, 'w') as f:
            json.dump(scores, f)

    def calculate_score(self) -> int:
        base_score = 1000
        time_penalty = self.get_elapsed_time() // 30  # Penalty every 30 seconds
        mistake_penalty = self.mistakes * 50
        difficulty_bonus = (self.difficulty - 1) * 500
        hint_penalty = (3 - self.hint_count) * 100
        
        return max(0, base_score + difficulty_bonus - time_penalty - mistake_penalty - hint_penalty)

    def pause_game(self):
        if not self.is_paused:
            self.pause_time = time.time()
            self.is_paused = True
        else:
            self.pause_time = time.time() - self.pause_time
            self.is_paused = False

    def get_elapsed_time(self) -> int:
        if not self.start_time:
            return 0
        if self.is_paused:
            return int(self.pause_time - self.start_time - self.pause_time)
        return int(time.time() - self.start_time - self.pause_time)

    def update_conflicts(self):
        if not self.auto_check:
            return

        for i in range(9):
            for j in range(9):
                self.board[i][j].has_conflict = False

        for i in range(9):
            for j in range(9):
                if self.board[i][j].value == 0:
                    continue
                
                # Check row and column
                for k in range(9):
                    if k != j and self.board[i][k].value == self.board[i][j].value:
                        self.board[i][j].has_conflict = True
                        self.board[i][k].has_conflict = True
                    if k != i and self.board[k][j].value == self.board[i][j].value:
                        self.board[i][j].has_conflict = True
                        self.board[k][j].has_conflict = True

                # Check box
                box_row, box_col = 3 * (i // 3), 3 * (j // 3)
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        if (r != i or c != j) and self.board[r][c].value == self.board[i][j].value:
                            self.board[i][j].has_conflict = True
                            self.board[r][c].has_conflict = True

    def highlight_related(self, row: int, col: int):
        # Reset highlights
        for i in range(9):
            for j in range(9):
                self.board[i][j].highlighted = False

        # Highlight same row, column, and box
        for i in range(9):
            self.board[row][i].highlighted = True
            self.board[i][col].highlighted = True

        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                self.board[i][j].highlighted = True

        # Highlight same value
        value = self.board[row][col].value
        if value != 0:
            for i in range(9):
                for j in range(9):
                    if self.board[i][j].value == value:
                        self.board[i][j].highlighted = True

def show_high_scores():
    try:
        with open(HIGH_SCORES_FILE, 'r') as f:
            scores = json.load(f)
            print("\nHigh Scores:")
            print("─" * 60)
            print(f"{'Rank':<6}{'Difficulty':<12}{'Time':<10}{'Mistakes':<10}{'Score':<8}Date")
            print("─" * 60)
            for i, score in enumerate(scores[:10], 1):
                diff_name = ['Easy', 'Medium', 'Hard'][score['difficulty']-1]
                time_str = f"{score['time']//60:02d}:{score['time']%60:02d}"
                print(f"{i:<6}{diff_name:<12}{time_str:<10}{score['mistakes']:<10}{score['score']:<8}{score['date']}")
    except:
        print("No high scores yet.")
    input("\nPress Enter to continue...")

def show_achievements(game):
    print("\nAchievements:")
    print("─" * 50)
    achievements_exist = False
    for name, achievement in game.achievements.items():
        status = "✓" if achievement.earned else "✗"
        print(f"{status} {achievement.name}: {achievement.description}")
        if achievement.earned:
            achievements_exist = True
            earned_date = achievement.earned_date.strftime("%Y-%m-%d") if achievement.earned_date else "Unknown"
            print(f"   Earned on: {earned_date}")
    
    if not achievements_exist:
        print("No achievements earned yet.")
    input("\nPress Enter to continue...")

def main():
    game = SudokuGame()
    
    while True:
        game.clear_screen()
        print(f"{Fore.CYAN}╔════════════════════════════════════════════╗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}║{Style.RESET_ALL}                          S U D O K U       {Fore.CYAN}║{Style.RESET_ALL}")
        print(f"{Fore.CYAN}╚════════════════════════════════════════════╝{Style.RESET_ALL}")

        print("\nMain Menu:")
        print("1. New Game")
        print("2. Load Game")
        print("3. High Scores")
        print("4. Achievements")
        print("5. Quit")
        
        try:
            choice = input("\nChoice (1-5): ").strip()
            
            if choice == "5":
                print("\nThanks for playing!")
                exit()
                
            elif choice == "3":
                show_high_scores()
                continue
                
            elif choice == "4":
                show_achievements(game)
                continue
                
            elif choice == "2":
                if game.load_game():
                    print("Game loaded successfully!")
                    time.sleep(1)
                    break
                else:
                    print("No saved game found.")
                    input("Press Enter to continue...")
                    continue
                    
            elif choice == "1":
                print("\nSelect difficulty level:")
                print("1. Easy (40 hints)")
                print("2. Medium (30 hints)")
                print("3. Hard (25 hints)")
                
                while True:
                    try:
                        difficulty = int(input("Choice (1-3): "))
                        if 1 <= difficulty <= 3:
                            game.difficulty = difficulty
                            game.generate_puzzle(difficulty)
                            break
                        print("Please enter a number between 1 and 3.")
                    except ValueError:
                        print("Please enter a valid number.")
                break
                
        except ValueError:
            print("Please enter a valid choice.")
            time.sleep(1)

    note_mode = False
    
    # Main game loop
    while True:
        game.print_board()
        
        command = input("\nEnter command: ").lower()
        
        if command in ['w', 'a', 's', 'd']:  # Movement
            row, col = game.selected_cell
            if command == 'w' and row > 0:
                game.selected_cell = (row - 1, col)
            elif command == 's' and row < 8:
                game.selected_cell = (row + 1, col)
            elif command == 'a' and col > 0:
                game.selected_cell = (row, col - 1)
            elif command == 'd' and col < 8:
                game.selected_cell = (row, col + 1)
                
        elif command == 'q':  # Quit
            save = input("Save game before quitting? (y/n): ").lower() == 'y'
            if save:
                game.save_game()
                print("Game saved!")
            print("\nThanks for playing!")
            break
            
        elif command == 'n':  # Toggle notes
            note_mode = not note_mode
            print(f"Note mode: {'ON' if note_mode else 'OFF'}")
            
        elif command == 'h':  # Hint
            if game.hint_count > 0:
                if game.use_hint():
                    print("Hint used!")
                else:
                    print("Can't use hint on this cell!")
            else:
                print("No hints remaining!")
                
        elif command == 'p':  # Pause
            game.pause_game()
            if game.is_paused:
                input("Game paused. Press Enter to continue...")
                game.pause_game()
                
        elif command == 's':  # Save
            game.save_game()
            print("Game saved!")
            
        elif command == 'l':  # Load
            if game.load_game():
                print("Game loaded!")
            else:
                print("No saved game found!")
                
        elif command == 'tab':  # Toggle auto-check
            game.auto_check = not game.auto_check
            print(f"Auto-check: {'ON' if game.auto_check else 'OFF'}")
            
        elif command.isdigit() and 1 <= int(command) <= 9:
            row, col = game.selected_cell
            num = int(command)
            
            if game.make_move(row, col, num, note_mode):
                if game.is_complete():
                    game.print_board()
                    elapsed = game.get_elapsed_time()
                    final_score = game.calculate_score()
                    
                    print(f"\n{Fore.GREEN}Congratulations! You've solved the puzzle!{Style.RESET_ALL}")
                    print(f"Time: {elapsed // 60:02d}:{elapsed % 60:02d}")
                    print(f"Mistakes: {game.mistakes}")
                    print(f"Final Score: {final_score}")
                    
                    game.update_high_scores()
                    input("\nPress Enter to continue...")
                    break
            else:
                print("Invalid move!")
        
        # Update board state
        game.update_conflicts()
        game.highlight_related(*game.selected_cell)
        
        if command.strip():  # Only sleep if a command was entered
            time.sleep(0.1)  # Small delay for better user experience

if __name__ == "__main__":
    main()
