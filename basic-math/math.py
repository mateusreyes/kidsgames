import pygame
import random
import sys
import json
import os
from datetime import date
from dataclasses import dataclass, field
from constants import *

pygame.init()

# Windowed maximized
info = pygame.display.Info()
W, H = info.current_w - WINDOW_MARGIN_W, info.current_h - WINDOW_MARGIN_H
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption(WINDOW_TITLE)

# Fonts
font_huge = pygame.font.SysFont(FONT_NAME, FONT_SIZE_HUGE, bold=True)
font_big = pygame.font.SysFont(FONT_NAME, FONT_SIZE_BIG, bold=True)
font_med = pygame.font.SysFont(FONT_NAME, FONT_SIZE_MED)
font_sm = pygame.font.SysFont(FONT_NAME, FONT_SIZE_SM)
font_xs = pygame.font.SysFont(FONT_NAME, FONT_SIZE_XS)

# Colors
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

clock = pygame.time.Clock()

# Sounds
_sound_enabled = True
try:
    pygame.mixer.init()
except pygame.error:
    _sound_enabled = False

_sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")


class _DummySound:
    def play(self):
        pass


if _sound_enabled:
    snd_correct = pygame.mixer.Sound(os.path.join(_sound_dir, SOUND_CORRECT))
    snd_wrong = pygame.mixer.Sound(os.path.join(_sound_dir, SOUND_WRONG))
    snd_easy = pygame.mixer.Sound(os.path.join(_sound_dir, SOUND_EASY))
else:
    snd_correct = _DummySound()
    snd_wrong = _DummySound()
    snd_easy = _DummySound()

# Background image
_img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
_bg_raw = pygame.image.load(os.path.join(_img_dir, BG_IMAGE)).convert()
_bg_cache = {}


def draw_bg(surface):
    size = surface.get_size()
    if size not in _bg_cache:
        _bg_cache[size] = pygame.transform.smoothscale(_bg_raw, size)
    surface.blit(_bg_cache[size], (0, 0))


SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), SAVE_FILENAME)


def load_save():
    today = date.today().isoformat()
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            daily_earned = data.get("daily_earned", 0.0)
            last_date = data.get("last_date", "")
            if last_date != today:
                daily_earned = 0.0
            return (data.get("money", 0.0), data.get("best_streak", 0),
                    daily_earned, data.get("easy_earned", 0.0))
        except (json.JSONDecodeError, IOError):
            pass
    return 0.0, 0, 0.0, 0.0


def save_game(money, best_streak, daily_earned, easy_earned):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump({
                "money": round(money, 2),
                "best_streak": best_streak,
                "daily_earned": round(daily_earned, 2),
                "easy_earned": round(easy_earned, 2),
                "last_date": date.today().isoformat(),
            }, f)
    except IOError:
        pass


def gen_operands(level):
    if level == 1:
        return random.randint(1, 9), random.randint(1, 9)
    elif level == 2:
        return random.randint(10, 50), random.randint(2, 9)
    else:
        return random.randint(10, 99), random.randint(10, 99)


def _is_trivial(a, b, op_index):
    """Reject questions that are too easy (e.g. 1+3, 2*1, 5-0)."""
    if op_index == 0:  # addition
        return a + b <= 5
    elif op_index == 1:  # subtraction
        return a - b == 0 or min(a, b) <= 1
    elif op_index == 2:  # multiplication
        return min(a, b) <= 1
    return False  # division is already constrained


