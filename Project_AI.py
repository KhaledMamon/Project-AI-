import tkinter as tk
from tkinter import messagebox
import shogi  # type: ignore
import random
import os
from PIL import Image, ImageTk  # type: ignore

# Configuration & Constants
PIECE_NAMES = {
    'K': '玉',  'G': '金',
    'P': '歩',  '+P': 'と', 
    'L': '香',  '+L': '杏',  
    'N': '桂',  '+N': '圭',
    'S': '銀',  '+S': '全',  
    'B': '角',  '+B': '馬',
    'R': '飛',  '+R': '龍',

    'k': '王',  'g': '金',
    'p': '歩',  '+p': 'と', 
    'l': '香',  '+l': '杏', 
    'n': '桂',  '+n': '圭',
    's': '銀',  '+s': '全', 
    'b': '角',  '+b': '馬',
    'r': '飛',  '+r': '龍',
}

PIECE_IMAGE_MAPPING = {
    'K': 'king0.png',   'G': 'gold0.png', 
    'P': 'soldier0.png',  '+P': 'soldier00.png',
    'L': 'sheft0.png',  '+L': 'sheft00.png', 
    'N': 'hourse0.png',  '+N': 'hourse00.png',  
    'S': 'silver0.png',  '+S': 'silver00.png',  
    'B': 'elepent0.png',  '+B': 'elepent00.png',  
    'R': 'fort0.png',  '+R': 'fort00.png',

    'k': 'king0.png',  'g': 'gold0.png', 
    'p': 'soldier0.png',  '+p': 'soldier00.png', 
    'l': 'sheft0.png',  '+l': 'sheft00.png', 
    'n': 'hourse0.png',  '+n': 'hourse00.png', 
    's': 'silver0.png',  '+s': 'silver00.png', 
    'b': 'elepent0.png',  '+b': 'elepent00.png',
    'r': 'fort0.png',  '+r': 'fort00.png',
}

PIECE_VALUES = {
    shogi.PAWN:   1,   # soldir
    shogi.LANCE:  3,   # sheft
    shogi.KNIGHT: 3,   # Horse
    shogi.SILVER: 5,   
    shogi.GOLD:   6,   
    shogi.BISHOP: 8,   # Elephant
    shogi.ROOK:   10,  # Fort
    shogi.KING:   1000
}

# AI Logic
def evaluate_board(board):
    score = 0
    for square in range(81):
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES.get(piece.piece_type, 0)
            score += value if piece.color == shogi.BLACK else -value
    return score

# Easy Algorithm: Random Move
def random_ai_move(board):
    return random.choice(list(board.legal_moves))

# Medium & Hard Algorithm: Alpha-Beta depth 2 & 3
def alphabeta(board, depth, alpha, beta, maximizing):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None
    best_move = None
    if maximizing:
        max_eval = -float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = alphabeta(board, depth-1, alpha, beta, False)
            board.pop()
            if eval_score > max_eval:
                max_eval, best_move = eval_score, move
            alpha = max(alpha, eval_score)
            if beta <= alpha: break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in board.legal_moves:
            board.push(move)
            eval_score, _ = alphabeta(board, depth-1, alpha, beta, True)
            board.pop()
            if eval_score < min_eval:
                min_eval, best_move = eval_score, move
            beta = min(beta, eval_score)
            if beta <= alpha: break
        return min_eval, best_move

