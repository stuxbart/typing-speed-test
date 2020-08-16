import pygame
import random
import string
from clock import Clock


pygame.init()
pygame.font.init()


class Text:
    def __init__(self, x: int = 0, y: int = 0, text: str = "", size: int = 20,
                 color: tuple = (0, 0, 0), centered: bool = True):
        self.pos_x = x
        self.pos_y = y
        self.width = 0
        self.height = 0
        self.centered = centered
        self.font = pygame.font.SysFont('Arial', size)
        self.color = color
        self.text = text
        self.surface = self.font.render(self.text, True, self.color)

    @property
    def x(self):
        if self.centered:
            return self.pos_x - int(self.width/2)
        else:
            return self.pos_x

    @property
    def y(self):
        if self.centered:
            return self.pos_y - int(self.height/2)
        else:
            return self.pos_y

    def draw(self, window):
        window.blit(self.surface, (self.x, self.y))

    def set_text(self, text):
        self.text = text
        self.surface = self.font.render(self.text, True, self.color)
        self.width, self.height = self.font.size(self.text)

    def set_position(self, x=None, y=None):
        if x is not None:
            self.pos_x = x
        if y is not None:
            self.pos_y = y


class Button:
    def __init__(self, x: int = 0, y: int = 0, w: int = 200, h: int = 100, filename: str = ""):
        self.pos_x = x
        self.pos_y = y
        self.width = w
        self.height = h
        self.img = pygame.image.load(filename)
        self.callback = None

    @property
    def rect(self):
        return [self.pos_x, self.pos_y, self.width, self.height]

    def connect(self, callback):
        self.callback = callback

    def draw(self, window):
        window.blit(self.img, self.rect)

    def check_clicked(self, x, y):
        if self.pos_x < x < self.pos_x + self.width and self.pos_y < y < self.pos_y + self.height:
            if self.callback is not None:
                self.callback()
            return True
        return False

    def change_position(self, x, y):
        self.pos_x = x
        self.pos_y = y


class Scene:
    def __init__(self, parent):
        self.parent = parent
        self.drawable = []
        self.bg_color = (100, 100, 200)

    def draw(self, window):
        window.fill(self.bg_color)
        for d in self.drawable:
            d.draw(window)

    def clicked(self, x, y):
        for d in self.drawable:
            if isinstance(d, Button):
                clicked = d.check_clicked(x, y)
                if clicked:
                    break

    def get_input(self, key):
        pass


class StartScene(Scene):
    def __init__(self, parent):
        super().__init__(parent)
        self.start_btn = Button(300, 200, 200, 100, "./imgs/start_btn.png")
        self.start_btn.connect(self.start_game)
        self.drawable.append(self.start_btn)

    def start_game(self):
        self.parent.change_scene("game_scene")


class GameScene(Scene):
    def __init__(self, parent):
        super().__init__(parent)
        self.reset_btn = Button(300, 400, 200, 100, "./imgs/reset_btn.png")
        self.reset_btn.connect(self.reset_game)
        self.drawable.append(self.reset_btn)

        self.sentence = Text(400, 150)
        self.drawable.append(self.sentence)

        self.typed_sentence_text = Text(400, 200, centered=False)
        self.drawable.append(self.typed_sentence_text)

        self.time_text = Text(400, 50)
        self.drawable.append(self.time_text)

        self.bg_color = (200, 200, 225)

        self.clock = Clock()
        self.time_text.set_text(f"{self.clock.time: .2f}")

        self.sentences = []

        try:
            with open('./sentences.txt') as f:
                for s in f:
                    self.sentences.append(s.strip())
        except FileExistsError:
            print("Cannot open file")
            exit()

        self.current_sentence = random.choice(self.sentences)
        self.sentence.set_text(self.current_sentence)

        self.typed_sentence_text.set_position(x=self.sentence.x)
        self.typed_sentence = ""

        self.started = False

    def reset_game(self):
        self.typed_sentence = ""
        self.typed_sentence_text.set_text(self.typed_sentence)
        self.clock.stop()
        self.clock.reset_time()
        self.started = False

    def get_input(self, event):
        if event.key == pygame.K_BACKSPACE:
            self.typed_sentence = self.typed_sentence[:-1]
        elif event.key == pygame.K_RETURN:
            self.clock.stop()
            self.parent.change_scene("summary_scene")
            self.parent.current_scene.set_time(self.clock.time)
            self.parent.current_scene.set_text(self.sentence.text)
            self.parent.current_scene.set_typed_text(self.typed_sentence)

        else:
            if event.unicode != '':
                if event.unicode in string.printable:
                    self.typed_sentence += event.unicode
                    if not self.started:
                        self.started = True
                        self.clock.start()
        self.typed_sentence_text.set_text(self.typed_sentence)

    def update_clock(self):
        self.clock.tick()
        self.time_text.set_text(f"{self.clock.time: .2f}")

    def random_sentence(self):
        self.current_sentence = random.choice(self.sentences)
        self.sentence.set_text(self.current_sentence)
        self.typed_sentence_text.set_position(x=self.sentence.x)
        self.typed_sentence = ""


