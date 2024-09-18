import pygame
import random
import sys
from pygame.locals import *

# 初始化 Pygame
pygame.init()
pygame.mixer.init()

# 加载背景音乐
pygame.mixer.music.load("bgm.ogg")
pygame.mixer.music.set_volume(0.5)  # 设置音乐音量（0.0 到 1.0）
pygame.mixer.music.play(-1)  # -1 表示循环播放

# 定义难度级别
difficulties = {
    '简单': {
        'game_time': 120,
        'layers': 2,
    },
    '困难': {
        'game_time': 90,
        'layers': 3,
    },
    '地狱': {
        'game_time': 60,
        'layers': 4,
    }
}

# 默认难度
current_difficulty = '简单'

# 定义常量
WIDTH, HEIGHT = 600, 600
TILE_SIZE = 60  
GRID_SIZE = TILE_SIZE
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG_COLOR = (200, 200, 200)
FONT_PATH = r'C:\Users\刘哲睿\Desktop\Typora\client\simhei.ttf'
FONT_SIZE = 36
GAME_TIME = 60

# 创建窗口
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("消了个消")

# 加载字体
FONT = pygame.font.Font(FONT_PATH, FONT_SIZE)

# 加载图案图片
pattern_images = [pygame.image.load(f"p{i}.png") for i in range(1, 7)]
pattern_images = [pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE)) for img in pattern_images]

# 加载时钟图片
clock_image = pygame.image.load("clock.jpeg")
# 缩小时钟图片
small_clock_size = 60
clock_image = pygame.transform.scale(clock_image, (small_clock_size, small_clock_size))
gray_clock_image = None

# 游戏板
board = []
slots = [None] * 7
selected = []
score = 0
clock_uses_left = 0
game_over = False
victory = False

# 创建一个 Clock 对象
timer = pygame.time.Clock()

# 初始化游戏
def initialize_game(difficulty):
    global GAME_TIME, score, clock_uses_left, game_over, victory, slots
    settings = difficulties[difficulty]
    GAME_TIME = settings['game_time']
    score = 0
    clock_uses_left = 2 if difficulty == '简单' else 1 if difficulty == '困难' else 0
    game_over = False
    victory = False
    slots = [None] * 7  # 清空格子
    generate_board()


