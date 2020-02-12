"""
Это классическая игра flappy bird на python и pygame

"""
import pygame
import random
import os
import time
import neat
import visualize
import pickle
pygame.font.init()  # init font

WIN_WIDTH = 600
WIN_HEIGHT = 800
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/Vadim/Desktop/NEAT-Flappy-Bird-master/imgs/pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("C:/Users/Vadim/Desktop/NEAT-Flappy-Bird-master/imgs/bg.png")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/Vadim/Desktop/NEAT-Flappy-Bird-master/imgs/bird1.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/Vadim/Desktop/NEAT-Flappy-Bird-master/imgs/bird2.png"))), pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/Vadim/Desktop/NEAT-Flappy-Bird-master/imgs/bird3.png")))]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("C:/Users/Vadim/Desktop/NEAT-Flappy-Bird-master/imgs/base.png")).convert_alpha())

gen = 0

class Bird:
    """
    Bird class представленный в flappy bird
    """
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        """
        Инициализация объектов
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        """
        совершает прыжок птицы
        
        :return: None
        """
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        """
        совершает прыжок птицы
        :return: None
        """
        self.tick_count += 1

        # для ускорения вниз
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement

        # предельная скорость
        if displacement >= 16:
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL

    def draw(self, win):
        """
        Рисование 
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1

        # Анимации птицы, перебор трех изображений
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0

        # нырок вниз,птица не хлопает
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2


        # наклон птицы
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        """
        получает маску для текущего изображения птицы
        :return: None
        """
        return pygame.mask.from_surface(self.img)


class Pipe():
    """
    представляет объект трубы
    """
    GAP = 200
    VEL = 5

    def __init__(self, x):
        """
        инициализация объекта трубы
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # верх и низ трубы
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        установливает высоту трубы, сверху экрана
        :return: None
        """
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        """
        перемещает трубу на основе vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        рисунок верха и низа трубы
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        возвращает, если точка сталкивается с трубой
        :param bird: Bird object
        :return: Bool
        """
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask,top_offset)

        if b_point or t_point:
            return True

        return False

class Base:
    """
    Представляет движущийся пол игры

    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y):
        """
        Инициализирование объектов
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        перемещение пола ,чтобы был вид прокрутки
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Рисунок изображений. Это два изображения, которые движутся вместе.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    
    Поверните поверхность и поднесите ее к окну
    : param surf: поверхность, на которую нужно копить
    : param image: поверхность изображения для вращения
    : param topLeft: верхняя левая позиция изображения
    : угол параметра: значение с плавающей точкой для угла
    :return: None

    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind):
    """
    рисует окна для основного игрового циклаp
    : param win: поверхность окна Pygame
    : param bird: bird объект
    : param pipe: Список труб
    : оценка параметра: оценка игры (int)
    : param gen: текущее поколение
    : param pipe_ind: индекс ближайшей трубы
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0))

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # рисунок линий от птицы до трубы
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # рисунок птицы
        bird.draw(win)

    # счет
    score_label = STAT_FONT.render("Счёт: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # поколение
    score_label = STAT_FONT.render("Ген: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # количество птиц
    score_label = STAT_FONT.render("Количество птиц: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
    
    запускает симуляцию текущего количества
    птиц и устанавливает их движение на основе расстояния, которое они
    могут достичь в игре.
    """
    global WIN, gen
    win = WIN
    gen += 1

    # начать с создания списков, содержащих сам геном
    # нейронная сеть, связанная с геномом и
    # объект птица, которая использует эту сеть для воспроизведения
    nets = []
    birds = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0  # начать с уровня 0 
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350))
        ge.append(genome)

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock()

    run = True

    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # определить, используется ли первая или вторая
                pipe_ind = 1                                                                 # труба на экране для ввода нейронной сети

        for x, bird in enumerate(birds):  # дать каждой птице пригодность 0,1 для каждого кадра, который остается живым
            ge[x].fitness += 0.1
            bird.move()

            # отправить местоположение птицы, расположение верхней и нижней труб и определить по сети, прыгать или нет
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # мы используем функцию активации tanh, поэтому результат будет между -1 и 1. если скачок более 0,5
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()

            # проверить на столкновение

            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True

        if add_pipe:
            score += 1

            # можете добавить эту строку, чтобы дать больше вознаграждения за прохождение через трубу (не требуется)

            for genome in ge:
                genome.fitness += 5

            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # перерыв, если счет становится достаточно большим
        '''if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break'''


def run(config_file):
    """
    запускает алгоритм NEAT, чтобы обучить нейронную сеть играть в беспечную fluppi bird.
    : param config_file: расположение файла конфигурации
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Создайте совокупность, которая является объектом верхнего уровня для запуска NEAT.
    p = neat.Population(config)

    # Добавьте репортер stdout, чтобы показать прогресс в терминале.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Lj 50 генов
    winner = p.run(eval_genomes, 50)

    # показать окончательную статистику
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':

    # Определить путь к файлу конфигурации. Это путь обозначен
    # здесь, чтобы скрипт успешно работал независимо от
    # текущей работы каталога.

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
