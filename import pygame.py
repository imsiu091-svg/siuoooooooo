import pygame
import sys
import math
import random

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 640, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Super Mario Bros.")
clock = pygame.time.Clock()

# ── Colors ──────────────────────────────────────────────
SKY        = (92, 148, 252)
WHITE      = (255, 255, 255)
BLACK      = (0, 0, 0)
YELLOW     = (247, 208, 56)
D_YELLOW   = (192, 144,  0)
RED        = (229,  42,  42)
BLUE       = ( 26,  99, 212)
SKIN       = (200, 129,  74)
BROWN      = ( 92,  51,  23)
D_BROWN    = (139,  64,   0)
GREEN      = ( 76, 172,  32)
D_GREEN    = ( 40,  96,  16)
GROUND_C   = (224, 160,  96)
GROUND_D   = (192, 112,  48)
PIPE_G     = ( 58, 144,  24)
GOOMBA_C   = (192, 112,  48)
GRAY       = (128, 128, 128)
D_GRAY     = ( 80,  80,  80)
ORANGE     = (210, 105,  30)
SHELL_GRN  = ( 50, 180,  60)
D_SHELL    = ( 20, 100,  30)

# ── Fonts ───────────────────────────────────────────────
try:
    FL = pygame.font.Font(None, 60)
    FM = pygame.font.Font(None, 36)
    FS = pygame.font.Font(None, 22)
    FT = pygame.font.Font(None, 16)
except:
    FL = pygame.font.SysFont("monospace", 40, bold=True)
    FM = pygame.font.SysFont("monospace", 28, bold=True)
    FS = pygame.font.SysFont("monospace", 18, bold=True)
    FT = pygame.font.SysFont("monospace", 12)

def txt(surf, text, font, color, x, y, shadow=BLACK, off=3):
    surf.blit(font.render(text, False, shadow), (x+off, y+off))
    surf.blit(font.render(text, False, color),  (x, y))

# ══════════════════════════════════════════════════════════
#  DRAW HELPERS
# ══════════════════════════════════════════════════════════
def draw_cloud(surf, x, y):
    for r in [(x+10,y+10,60,20),(x,y+20,80,25),(x+15,y,50,25)]:
        pygame.draw.rect(surf, WHITE, r, border_radius=6)

def draw_pipe(surf, x, y, h):
    pygame.draw.rect(surf, PIPE_G,   (x+4, y, 32, h))
    pygame.draw.rect(surf, D_GREEN,  (x+28, y, 8, h))
    pygame.draw.rect(surf, GREEN,    (x, y-10, 40, 14), border_radius=3)
    pygame.draw.rect(surf, D_GREEN,  (x+32, y-10, 8, 14), border_radius=3)
    pygame.draw.rect(surf, WHITE,    (x, y-10, 40, 14), 2, border_radius=3)
    pygame.draw.rect(surf, WHITE,    (x+4, y, 32, h), 2)

def draw_q_block(surf, x, y, used=False):
    c = GRAY if used else YELLOW
    dc = D_GRAY if used else D_YELLOW
    pygame.draw.rect(surf, c,     (x, y, 32, 32))
    pygame.draw.rect(surf, WHITE, (x, y, 32, 32), 3)
    pygame.draw.rect(surf, dc,    (x+3, y+3, 26, 26))
    if not used:
        q = FM.render("?", False, dc)
        surf.blit(q, (x+8, y+6))

def draw_brick(surf, x, y):
    pygame.draw.rect(surf, D_BROWN,  (x, y, 32, 32))
    pygame.draw.rect(surf, WHITE,    (x, y, 32, 32), 2)
    pygame.draw.rect(surf, GROUND_D, (x+2, y+2, 28, 28))
    pygame.draw.line(surf, D_BROWN, (x+2,y+16),(x+30,y+16), 2)
    pygame.draw.line(surf, D_BROWN, (x+16,y+2),(x+16,y+15), 2)
    pygame.draw.line(surf, D_BROWN, (x+8, y+17),(x+8, y+30), 2)

