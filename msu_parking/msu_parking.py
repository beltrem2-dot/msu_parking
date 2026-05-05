"""
=============================================================
  PRECISION PARKING — MSU CS Project  (HARD MODE v2)
=============================================================
  Authors : Ezekiel Deravil, Ryan Dominguez, & Mia Beltre
  Course  : CSIT 114
  Date    : 2026

  HOW TO INSTALL PYGAME:
      pip install pygame

  HOW TO RUN:
      python msu_parking.py

  CONTROLS:
      UP    — Accelerate forward
      DOWN  — Reverse
      LEFT  — Steer left
      RIGHT — Steer right
      R     — Restart / retry level
      SPACE — Confirm on menu screens

  OBJECTIVE:
      Park your car FULLY inside the green zone, aligned
      with the direction arrow, on each of 5 brutal levels.
      Stay in bounds, dodge obstacles, beat the clock!

  WHAT'S HARDER IN v2:
      - Car is faster + slipperier (less friction per level)
      - Steering becomes less responsive at high speed (drift)
      - Parking zones are smaller and require tighter angles
      - Must be nearly stopped to start the hold timer
      - Hold time increased from 1.2s → 2.0s
      - ALL levels now have time limits (45s → 25s)
      - Level 3: must park SIDEWAYS (90° angle)
      - Level 5: must REVERSE-IN (180° angle) in 25s
      - Narrow corridor class creates tight squeeze passages
      - Movers have staggered offsets → impossible to predict
      - HUD shows speed, angle, and required angle live
      - Grade system at the end (S/A/B/C)
=============================================================
"""

import pygame
import sys
import math
import random

# ── Init ──────────────────────────────────────────────────
pygame.init()
pygame.mixer.init()

# ── Constants ────────────────────────────────────────────
SCREEN_W, SCREEN_H = 900, 650
FPS = 60

# Color palette
C_BG        = (20,  22,  32)
C_ROAD      = (44,  49,  60)
C_LINE      = (200, 190, 140)
C_PLAYER    = (220, 70,  50)
C_ZONE_IDLE = (60,  180, 80,  100)
C_ZONE_OK   = (100, 255, 120, 190)
C_ZONE_BAD  = (255, 80,  60,  130)
C_CONE      = (240, 120, 20)
C_BARRIER   = (160, 165, 185)
C_MOVER     = (70,  120, 210)
C_TEXT      = (225, 225, 225)
C_ACCENT    = (255, 200, 50)
C_WHITE     = (255, 255, 255)
C_RED       = (220, 55,  55)
C_GREEN     = (55,  205, 85)
C_ORANGE    = (255, 140, 30)

# ── Screen ───────────────────────────────────────────────
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Precision Parking — HARD MODE")
clock  = pygame.time.Clock()

# ── Fonts ────────────────────────────────────────────────
font_big   = pygame.font.SysFont("consolas", 54, bold=True)
font_med   = pygame.font.SysFont("consolas", 30, bold=True)
font_small = pygame.font.SysFont("consolas", 20)
font_tiny  = pygame.font.SysFont("consolas", 15)

# ── Sounds ───────────────────────────────────────────────
def make_beep(freq=440, duration=0.08, volume=0.25):
    sr = 44100
    n  = int(sr * duration)
    buf = bytearray(n * 2)
    for i in range(n):
        v = int(32767 * volume * math.sin(2 * math.pi * freq * i / sr))
        buf[2*i]   = v & 0xFF
        buf[2*i+1] = (v >> 8) & 0xFF
    s = pygame.mixer.Sound(buffer=buf)
    s.set_volume(volume)
    return s

try:
    SFX_CRASH = make_beep(100, 0.30, 0.40)
    SFX_WIN   = make_beep(660, 0.15, 0.30)
    SFX_TICK  = make_beep(300, 0.04, 0.15)
except Exception:
    class _S:
        def play(self): pass
    SFX_CRASH = SFX_WIN = SFX_TICK = _S()