def generate_board():
    global board
    layers = difficulties[current_difficulty]['layers']
    image_size = TILE_SIZE
    board = []
    image_indices = []

    # 计算总共需要多少张图片，并确保每种图片数量是3的倍数
    num_images_per_layer = 15
    total_images = num_images_per_layer * layers
    num_patterns = len(pattern_images)

    num_per_pattern = (total_images // num_patterns) // 3 * 3  # 确保每种图片的数量是3的倍数
    if total_images % num_patterns != 0:
        num_per_pattern += 3  # 处理余数，确保总数是3的倍数

    for i in range(num_patterns):
        image_indices.extend([i] * num_per_pattern)

    random.shuffle(image_indices)  # 随机打乱图片索引

    # 生成各层图片的位置
    for layer in range(layers):
        positions = []
        for _ in range(num_images_per_layer):  # 每个图层生成15张图片
            while True:
                x = random.randint(0, WIDTH - image_size)
                y = random.randint(0, HEIGHT - GRID_SIZE - image_size)  # 确保图片不会低于格子区域

                overlapping = False
                for pos in positions:
                    if abs(x - pos[0]) < image_size and abs(y - pos[1]) < image_size:
                        overlapping = True
                        break

                if not overlapping:
                    positions.append((x, y))
                    if image_indices:  # 确保 image_indices 不为空
                        pattern_index = image_indices.pop()
                        board.append({'pattern': pattern_index, 'layer': layer, 'x': x, 'y': y})
                    break

# 绘制游戏板
def draw_board():
    screen.fill(BG_COLOR)

    # 加载并绘制背景图
    background_image = pygame.image.load("bk.webp")
    background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
    screen.blit(background_image, (0, 0))

    sorted_board = sorted(board, key=lambda item: item['layer'])

    for item in sorted_board:
        image = pattern_images[item['pattern']]
        x_pos = item['x']
        y_pos = item['y']
        screen.blit(image, (x_pos, y_pos))

    draw_score()
    draw_timer()
    draw_clock(gray_clock_image)
    draw_slots()


def draw_score():
    score_text = FONT.render(f"分数: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))

def draw_timer():
    time_elapsed = pygame.time.get_ticks() - start_ticks
    time_left = max(GAME_TIME * 1000 - time_elapsed, 0)
    timer_text = FONT.render(f"时间: {time_left // 1000:02d}:{(time_left // 10) % 100:02d}", True, WHITE)
    screen.blit(timer_text, (WIDTH - 150, 10))

def draw_clock(gray_image):
    if clock_uses_left > 0:
        screen.blit(clock_image, (WIDTH - small_clock_size, HEIGHT - small_clock_size))
    else:
        if gray_image is None:
            gray_image = make_grayscale(clock_image)
        screen.blit(gray_image, (WIDTH - small_clock_size, HEIGHT - small_clock_size))

def make_grayscale(image):
    gray_image = pygame.Surface(image.get_size())
    for y in range(image.get_height()):
        for x in range(image.get_width()):
            color = image.get_at((x, y))
            average = (color.r + color.g + color.b) // 3
            gray_color = (average, average, average)
            gray_image.set_at((x, y), gray_color)
    return gray_image

def draw_slots():
    # 计算底部格子的起始位置以居中
    start_x = (WIDTH - GRID_SIZE * 7) // 2
    y = HEIGHT - GRID_SIZE

    for i, slot in enumerate(slots):
        x = start_x + i * GRID_SIZE
        pygame.draw.rect(screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE), 1)
        if slot is not None:
            image = pattern_images[slot['pattern']]
            screen.blit(image, (x, y))


def handle_click(x, y):
    global selected, score, clock_uses_left, GAME_TIME, game_over, victory
    if game_over:
        return

    if x > WIDTH - small_clock_size and y > HEIGHT - small_clock_size:
        if clock_uses_left > 0:
            clock_uses_left -= 1
            GAME_TIME += 10
        return

    clicked_item = None
    for item in reversed(board):
        image_rect = pygame.Rect(item['x'], item['y'], TILE_SIZE, TILE_SIZE)
        expanded_rect = pygame.Rect(item['x'] - 5, item['y'] - 5, TILE_SIZE + 10, TILE_SIZE + 10)
        if expanded_rect.collidepoint(x, y):
            clicked_item = item
            break

    if clicked_item:
        if len(selected) < 7:
            # 寻找第一个空的格子
            empty_slot_index = next((i for i, slot in enumerate(slots) if slot is None), None)
            if empty_slot_index is not None:
                slots[empty_slot_index] = clicked_item
                selected.append(clicked_item)
                board.remove(clicked_item)
                check_elimination()
        else:
            selected.clear()


def check_elimination():
    global board, score, victory, game_over

    # 检查是否有三个相同的图片
    for i in range(len(slots)):
        if slots[i] is not None:
            same_count = 1
            for j in range(i + 1, len(slots)):
                if slots[j] is not None and slots[j]['pattern'] == slots[i]['pattern']:
                    same_count += 1
                    if same_count == 3:
                        for k in range(i, j + 1):
                            slots[k] = None
                        score += 30
                        board = [item for item in board if item not in slots]
                        # 重新排列格子中的图片
                        rearrange_slots()
                        break

    # 检查是否胜利
    if not board and not any(slot is not None for slot in slots):
        victory = True
        game_over = True
        return

    # 检查是否失败
    if all(slot is not None for slot in slots):
        game_over = True

def rearrange_slots():
    global slots

    # 重新排列格子中的图片
    new_slots = [slot for slot in slots if slot is not None]
    new_slots.extend([None] * (7 - len(new_slots)))
    slots = new_slots

def show_start_screen():
    global current_difficulty
    screen.fill(BG_COLOR)
    try:
        start_screen_image = pygame.image.load("background.jpeg")
        start_screen_image = pygame.transform.scale(start_screen_image, (WIDTH, HEIGHT))
        screen.blit(start_screen_image, (0, 0))
    except pygame.error as e:
        print(f"无法加载开始界面背景图片：{e}")

    easy_text = FONT.render("简单", True, WHITE)
    hard_text = FONT.render("困难", True, WHITE)
    veryhard_text = FONT.render("地狱", True, WHITE)
    start_text = FONT.render("点击开始游戏", True, WHITE)
    quit_text = FONT.render("退出游戏", True, WHITE)

    easy_rect = easy_text.get_rect(center=(WIDTH / 2, 100))
    hard_rect = hard_text.get_rect(center=(WIDTH / 2, 200))
    veryhard_rect = veryhard_text.get_rect(center=(WIDTH / 2, 300))
    start_rect = start_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 100))
    quit_rect = quit_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 200))

    screen.blit(easy_text, easy_rect)
    screen.blit(hard_text, hard_rect)
    screen.blit(veryhard_text, veryhard_rect)
    screen.blit(start_text, start_rect)
    screen.blit(quit_text, quit_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    current_difficulty = '简单'
                    return
                elif hard_rect.collidepoint(event.pos):
                    current_difficulty = '困难'
                    return
                elif veryhard_rect.collidepoint(event.pos):
                    current_difficulty = '地狱'
                    return
                elif start_rect.collidepoint(event.pos):
                    return
                elif quit_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def show_end_screen():
    global victory, score

    # 加载背景图
    victory_image = pygame.image.load("win.jpeg")
    failure_image = pygame.image.load("fail.jpeg")

    # 将背景图缩放到窗口大小
    victory_image = pygame.transform.scale(victory_image, (WIDTH, HEIGHT))
    failure_image = pygame.transform.scale(failure_image, (WIDTH, HEIGHT))

    screen.fill(BG_COLOR)
    
    if victory:
        screen.blit(victory_image, (0, 0))
        end_text = "恭喜你，获胜！"
    else:
        screen.blit(failure_image, (0, 0))
        end_text = "游戏结束，失败了！"
    
    end_text_render = FONT.render(end_text, True, WHITE)
    score_text = FONT.render(f"得分: {score}", True, WHITE)
    end_text_rect = end_text_render.get_rect(center=(WIDTH / 2, HEIGHT / 2 - 50))
    score_text_rect = score_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 50))

    # 绘制“返回主菜单”按钮
    button_font = pygame.font.Font(FONT_PATH, 24)
    button_text = button_font.render("返回主菜单", True, WHITE)
    button_rect = button_text.get_rect(center=(WIDTH / 2, HEIGHT / 2 + 150))
    pygame.draw.rect(screen, BLACK, button_rect.inflate(20, 10))  # 绘制按钮背景
    screen.blit(button_text, button_rect)

    screen.blit(end_text_render, end_text_rect)
    screen.blit(score_text, score_text_rect)

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return  # 返回主菜单

def main():
    global start_ticks, game_over, victory

    while True:
        show_start_screen()
        initialize_game(current_difficulty)
        start_ticks = pygame.time.get_ticks()

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == MOUSEBUTTONDOWN:
                    x, y = event.pos
                    handle_click(x, y)

            if not game_over:
                draw_board()
                pygame.display.flip()
                timer.tick(FPS)

            if not game_over and (pygame.time.get_ticks() - start_ticks >= GAME_TIME * 1000):
                game_over = True

            if game_over:
                show_end_screen()
                break


if __name__ == "__main__":
    main()
