import asyncio
import pygame as pg
import random
import threading
import sys


x_coord = None
fruit_flag = False
game_running = True


class ServerConnection:
    def __init__(self):
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)

    async def receive_loop(self):
        await self.connect()
        global x_coord, fruit_flag
        while game_running:
            data = await self.reader.read(100)
            x_coord = int(data.decode())
            fruit_flag = True


def receive_thread(server_connection):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(server_connection.receive_loop())


class ObjectClient:
    def __init__(self):
        self.fruit_paths = ["./img/dona.png", "./img/duff.png", "./img/llamarada.png",
                            "./img/tomaco.png",]
        self.fruit_imgs = []
        self.fruits = []
        self.fruits_caught = 0
        self.fruits_missed = 0
        self.game_over = False
        self.basket_x = WIDTH // 2 - BASKET_WIDTH // 2

    def load_images(self):
        for path in self.fruit_paths:
            img = pg.image.load(path).convert_alpha()
            img = pg.transform.scale(img, (50, 50))
            self.fruit_imgs.append(img)

    def spawn_object(self, x_coord):
        fruit_img = random.choice(self.fruit_imgs)
        fruit = {"img": fruit_img, "x": x_coord, "y": 0}
        self.fruits.append(fruit)

    def show_game_over_screen(self):
        window.fill(WHITE)
        font = pg.font.Font(None, 50)
        text = font.render("Game Over", True, RED)
        text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        window.blit(text, text_rect)
        pg.display.update()

    async def main(self):
        global fruit_flag, game_running
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
        self.reader = reader
        clock = pg.time.Clock()
        showing_start_screen = True
        self.load_images()
        while game_running:
            if showing_start_screen:
                window.fill(WHITE)
                font = pg.font.Font(None, 50)
                text = font.render("Come con Homero", True, RED)
                text_rect = text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
                window.blit(text, text_rect)
                start_button = pg.Rect(WIDTH/2 - 100, HEIGHT/2, 200, 50)
                pg.draw.rect(window, RED, start_button)
                font = pg.font.Font(None, 30)
                start_text = font.render("Comenzar", True, WHITE)
                start_text_rect = start_text.get_rect(
                    center=start_button.center)
                window.blit(start_text, start_text_rect)
                pg.display.update()
                for event in pg.event.get():
                    if event.type == pg.QUIT:
                        game_running = False
                    elif event.type == pg.MOUSEBUTTONDOWN:
                        mouse_pos = pg.mouse.get_pos()
                        if start_button.collidepoint(mouse_pos):
                            showing_start_screen = False
                            self.fruits_caught = 0
                            self.fruits_missed = 0
                            self.fruits.clear()
            else:
                if not self.game_over:
                    for event in pg.event.get():
                        if event.type == pg.QUIT:
                            game_running = False

                    window.fill(WHITE)

                    keys = pg.key.get_pressed()
                    if keys[pg.K_LEFT] and self.basket_x > 0:
                        self.basket_x -= 5
                    if keys[pg.K_RIGHT] and self.basket_x < WIDTH - BASKET_WIDTH:
                        self.basket_x += 5

                    if fruit_flag:
                        self.spawn_object(x_coord)
                        fruit_flag = False

                    window.blit(basket_img, (self.basket_x,
                                HEIGHT - BASKET_HEIGHT))

                    for fruit in self.fruits[:]:
                        window.blit(fruit["img"], (fruit["x"], fruit["y"]))
                        fruit["y"] += FRUIT_FALL_SPEED
                        if fruit["y"] > HEIGHT:
                            self.fruits.remove(fruit)
                            if not self.game_over:
                                self.fruits_missed += 1
                                if self.fruits_missed >= 5:
                                    self.game_over = True

                    for fruit in self.fruits[:]:
                        if fruit["y"] + 50 > HEIGHT - BASKET_HEIGHT and \
                                self.basket_x < fruit["x"] < self.basket_x + BASKET_WIDTH:
                            self.fruits.remove(fruit)
                            self.fruits_caught += 1

                    font = pg.font.Font(None, 30)
                    text_caught = font.render(
                        f"Comida atrapada: {self.fruits_caught}", True, RED)
                    window.blit(text_caught, (20, 15))

                    text_missed = font.render(f"Comida no atrapadas: {
                        self.fruits_missed}", True, RED)
                    window.blit(text_missed, (20, 50))

                    pg.display.update()
                    clock.tick(60)

                    if self.game_over:
                        self.show_game_over_screen()

            if not game_running:
                break
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    game_running = False
        pg.quit()
        sys.exit()


if __name__ == "__main__":
    pg.init()
    WIDTH, HEIGHT = 800, 600
    window = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("Atrapando Comida con Homero")

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)

    BASKET_WIDTH = 100
    BASKET_HEIGHT = 100

    basket_img = pg.transform.scale(pg.image.load(
        "./img/homero.png"), (BASKET_WIDTH, BASKET_HEIGHT))

    FRUIT_FALL_SPEED = 1

    server_connection = ServerConnection()

    threading.Thread(target=receive_thread, args=(
        server_connection,), daemon=True).start()

    fruit_client = ObjectClient()
    asyncio.run(fruit_client.main())