def draw_ground_tiles(surf, cam_x):
    GROUND_Y = HEIGHT - 60
    pygame.draw.rect(surf, (107,194,55), (0, GROUND_Y-12, WIDTH, 12))
    pygame.draw.rect(surf, GROUND_C,    (0, GROUND_Y, WIDTH, 60))
    pygame.draw.rect(surf, GROUND_D,    (0, GROUND_Y, WIDTH, 5))
    tile = 32
    off = int(cam_x) % tile
    for tx in range(-off, WIDTH+tile, tile):
        pygame.draw.rect(surf, GROUND_D, (tx, GROUND_Y, tile, 60), 1)

def draw_mario(surf, x, y, facing_right=True, frame=0, dead=False):
    if dead:
        # flat squashed
        pygame.draw.rect(surf, RED,   (x+4, y+16, 24, 8))
        pygame.draw.rect(surf, BLUE,  (x+2, y+24, 28, 8))
        pygame.draw.rect(surf, SKIN,  (x+4,  y+8, 24, 8))
        pygame.draw.rect(surf, RED,   (x+8,  y+0, 16, 8))
        return
    walk_bob = (frame // 6) % 2 if not dead else 0
    mx = x if facing_right else x+32
    flip = 1 if facing_right else -1
    def px(dx,dy,w,h,color):
        rx = mx+dx*flip if facing_right else mx-dx*flip-w
        pygame.draw.rect(surf, color, (rx, y+dy, w, h))
    # hat
    px(8,0,16,4,RED); px(4,4,24,4,RED)
    # face
    px(4,8,20,4,SKIN); px(4,8,8,2,BROWN); px(16,8,4,2,BROWN)
    px(0,12,28,8,SKIN); px(4,12,4,4,WHITE); px(6,14,2,2,BLACK)
    px(12,16,12,4,BROWN)
    # body
    px(4,20,24,8,RED)
    px(4,20,4,8,BLUE); px(24,20,4,8,BLUE); px(8,24,16,4,BLUE)
    # legs (walk anim)
    if walk_bob == 0:
        px(4,28,10,8,BLUE); px(16,28,10,8,BLUE)
        px(2,36,12,4,BROWN); px(16,36,12,4,BROWN)
    else:
        px(4,28,8,10,BLUE); px(18,28,10,8,BLUE)
        px(1,36,10,4,BROWN); px(17,36,12,4,BROWN)
    px(0,20,4,6,SKIN); px(28,20,4,4,SKIN)

def draw_goomba(surf, x, y, frame=0):
    bob = (frame//8)%2
    fy = y + bob
    pygame.draw.rect(surf, D_BROWN,  (x+4,  fy,    24, 20))
    pygame.draw.rect(surf, GOOMBA_C, (x,    fy+8,  36, 16))
    pygame.draw.rect(surf, WHITE,    (x+5,  fy+8,   8,  8))
    pygame.draw.rect(surf, WHITE,    (x+23, fy+8,   8,  8))
    pygame.draw.rect(surf, BLACK,    (x+7,  fy+10,  4,  4))
    pygame.draw.rect(surf, BLACK,    (x+25, fy+10,  4,  4))
    pygame.draw.rect(surf, D_BROWN,  (x+2,  fy+22, 12, 10))
    pygame.draw.rect(surf, D_BROWN,  (x+22, fy+22, 12, 10))
    pygame.draw.rect(surf, BROWN,    (x+8,  fy+20,  6,  4))
    pygame.draw.rect(surf, GOOMBA_C, (x+14, fy+20, 8,   4))
    pygame.draw.rect(surf, BROWN,    (x+22, fy+20,  6,  4))

def draw_shell(surf, x, y, frame=0):
    # Koopa shell (sideways)
    pygame.draw.ellipse(surf, SHELL_GRN, (x, y+4, 36, 24))
    pygame.draw.ellipse(surf, D_SHELL,   (x+4, y+8, 28, 16))
    pygame.draw.ellipse(surf, WHITE,     (x, y+4, 36, 24), 2)
    # pattern lines
    pygame.draw.line(surf, D_SHELL, (x+18, y+6), (x+18, y+26), 2)
    pygame.draw.line(surf, D_SHELL, (x+4,  y+16), (x+32, y+16), 2)

def draw_coin_anim(surf, x, y, frame):
    scale = abs(math.cos(frame * 0.15))
    w = max(2, int(20*scale))
    cx = x + (20-w)//2
    pygame.draw.rect(surf, YELLOW,   (cx, y, w, 20))
    if w > 6:
        pygame.draw.rect(surf, D_YELLOW, (cx+w//2-2, y+2, 4, 16))

# ══════════════════════════════════════════════════════════
#  LEVEL DATA  (world coordinates, cam scrolls)
# ══════════════════════════════════════════════════════════
GROUND_Y = HEIGHT - 60   # top of ground in screen coords
TILE     = 32

LEVEL_W  = 3200   # total level pixel width

# Platforms: (world_x, world_y, tile_count)
PLATFORMS = [
    (200, GROUND_Y-96,  3),
    (380, GROUND_Y-128, 4),
    (580, GROUND_Y-96,  3),
    (750, GROUND_Y-160, 5),
    (950, GROUND_Y-96,  3),
    (1100,GROUND_Y-128, 4),
    (1300,GROUND_Y-96,  2),
    (1500,GROUND_Y-160, 5),
    (1700,GROUND_Y-96,  3),
    (1900,GROUND_Y-128, 4),
    (2100,GROUND_Y-96,  3),
    (2300,GROUND_Y-160, 5),
    (2500,GROUND_Y-96,  3),
    (2700,GROUND_Y-128, 4),
]

# Q blocks: (world_x, world_y, type)  type: 'coin','mushroom'
Q_BLOCKS = [
    (220, GROUND_Y-160, 'coin'),
    (410, GROUND_Y-192, 'coin'),
    (600, GROUND_Y-160, 'coin'),
    (770, GROUND_Y-224, 'coin'),
    (960, GROUND_Y-160, 'coin'),
    (1120,GROUND_Y-192, 'coin'),
    (1520,GROUND_Y-224, 'coin'),
    (1720,GROUND_Y-160, 'coin'),
    (1920,GROUND_Y-192, 'coin'),
    (2320,GROUND_Y-224, 'coin'),
    (2520,GROUND_Y-160, 'coin'),
    (2720,GROUND_Y-192, 'coin'),
]

BRICK_ROWS = [
    (260, GROUND_Y-160, 3),
    (450, GROUND_Y-128, 2),
    (640, GROUND_Y-160, 2),
    (820, GROUND_Y-160, 3),
    (1160,GROUND_Y-128, 3),
    (1560,GROUND_Y-160, 2),
    (1760,GROUND_Y-160, 2),
    (1960,GROUND_Y-128, 3),
    (2360,GROUND_Y-160, 2),
    (2560,GROUND_Y-160, 3),
    (2760,GROUND_Y-192, 3),
]

PIPES = [
    (300,  GROUND_Y-80,  80),
    (680,  GROUND_Y-96,  96),
    (1050, GROUND_Y-80,  80),
    (1400, GROUND_Y-112, 112),
    (1800, GROUND_Y-80,  80),
    (2200, GROUND_Y-96,  96),
    (2600, GROUND_Y-80,  80),
    (2950, GROUND_Y-112, 112),
]

# Goombas: (world_x, patrol_range)
GOOMBA_DATA = [
    (400,  80), (700,  80), (950,  100), (1200, 80),
    (1500, 100),(1750, 80), (2000, 100), (2250, 80),
    (2500, 100),(2750, 80), (2950, 80),
]

# Koopas (엉금엉금): (world_x, patrol_range)
KOOPA_DATA = [
    (550,  100), (900,  100), (1350, 100),
    (1650, 100), (2100, 100), (2400, 100),
    (2800, 100),
]

# ── Entity classes ────────────────────────────────────────
class Mario:
    W, H = 32, 40
    SPEED   = 3.5
    JUMP_V  = -13
    GRAVITY = 0.55

    def __init__(self):
        self.x    = 80.0
        self.y    = float(GROUND_Y - self.H)
        self.vx   = 0.0
        self.vy   = 0.0
        self.on_ground = False
        self.facing_right = True
        self.alive  = True
        self.dead_timer = 0
        self.invincible = 0  # frames of invincibility after hit

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, keys, platforms, q_blocks, bricks, pipes):
        if not self.alive:
            self.dead_timer += 1
            if self.dead_timer == 30:
                self.vy = -12
            self.vy += self.GRAVITY
            self.y  += self.vy
            return

        if self.invincible > 0:
            self.invincible -= 1

        # Horizontal
        self.vx = 0
        if keys[pygame.K_RIGHT]:
            self.vx =  self.SPEED; self.facing_right = True
        if keys[pygame.K_LEFT]:
            self.vx = -self.SPEED; self.facing_right = False
        self.x += self.vx
        self.x  = max(0, min(self.x, LEVEL_W - self.W))

        # Vertical
        self.vy += self.GRAVITY
        self.y  += self.vy
        self.on_ground = False

        # Ground
        if self.y + self.H >= GROUND_Y:
            self.y = GROUND_Y - self.H
            self.vy = 0
            self.on_ground = True

        # Platforms
        for (px, py, cnt) in platforms:
            pr = pygame.Rect(px, py, cnt*TILE, TILE)
            mr = self.rect
            if mr.colliderect(pr):
                if self.vy > 0 and mr.bottom - self.vy <= pr.top + 4:
                    self.y = pr.top - self.H
                    self.vy = 0
                    self.on_ground = True

        # Q blocks (hit from below)
        for qb in q_blocks:
            if qb['used']: continue
            qr = pygame.Rect(qb['x'], qb['y'], TILE, TILE)
            mr = self.rect
            if mr.colliderect(qr):
                if self.vy < 0 and mr.top >= qr.bottom - 4:
                    self.vy = 2
                    qb['used'] = True
                    qb['anim']  = 10
                    return

        # Bricks (head-bump)
        for br in bricks:
            brr = pygame.Rect(br['x'], br['y'], TILE, TILE)
            mr  = self.rect
            if mr.colliderect(brr):
                if self.vy < 0 and mr.top >= brr.bottom - 4:
                    self.vy = 2

        # Pipe collision (side + top)
        for (ppx, ppy, pph) in pipes:
            pr = pygame.Rect(ppx, ppy-10, 40, pph+10)
            mr = self.rect
            if mr.colliderect(pr):
                if self.vy > 0 and mr.bottom - self.vy <= pr.top + 6:
                    self.y = pr.top - self.H
                    self.vy = 0
                    self.on_ground = True
                elif self.vx > 0 and mr.right - self.vx <= pr.left + 4:
                    self.x = pr.left - self.W
                elif self.vx < 0 and mr.left - self.vx >= pr.right - 4:
                    self.x = pr.right

        if keys[pygame.K_UP] and self.on_ground:
            self.vy = self.JUMP_V

    def die(self):
        if not self.alive: return
        self.alive = False
        self.vy = -8

class Goomba:
    W, H = 36, 32
    SPEED = 1.2

    def __init__(self, x, patrol):
        self.x     = float(x)
        self.y     = float(GROUND_Y - self.H)
        self.patrol= patrol
        self.start = float(x)
        self.dir   = -1
        self.alive = True
        self.squish_timer = 0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.W, self.H)

    def update(self, platforms, pipes):
        if not self.alive:
            self.squish_timer += 1
            return
        self.x += self.SPEED * self.dir
        if self.x < self.start - self.patrol: self.dir =  1
        if self.x > self.start + self.patrol: self.dir = -1

        # Ground
        self.y = GROUND_Y - self.H
        # Platform
        for (px,py,cnt) in platforms:
            pr = pygame.Rect(px,py,cnt*TILE,TILE)
            mr = self.rect
            if mr.colliderect(pr) and mr.bottom <= pr.top + self.SPEED + 2:
                self.y = pr.top - self.H
        # Pipe wall
        for (ppx,ppy,pph) in pipes:
            pr = pygame.Rect(ppx, ppy-10, 40, pph+10)
            mr = self.rect
            if mr.colliderect(pr):
                self.dir *= -1

    def squish(self):
        self.alive = False
        self.squish_timer = 0

class Koopa:
    W, H = 36, 40
    SPEED      = 1.0
    SHELL_SPEED= 6.0

    def __init__(self, x, patrol):
        self.x     = float(x)
        self.y     = float(GROUND_Y - self.H)
        self.patrol= patrol
        self.start = float(x)
        self.dir   = -1
        self.alive = True
        self.shell_mode  = False
        self.shell_moving= False
        self.shell_dir   = 1
        self.shell_timer = 0   # 0 = just stomped (still), >200 revive
        self.dead        = False
        self.vy          = 0

    @property
    def rect(self):
        h = 28 if self.shell_mode else self.H
        return pygame.Rect(int(self.x), int(self.y + (self.H-h)), self.W, h)

    def update(self, platforms, pipes):
        if self.dead: return
        spd = self.SHELL_SPEED if (self.shell_mode and self.shell_moving) else \
              (self.SPEED if not self.shell_mode else 0)

        self.x += spd * self.dir
        # Ground
        self.y = GROUND_Y - self.H
        for (px,py,cnt) in platforms:
            pr = pygame.Rect(px,py,cnt*TILE,TILE)
            mr = self.rect
            if mr.colliderect(pr) and mr.bottom <= pr.top + spd + 2:
                self.y = pr.top - (self.H - (0 if not self.shell_mode else 12))
        for (ppx,ppy,pph) in pipes:
            pr = pygame.Rect(ppx, ppy-10, 40, pph+10)
            mr = self.rect
            if mr.colliderect(pr):
                self.dir *= -1

        if not self.shell_mode:
            if self.x < self.start - self.patrol: self.dir =  1
            if self.x > self.start + self.patrol: self.dir = -1

    def stomp(self):
        if self.shell_mode:
            self.shell_moving = not self.shell_moving
            if self.shell_moving:
                self.shell_dir = self.dir
        else:
            self.shell_mode   = True
            self.shell_moving = False

    def kick(self, kick_dir):
        self.shell_moving = True
        self.dir = kick_dir

# ══════════════════════════════════════════════════════════
#  GAME STATE
# ══════════════════════════════════════════════════════════
STATE_INTRO = 0
STATE_GAME  = 1
STATE_DEAD  = 2
STATE_WIN   = 3

state      = STATE_INTRO
score      = 0
coins      = 0
lives      = 3
game_frame = 0
sel_opt    = 0
blink_on   = True
blink_t    = 0
intro_frame= 0
intro_mario_x  = 80
intro_mario_dir= 1
intro_goomba_x = 500

coin_anims = []   # [{x,y,frame}]

def init_game():
    global mario, goombas, koopas, q_blocks, bricks_list, game_frame, score, coins, cam_x
    mario = Mario()
    cam_x = 0.0

    q_blocks = [{'x':qx,'y':qy,'type':qt,'used':False,'anim':0} for (qx,qy,qt) in Q_BLOCKS]
    bricks_list = [{'x':bx+i*TILE,'y':by} for (bx,by,cnt) in BRICK_ROWS for i in range(cnt)]
    goombas = [Goomba(gx, pr) for (gx,pr) in GOOMBA_DATA]
    koopas  = [Koopa(kx, pr)  for (kx,pr) in KOOPA_DATA]
    game_frame = 0

# ══════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════
running = True
while running:
    dt = clock.tick(60)
    game_frame += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # ── Intro ──
            if state == STATE_INTRO:
                if event.key == pygame.K_UP:   sel_opt = 0
                if event.key == pygame.K_DOWN: sel_opt = 1
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    init_game()
                    state = STATE_GAME

            # ── Dead / Win ──
            elif state in (STATE_DEAD, STATE_WIN):
                if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    state = STATE_INTRO

    keys = pygame.key.get_pressed()

    # ══════════════════════════════════════════════════════
    #  INTRO SCENE
    # ══════════════════════════════════════════════════════
    if state == STATE_INTRO:
        intro_frame += 1
        if intro_frame % 2 == 0:
            intro_mario_x += intro_mario_dir * 2
            if intro_mario_x > WIDTH-120: intro_mario_dir = -1
            if intro_mario_x < 60:        intro_mario_dir =  1
        intro_goomba_x -= 1
        if intro_goomba_x < -50: intro_goomba_x = WIDTH + 50

        blink_t += 1
        if blink_t >= 30: blink_on = not blink_on; blink_t = 0

        screen.fill(SKY)
        draw_cloud(screen, 50, 30)
        draw_cloud(screen, 430, 20)

        # Title
        title = "SUPER MARIO BROS."
        tw = FL.size(title)[0]
        txt(screen, title, FL, YELLOW, (WIDTH-tw)//2, 60)

        if blink_on:
            ps = "< PRESS ENTER >"
            pw = FS.size(ps)[0]
            txt(screen, ps, FS, WHITE, (WIDTH-pw)//2, 150)

        for i, opt in enumerate(["1 PLAYER GAME", "2 PLAYER GAME"]):
            prefix = "* " if i == sel_opt else "  "
            color  = YELLOW if i == sel_opt else WHITE
            line   = prefix + opt
            lw     = FS.size(line)[0]
            txt(screen, line, FS, color, (WIDTH-lw)//2, 190+i*30)

        ts = "TOP -  000000"
        txt(screen, ts, FT, YELLOW, (WIDTH-FT.size(ts)[0])//2, 260, off=2)

        draw_q_block(screen, 240, 220)
        draw_q_block(screen, 280, 210)
        draw_brick(screen,   320, 220)
        draw_coin_anim(screen, 258, 195, intro_frame)

        draw_pipe(screen, 20,  GROUND_Y-80,  80)
        draw_pipe(screen, 580, GROUND_Y-100, 100)

        draw_ground_tiles(screen, 0)
        draw_goomba(screen, int(intro_goomba_x), GROUND_Y-32, intro_frame)
        draw_mario(screen, intro_mario_x, GROUND_Y-40,
                   intro_mario_dir > 0, intro_frame)

        txt(screen, "(C)1985 NINTENDO", FT, WHITE,
            (WIDTH-FT.size("(C)1985 NINTENDO")[0])//2, GROUND_Y-24, off=1)

        pygame.display.flip()
        continue

    # ══════════════════════════════════════════════════════
    #  GAME LOGIC
    # ══════════════════════════════════════════════════════
    if state == STATE_GAME:
        mario.update(keys, PLATFORMS, q_blocks, bricks_list, PIPES)

        # Camera follows mario (center)
        cam_x = mario.x - WIDTH//2 + mario.W//2
        cam_x = max(0, min(cam_x, LEVEL_W - WIDTH))

        # ── Enemies ──
        for g in goombas:
            g.update(PLATFORMS, PIPES)
        for k in koopas:
            k.update(PLATFORMS, PIPES)

        # ── Coin anims ──
        for ca in coin_anims[:]:
            ca['frame'] += 1
            if ca['frame'] > 30: coin_anims.remove(ca)

        # ── Mario vs Goomba ──
        if mario.alive and mario.invincible == 0:
            for g in goombas:
                if not g.alive: continue
                mr = mario.rect; gr = g.rect
                if mr.colliderect(gr):
                    # stomp: mario falling + feet near goomba top
                    if mario.vy > 0 and mr.bottom - mario.vy <= gr.top + 8:
                        g.squish()
                        mario.vy = -7
                        score += 100
                    else:
                        mario.die()
                        lives -= 1

        # ── Mario vs Koopa ──
        if mario.alive and mario.invincible == 0:
            for k in koopas:
                if k.dead: continue
                mr = mario.rect; kr = k.rect
                if mr.colliderect(kr):
                    if k.shell_mode:
                        # kick shell
                        kick_dir = 1 if mario.x < k.x else -1
                        k.kick(kick_dir)
                        mario.vy = -7
                        score += 200
                    else:
                        if mario.vy > 0 and mr.bottom - mario.vy <= kr.top + 8:
                            k.stomp()
                            mario.vy = -7
                            score += 200
                        else:
                            mario.die()
                            lives -= 1

        # ── Shell vs Goomba ──
        for k in koopas:
            if k.shell_mode and k.shell_moving:
                for g in goombas:
                    if not g.alive: continue
                    if k.rect.colliderect(g.rect):
                        g.squish(); score += 200
                for k2 in koopas:
                    if k2 is k or k2.dead or not k2.shell_mode: continue
                    if k.rect.colliderect(k2.rect):
                        k2.dead = True; score += 200

        # ── Fall off screen → die ──
        if mario.alive and mario.y > HEIGHT + 100:
            mario.die(); lives -= 1

        # ── Dead transition ──
        if not mario.alive and mario.dead_timer > 90:
            if lives <= 0:
                state = STATE_DEAD
            else:
                init_game()

        # ── Win (reach end of level) ──
        if mario.x > LEVEL_W - 100:
            state = STATE_WIN

    # ══════════════════════════════════════════════════════
    #  RENDER
    # ══════════════════════════════════════════════════════
    screen.fill(SKY)

    if state in (STATE_GAME, STATE_DEAD, STATE_WIN):
        cx = int(cam_x)

        # Clouds (parallax lite)
        draw_cloud(screen, 60  - cx//4, 30)
        draw_cloud(screen, 350 - cx//4, 20)
        draw_cloud(screen, 700 - cx//4, 35)
        draw_cloud(screen, 1100- cx//4, 25)

        draw_ground_tiles(screen, cam_x)

        # Pipes
        for (ppx, ppy, pph) in PIPES:
            draw_pipe(screen, ppx-cx, ppy, pph)

        # Platforms (bricks style)
        for (px,py,cnt) in PLATFORMS:
            for i in range(cnt):
                draw_brick(screen, px-cx+i*TILE, py)

        # Q blocks
        for qb in q_blocks:
            by = qb['y']
            if qb['anim'] > 0:
                by -= qb['anim'] * 2
                qb['anim'] -= 1
            draw_q_block(screen, qb['x']-cx, by, qb['used'])

        # Bricks
        for br in bricks_list:
            draw_brick(screen, br['x']-cx, br['y'])

        # Coin anims
        for ca in coin_anims:
            draw_coin_anim(screen, ca['x']-cx, ca['y']-ca['frame']*3, ca['frame'])

        # Enemies
        for g in goombas:
            if g.squish_timer > 20: continue
            if not g.alive:
                # squished flat
                pygame.draw.rect(screen, GOOMBA_C, (int(g.x)-cx, GROUND_Y-8, g.W, 8))
            else:
                draw_goomba(screen, int(g.x)-cx, int(g.y), game_frame)

        for k in koopas:
            if k.dead: continue
            if k.shell_mode:
                draw_shell(screen, int(k.x)-cx, int(k.y)+12)
            else:
                # simple Koopa (green goomba tinted)
                sx = int(k.x)-cx; sy = int(k.y)
                pygame.draw.rect(screen, SHELL_GRN, (sx+4, sy, 28, 24))
                pygame.draw.rect(screen, D_SHELL,   (sx+8, sy-8, 20, 12), border_radius=4)
                pygame.draw.rect(screen, (224,200,100),(sx, sy+8, 36, 20))
                pygame.draw.rect(screen, WHITE, (sx+6, sy+10, 6, 6))
                pygame.draw.rect(screen, WHITE, (sx+24,sy+10, 6, 6))
                pygame.draw.rect(screen, BLACK, (sx+8, sy+12, 3, 3))
                pygame.draw.rect(screen, BLACK, (sx+26,sy+12, 3, 3))
                pygame.draw.rect(screen, D_SHELL, (sx+2, sy+26, 14, 10))
                pygame.draw.rect(screen, D_SHELL, (sx+20,sy+26, 14, 10))

        # Mario
        draw_mario(screen, int(mario.x)-cx, int(mario.y),
                   mario.facing_right, game_frame,
                   dead=not mario.alive)

        # HUD
        hud_bg = pygame.Surface((WIDTH, 36), pygame.SRCALPHA)
        hud_bg.fill((0,0,0,120))
        screen.blit(hud_bg, (0,0))
        txt(screen, f"MARIO", FT, WHITE, 10, 6, off=1)
        txt(screen, f"{score:06d}", FT, WHITE, 10, 18, off=1)
        txt(screen, f"x{coins:02d}", FT, WHITE, 160, 12, off=1)
        txt(screen, "WORLD", FT, WHITE, 280, 6, off=1)
        txt(screen, "1-1",   FT, WHITE, 290, 18, off=1)
        txt(screen, "TIME",  FT, WHITE, 430, 6, off=1)
        txt(screen, "LIVES", FT, WHITE, 560, 6, off=1)
        txt(screen, f"x{lives}", FT, WHITE, 572, 18, off=1)

        # Win overlay
        if state == STATE_WIN:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            screen.blit(ov, (0,0))
            wt = FM.render("COURSE CLEAR!", False, YELLOW)
            screen.blit(wt, ((WIDTH-wt.get_width())//2, 160))
            sub = FS.render("PRESS ENTER", False, WHITE)
            screen.blit(sub, ((WIDTH-sub.get_width())//2, 210))

        # Dead overlay
        if state == STATE_DEAD:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0,0,0,160))
            screen.blit(ov, (0,0))
            gt = FM.render("GAME OVER", False, RED)
            screen.blit(gt, ((WIDTH-gt.get_width())//2, 160))
            sub = FS.render("PRESS ENTER", False, WHITE)
            screen.blit(sub, ((WIDTH-sub.get_width())//2, 210))

    pygame.display.flip()

pygame.quit()
sys.exit()