# ═══════════════════════════════════════════════════════════
#  CLASS: PlayerCar
# ═══════════════════════════════════════════════════════════
class PlayerCar:
    """
    Arcade-physics car.
    v2 changes:
      - Higher base top speed (5.5 vs 4.5)
      - Lower friction (0.88 vs 0.92) — more slide
      - Steering becomes less responsive at high speed (drift)
      - Levels amplify all stats via car_sensitivity
    """
    WIDTH  = 28
    HEIGHT = 50

    def __init__(self, x, y, angle=0.0):
        self.x            = float(x)
        self.y            = float(y)
        self.angle        = float(angle)
        self.speed        = 0.0
        self.max_speed    = 5.5
        self.acceleration = 0.22
        self.friction     = 0.88
        self.steer_speed  = 3.2
        self.crashed      = False

    def reset(self, x, y, angle=0.0):
        self.x       = float(x)
        self.y       = float(y)
        self.angle   = float(angle)
        self.speed   = 0.0
        self.crashed = False

    def handle_input(self, keys):
        if keys[pygame.K_UP]:
            self.speed += self.acceleration
        elif keys[pygame.K_DOWN]:
            self.speed -= self.acceleration * 0.65

        self.speed = max(-self.max_speed * 0.55, min(self.max_speed, self.speed))

        # Speed-dependent steering: harder to turn at high speed
        if abs(self.speed) > 0.1:
            direction = 1 if self.speed > 0 else -1
            ratio     = abs(self.speed) / self.max_speed
            eff_steer = self.steer_speed * (1.0 - 0.35 * ratio)
            if keys[pygame.K_LEFT]:
                self.angle -= eff_steer * direction
            if keys[pygame.K_RIGHT]:
                self.angle += eff_steer * direction

    def update(self):
        rad         = math.radians(self.angle)
        self.x     += self.speed * math.sin(rad)
        self.y     -= self.speed * math.cos(rad)
        self.speed *= self.friction
        if abs(self.speed) < 0.04:
            self.speed = 0.0

    def get_rect(self):
      shrink = 10
        return pygame.Rect(int(self.x - self.WIDTH  // 2),
                           int(self.y - self.HEIGHT // 2),
                           self.WIDTH - shrink
                           self.HEIGHT - shrink)

    def draw(self, surf):
        """
        # TODO: Replace with Ezekiel's custom car sprite (load PNG, rotate, blit)
        """
        cs = pygame.Surface((self.WIDTH + 6, self.HEIGHT + 6), pygame.SRCALPHA)
        cx = (self.WIDTH  + 6) // 2
        cy = (self.HEIGHT + 6) // 2

        # Body
        pygame.draw.rect(cs, C_PLAYER,
                         (cx - self.WIDTH//2, cy - self.HEIGHT//2,
                          self.WIDTH, self.HEIGHT), border_radius=5)
        # Windshield
        pygame.draw.rect(cs, (140, 200, 230, 200),
                         (cx - self.WIDTH//2 + 4, cy - self.HEIGHT//2 + 4,
                          self.WIDTH - 8, 13), border_radius=3)
        # Rear window
        pygame.draw.rect(cs, (100, 160, 190, 180),
                         (cx - self.WIDTH//2 + 5, cy + self.HEIGHT//2 - 17,
                          self.WIDTH - 10, 9), border_radius=2)
        # Wheels
        for wx, wy in [(-self.WIDTH//2-2, -self.HEIGHT//2+4),
                       ( self.WIDTH//2-4, -self.HEIGHT//2+4),
                       (-self.WIDTH//2-2,  self.HEIGHT//2-13),
                       ( self.WIDTH//2-4,  self.HEIGHT//2-13)]:
            pygame.draw.rect(cs, (30, 30, 30), (cx+wx, cy+wy, 6, 9), border_radius=2)

        rotated = pygame.transform.rotate(cs, -self.angle)
        surf.blit(rotated, rotated.get_rect(center=(int(self.x), int(self.y))))


# ═══════════════════════════════════════════════════════════
#  CLASS: ParkingZone
# ═══════════════════════════════════════════════════════════
class ParkingZone:
    """
    v2 changes:
      - required_time = 2.0s (was 1.2s)
      - Car must be nearly stopped (speed < 0.8) to count
      - Timer decays 3x faster if still moving inside zone
      - Shows required-angle arrow on the zone
      - Zone turns red if car enters too fast
    """

    def __init__(self, x, y, w, h, required_angle=0, angle_tolerance=15):
        self.rect            = pygame.Rect(x, y, w, h)
        self.required_angle  = float(required_angle)
        self.angle_tolerance = float(angle_tolerance)
        self.park_timer      = 0.0
        self.required_time   = 2.0
        self.is_parked       = False
        self.moving_penalty  = False

    def check(self, car, dt):
        angle_ok = True
        inside   = self.rect.contains(car.get_rect())
        slow_ok  = abs(car.speed) < 0.8

        self.moving_penalty = inside and not slow_ok

        if inside and angle_ok and slow_ok and not car.crashed:
            self.park_timer += dt
            self.is_parked  = True
            return self.park_timer >= self.required_time
        else:
            decay = 3.0 if not slow_ok else 1.5
            self.park_timer = max(0.0, self.park_timer - dt * decay)
            self.is_parked  = False
        return False

    def _angle_aligned(self, angle):
        def smallest_diff(a, b):
            d = (a - b) % 360
            if d > 180:
                d -= 360
            return d

        diff_forward = smallest_diff(angle, self.required_angle)
        diff_reverse = smallest_diff(angle, self.required_angle + 180)
        return (abs(diff_forward) <= self.angle_tolerance or
                abs(diff_reverse) <= self.angle_tolerance)

    def draw(self, surf):
        """
        # TODO: Replace with Ezekiel's parking zone texture/sprite
        """
        color = (C_ZONE_BAD if self.moving_penalty else
                 C_ZONE_OK  if self.is_parked else C_ZONE_IDLE)
        zs = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        zs.fill(color)
        surf.blit(zs, self.rect.topleft)

        border = (C_GREEN  if self.is_parked else
                  C_ORANGE if self.moving_penalty else C_LINE)
        pygame.draw.rect(surf, border, self.rect, 3)

        # "P" label
        lbl = font_small.render("P", True, C_WHITE)
        surf.blit(lbl, lbl.get_rect(center=self.rect.center))

        # TODO: Replace with Ezekiel's parking marker graphic

        # Hold-progress bar
        if self.park_timer > 0:
            bw = int(self.rect.w * (self.park_timer / self.required_time))
            pygame.draw.rect(surf, C_GREEN,
                             pygame.Rect(self.rect.x, self.rect.bottom+4, bw, 6),
                             border_radius=3)


# ═══════════════════════════════════════════════════════════
#  CLASS: Obstacle  (static)
# ═══════════════════════════════════════════════════════════
class Obstacle:
    """
    Static obstacle: 'cone' or 'wall'.
    Walls now support custom width/height and have warning stripes.
    """

    def __init__(self, x, y, kind="cone", w=None, h=None):
        self.x    = x
        self.y    = y
        self.kind = kind
        if kind == "cone":
            self.rect = pygame.Rect(x-10, y-10, 20, 20)
        else:
            self.rect = pygame.Rect(x, y, w or 90, h or 18)

    def collides_with(self, car):
        return self.rect.colliderect(car.get_rect())

    def draw(self, surf):
        """
        # TODO: Replace cone with Ezekiel's cone/barrel sprite
        # TODO: Replace wall with Ezekiel's concrete barrier sprite
        """
        if self.kind == "cone":
            pts = [(self.x, self.y-12), (self.x-10, self.y+8), (self.x+10, self.y+8)]
            pygame.draw.polygon(surf, C_CONE, pts)
            pygame.draw.polygon(surf, C_WHITE, pts, 1)
            pygame.draw.rect(surf, C_WHITE, (self.x-8, self.y+3, 16, 4))
        else:
            pygame.draw.rect(surf, C_BARRIER, self.rect, border_radius=3)
            # Warning stripes
            sw = 14
            for sx in range(self.rect.x, self.rect.right, sw*2):
                sr = pygame.Rect(sx, self.rect.y, sw, self.rect.h).clip(self.rect)
                pygame.draw.rect(surf, C_ORANGE, sr)
            pygame.draw.rect(surf, (70, 72, 88), self.rect, 2, border_radius=3)


# ═══════════════════════════════════════════════════════════
#  CLASS: MovingObstacle
# ═══════════════════════════════════════════════════════════
class MovingObstacle:
    """
    Moves back and forth.
    v2: start_offset staggers movers so they're never in sync.
    """

    def __init__(self, x, y, w, h, axis="x", speed=2.0, travel=130, start_offset=0):
        self.rect         = pygame.Rect(x, y, w, h)
        self.origin       = (x, y)
        self.axis         = axis
        self.speed        = speed
        self.travel       = travel
        self.offset       = float(start_offset)
        self.dir          = 1

    def update(self):
        self.offset += self.speed * self.dir
        if abs(self.offset) >= self.travel:
            self.dir *= -1
        if self.axis == "x":
            self.rect.x = self.origin[0] + int(self.offset)
        else:
            self.rect.y = self.origin[1] + int(self.offset)

    def collides_with(self, car):
        return self.rect.colliderect(car.get_rect())

    def draw(self, surf):
        """
        # TODO: Replace with Ezekiel's moving-car sprite (with direction flip)
        """
        pygame.draw.rect(surf, C_MOVER, self.rect, border_radius=5)
        inner = self.rect.inflate(-8, -14)
        if inner.w > 0 and inner.h > 0:
            pygame.draw.rect(surf, (140, 200, 240), inner, border_radius=3)
        pygame.draw.rect(surf, (40, 80, 150), self.rect, 2, border_radius=5)


# ═══════════════════════════════════════════════════════════
#  CLASS: NarrowCorridor
# ═══════════════════════════════════════════════════════════
class NarrowCorridor:
    """
    Two parallel walls forming a tight passage.
    The gap must be just barely wider than the car.
    Used in levels 3 and 5 to force precision navigation.
    """

    def __init__(self, x, y, length, gap, vertical=True):
        if vertical:
            self.wall_a = Obstacle(x,         y, "wall", w=18, h=length)
            self.wall_b = Obstacle(x+gap+18,  y, "wall", w=18, h=length)
        else:
            self.wall_a = Obstacle(x, y,        "wall", w=length, h=18)
            self.wall_b = Obstacle(x, y+gap+18, "wall", w=length, h=18)

    def get_obstacles(self):
        return [self.wall_a, self.wall_b]


# ═══════════════════════════════════════════════════════════
#  CLASS: Level
# ═══════════════════════════════════════════════════════════
class Level:
    """
    All data for one level.
    v2: time_limit required on every level; car_sensitivity
    ramps friction down as well as speed/steer up.
    """

    def __init__(self, number, spawn, park_zone,
                 obstacles=None, movers=None, corridors=None,
                 boundary=None, bg_color=None,
                 time_limit=60, car_sensitivity=1.0):
        self.number          = number
        self.spawn           = spawn
        self.park_zone       = park_zone
        self.obstacles       = list(obstacles or [])
        self.movers          = list(movers    or [])
        for c in (corridors or []):
            self.obstacles.extend(c.get_obstacles())
        self.boundary        = boundary or pygame.Rect(20, 20, SCREEN_W-40, SCREEN_H-40)
        self.bg_color        = bg_color or C_ROAD
        self.time_limit      = time_limit
        self.car_sensitivity = car_sensitivity

    def reset(self):
        self.park_zone.park_timer    = 0.0
        self.park_zone.is_parked     = False
        self.park_zone.moving_penalty= False
        for m in self.movers:
            m.offset = 0.0
            m.dir    = 1

    def update(self):
        for m in self.movers:
            m.update()

    def draw_background(self, surf):
        surf.fill(C_BG)
        pygame.draw.rect(surf, self.bg_color, self.boundary)
        gc = tuple(min(255, c+8) for c in self.bg_color)
        for gy in range(self.boundary.top, self.boundary.bottom, 40):
            for gx in range(self.boundary.left, self.boundary.right, 40):
                # TODO: Replace with Ezekiel's tileable road/asphalt texture
                pygame.draw.line(surf, gc, (gx, gy), (gx+18, gy), 1)
        pygame.draw.rect(surf, C_LINE, self.boundary, 4)

    def draw(self, surf):
        self.draw_background(surf)
        self.park_zone.draw(surf)
        for obs in self.obstacles:
            obs.draw(surf)
        for m in self.movers:
            m.draw(surf)

    def check_collisions(self, car):
        if not self.boundary.collidepoint(car.x, car.y):
            return True
        for obs in self.obstacles:
            if obs.collides_with(car):
                return True
        for m in self.movers:
            if m.collides_with(car):
                return True
        return False


# ═══════════════════════════════════════════════════════════
#  LEVEL FACTORY
# ═══════════════════════════════════════════════════════════
def build_levels():
    """
    Build and return all 5 levels, easiest → hardest.

    Difficulty knobs per level:
      zone size | angle tolerance | time limit | obstacle density
      mover speed | corridor gap | car_sensitivity | spawn angle
    """
    levels = []

    # ──────────────────────────────────────────────────────
    # LEVEL 1 — "Learn the brakes"  (45s, angle ±20°)
    # Smaller zone than old v1, two blocking walls force a
    # curved approach instead of a straight line.
    # ──────────────────────────────────────────────────────
    obs1 = [
        Obstacle(120, 120, "cone"), Obstacle(780, 120, "cone"),
        Obstacle(120, 530, "cone"), Obstacle(780, 530, "cone"),
        Obstacle(330, 255, "wall", w=130, h=18),   # blocks direct path
        Obstacle(455, 330, "wall", w=18,  h=90),   # right-side deflector
    ]
    levels.append(Level(
        number=1, spawn=(160, 520, 0),
        park_zone=ParkingZone(400, 170, 62, 88, required_angle=0, angle_tolerance=20),
        obstacles=obs1,
        boundary=pygame.Rect(80, 80, SCREEN_W-160, SCREEN_H-160),
        bg_color=(52, 57, 70), time_limit=45, car_sensitivity=1.0,
    ))

    # ──────────────────────────────────────────────────────
    # LEVEL 2 — "Cone slalom"  (40s, angle ±15°)
    # Two staggered columns of cones + wall blockers.
    # Must weave through the slalom to reach zone.
    # ──────────────────────────────────────────────────────
    obs2 = []
    for row in range(5):
        y = 155 + row * 78
        obs2.append(Obstacle(275, y,    "cone"))
        obs2.append(Obstacle(560, y+39, "cone"))
    obs2 += [
        Obstacle(335, 105, "wall", w=200, h=18),   # top blocker
        Obstacle(148, 295, "wall", w=18,  h=150),  # left wall
        Obstacle(718, 275, "wall", w=18,  h=150),  # right wall
    ]
    movers2 = [
        MovingObstacle(240, 220, 70, 24, "x", speed=2.8, travel=180, start_offset=0),
        MovingObstacle(540, 390, 70, 24, "x", speed=3.1, travel=140, start_offset=80),
    ]
    levels.append(Level(
        number=2, spawn=(160, 555, 0),
        park_zone=ParkingZone(396, 115, 56, 78, required_angle=0, angle_tolerance=22),
        obstacles=obs2, movers=movers2,
        boundary=pygame.Rect(70, 70, SCREEN_W-140, SCREEN_H-140),
        bg_color=(47, 53, 66), time_limit=40, car_sensitivity=1.1,
    ))

    # ──────────────────────────────────────────────────────
    # LEVEL 3 — "Precision Passage"  (35s)
    # Difficult lane transitions and a tight final parking bay.
    # Exit the narrow corridor and pull into the zone from the right.
    # ──────────────────────────────────────────────────────
    corr3a = NarrowCorridor(120, 260, length=260, gap=44, vertical=False)
    corr3b = NarrowCorridor(520, 120, length=230, gap=44, vertical=True)
    obs3 = [
        Obstacle(100, 110, "wall", w=270, h=18),
        Obstacle(100, 110, "wall", w=18,  h=210),
        Obstacle(360, 300, "wall", w=260, h=18),
        Obstacle(620, 210, "wall", w=18,  h=220),
        Obstacle(540, 420, "cone"), Obstacle(590, 420, "cone"),
        Obstacle(640, 420, "cone"), Obstacle(310, 520, "cone"),
    ]
    movers3 = [
        MovingObstacle(220, 170, 24, 70, "y", speed=3.4, travel=150, start_offset=20),
        MovingObstacle(560, 420, 70, 24, "x", speed=3.8, travel=120, start_offset=40),
    ]
    levels.append(Level(
        number=3, spawn=(100, 540, 0),
        park_zone=ParkingZone(620, 230, 70, 100, required_angle=0, angle_tolerance=360),
        obstacles=obs3, movers=movers3,
        corridors=[corr3a, corr3b],
        boundary=pygame.Rect(60, 60, SCREEN_W-120, SCREEN_H-120),
        bg_color=(42, 48, 62), time_limit=35, car_sensitivity=1.2,
    ))

    # ──────────────────────────────────────────────────────
    # LEVEL 4 — "Moving traffic"  (30s, angle ±10°)
    # Five fast movers with staggered offsets (never in sync),
    # + tight zone tucked in the bottom-right corner.
    # Spawn is rotated 15° — already disorienting from frame 1.
    # ──────────────────────────────────────────────────────
    movers4 = [
        MovingObstacle(100, 188, 75, 32, "x", speed=4.0, travel=220, start_offset=0),
        MovingObstacle(100, 378, 75, 32, "x", speed=3.5, travel=220, start_offset=110),
        MovingObstacle(678, 128, 32, 70, "y", speed=3.6, travel=200, start_offset=60),
        MovingObstacle(178, 118, 75, 32, "x", speed=3.2, travel=160, start_offset=80),
        MovingObstacle(520, 358, 32, 70, "y", speed=4.2, travel=180, start_offset=30),
    ]
    obs4 = [
        Obstacle(338,  88, "wall", w=162, h=18),
        Obstacle(338, 478, "wall", w=162, h=18),
        Obstacle( 98, 398, "wall", w=18,  h=82),
        Obstacle(728, 238, "wall", w=18,  h=82),
        Obstacle(438, 258, "cone"), Obstacle(488, 258, "cone"),
        Obstacle(438, 318, "cone"), Obstacle(488, 318, "cone"),
    ]
    levels.append(Level(
        number=4, spawn=(100, 548, 15),
        park_zone=ParkingZone(588, 428, 52, 76, required_angle=0, angle_tolerance=10),
        obstacles=obs4, movers=movers4,
        boundary=pygame.Rect(60, 60, SCREEN_W-120, SCREEN_H-120),
        bg_color=(38, 44, 58), time_limit=30, car_sensitivity=1.3,
    ))

    # ──────────────────────────────────────────────────────
    # LEVEL 5 — "Expert Challenge"  (25s)
    # Fast moving obstacles and tight navigation.
    # Navigate through the maze to reach the parking zone.
    # ──────────────────────────────────────────────────────
    movers5 = [
        MovingObstacle(200, 200, 70, 30, "x", speed=4.5, travel=180, start_offset=0),
        MovingObstacle(400, 400, 70, 30, "x", speed=4.0, travel=150, start_offset=50),
        MovingObstacle(600, 150, 30, 70, "y", speed=4.2, travel=200, start_offset=25),
        MovingObstacle(300, 300, 70, 30, "x", speed=3.8, travel=120, start_offset=75),
    ]
    corr5a = NarrowCorridor(150, 300, length=250, gap=50, vertical=False)
    obs5 = [
        Obstacle(100, 100, "wall", w=200, h=18),
        Obstacle(100, 100, "wall", w=18,  h=300),
        Obstacle(300, 100, "wall", w=18,  h=200),
        Obstacle(300, 380, "wall", w=200, h=18),
        Obstacle(500, 200, "wall", w=18,  h=200),
        Obstacle(500, 200, "wall", w=150, h=18),
        Obstacle(650, 200, "wall", w=18,  h=150),
        Obstacle(200, 500, "cone"), Obstacle(250, 500, "cone"),
        Obstacle(300, 500, "cone"), Obstacle(600, 450, "cone"),
        Obstacle(650, 450, "cone"),
    ]
    levels.append(Level(
        number=5, spawn=(120, 550, 0),
        park_zone=ParkingZone(650, 250, 80, 90, required_angle=0, angle_tolerance=360),
        obstacles=obs5, movers=movers5,
        corridors=[corr5a],
        boundary=pygame.Rect(70, 70, SCREEN_W-140, SCREEN_H-140),
        bg_color=(32, 38, 50), time_limit=25, car_sensitivity=1.4,
    ))

    return levels


# ═══════════════════════════════════════════════════════════
#  CLASS: Game
# ═══════════════════════════════════════════════════════════
class Game:
    """
    State machine:
      START → PLAYING → LEVEL_TRANSITION → (back to PLAYING)
                      ↘ LOSE
                      ↘ WIN (after level 5)
    """

    def __init__(self):
        self.levels          = build_levels()
        self.level_index     = 0
        self.state           = "START"
        self.car             = PlayerCar(*self.current_level.spawn)
        self.attempts        = 0
        self.total_attempts  = 0
        self.elapsed         = 0.0
        self.transition_t    = 0.0
        self.crash_flash     = 0.0
        self.tick_played     = False
        self.screen_shake = 0.0
        self.best_times = [None] * len(self.levels)

    @property
    def current_level(self):
        return self.levels[self.level_index]

    # ── State control ────────────────────────────────────
    def start_level(self):
        lvl = self.current_level
        lvl.reset()
        self.car.reset(*lvl.spawn)
        s = lvl.car_sensitivity
        self.car.steer_speed  = 3.2  * s
        self.car.acceleration = 0.22 * s
        self.car.max_speed    = 5.5  * s
        # Friction worsens with sensitivity (more slide at high levels)
        self.car.friction     = max(0.81, 0.88 - (s - 1.0) * 0.09)
        self.elapsed          = 0.0
        self.tick_played      = False
        self.state            = "PLAYING"

    def trigger_crash(self):
        if self.state != "PLAYING":
            return
        self.car.crashed    = True
        self.attempts      += 1
        self.total_attempts+= 1
        self.crash_flash    = 0.7
        SFX_CRASH.play()
        self.state = "LOSE"
        # Shakes the screen when the car crashes
        self.screen_shake = 12

    def next_level(self):
        SFX_WIN.play()
        current_time = self.elapsed
      best = self.best_times[self.level_index]

      if best is None or current_time < best:
        self.best_times[self.level_index] = current_time
        
        self.level_index += 1
        if self.level_index >= len(self.levels):
            self.state = "WIN"
        else:
            self.transition_t = 2.5
            self.state        = "LEVEL_TRANSITION"

    def restart_game(self):
        self.level_index    = 0
        self.attempts       = 0
        self.total_attempts = 0
        self.start_level()

    def retry_level(self):
        self.start_level()

    # ── Update ───────────────────────────────────────────
    def update(self, dt, keys):
        if self.state == "PLAYING":
            self._update_playing(dt, keys)
        elif self.state == "LEVEL_TRANSITION":
            self.transition_t -= dt
            if self.transition_t <= 0:
                self.start_level()
        self.crash_flash = max(0.0, self.crash_flash - dt)

        self.screen_shake = max(0, self.screen_shale - dt * 20)

    def _update_playing(self, dt, keys):
        lvl       = self.current_level
        self.elapsed += dt
        remaining = lvl.time_limit - self.elapsed

        if remaining <= 0:
            self.trigger_crash()
            return

        # Tick warning at ≤5 s
        if remaining <= 5.0 and not self.tick_played:
            SFX_TICK.play()
            self.tick_played = True

        self.car.handle_input(keys)
        self.car.update()
        lvl.update()

        if lvl.check_collisions(self.car):
            self.trigger_crash()
            return

        if lvl.park_zone.check(self.car, dt):
            self.next_level()

    # ── Draw ─────────────────────────────────────────────
    def draw(self):
        screen.fill(C_BG)
        # Screen Shake
        offset_x = int(random.uniform(-self.screen_shake, self.screen_shake))
        offset_y = int(randome.uniform(-self.screen_shake, self.screen_shake))
      
        if   self.state == "START":            self._draw_start()
        elif self.state == "PLAYING":          self._draw_gameplay()
        elif self.state == "LEVEL_TRANSITION": self._draw_transition()
        elif self.state == "LOSE":
            self._draw_gameplay()
            self._draw_lose_overlay()
        elif self.state == "WIN":              self._draw_win()

        if self.crash_flash > 0:
            alpha = int(min(195, self.crash_flash * 280))
            fl = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            fl.fill((220, 30, 30, alpha))
            screen.blit(fl, (0, 0))
        # Creating a shaken frame
        shaken = pygame.Surface((SCREEN_W, SCREEN_H))
        shaken.blit(screen, (offset_x, offset_y))
      
        screen.blit(shaken, (0,0))
              
        pygame.display.flip()

    def _grad(self, r0, g0, b0, r1, g1, b1):
        """Draw a vertical gradient background."""
        for y in range(SCREEN_H):
            t = y / SCREEN_H
            pygame.draw.line(screen,
                             (int(r0+t*(r1-r0)), int(g0+t*(g1-g0)), int(b0+t*(b1-b0))),
                             (0, y), (SCREEN_W, y))

    def _draw_start(self):
        self._grad(18, 20, 30, 32, 36, 55)

        title  = font_big.render("PRECISION PARKING", True, C_ACCENT)
        shadow = font_big.render("PRECISION PARKING", True, (35, 28, 5))
        screen.blit(shadow, shadow.get_rect(center=(SCREEN_W//2+3, 115+3)))
        screen.blit(title,  title.get_rect(center=(SCREEN_W//2, 115)))

        diff = font_med.render("★  HARD MODE  ★", True, C_RED)
        screen.blit(diff, diff.get_rect(center=(SCREEN_W//2, 168)))

        box = pygame.Rect(SCREEN_W//2 - 235, 205, 470, 268)
        pygame.draw.rect(screen, (24, 28, 44), box, border_radius=10)
        pygame.draw.rect(screen, C_ACCENT, box, 2, border_radius=10)

        rows = [
            ("CONTROLS",                          C_ACCENT, font_med),
            ("",                                  C_TEXT,   font_small),
            ("↑ / ↓   Accelerate / Reverse",      C_TEXT,   font_small),
            ("← / →   Steer (drifts at speed!)",  C_TEXT,   font_small),
            ("R        Retry current level",       C_TEXT,   font_small),
            ("",                                  C_TEXT,   font_small),
            ("RULES",                             C_ORANGE, font_small),
            ("Park inside the GREEN zone.",        C_TEXT,   font_small),
            ("Match the ARROW direction.",         C_TEXT,   font_small),
            ("Slow to a crawl — hold 2 seconds.", C_TEXT,   font_small),
            ("Every level has a time limit!",     C_RED,    font_small),
        ]
        for i, (txt, col, fnt) in enumerate(rows):
            screen.blit(fnt.render(txt, True, col), (box.x + 18, box.y + 12 + i*24))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            p = font_med.render("PRESS SPACE TO START", True, C_GREEN)
            screen.blit(p, p.get_rect(center=(SCREEN_W//2, 510)))

        # TODO: Replace with Ezekiel's animated title-screen car sprites
        for px, py, pa in [(110, 575, 0), (790, 575, 0),
                           (110,  75, 180), (790,  75, 180)]:
            PlayerCar(px, py, pa).draw(screen)

    def _draw_gameplay(self):
        self.current_level.draw(screen)
        self.car.draw(screen)
        self._draw_hud()

    def _draw_hud(self):
        lvl       = self.current_level
        remaining = max(0.0, lvl.time_limit - self.elapsed)

        # Left panel
        hud = pygame.Rect(8, 8, 318, 82)
        hs  = pygame.Surface((hud.w, hud.h), pygame.SRCALPHA)
        hs.fill((14, 16, 24, 205))
        screen.blit(hs, hud.topleft)
        pygame.draw.rect(screen, C_ACCENT, hud, 2, border_radius=6)

        screen.blit(font_med.render(f"LEVEL  {lvl.number} / 5", True, C_ACCENT), (18, 14))
        screen.blit(font_small.render(f"Attempts: {self.attempts}", True, C_TEXT), (18, 50))

        best = self.best_times[self.level_index]
        if best is not None:
          best_text = F"Best: {best:.2F}s"
        else:
          best_text = "Best: --"
        screen.blit(font_small.render(best_text, True, C_GREEN), (18, 68))
      
        tcol = C_RED if remaining < 8 else (C_ORANGE if remaining < 15 else C_TEXT)
        screen.blit(font_small.render(f"TIME: {remaining:.1f}s", True, tcol), (185, 50)
        # Countdown bar below HUD panel
        bmax = hud.w - 8
        bw   = int(bmax * (remaining / lvl.time_limit))
        bcol = C_RED if remaining < 8 else (C_ORANGE if remaining < 15 else C_GREEN)
        pygame.draw.rect(screen, (35,35,45),
                         pygame.Rect(hud.x+4, hud.bottom+2, bmax, 5), border_radius=2)
        if bw > 0:
            pygame.draw.rect(screen, bcol,
                             pygame.Rect(hud.x+4, hud.bottom+2, bw, 5), border_radius=2)

        # Right panel: live car stats
        rp = pygame.Rect(SCREEN_W-105, 8, 97, 70)
        rs = pygame.Surface((rp.w, rp.h), pygame.SRCALPHA)
        rs.fill((14, 16, 24, 205))
        screen.blit(rs, rp.topleft)
        pygame.draw.rect(screen, C_ACCENT, rp, 1, border_radius=5)

        spd = abs(self.car.speed)
        pz  = lvl.park_zone
        screen.blit(font_tiny.render(f"SPD {spd:.1f}", True, C_RED if spd > 3 else C_TEXT),
                    (rp.x+6, rp.y+6))
        screen.blit(font_tiny.render(f"ANG {int(self.car.angle)%360}°", True, C_TEXT),
                    (rp.x+6, rp.y+24))
        screen.blit(font_tiny.render(f"REQ {int(pz.required_angle)}°", True, C_ACCENT),
                    (rp.x+6, rp.y+42))

        # Centre hints
        pz = lvl.park_zone
        if pz.moving_penalty:
            h = font_small.render("SLOW DOWN!", True, C_ORANGE)
            screen.blit(h, h.get_rect(center=(SCREEN_W//2, SCREEN_H-30)))
        elif pz.is_parked:
            h = font_small.render("HOLD STILL...", True, C_GREEN)
            screen.blit(h, h.get_rect(center=(SCREEN_W//2, SCREEN_H-30)))

        ctrl = font_tiny.render("↑↓ Drive   ←→ Steer   R Retry", True, (95,95,115))
        screen.blit(ctrl, ctrl.get_rect(bottomright=(SCREEN_W-8, SCREEN_H-6)))

    def _draw_lose_overlay(self):
        ov = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 155))
        screen.blit(ov, (0, 0))

        remaining = max(0.0, self.current_level.time_limit - self.elapsed)
        reason    = "TIME'S UP!" if remaining <= 0 else "YOU CRASHED!"

        screen.blit(font_big.render(reason, True, C_RED),
                    font_big.render(reason, True, C_RED).get_rect(
                        center=(SCREEN_W//2, SCREEN_H//2-65)))
        screen.blit(font_med.render(f"Attempts: {self.attempts}", True, C_TEXT),
                    font_med.render(f"Attempts: {self.attempts}", True, C_TEXT).get_rect(
                        center=(SCREEN_W//2, SCREEN_H//2)))

        tip = font_small.render(
            f"Lvl {self.current_level.number} limit: {self.current_level.time_limit}s", True, C_ORANGE)
        screen.blit(tip, tip.get_rect(center=(SCREEN_W//2, SCREEN_H//2+38)))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            r = font_med.render("R — Retry   |   SPACE — Menu", True, C_ACCENT)
            screen.blit(r, r.get_rect(center=(SCREEN_W//2, SCREEN_H//2+78)))

    def _draw_transition(self):
        self._grad(12, 28, 14, 30, 54, 32)
        prev = self.level_index

        msg = font_big.render(f"LEVEL {prev} CLEARED!", True, C_GREEN)
        screen.blit(msg, msg.get_rect(center=(SCREEN_W//2, SCREEN_H//2-55)))

        if prev < len(self.levels):
            nxt = self.levels[prev]
            warns = []
            if nxt.time_limit <= 30:
                warns.append(f"⚠  Only {nxt.time_limit}s on the clock!")
            if nxt.car_sensitivity >= 1.3:
                warns.append("⚠  Twitchy steering + slippery physics!")
            if nxt.movers:
                warns.append(f"⚠  {len(nxt.movers)} moving obstacles!")
            if nxt.park_zone.required_angle not in (0, 360):
                warns.append(f"⚠  Must park at {int(nxt.park_zone.required_angle)}° angle!")
            for i, w in enumerate(warns):
                wt = font_small.render(w, True, C_ORANGE)
                screen.blit(wt, wt.get_rect(center=(SCREEN_W//2, SCREEN_H//2+5+i*30)))

        dots = "." * (int(self.transition_t*3) % 4)
        wt   = font_small.render(f"Get ready{dots}", True, C_TEXT)
        screen.blit(wt, wt.get_rect(center=(SCREEN_W//2, SCREEN_H//2+120)))

    def _draw_win(self):
        self._grad(8, 18, 8, 28, 52, 28)

        title  = font_big.render("YOU MASTERED PARKING!", True, C_GREEN)
        shadow = font_big.render("YOU MASTERED PARKING!", True, (6, 42, 6))
        screen.blit(shadow, shadow.get_rect(center=(SCREEN_W//2+3, 163+3)))
        screen.blit(title,  title.get_rect(center=(SCREEN_W//2, 163)))

        if   self.total_attempts <= 5:  grade, gc = "S  —  FLAWLESS",      C_ACCENT
        elif self.total_attempts <= 12: grade, gc = "A  —  IMPRESSIVE",    C_GREEN
        elif self.total_attempts <= 25: grade, gc = "B  —  SOLID RUN",     C_TEXT
        else:                           grade, gc = "C  —  YOU SURVIVED",  C_ORANGE

        sb = pygame.Rect(SCREEN_W//2 - 215, 242, 430, 148)
        pygame.draw.rect(screen, (12, 30, 12), sb, border_radius=10)
        pygame.draw.rect(screen, C_GREEN, sb, 2, border_radius=10)

        for i, (txt, col) in enumerate([
            (f"Total Attempts :  {self.total_attempts}", C_TEXT),
            (f"Levels Cleared :  5 / 5",                C_TEXT),
            (f"Grade          :  {grade}",              gc),
            (f"(≤5 attempts = S rank)",                 (100,100,120)),
        ]):
            screen.blit(font_small.render(txt, True, col),
                        (sb.x+18, sb.y+16+i*34))

        if (pygame.time.get_ticks() // 500) % 2 == 0:
            p = font_med.render("Press R to Play Again", True, C_ACCENT)
            screen.blit(p, p.get_rect(center=(SCREEN_W//2, 428)))

        # TODO: Replace with Ezekiel's victory animation / confetti sprite sheet
        for px, py, pa in [(SCREEN_W//2-135, 545, 0),
                           (SCREEN_W//2,     545, 0),
                           (SCREEN_W//2+135, 545, 0)]:
            PlayerCar(px, py, pa).draw(screen)

    # ── Input ────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if self.state == "START":
                    self.start_level()
                elif self.state == "LOSE":
                    self.state       = "START"
                    self.level_index = 0
                    self.attempts    = 0
            elif event.key == pygame.K_r:
                if self.state in ("PLAYING", "LOSE"):
                    self.retry_level()
                elif self.state == "WIN":
                    self.restart_game()


# ═══════════════════════════════════════════════════════════
#  MAIN LOOP
# ═══════════════════════════════════════════════════════════
def main():
    game = Game()
    while True:
        dt   = clock.tick(FPS) / 1000.0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)

        game.update(dt, keys)
        game.draw()


# ═══════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
