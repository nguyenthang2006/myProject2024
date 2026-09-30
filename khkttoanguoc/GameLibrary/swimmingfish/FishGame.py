import pygame
import sys
import random
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db as firebase_db
import datetime

def draw_floor(screen, floor, floor_x_pos):
    screen.blit(floor, (floor_x_pos, 650))
    screen.blit(floor, (floor_x_pos + 432, 650))

def create_pipe(pipe_surface, pipe_height):
    random_pipe_pos = random.choice(pipe_height)
    bottom_pipe = pipe_surface.get_rect(midtop=(800, random_pipe_pos))
    top_pipe = pipe_surface.get_rect(midtop=(800, random_pipe_pos - 850))
    return bottom_pipe, top_pipe

def move_pipe(pipes):               
    for pipe in pipes:
        pipe.centerx -= 25
    return pipes

def draw_pipe(screen, pipe_surface, pipes):
    for pipe in pipes:
        if pipe.bottom >= 100:
            screen.blit(pipe_surface, pipe)
        else:
            flip_pipe = pygame.transform.flip(pipe_surface, False, True)
            screen.blit(flip_pipe, pipe)

def check_collision(fish_rect, pipes, hit_sound):
    for pipe in pipes:
        if fish_rect.colliderect(pipe):
            hit_sound.play()
            return False
    if fish_rect.top <= -10 or fish_rect.bottom >= 600:
        return False
    return True

def rotate_fish(fish, fish_movement, fish_list, fish_index):
    new_fish = pygame.transform.rotozoom(fish_list[fish_index], - fish_movement * 2, 1)
    return new_fish

def fish_animation(fish_list, fish_index, fish_rect):
    new_fish = fish_list[fish_index]
    new_fish_rect = new_fish.get_rect(center=(100, fish_rect.centery))
    return new_fish, new_fish_rect

def score_display(screen, game_font, score):
    score_surface = game_font.render(str(int(score)), True, (0, 0, 0))
    score_rect = score_surface.get_rect(center=(216, 100))
    screen.blit(score_surface, score_rect)

def update_score(score, high_score):
    if score > high_score:
        high_score = score
    return high_score 

def send_score_to_firebase(score, email):
    if not firebase_admin._apps:
        cred = credentials.Certificate("D:/Downloads/khkttoanguoc/khkttoanquoc-firebase-adminsdk-n1m40-4fc83d627b.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://khkttoanquoc-default-rtdb.asia-southeast1.firebasedatabase.app/'
        })

    db = firebase_db.reference()

    # Kiểm tra xem tài khoản người dùng đã tồn tại trong cơ sở dữ liệu chưa
    user_data = db.child("users").order_by_child("email").equal_to(email).get()
    if user_data:
        for user_id, data in user_data.items():
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            # Tạo đường dẫn cho thư mục của tài khoản người dùng
            user_path = f"users/{user_id}/swimming_fish"  # Đổi tên thư mục nếu cần thiết
            # Gửi điểm số vào thư mục của tài khoản người dùng
            db.child(user_path).push({
                "score": score,
                "timestamp": current_time
            })



def run_fish_game(email):
    # Khởi tạo pygame và cấu hình cửa sổ
    pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    pygame.init()
    logo_path = "D:/Downloads/khktqg/GuiImage/logo.ico"
    logo_image = pygame.image.load(logo_path)
    pygame.display.set_icon(logo_image)
    screen = pygame.display.set_mode((768, 768))
    pygame.display.set_caption('fish game')
    clock = pygame.time.Clock()
    game_font = pygame.font.Font('GameLibrary/swimmingfish/FishGameSrc/04B_19.TTF', 35)

    # Tạo các biến cho trò chơi
    gravity = 0.85
    fish_movement = 0
    game_active = True
    score = 0
    high_score = 0

    # Load hình ảnh và âm thanh
    bg = pygame.image.load('GameLibrary/swimmingfish/FishGameSrc/image/seabackground.png').convert()
    bg = pygame.transform.scale2x(bg)
    floor = pygame.image.load('GameLibrary/swimmingfish/FishGameSrc/image/seadown.png').convert()
    floor = pygame.transform.scale2x(floor)
    floor_x_pos = 0

    fish_down = pygame.transform.scale2x(pygame.image.load('GameLibrary/swimmingfish/FishGameSrc/image/fishdown.png').convert_alpha())
    fish_mid = pygame.transform.scale2x(pygame.image.load('GameLibrary/swimmingfish/FishGameSrc/image/fishmid.png').convert_alpha())
    fish_up = pygame.transform.scale2x(pygame.image.load('GameLibrary/swimmingfish/FishGameSrc/image/fishup.png').convert_alpha())
    fish_list = [fish_down, fish_mid, fish_up]
    fish_index = 0
    fish = fish_list[fish_index]
    fish_rect = fish.get_rect(center=(100, 384))

    fishflap = pygame.USEREVENT + 1
    pygame.time.set_timer(fishflap, 200)

    pipe_surface = pygame.image.load('GameLibrary/swimmingfish/FishGameSrc/image/seacolum.jpg').convert()
    pipe_surface = pygame.transform.scale2x(pipe_surface)
    pipe_list = []
    spawnpipe = pygame.USEREVENT
    pygame.time.set_timer(spawnpipe, 1200)
    pipe_height = [675, 625, 650]

    game_over_surface = pygame.transform.scale2x(pygame.image.load('GameLibrary/swimmingfish/FishGameSrc/image/messsage.png').convert_alpha())
    game_over_rect = game_over_surface.get_rect(center=(432, 384))

    flap_sound = pygame.mixer.Sound('GameLibrary/swimmingfish/FishGameSrc/sound/sfx_wing.wav')
    hit_sound = pygame.mixer.Sound('GameLibrary/swimmingfish/FishGameSrc/sound/sfx_hit.wav')
    score_sound = pygame.mixer.Sound('GameLibrary/swimmingfish/FishGameSrc/sound/sfx_point.wav')

    # Vòng lặp chính của trò chơi
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_SPACE or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    if game_active:
                        fish_movement = 0
                        fish_movement = -11
                        flap_sound.play()
                    elif not game_active and event.key == pygame.K_SPACE or event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        game_active = True
                        pipe_list.clear()
                        fish_rect.center = (100, 384)
                        fish_movement = 0
                        score = 0
            if event.type == spawnpipe:
                pipe_list.extend(create_pipe(pipe_surface, pipe_height))
            if event.type == fishflap:
                if fish_index < 2:
                    fish_index += 1
                else:
                    fish_index = 0

        screen.blit(bg, (0, 0))

        if game_active:
            fish_movement += gravity
            rotated_fish = rotate_fish(fish, fish_movement, fish_list, fish_index)
            fish_rect.centery += fish_movement
            screen.blit(rotated_fish, fish_rect)
            game_active = check_collision(fish_rect, pipe_list, hit_sound)
            pipe_list = move_pipe(pipe_list)
            draw_pipe(screen, pipe_surface, pipe_list)
            for pipe in pipe_list:
                if pipe.centerx == 100:
                    score += 0.5
                    score_sound.play()
            score_display(screen, game_font, score)
        else:
            screen.blit(game_over_surface, game_over_rect)
            high_score = update_score(score, high_score)
            score_display(screen, game_font, score)

        floor_x_pos -= 1
        draw_floor(screen, floor, floor_x_pos)

        if floor_x_pos <= -432:
            floor_x_pos = 0

        if not game_active:
            send_score_to_firebase(score, email)  # Truyền email vào hàm send_score_to_firebase

        pygame.display.update()
        clock.tick(10)


'''if __name__ == "__main__":
    run_fish_game()'''
