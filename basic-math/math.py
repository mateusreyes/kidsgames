import pygame
import random
import sys
import json
import os
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
pygame.mixer.init()
_sound_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sounds")
snd_correct = pygame.mixer.Sound(os.path.join(_sound_dir, SOUND_CORRECT))
snd_wrong = pygame.mixer.Sound(os.path.join(_sound_dir, SOUND_WRONG))
snd_easy = pygame.mixer.Sound(os.path.join(_sound_dir, SOUND_EASY))

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
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
            return data.get("money", 0.0), data.get("best_streak", 0)
        except (json.JSONDecodeError, IOError):
            pass
    return 0.0, 0


def save_game(money, best_streak):
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump({"money": round(money, 2), "best_streak": best_streak}, f)
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
        draw_text("ELISE & ERIK", font_huge, GOLD, W // 2, 90)
        draw_text("MATH GAME", font_big, GOLD, W // 2, 175)
        draw_text("Choose an operation:", font_med, GRAY, W // 2, 270)

        buttons = []
        for i, op in enumerate(OPERATIONS):
            btn = draw_button(f"{op['symbol']}   {op['name']}", font_med,
                              W // 2, 370 + i * 95, 500, 75, op["color"], mouse_pos)
            buttons.append(btn)

        draw_text("ESC = quit", font_xs, GRAY, W // 2, H - 40)
        pygame.display.flip()


# ── MENU: pick level ──
def menu_level(op_index):
    op = OPERATIONS[op_index]
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
                        if i + 1 == 1:
                            snd_easy.play()
                        return i + 1

        screen.fill(BG)
        draw_bg(screen)
        draw_text(f"{op['symbol']}   {op['name']}", font_huge, op["color"], W // 2, 120)
        draw_text("Choose difficulty:", font_med, GRAY, W // 2, 230)

        buttons = []
        for i in range(3):
            by = 340 + i * 110
            btn = draw_button(LEVEL_NAMES[i], font_med,
                              W // 2, by, 550, 75, op["color"], mouse_pos)
            buttons.append(btn)
            draw_text(LEVEL_DESC[i], font_xs, GRAY, W // 2, by + 52)

        back_btn = draw_button("< Back", font_sm, 120, H - 50, 180, 55, CARD, mouse_pos)
        pygame.display.flip()


# ── GAME LOOP ──
def game_loop(op_index, level, money, best_streak_global):
    op = OPERATIONS[op_index]
    asked = set()
    booster = OP_BOOSTER[op_index]
    reward = round(LEVEL_REWARD[level] * booster, 2)
    a, b, symbol, answer = new_problem(op_index, level, asked)
    user_input = ""
    streak = 0
    best_streak = best_streak_global
    problems_done = 0
    tries = 0
    max_tries = MAX_TRIES
    feedback = ""
    feedback_timer = 0
    feedback_color = GREEN
    tick = 0
    menu_btn = pygame.Rect(0, 0, 0, 0)
    timer_ms = 0
    timer_limit = LEVEL_TIMER[level]

    while True:
        dt = clock.tick(FPS)
        tick += 1
        mouse_pos = pygame.mouse.get_pos()

        # Timer: skip to new question when time runs out
        timer_ms += dt
        if timer_ms >= timer_limit:
            timer_ms = 0
            money = round(max(0, money - TIMER_PENALTY), 2)
            streak = 0
            snd_wrong.play()
            feedback = f"Time's up!  Answer was {answer}.   -${TIMER_PENALTY:.2f}"
            feedback_color = ORANGE
            feedback_timer = FEEDBACK_DURATION
            a, b, symbol, answer = new_problem(op_index, level, asked)
            user_input = ""
            tries = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if menu_btn.collidepoint(event.pos):
                    save_game(money, best_streak)
                    return money, best_streak
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    save_game(money, best_streak)
                    return money, best_streak  # back to menus
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if not user_input:
                        continue
                    try:
                        guess = int(user_input)
                    except ValueError:
                        user_input = ""
                        continue

                    if guess == answer:
                        snd_correct.play()
                        money = round(money + reward, 2)
                        streak += 1
                        best_streak = max(best_streak, streak)
                        problems_done += 1
                        cheer = random.choice(CHEERS)
                        feedback = f"{cheer}   +${reward:.2f}"
                        if streak > 1:
                            feedback += f"   (streak: {streak})"
                        feedback_color = GREEN
                        a, b, symbol, answer = new_problem(op_index, level, asked)
                        user_input = ""
                        tries = 0
                        timer_ms = 0
                        save_game(money, best_streak)
                    else:
                        snd_wrong.play()
                        tries += 1
                        money = round(max(0, money - WRONG_PENALTY), 2)
                        streak = 0
                        timer_ms = 0
                        if tries >= max_tries:
                            feedback = f"Answer was {answer}.   New question!   -${WRONG_PENALTY:.2f}"
                            feedback_color = ORANGE
                            a, b, symbol, answer = new_problem(op_index, level, asked)
                            user_input = ""
                            tries = 0
                        else:
                            left = max_tries - tries
                            feedback = f"Wrong!  -${WRONG_PENALTY:.2f}    ({left} {'try' if left == 1 else 'tries'} left)"
                            feedback_color = RED
                            user_input = ""

                    feedback_timer = FEEDBACK_DURATION

                elif event.key == pygame.K_BACKSPACE:
                    user_input = user_input[:-1]
                elif event.key == pygame.K_MINUS and not user_input:
                    user_input = "-"
                elif event.unicode.isdigit() and len(user_input) < MAX_INPUT_LEN:
                    user_input += event.unicode

        if feedback_timer > 0:
            feedback_timer -= 1

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
        draw_text(f"$ {money:.2f}", font_sm, WHITE, 145, 35)

        # Title
        draw_text(f"{op['name']}  —  {LEVEL_NAMES[level - 1].split(':')[0]}",
                  font_xs, op["color"], CX, 35)

        # Streak
        if streak > 0:
            pygame.draw.rect(screen, ORANGE, (W - 240, 10, 220, 50), border_radius=25)
            draw_text(f"Streak: {streak}", font_xs, WHITE, W - 130, 35)

        # ── Compute available area ──
        area_top = bar_h + 10
        area_bot = H - 10
        area_h = area_bot - area_top

        # ── Problem card ──
        card_w = min(750, W - 60)
        card_h = min(180, int(area_h * 0.28))
        card_x = CX - card_w // 2
        card_y = area_top + 10
        pygame.draw.rect(screen, CARD, (card_x, card_y, card_w, card_h), border_radius=20)
        pygame.draw.rect(screen, CARD_LIT, (card_x, card_y, card_w, card_h), 2, border_radius=20)

        # Equation
        equation = f"{a}  {symbol}  {b}  ="
        draw_text(equation, font_big, WHITE, CX, card_y + card_h // 2 - 10)

        # Tries dots
        if tries > 0:
            dots = ""
            for i in range(max_tries):
                dots += "X " if i < tries else "O "
            draw_text(dots.strip(), font_sm, RED if tries >= 3 else GRAY,
                      CX, card_y + card_h - 25)

        # ── Answer input ──
        input_y = card_y + card_h + 20
        field_w, field_h = 300, 60

        draw_text("Your answer:", font_xs, GRAY, CX, input_y)

        ib = pygame.Rect(CX - field_w // 2, input_y + 18, field_w, field_h)
        pygame.draw.rect(screen, INPUT_BG, ib, border_radius=12)
        pygame.draw.rect(screen, op["color"], ib, 4, border_radius=12)
        cursor = "|" if tick % FPS < FPS // 2 else ""
        draw_text((user_input + cursor) or "?", font_big,
                  WHITE if user_input else GRAY, ib.centerx, ib.centery)

        # ── Hint ──
        draw_text("Type answer + ENTER",
                  font_xs, GRAY, CX, ib.bottom + 20)

        # ── Feedback ──
        if feedback_timer > 0:
            draw_text(feedback, font_sm, feedback_color, CX, ib.bottom + 55)

        # ── Bottom bar: stats + timer + menu ──
        bot_y = H - 60

        # Menu button (bottom left)
        menu_btn = draw_button("< Menu", font_xs, 100, bot_y, 160, 45, CARD, mouse_pos)

        # Timer display (bottom right)
        secs_left = max(0, (timer_limit - timer_ms)) / 1000.0
        timer_color = RED if secs_left < 2 else GRAY
        draw_text(f"-${TIMER_PENALTY:.2f} in {secs_left:.0f}s", font_xs, timer_color, W - 110, bot_y)

        # Stats (center bottom)
        draw_text(f"Solved: {problems_done}   |   Best streak: {best_streak}",
                  font_xs, GRAY, CX, bot_y - 20)
        bar_w = min(400, W - 300)
        draw_progress_bar(problems_done, CX - bar_w // 2, bot_y, bar_w, 24)

        pygame.display.flip()


def main():
    money, best_streak = load_save()
    while True:
        op_index = menu_operation()
        level = menu_level(op_index)
        if level is None:
            continue
        money, best_streak = game_loop(op_index, level, money, best_streak)


if __name__ == "__main__":
    main()
