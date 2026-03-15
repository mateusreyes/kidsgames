# ── Window ──
WINDOW_TITLE = "Elise & Erik Math Game"
WINDOW_MARGIN_W = 40
WINDOW_MARGIN_H = 80

# ── Font ──
FONT_NAME = "Arial"
FONT_SIZE_HUGE = 110
FONT_SIZE_BIG = 84
FONT_SIZE_MED = 56
FONT_SIZE_SM = 42
FONT_SIZE_XS = 34

# ── Colors ──
WHITE = (255, 255, 255)
BLACK = (30, 30, 30)
GREEN = (46, 204, 113)
DGREEN = (39, 174, 96)
RED = (231, 76, 60)
BLUE = (52, 152, 219)
GOLD = (241, 196, 15)
GRAY = (200, 200, 200)
ORANGE = (230, 126, 34)
PURPLE = (155, 89, 182)
BG = (34, 47, 62)
CARD = (52, 73, 94)
CARD_LIT = (62, 88, 112)
TOP_BAR_BG = (20, 30, 45)
INPUT_BG = (40, 50, 70)
PROGRESS_BG = (30, 30, 50)

# ── Sound files ──
SOUND_CORRECT = "correct.mp3"
SOUND_WRONG = "wrong.mp3"
SOUND_EASY = "easy.mp3"

# ── Background image ──
BG_IMAGE = "bg.webp"

# ── Cheers ──
CHEERS = [
    "Awesome!", "Brilliant!", "Nailed it!", "You're on fire!",
    "Math genius!", "Ka-ching!", "Superb!", "Wow!", "Amazing!",
    "Fantastic!", "Perfect!", "Excellent!", "Great job!", "Nice one!",
]

# ── Operations ──
OPERATIONS = [
    {"name": "Addition", "symbol": "+", "color": GREEN},
    {"name": "Subtraction", "symbol": "-", "color": BLUE},
    {"name": "Multiplication", "symbol": "x", "color": ORANGE},
    {"name": "Division", "symbol": "/", "color": PURPLE},
]

# ── Levels ──
LEVEL_NAMES = ["Level 1: Easy", "Level 2: Medium", "Level 3: Hard"]
LEVEL_DESC = ["Single-digit (1-9)", "Two-digit (10-50)", "Double-digit (10-99)"]
LEVEL_REWARD = {1: 0.01, 2: 0.02, 3: 0.04}
LEVEL_TIMER = {1: 6000, 2: 50000, 3: 100000}  # ms per question

# ── Operation boosters ──
OP_BOOSTER = {0: 1, 
              1: 1, 
              2: 2, 
              3: 3}  # +1x, -2x, x3x, /4x

# ── Gameplay ──
EASY_PROMO_THRESHOLD = 10  # correct answers on Easy before auto-promoting to Medium
EASY_EARN_LIMIT = 1.00  # max $ earnable on Easy before it gets disabled
MAX_TRIES = 3
WRONG_PENALTY = 0.03
TIMER_PENALTY = 0.02
DAILY_LIMIT = 10.00
MAX_INPUT_LEN = 8
FPS = 30
FEEDBACK_DURATION = 150  # frames

# ── Save file ──
SAVE_FILENAME = "save.json"