def new_problem(op_index, level, asked):
    for _ in range(500):  # safety cap
        if op_index == 0:  # Addition
            a, b = gen_operands(level)
            if _is_trivial(a, b, op_index):
                continue
            key = (op_index, level, a, b)
            if key in asked:
                continue
            asked.add(key)
            return a, b, "+", a + b
        elif op_index == 1:  # Subtraction
            a, b = gen_operands(level)
            if a < b:
                a, b = b, a
            if _is_trivial(a, b, op_index):
                continue
            key = (op_index, level, a, b)
            if key in asked:
                continue
            asked.add(key)
            return a, b, "-", a - b
        elif op_index == 2:  # Multiplication
            a, b = gen_operands(level)
            if _is_trivial(a, b, op_index):
                continue
            key = (op_index, level, a, b)
            if key in asked:
                continue
            asked.add(key)
            return a, b, "x", a * b
        else:  # Division
            if level == 1:
                b = random.randint(2, 9)
                ans = random.randint(2, 9)
            elif level == 2:
                b = random.randint(2, 9)
                ans = random.randint(10, 50)
            else:
                b = random.randint(10, 99)
                ans = random.randint(2, 20)
            a = b * ans
            key = (op_index, level, a, b)
            if key in asked:
                continue
            asked.add(key)
            return a, b, "/", ans
    # fallback: allow repeats if pool exhausted
    asked.clear()
    return new_problem(op_index, level, asked)


@dataclass
class Problem:
    a: int
    b: int
    symbol: str
    answer: int


@dataclass
class QuizState:
    op_index: int
    level: int
    money: float
    best_streak: int
    daily_earned: float = 0.0
    easy_earned: float = 0.0
    asked: set = field(default_factory=set)
    problem: Problem = None
    user_input: str = ""
    streak: int = 0
    problems_done: int = 0
    tries: int = 0
    feedback: str = ""
    feedback_timer: int = 0
    feedback_color: tuple = GREEN
    timer_ms: int = 0

    def __post_init__(self):
        self.booster = OP_BOOSTER[self.op_index]
        self.reward = round(LEVEL_REWARD[self.level] * self.booster, 2)
        self.timer_limit = LEVEL_TIMER[self.level]
        self.next_problem()

    def next_problem(self):
        a, b, symbol, answer = new_problem(self.op_index, self.level, self.asked)
        self.problem = Problem(a, b, symbol, answer)
        self.user_input = ""
        self.tries = 0
        self.timer_ms = 0

    def check_answer(self, guess):
        if guess == self.problem.answer:
            snd_correct.play()
            if self.daily_earned < DAILY_LIMIT:
                actual_reward = min(self.reward, round(DAILY_LIMIT - self.daily_earned, 2))
                self.money = round(self.money + actual_reward, 2)
                self.daily_earned = round(self.daily_earned + actual_reward, 2)
                if self.level == 1:
                    self.easy_earned = round(self.easy_earned + actual_reward, 2)
            else:
                actual_reward = 0.0
            self.streak += 1
            self.best_streak = max(self.best_streak, self.streak)
            self.problems_done += 1
            # Auto-promote from Easy to Medium after enough correct answers
            if self.level == 1 and self.problems_done >= EASY_PROMO_THRESHOLD:
                self.level = 2
                self.reward = round(LEVEL_REWARD[self.level] * self.booster, 2)
                self.timer_limit = LEVEL_TIMER[self.level]
                self.asked.clear()
            cheer = random.choice(CHEERS)
            if self.daily_earned >= DAILY_LIMIT:
                self.feedback = f"{cheer}   Daily $10 limit reached!"
            else:
                self.feedback = f"{cheer}   +${actual_reward:.2f}"
            if self.streak > 1:
                self.feedback += f"   (streak: {self.streak})"
            self.feedback_color = GREEN
            self.next_problem()
            save_game(self.money, self.best_streak, self.daily_earned, self.easy_earned)
        else:
            snd_wrong.play()
            self.tries += 1
            self.money = round(max(0, self.money - WRONG_PENALTY), 2)
            self.streak = 0
            self.timer_ms = 0
            if self.tries >= MAX_TRIES:
                self.feedback = f"Answer was {self.problem.answer}.   New question!   -${WRONG_PENALTY:.2f}"
                self.feedback_color = ORANGE
                self.next_problem()
            else:
                left = MAX_TRIES - self.tries
                self.feedback = f"Wrong!  -${WRONG_PENALTY:.2f}    ({left} {'try' if left == 1 else 'tries'} left)"
                self.feedback_color = RED
                self.user_input = ""
        self.feedback_timer = FEEDBACK_DURATION
        save_game(self.money, self.best_streak, self.daily_earned, self.easy_earned)

    def handle_timeout(self):
        self.money = round(max(0, self.money - TIMER_PENALTY), 2)
        self.streak = 0
        snd_wrong.play()
        self.feedback = f"Time's up!  Answer was {self.problem.answer}.   -${TIMER_PENALTY:.2f}"
        self.feedback_color = ORANGE
        self.feedback_timer = FEEDBACK_DURATION
        self.next_problem()