class SummaryScene(Scene):
    def __init__(self, parent):
        super().__init__(parent)
        self.time = 0
        self.text = ""
        self.typed_text = ""

        self.bg_color = (100, 100, 200)

        self.time_text = Text(400, 50)
        self.drawable.append(self.time_text)
        self.time_text.set_text(str(self.time))

        self.wpm_text = Text(400, 100)
        self.drawable.append(self.wpm_text)

        self.accuracy_text = Text(400, 150)
        self.drawable.append(self.accuracy_text)

        self.start_btn = Button(300, 200, 200, 100, "./imgs/start_btn.png")
        self.start_btn.connect(self.start_game)
        self.drawable.append(self.start_btn)

    def start_game(self):
        self.parent.change_scene("game_scene")
        self.parent.current_scene.random_sentence()
        self.parent.current_scene.reset_game()

    @property
    def words_count(self):
        return len(self.typed_text.split())

    @property
    def words_per_minute(self):
        if self.time:
            return self.words_count / self.time * 60
        else:
            return 0

    @property
    def accuracy(self):
        text_length = len(self.text)
        typed_text_len = len(self.typed_text)
        if typed_text_len < text_length:
            typed_text = self.typed_text + "#" * (text_length - typed_text_len)
        elif text_length < typed_text_len:
            typed_text = self.typed_text[:text_length]
        else:
            typed_text = self.typed_text

        good = 0
        for l1, l2 in zip(self.text, typed_text):
            if l1 == l2:
                good += 1

        accuracy = good / text_length * 100
        return accuracy

    def set_time(self, time):
        self.time = time
        self.time_text.set_text(f"Time: {self.time}s")
        self.wpm_text.set_text(f"WPM: {self.words_per_minute}")

    def set_typed_text(self, typed_text):
        self.typed_text = typed_text
        self.time_text.set_text(f"Time: {self.time: .2f}s")
        self.wpm_text.set_text(f"WPM: {self.words_per_minute: .2f}")
        self.accuracy_text.set_text(f"Accuracy: {self.accuracy:.2f}%")

    def set_text(self, text):
        self.text = text


class Window:
    def __init__(self):
        self.win = pygame.display.set_mode((800, 500))
        pygame.display.set_caption("Typing Speed Test")

        self.scenes = {
            "start_scene": StartScene(self),
            "game_scene": GameScene(self),
            "summary_scene": SummaryScene(self)
        }
        self.current_scene = self.scenes['start_scene']

        self.running = True

    def run(self):
        while self.running:
            self.events()
            if self.current_scene == self.scenes['game_scene']:
                self.current_scene.update_clock()
            self.current_scene.draw(self.win)
            pygame.display.update()

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                self.current_scene.clicked(x, y)
            elif event.type == pygame.KEYDOWN:
                self.current_scene.get_input(event)

    def change_scene(self, scene):
        if scene in self.scenes:
            self.current_scene = self.scenes[scene]
        else:
            print("Wrong scene")


if __name__ == "__main__":
    win = Window()
    win.run()