# View Class (UI)
class ShogiBoardView:
    def __init__(self, root, controller):
        self.root = root
        self.controller = controller
        self.root.title("Shogi Arena - Pro Dashboard")
        self.root.configure(bg='#333333') # Dark background for the app window
        
        self.buttons = {}
        self.piece_images = {}
        self.dummy_img = tk.PhotoImage(width=1, height=1)
        
        self.load_images()
        self.build_ui()

    def load_images(self):
        img_dir = 'Final Version/Images'
        size = (45, 45) 
        if not os.path.exists(img_dir): return
        
        for symbol, filename in PIECE_IMAGE_MAPPING.items():
            path = os.path.join(img_dir, filename)
            if os.path.exists(path):
                try:
                    pil_image = Image.open(path).convert("RGBA")
                    resized_image = pil_image.resize(size, Image.Resampling.LANCZOS)
                    self.piece_images[symbol] = ImageTk.PhotoImage(resized_image)
                    self.piece_images[symbol.lower()] = ImageTk.PhotoImage(resized_image.rotate(180))
                except Exception as e:
                    pass

    def build_ui(self):
        # Main Layout Frames
        self.left_panel = tk.Frame(self.root, bg='#2C3E50', width=200, padx=10, pady=10)
        self.center_panel = tk.Frame(self.root, bg='#D2B48C', padx=15, pady=15)
        self.right_panel = tk.Frame(self.root, bg='#2C3E50', width=200, padx=10, pady=10)
        self.bottom_panel = tk.Frame(self.root, bg='#1A252F', pady=10)

        self.left_panel.grid(row=0, column=0, sticky="nsew")
        self.center_panel.grid(row=0, column=1)
        self.right_panel.grid(row=0, column=2, sticky="nsew")
        self.bottom_panel.grid(row=1, column=0, columnspan=3, sticky="ew")

        # Left Panel
        tk.Label(self.left_panel, text=" AI (White) ▼", font=('Arial', 14, 'bold'), fg='white', bg='#2C3E50').pack(pady=10)
        tk.Label(self.left_panel, text="Captured Pieces:", font=('Arial', 10), fg='#BDC3C7', bg='#2C3E50').pack()
        self.ai_captured_lbl = tk.Label(self.left_panel, text="None", font=('Arial', 12), fg='white', bg='#34495E', width=15, height=5)
        self.ai_captured_lbl.pack(pady=5)

        # Center Panel
        self.board_frame = tk.Frame(self.center_panel, bg='black') # Black border
        self.board_frame.pack()
        for r in range(9):
            for c in range(9):
                btn = tk.Button(self.board_frame, image=self.dummy_img, width=70, height=70,
                                compound="center", bg='#F5DEB3', relief="flat", borderwidth=1,
                                command=lambda row=r, col=c: self.controller.on_square_clicked(row, col))
                btn.grid(row=r, column=8-c, padx=0.5, pady=0.5) # 1px padding for grid lines
                self.buttons[(r, c)] = btn
                
        self.status_lbl = tk.Label(self.center_panel, text="Game Started", font=('Arial', 12, 'bold'), bg='#D2B48C')
        self.status_lbl.pack(pady=10)

        # Right Panel
        tk.Label(self.right_panel, text="👤 You (Black) ▲", font=('Arial', 14, 'bold'), fg='white', bg='#2C3E50').pack(pady=10)
        tk.Label(self.right_panel, text="Captured Pieces:", font=('Arial', 10), fg='#BDC3C7', bg='#2C3E50').pack()
        self.player_captured_lbl = tk.Label(self.right_panel, text="None", font=('Arial', 12), fg='white', bg='#34495E', width=15, height=5)
        self.player_captured_lbl.pack(pady=5)
        
        tk.Label(self.right_panel, text="Move History", font=('Arial', 10, 'bold'), fg='white', bg='#2C3E50').pack(pady=(20, 5))
        self.history_list = tk.Listbox(self.right_panel, height=15, width=20, bg='#34495E', fg='white', borderwidth=0)
        self.history_list.pack()

        # Bottom Panel
        control_frame = tk.Frame(self.bottom_panel, bg='#1A252F')
        control_frame.pack()
        
        btn_style = {'font':('Arial', 12, 'bold'), 'fg':'white', 'bg':'#2980B9', 'width':10, 'relief':'flat'}
        tk.Button(control_frame, text="⏪ Undo", command=self.controller.undo_move, **btn_style).pack(side=tk.LEFT, padx=10)
        tk.Button(control_frame, text="Resign", command=self.controller.resign_game, bg='#C0392B', fg='white', font=('Arial', 12, 'bold'), width=10, relief='flat').pack(side=tk.LEFT, padx=10)
        
        level_frame = tk.Frame(control_frame, bg='#1A252F')
        level_frame.pack(side=tk.LEFT, padx=20)
        tk.Label(level_frame, text="AI Level:", fg='white', bg='#1A252F', font=('Arial', 10)).pack(side=tk.LEFT)
        for lvl in ["easy", "medium", "hard"]:
            tk.Button(level_frame, text=lvl.capitalize(), command=lambda l=lvl: self.controller.set_level(l), bg='#7F8C8D', fg='white', relief='flat').pack(side=tk.LEFT, padx=2)

    def refresh_ui(self, board, last_move=None):
        # 1. Update Board Squares
        for r in range(9):
            for c in range(9):
                square = r * 9 + c
                piece = board.piece_at(square)
                btn = self.buttons[(r, c)]
                btn.config(bg='#F5DEB3') # Reset color

                if piece:
                    symbol = piece.symbol()
                    if symbol in self.piece_images:
                        btn.config(image=self.piece_images[symbol], text="")
                    else:
                        is_promoted = '+' in symbol
                        name = PIECE_NAMES.get(symbol.upper(), symbol.upper().replace('+', ''))
                        color = "red" if is_promoted else "black"
                        direction = "▲" if piece.color == shogi.BLACK else "▼"
                        btn.config(image=self.dummy_img, text=f"{direction}\n{name}", fg=color, font=('Arial', 12, 'bold'))
                else:
                    btn.config(image=self.dummy_img, text="")

        # 2. Update Captured Pieces
        def format_komadai(color):
            pieces = board.pieces_in_hand[color]
            text = ""
            for piece_type, count in pieces.items():
                if count > 0:
                    symbol = shogi.Piece(piece_type, color).symbol().upper()
                    name = PIECE_NAMES.get(symbol, symbol).replace('\n | ', '').replace('\n ↑ ', '').replace('\n ⋎ ', '') # Clean text
                    text += f"{name}: {count}\n"
            return text if text else "None"

        self.player_captured_lbl.config(text=format_komadai(shogi.BLACK))
        self.ai_captured_lbl.config(text=format_komadai(shogi.WHITE))

        # 3. Update Move History
        if last_move:
            turn_num = len(board.move_stack)
            self.history_list.insert(tk.END, f"{turn_num}. {last_move}")
            self.history_list.yview(tk.END) # Auto-scroll to bottom

    def highlight_selected(self, row, col):
        self.buttons[(row, col)].config(bg='#F1C40F') # Yellow

    def highlight_destinations(self, squares_list):
        for square in squares_list:
            r, c = square // 9, square % 9
            self.buttons[(r, c)].config(bg='#2ECC71') # Green

    def update_status(self, text):
        self.status_lbl.config(text=text)