def draw_text(text, font, color, x, y, center=True):
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=(x, y)) if center else surf.get_rect(topleft=(x, y))
    screen.blit(surf, rect)
    return rect


def draw_button(text, font, x, y, w, h, color, mouse_pos):
    rect = pygame.Rect(x - w // 2, y - h // 2, w, h)
    hover = rect.collidepoint(mouse_pos)
    c = tuple(min(255, v + 30) for v in color) if hover else color
    pygame.draw.rect(screen, c, rect, border_radius=14)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=14)
    draw_text(text, font, WHITE, x, y)
    return rect


def draw_glass_panel(x, y, w, h, alpha=140, radius=24):
    """Draw a semi-transparent dark panel (frosted glass effect)."""
    panel = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(panel, (20, 25, 40, alpha), (0, 0, w, h), border_radius=radius)
    pygame.draw.rect(panel, (255, 255, 255, 40), (0, 0, w, h), 2, border_radius=radius)
    screen.blit(panel, (x, y))


def draw_progress_bar(problems_done, x, y, w, h):
    level = problems_done // 10
    progress = (problems_done % 10) / 10.0
    pygame.draw.rect(screen, PROGRESS_BG, (x, y, w, h), border_radius=h // 2)
    fill_w = int(w * progress)
    if fill_w > 0:
        pygame.draw.rect(screen, BLUE, (x, y, fill_w, h), border_radius=h // 2)
    pygame.draw.rect(screen, WHITE, (x, y, w, h), 2, border_radius=h // 2)
    draw_text(f"Level {level + 1}", font_xs, WHITE, x + w // 2, y + h // 2)


# ── MENU: pick operation ──
def menu_operation():
    buttons = []
    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, btn in enumerate(buttons):
                    if btn.collidepoint(event.pos):
                        return i

        screen.fill(BG)
        draw_bg(screen)

        # Vertical centering
        num_ops = len(OPERATIONS)
        block_h = 110 + 85 + 120 + num_ops * 95 + 80
        start_y = max(60, (H - block_h) // 2)

        # Glass panel behind content
        last_btn_y = start_y + 370 + (num_ops - 1) * 95
        panel_w = 900
        panel_top = start_y - 140
        panel_bot = last_btn_y + 120
        draw_glass_panel(W // 2 - panel_w // 2, panel_top, panel_w, panel_bot - panel_top)

        draw_text("ELISE & ERIK", font_huge, RED, W // 2, start_y)
        draw_text("MATH GAME", font_big, RED, W // 2, start_y + 85)
        draw_text("Choose an operation:", font_big, WHITE, W // 2, start_y + 230)

        buttons = []
        for i, op in enumerate(OPERATIONS):
            btn = draw_button(f"{op['symbol']}   {op['name']}", font_med,
                              W // 2, start_y + 370 + i * 95, 500, 75, op["color"], mouse_pos)
            buttons.append(btn)

        draw_text("ESC = quit", font_xs, BLACK, W // 2, H - 40)
        pygame.display.flip()


# ── MENU: pick level ──
def menu_level(op_index, easy_earned):
    op = OPERATIONS[op_index]
    easy_locked = easy_earned >= EASY_EARN_LIMIT
    buttons = []
    back_btn = pygame.Rect(0, 0, 0, 0)
    while True:
        clock.tick(FPS)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return None
                for i, btn in enumerate(buttons):
                    if btn.collidepoint(event.pos):
                        if i + 1 == 1 and easy_locked:
                            continue
                        if i + 1 == 1:
                            snd_easy.play()
                        return i + 1

        screen.fill(BG)
        draw_bg(screen)

        # Vertical centering
        block_h = 110 + 120 + 3 * 110 + 80
        start_y = max(60, (H - block_h) // 2)

        # Glass panel behind content
        last_btn_y = start_y + 310 + 2 * 110
        panel_w = 900
        panel_top = start_y - 140
        panel_bot = last_btn_y + 120
        draw_glass_panel(W // 2 - panel_w // 2, panel_top, panel_w, panel_bot - panel_top)

        draw_text(f"{op['symbol']}   {op['name']}", font_huge, op["color"], W // 2, start_y)
        draw_text("Choose difficulty:", font_med, WHITE, W // 2, start_y + 170)

        buttons = []
        for i in range(3):
            by = start_y + 310 + i * 110
            if i == 0 and easy_locked:
                btn = draw_button(LEVEL_NAMES[i], font_med,
                                  W // 2, by, 550, 75, GRAY, mouse_pos)
                draw_text(f"Locked  (${easy_earned:.2f}/${EASY_EARN_LIMIT:.2f} earned)",
                          font_xs, RED, W // 2, by + 52)
            else:
                btn = draw_button(LEVEL_NAMES[i], font_med,
                                  W // 2, by, 550, 75, op["color"], mouse_pos)
                draw_text(LEVEL_DESC[i], font_xs, GRAY, W // 2, by + 52)
            buttons.append(btn)

        back_btn = draw_button("< Back", font_sm, 120, H - 50, 180, 55, CARD, mouse_pos)
        pygame.display.flip()


# ── GAME LOOP ──
def game_loop(op_index, level, money, best_streak_global, daily_earned, easy_earned):
    op = OPERATIONS[op_index]
    q = QuizState(op_index, level, money, best_streak_global, daily_earned, easy_earned)
    tick = 0
    menu_btn = pygame.Rect(0, 0, 0, 0)

    while True:
        dt = clock.tick(FPS)
        tick += 1
        mouse_pos = pygame.mouse.get_pos()

        # Timer: skip to new question when time runs out
        q.timer_ms += dt
        if q.timer_ms >= q.timer_limit:
            q.handle_timeout()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_btn.collidepoint(event.pos):
                    save_game(q.money, q.best_streak, q.daily_earned, q.easy_earned)
                    return q.money, q.best_streak, q.daily_earned, q.easy_earned
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(q.money, q.best_streak, q.daily_earned, q.easy_earned)
                    return q.money, q.best_streak, q.daily_earned, q.easy_earned
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if not q.user_input:
                        continue
                    try:
                        guess = int(q.user_input)
                    except ValueError:
                        q.user_input = ""
                        continue
                    q.check_answer(guess)

                elif event.key == pygame.K_BACKSPACE:
                    q.user_input = q.user_input[:-1]
                elif event.key == pygame.K_MINUS and not q.user_input:
                    q.user_input = "-"
                elif event.unicode.isdigit() and len(q.user_input) < MAX_INPUT_LEN:
                    q.user_input += event.unicode

        if q.feedback_timer > 0:
            q.feedback_timer -= 1

        # === DRAW ===
        W, H = screen.get_size()
        CX = W // 2
        screen.fill(BG)
        draw_bg(screen)

        # ── Top bar ──
        bar_h = 70
        pygame.draw.rect(screen, TOP_BAR_BG, (0, 0, W, bar_h))
        pygame.draw.line(screen, op["color"], (0, bar_h - 1), (W, bar_h - 1), 3)

        # Money
        pygame.draw.rect(screen, DGREEN, (20, 10, 250, 50), border_radius=25)
        draw_text(f"$ {q.money:.2f}", font_sm, WHITE, 145, 35)

        # Title
        draw_text(f"{op['name']}  —  {LEVEL_NAMES[q.level - 1].split(':')[0]}",
                  font_xs, op["color"], CX, 35)

        # Streak
        if q.streak > 0:
            pygame.draw.rect(screen, ORANGE, (W - 240, 10, 220, 50), border_radius=25)
            draw_text(f"Streak: {q.streak}", font_xs, WHITE, W - 130, 35)

        # ── Compute available area ──
        area_top = bar_h + 10
        area_bot = H - 70
        area_h = area_bot - area_top

        # ── Problem card ──
        card_w = min(750, W - 60)
        card_h = min(180, int(area_h * 0.28))
        field_w = (W - 120) * 2 // 5
        field_h = 162

        # Total content block height: card + gap + label + input + hint + feedback
        content_h = card_h + 20 + 30 + field_h + 25 + 50
        content_top = area_top + (area_h - content_h) // 2

        card_x = CX - card_w // 2
        card_y = content_top

        # Glass panel behind quiz content
        panel_w = max(card_w, field_w) + 80
        panel_top = card_y - 30
        panel_bot = card_y + card_h + 120 + 70 + field_h + 80
        draw_glass_panel(CX - panel_w // 2, panel_top, panel_w, panel_bot - panel_top)

        pygame.draw.rect(screen, CARD, (card_x, card_y, card_w, card_h), border_radius=20)
        pygame.draw.rect(screen, CARD_LIT, (card_x, card_y, card_w, card_h), 2, border_radius=20)

        # Equation
        p = q.problem
        equation = f"{p.a}  {p.symbol}  {p.b}  ="
        draw_text(equation, font_big, WHITE, CX, card_y + card_h // 2 - 10)

        # Tries dots
        if q.tries > 0:
            dots = ""
            for i in range(MAX_TRIES):
                dots += "X " if i < q.tries else "O "
            draw_text(dots.strip(), font_sm, RED if q.tries >= 3 else GRAY,
                      CX, card_y + card_h - 25)

        # ── Answer input ──
        input_y = card_y + card_h + 120

        draw_text("Your answer:", font_xs, GRAY, CX, input_y)

        ib = pygame.Rect(CX - field_w // 2, input_y + 70, field_w, field_h)
        pygame.draw.rect(screen, INPUT_BG, ib, border_radius=14)
        pygame.draw.rect(screen, op["color"], ib, 4, border_radius=14)
        cursor = "|" if tick % FPS < FPS // 2 else ""
        draw_text((q.user_input + cursor) or "?", font_huge,
                  WHITE if q.user_input else GRAY, ib.centerx, ib.centery)

        # ── Hint ──
        draw_text("Type answer + ENTER",
                  font_xs, GRAY, CX, ib.bottom + 22)

        # ── Feedback ──
        if q.feedback_timer > 0:
            draw_text(q.feedback, font_sm, q.feedback_color, CX, ib.bottom + 58)

        # ── Bottom bar: stats + timer + menu ──
        bot_y = H - 60

        # Menu button (bottom left)
        menu_btn = draw_button("< Menu", font_xs, 100, bot_y, 160, 45, CARD, mouse_pos)

        # Timer display (bottom right)
        secs_left = max(0, (q.timer_limit - q.timer_ms)) / 1000.0
        timer_color = RED if secs_left < 2 else GRAY
        draw_text(f"-${TIMER_PENALTY:.2f} in {secs_left:.0f}s", font_xs, timer_color, W - 110, bot_y)

        # Stats (center bottom)
        draw_text(f"Solved: {q.problems_done}   |   Best streak: {q.best_streak}",
                  font_xs, GRAY, CX, bot_y - 20)
        bar_w = min(400, W - 300)
        draw_progress_bar(q.problems_done, CX - bar_w // 2, bot_y, bar_w, 24)

        pygame.display.flip()


def main():
    money, best_streak, daily_earned, easy_earned = load_save()
    while True:
        op_index = menu_operation()
        level = menu_level(op_index, easy_earned)
        if level is None:
            continue
        money, best_streak, daily_earned, easy_earned = game_loop(
            op_index, level, money, best_streak, daily_earned, easy_earned)


if __name__ == "__main__":
    main()
