import random
import json
import math
from kivy.config import Config
Config.set('graphics', 'width', '360')
Config.set('graphics', 'height', '640')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle, Line, PushMatrix, PopMatrix, Translate, Rotate, Scale
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import NumericProperty, StringProperty, ObjectProperty, ListProperty
from kivy.utils import get_color_from_hex
from kivy.core.text import Label as CoreLabel
from kivy.animation import Animation

WHITE = [1, 1, 1, 1]
BG_COLOR = [0.102, 0.102, 0.180, 1]
PLAYER_COLORS = [
    [0.914, 0.271, 0.376, 1],
    [0.961, 0.773, 0.094, 1],
    [0.325, 0.706, 0.961, 1],
    [0.584, 0.318, 0.953, 1],
    [0.239, 0.878, 0.502, 1],
]


class GameWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.game_state = 'menu'
        self.score = 0
        self.high_score = 0
        self.coins = 0

        self.player_x = 0
        self.player_y = 0
        self.player_r = 18
        self.player_vy = 0
        self.player_vx = 0
        self.is_grounded = True
        self.player_color_index = 0
        self.current_color = PLAYER_COLORS[0]

        self.obstacles = []
        self.coin_items = []
        self.particles = []
        self.stars = []

        self.gravity = -0.55
        self.jump_power = 11
        self.ground_h = 70
        self.game_speed = 5
        self.max_speed = 14
        self.speed_timer = 0
        self.obs_timer = 0
        self.obs_interval = 1.4

        self.score_label = None
        self.menu_labels = []
        self.gameover_labels = []
        self.needs_redraw = True

        Window.bind(on_resize=self.on_window_resize)
        self.load_data()
        self.init_stars()
        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.bind(size=self.on_window_resize)

    def on_window_resize(self, win=None, w=None, h=None):
        self.needs_redraw = True

    def load_data(self):
        try:
            with open(App.get_running_app().get_data_path('save.json'), 'r') as f:
                data = json.load(f)
                self.high_score = data.get('high_score', 0)
                self.coins = data.get('coins', 0)
                self.player_color_index = data.get('color', 0)
        except:
            self.high_score = 0
            self.coins = 0
            self.player_color_index = 0
        self.current_color = PLAYER_COLORS[self.player_color_index % len(PLAYER_COLORS)]

    def save_data(self):
        try:
            with open(App.get_running_app().get_data_path('save.json'), 'w') as f:
                json.dump({
                    'high_score': self.high_score,
                    'coins': self.coins,
                    'color': self.player_color_index,
                }, f)
        except:
            pass

    def init_stars(self):
        self.stars = []
        for _ in range(30):
            self.stars.append({
                'x': random.uniform(0, Window.width),
                'y': random.uniform(0, Window.height),
                's': random.uniform(1, 3),
                'b': random.uniform(0.3, 0.8),
            })

    def reset(self):
        self.score = 0
        self.game_speed = 5
        self.speed_timer = 0
        self.obs_timer = 0
        self.obs_interval = 1.4
        self.obstacles = []
        self.coin_items = []
        self.particles = []
        self.player_x = Window.width / 2 - self.player_r
        self.player_y = self.ground_h + 10
        self.player_vy = 0
        self.player_vx = 0
        self.is_grounded = True
        self.current_color = PLAYER_COLORS[self.player_color_index % len(PLAYER_COLORS)]

    def start_game(self):
        self.game_state = 'playing'
        self.reset()
        self.needs_redraw = True

    def game_over(self):
        self.game_state = 'gameover'
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_data()
        for _ in range(25):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(3, 8)
            self.particles.append({
                'x': self.player_x + self.player_r,
                'y': self.player_y + self.player_r,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'color': random.choice(PLAYER_COLORS),
                'life': 1.0,
                'size': random.uniform(3, 6),
            })
        self.needs_redraw = True

    def on_touch_down(self, touch):
        if self.game_state == 'menu':
            self.start_game()
            return
        if self.game_state == 'gameover':
            self.start_game()
            return
        if self.game_state == 'playing':
            self.jump()

    def jump(self):
        if self.is_grounded or self.player_y < self.ground_h + 40:
            self.player_vy = self.jump_power
            self.is_grounded = False
            for _ in range(6):
                self.particles.append({
                    'x': self.player_x + self.player_r + random.uniform(-5, 5),
                    'y': self.player_y - 2,
                    'vx': random.uniform(-1.5, 1.5),
                    'vy': random.uniform(-0.3, 0.3),
                    'color': self.current_color,
                    'life': 0.6,
                    'size': random.uniform(2, 4),
                })

    def spawn_obstacle(self):
        margin = 25
        lane_w = (Window.width - 2 * margin) / 3
        lane = random.randint(0, 2)
        w = random.randint(25, 60)
        h = random.randint(15, 30)
        x = margin + lane * lane_w + (lane_w - w) / 2
        self.obstacles.append({
            'x': x,
            'y': Window.height,
            'w': w,
            'h': h,
            'color': random.choice(PLAYER_COLORS[1:]),
        })

    def spawn_coin(self):
        if random.random() < 0.3:
            margin = 25
            lane_w = (Window.width - 2 * margin) / 3
            lane = random.randint(0, 2)
            x = margin + lane * lane_w + lane_w / 2 - 8
            self.coin_items.append({
                'x': x,
                'y': Window.height,
                'r': 8,
            })

    def rect_circle_collide(self, rx, ry, rw, rh, cx, cy, cr):
        closest_x = max(rx, min(cx, rx + rw))
        closest_y = max(ry, min(cy, ry + rh))
        dx = cx - closest_x
        dy = cy - closest_y
        return dx * dx + dy * dy < cr * cr

    def draw_text(self, text, x, y, font_size=24, color=WHITE, halign='center', valign='center'):
        try:
            label = CoreLabel(text=text, font_size=font_size, color=color)
            label.refresh()
            texture = label.texture
            tx = x - texture.width / 2 if halign == 'center' else x
            ty = y - texture.height / 2 if valign == 'center' else y
            Color(*color)
            Rectangle(pos=(tx, ty), size=texture.size, texture=texture)
        except:
            pass

    def draw_menu(self):
        self.draw_text('SKY HOP', Window.width / 2, Window.height * 0.65, 48, WHITE)
        self.draw_text(f'High Score: {int(self.high_score)}', Window.width / 2, Window.height * 0.55, 20, [0.7, 0.7, 0.7, 1])
        self.draw_text(f'Coins: {int(self.coins)}', Window.width / 2, Window.height * 0.50, 18, [0.961, 0.773, 0.094, 1])
        self.draw_text('TAP TO START', Window.width / 2, Window.height * 0.32, 22, [1, 1, 1, 0.6])

        Color(*[0.961, 0.773, 0.094, 0.8])
        RoundedRectangle(
            pos=(Window.width / 2 - 50, Window.height * 0.36),
            size=(100, 3),
            radius=[1.5]
        )

    def draw_playing(self):
        self.draw_text(str(int(self.score)), Window.width / 2, Window.height - 60, 48, WHITE)

        Color(*[0.961, 0.773, 0.094, 1])
        Ellipse(pos=(20, Window.height - 50), size=(16, 16))
        self.draw_text(f'{int(self.coins)}', 50, Window.height - 42, 16, [0.961, 0.773, 0.094, 1], halign='left')

    def draw_gameover(self):
        self.draw_text('GAME OVER', Window.width / 2, Window.height * 0.65, 42, [0.914, 0.271, 0.376, 1])
        self.draw_text(f'Score: {int(self.score)}', Window.width / 2, Window.height * 0.55, 26, WHITE)
        if self.score >= self.high_score and self.score > 0:
            self.draw_text('NEW BEST!', Window.width / 2, Window.height * 0.50, 18, [0.961, 0.773, 0.094, 1])
        else:
            self.draw_text(f'Best: {int(self.high_score)}', Window.width / 2, Window.height * 0.50, 18, [0.7, 0.7, 0.7, 1])
        self.draw_text('TAP TO RETRY', Window.width / 2, Window.height * 0.35, 20, [1, 1, 1, 0.6])

        Color(*[0.914, 0.271, 0.376, 0.8])
        RoundedRectangle(
            pos=(Window.width / 2 - 50, Window.height * 0.39),
            size=(100, 3),
            radius=[1.5]
        )

    def draw(self):
        self.canvas.clear()
        with self.canvas:
            Color(*BG_COLOR)
            Rectangle(pos=(0, 0), size=Window.size)

            for star in self.stars:
                Color(1, 1, 1, star['b'])
                Ellipse(pos=(star['x'], star['y']), size=(star['s'], star['s']))

            Color(*[0.086, 0.086, 0.157, 1])
            Rectangle(pos=(0, 0), size=(Window.width, self.ground_h))
            Color(*[0.914, 0.271, 0.376, 0.3])
            Rectangle(pos=(0, self.ground_h), size=(Window.width, 2))

            for obs in self.obstacles:
                Color(*obs['color'])
                RoundedRectangle(pos=(obs['x'], obs['y']), size=(obs['w'], obs['h']), radius=[4])

            for coin in self.coin_items:
                Color(*[0.961, 0.773, 0.094, 1])
                Ellipse(pos=(coin['x'], coin['y']), size=(coin['r'] * 2, coin['r'] * 2))
                Color(*[0.961, 0.773, 0.094, 0.3])
                Ellipse(pos=(coin['x'] - 2, coin['y'] - 2), size=(coin['r'] * 2 + 4, coin['r'] * 2 + 4))

            Color(*self.current_color)
            glow = self.current_color[:]
            glow[3] = 0.25
            Color(*glow)
            Ellipse(pos=(self.player_x - 6, self.player_y - 6), size=(self.player_r * 2 + 12, self.player_r * 2 + 12))
            Color(*self.current_color)
            Ellipse(pos=(self.player_x, self.player_y), size=(self.player_r * 2, self.player_r * 2))
            Color(1, 1, 1, 0.3)
            Ellipse(
                pos=(self.player_x + self.player_r * 0.3, self.player_y + self.player_r * 1.2),
                size=(self.player_r * 0.5, self.player_r * 0.3)
            )

            for p in self.particles:
                Color(*p['color'][:3], p['life'])
                Ellipse(pos=(p['x'] - p['size'] / 2, p['y'] - p['size'] / 2), size=(p['size'], p['size']))

            if self.game_state == 'menu':
                self.draw_menu()
            elif self.game_state == 'playing':
                self.draw_playing()
            elif self.game_state == 'gameover':
                self.draw_gameover()

    def update(self, dt):
        if self.game_state == 'playing':
            self.update_game(dt)

        if self.game_state == 'gameover':
            for p in self.particles[:]:
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['vy'] -= 0.2
                p['life'] -= 0.02
                if p['life'] <= 0:
                    self.particles.remove(p)

        self.draw()

    def update_game(self, dt):
        self.speed_timer += dt
        if self.speed_timer > 4:
            self.speed_timer = 0
            self.game_speed = min(self.game_speed + 0.2, self.max_speed)
            self.obs_interval = max(self.obs_interval - 0.03, 0.5)

        self.obs_timer += dt
        if self.obs_timer >= self.obs_interval:
            self.obs_timer = 0
            self.spawn_obstacle()
            self.spawn_coin()

        self.player_vy += self.gravity
        self.player_y += self.player_vy
        if self.player_y <= self.ground_h:
            self.player_y = self.ground_h
            self.player_vy = 0
            self.is_grounded = True

        cx = self.player_x + self.player_r
        cy = self.player_y + self.player_r

        for obs in self.obstacles[:]:
            obs['y'] -= self.game_speed
            if obs['y'] + obs['h'] < 0:
                self.obstacles.remove(obs)
                continue
            if not obs.get('passed') and obs['y'] + obs['h'] < self.player_y:
                obs['passed'] = True
                self.score += 1
            if self.rect_circle_collide(obs['x'], obs['y'], obs['w'], obs['h'], cx, cy, self.player_r):
                self.game_over()
                return

        for coin in self.coin_items[:]:
            coin['y'] -= self.game_speed
            if coin['y'] + coin['r'] * 2 < 0:
                self.coin_items.remove(coin)
                continue
            dx = cx - (coin['x'] + coin['r'])
            dy = cy - (coin['y'] + coin['r'])
            if dx * dx + dy * dy < (self.player_r + coin['r']) ** 2:
                self.coin_items.remove(coin)
                self.coins += 1
                self.save_data()
                for _ in range(8):
                    angle = random.uniform(0, math.pi * 2)
                    self.particles.append({
                        'x': coin['x'] + coin['r'],
                        'y': coin['y'] + coin['r'],
                        'vx': math.cos(angle) * 2,
                        'vy': math.sin(angle) * 2,
                        'color': [0.961, 0.773, 0.094, 1],
                        'life': 0.8,
                        'size': random.uniform(2, 4),
                    })

        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] -= 0.2
            p['life'] -= 0.03
            if p['life'] <= 0:
                self.particles.remove(p)


class HopGame(App):
    title = 'Sky Hop'

    def get_data_path(self, path):
        import os
        return os.path.join(self.user_data_dir, path)

    def build(self):
        Window.clearcolor = BG_COLOR
        game = GameWidget()
        return game


if __name__ == '__main__':
    HopGame().run()