#  Controller Class
class ShogiGameController:
    def __init__(self, root):
        self.root = root
        self.board = shogi.Board()
        self.selected_square = None
        self.ai_level = "medium"
        
        self.view = ShogiBoardView(root, self)
        self.view.refresh_ui(self.board)

    def set_level(self, level):
        self.ai_level = level
        messagebox.showinfo("AI Level", f"Difficulty changed to: {level.upper()}")

    def undo_move(self):
        if len(self.board.move_stack) >= 2:
            self.board.pop() # Undo AI
            self.board.pop() # Undo Player
            self.view.history_list.delete(tk.END)
            self.view.history_list.delete(tk.END)
            self.selected_square = None
            self.view.refresh_ui(self.board)
            self.view.update_status("Move Undone")

    def resign_game(self):
        if messagebox.askyesno("Resign", "Are you sure you want to resign?"):
            messagebox.showinfo("Game Over", "White (AI) wins by resignation!")
            self.board.reset()
            self.view.history_list.delete(0, tk.END)
            self.view.refresh_ui(self.board)

    def on_square_clicked(self, row, col):
        if self.board.turn != shogi.BLACK: return

        square = row * 9 + col

        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and piece.color == shogi.BLACK:
                self.selected_square = square
                self.view.refresh_ui(self.board)
                self.view.highlight_selected(row, col)
                
                legal_dests = [m.to_square for m in self.board.legal_moves if m.from_square == square]
                self.view.highlight_destinations(legal_dests)
        else:
            move = shogi.Move(self.selected_square, square)
            promo_move = shogi.Move(self.selected_square, square, promotion=True)
            target_move = None

            if move in self.board.legal_moves:
                target_move = move
                if promo_move in self.board.legal_moves:
                    if messagebox.askyesno("Promotion", "Promote this piece?"):
                        target_move = promo_move
            elif promo_move in self.board.legal_moves:
                target_move = promo_move

            if target_move:
                self.board.push(target_move)
                self.selected_square = None
                self.view.refresh_ui(self.board, last_move=target_move.usi())
                
                if not self.check_game_status():
                    self.view.update_status("AI is thinking...")
                    self.root.after(100, self.ai_turn)
            else:
                self.selected_square = None
                self.view.refresh_ui(self.board)

    def ai_turn(self):
        if self.board.is_game_over(): return

        depth = {"easy": 1, "medium": 2, "hard": 3}[self.ai_level]
        if self.ai_level == "easy":
            move = random_ai_move(self.board)
        else:
            _, move = alphabeta(self.board, depth, -float('inf'), float('inf'), False)
            
        if move:
            self.board.push(move)
            self.view.refresh_ui(self.board, last_move=move.usi())
            self.check_game_status()

    def check_game_status(self):
        if self.board.is_checkmate():
            winner = "White (AI)" if self.board.turn == shogi.BLACK else "Black (You)"
            messagebox.showinfo("Checkmate", f"Winner: {winner}")
            self.board.reset()
            self.view.history_list.delete(0, tk.END)
            self.view.refresh_ui(self.board)
            return True

        turn_text = "Your Turn ▲" if self.board.turn == shogi.BLACK else "AI Turn ▼"
        self.view.update_status(turn_text)
        return False


if __name__ == "__main__":
    root = tk.Tk()
    root.resizable(False, False) 
    app = ShogiGameController(root)
    root.mainloop()