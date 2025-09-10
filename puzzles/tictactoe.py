# puzzles/tictactoe.py
import random
from PIL import ImageDraw
from .base_puzzle import BasePuzzle

class TicTacToePuzzle(BasePuzzle):
    WIN_CONDITIONS = [[0, 1, 2], [3, 4, 5], [6, 7, 8], [0, 3, 6], [1, 4, 7], [2, 5, 8], [0, 4, 8], [2, 4, 6]]

    def generate(self):
        # Loop until a valid, non-ambiguous board is generated
        while True:
            board = self._generate_board_state()
            if board:
                start_board, winner, winning_move = board
                break
        
        # Create input image from the starting board
        input_image = self._create_new_image()
        draw_input = ImageDraw.Draw(input_image)
        self._draw_grid(draw_input)
        self._draw_board(draw_input, start_board)

        # Create target image by adding the winning move
        target_image = input_image.copy()
        draw_target = ImageDraw.Draw(target_image)
        
        row, col = winning_move // 3, winning_move % 3
        if winner == 'X':
            self._draw_x(draw_target, row, col, self.line_color)
        else:
            self._draw_o(draw_target, row, col, self.line_color)

        description = f"Please place the winning {winner} for the tic-tac-toe game"
        return input_image, target_image, description

    def _generate_board_state(self):
        board = [''] * 9
        
        win_line = random.choice(self.WIN_CONDITIONS)
        winner = random.choice(['X', 'O'])
        loser = 'O' if winner == 'X' else 'X'

        win_spots = random.sample(win_line, 2)
        winning_move = list(set(win_line) - set(win_spots))[0]
        for spot in win_spots:
            board[spot] = winner

        num_loser_marks = 2 if winner == 'X' else 3
        
        available_spots = [i for i, mark in enumerate(board) if mark == '' and i != winning_move]

        if len(available_spots) < num_loser_marks:
            return None # Not enough empty space, invalid game

        loser_spots = random.sample(available_spots, num_loser_marks)
        for spot in loser_spots:
            board[spot] = loser
        
        # Check for invalid states
        if self._check_win(board, loser) or self._check_win(board, winner):
            return None # Invalid or ambiguous puzzle

        # Create a version of the board *before* the winning move
        start_board = list(board)
        start_board[winning_move] = ''

        return start_board, winner, winning_move

    def _check_win(self, current_board, player):
        for line in self.WIN_CONDITIONS:
            if all(current_board[i] == player for i in line):
                return True
        return False

    def _draw_grid(self, draw):
        cell_size = self.img_size / 3
        for i in range(1, 3):
            draw.line([(i * cell_size, 10), (i * cell_size, self.img_size - 10)], fill=self.line_color, width=5)
            draw.line([(10, i * cell_size), (self.img_size - 10, i * cell_size)], fill=self.line_color, width=5)

    def _draw_board(self, draw, board_state):
        for i, mark in enumerate(board_state):
            row, col = i // 3, i % 3
            if mark == 'X':
                self._draw_x(draw, row, col, self.line_color)
            elif mark == 'O':
                self._draw_o(draw, row, col, self.line_color)

    def _draw_x(self, draw, r, c, color):
        cell_size = self.img_size / 3
        margin = cell_size * 0.2
        draw.line([(c * cell_size + margin, r * cell_size + margin), ((c + 1) * cell_size - margin, (r + 1) * cell_size - margin)], fill=color, width=8)
        draw.line([(c * cell_size + margin, (r + 1) * cell_size - margin), ((c + 1) * cell_size - margin, r * cell_size + margin)], fill=color, width=8)

    def _draw_o(self, draw, r, c, color):
        cell_size = self.img_size / 3
        margin = cell_size * 0.2
        draw.ellipse([(c * cell_size + margin, r * cell_size + margin), ((c + 1) * cell_size - margin, (r + 1) * cell_size - margin)], outline=color, width=8)