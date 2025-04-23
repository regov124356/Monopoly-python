import pygame, os, random

pygame.init()
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

SIZESCREEN = WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode(SIZESCREEN)
path_images = os.path.join(os.getcwd(), 'images')
path_music = os.path.join(os.getcwd(), 'music')
file_names = os.listdir(path_images)
clock = pygame.time.Clock()

BACKGROUND = pygame.image.load(os.path.join(path_images, 'board.png')).convert()
file_names.remove('board.png')
IMAGES = {}
for file_name in file_names:
    image_name = file_name[:-4].upper()
    IMAGES[image_name] = pygame.image.load(os.path.join(path_images, file_name)).convert_alpha(BACKGROUND)


class Player(pygame.sprite.Sprite):
    def __init__(self, id, image_player, x, y):
        super().__init__()
        self.id = id
        self.image = image_player
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.money = 2000000
        self.color = None
        self.position_property = 0
        self.number_of_players = None
        self.turns_blocked = 0
        self.properties_owned = []
        self.loose = False

    def update(self):
        player_turn_dices = self.position_property + dice1.roll_result + dice2.roll_result
        dublet = True if dice1.roll_result == dice2.roll_result else False

        if self.turns_blocked > 0 and not dublet:
            self.turns_blocked -= 1
            return
        else:
            self.turns_blocked = 0

        properties[self.position_property].remove_player(self)
        self.position_property = player_turn_dices % 32
        number_of_players = properties[self.position_property].add_player(self)

        if self.position_property == 24:  # Podroz
            properties[24].remove_player(self)
            self.position_property = random.randint(0, 31)
            while self.position_property == 24:
                self.position_property = random.randint(0, 31)
                number_of_players = properties[self.position_property].add_player(self)

        if self.position_property == 12 or self.position_property == 20 or self.position_property == 28: # Szansa
            random_number = random.randint(1, 3)
            if random_number == 1:
                self.money = self.money + 300000
            if random_number == 2:
                self.sell()
            if random_number == 3:
                properties[self.position_property].remove_player(self)
                self.position_property = random.randint(0, 31)
                number_of_players = properties[self.position_property].add_player(self)

        self.number_of_players = number_of_players

        if player_turn_dices > 31:  # Start
            self.money = self.money + 300000

        if self.position_property == 8:  # Bezludna wyspa
            self.turns_blocked = 3

        if self.position_property == 16: # Mistrzostwa swiata
            if len(self.properties_owned) > 0:
                property_up = self.properties_owned[random.randint(1, len(self.properties_owned)) - 1]
                property_up.rent = property_up.rent * 2

        if self.position_property == 30: # Podatek
            self.money = self.money * 0.9

        self.rect.topleft = properties[self.position_property].rect.topleft

        if self.number_of_players == 1:
            self.rect.topleft = (self.rect.topleft[0] - 10, self.rect.topleft[1] - 10)
        elif self.number_of_players == 2:
            self.rect.topleft = (self.rect.topleft[0] + 10, self.rect.topleft[1] - 10)
        elif self.number_of_players == 3:
            self.rect.topleft = (self.rect.topleft[0] - 10, self.rect.topleft[1] + 10)
        elif self.number_of_players == 4:
            self.rect.topleft = (self.rect.topleft[0] + 10, self.rect.topleft[1] + 10)

    def draw(self, surface):

        surface.blit(self.image, self.rect.topleft)

    def money_draw(self):
        if self == red_player:
            money_text = Text(f"{self.money / 1000}K", BLACK, 250, 225, 25, None)
            money_text.draw(screen)
        elif self == blue_player:
            money_text = Text(f"{self.money / 1000}K", BLACK, 535, 225, 25, None)
            money_text.draw(screen)
        elif self == green_player:
            money_text = Text(f"{self.money / 1000}K", BLACK, 250, 580, 25, None)
            money_text.draw(screen)
        else:
            money_text = Text(f"{self.money / 1000}K", BLACK, 535, 580, 25, None)
            money_text.draw(screen)

    def pay(self, player):
        rent = properties[self.position_property].rent
        while self.money < rent:
            if self.loose:
                break
            self.sell()
        self.money = self.money - rent
        player.money = player.money + rent

        if self.loose:
            return True

    def sell(self):
        liczba = len(self.properties_owned)
        if liczba < 1:
            self.loose = True
            return

        property_tmp = self.properties_owned[random.randint(1, liczba) - 1]

        if property_tmp.buildings_owned == 1:
            amount = property_tmp.price
        elif property_tmp.buildings_owned == 2:
            amount = property_tmp.price + property_tmp.house_price
        elif property_tmp.buildings_owned == 3:
            amount = property_tmp.price + 2 * property_tmp.house_price
        elif property_tmp.buildings_owned == 4:
            amount = property_tmp.price + 3 * property_tmp.house_price
        elif property_tmp.buildings_owned == 5:
            if property_tmp.number == 4 or property_tmp.number == 14 or property_tmp.number == 18 or property_tmp.number == 25:
                amount = property_tmp.price
            else:
                amount = property_tmp.price + 3 * property_tmp.house_price + property_tmp.hotel_price
        else:
            amount = 0

        property_tmp.player_own = None
        property_tmp.player_color = None
        property_tmp.buildings_owned = 0
        property_tmp.rent = 0
        self.properties_owned.remove(property_tmp)
        print(self.properties_owned)
        print(len(self.properties_owned))
        self.money = self.money + amount


class Dice(pygame.sprite.Sprite):
    def __init__(self, images, x, y):
        super().__init__()
        self.images = images
        self.image = images['1_DICE']
        self.rect = self.image.get_rect(center=(x, y))
        self.roll_result = None

    def update(self):
        self.roll_result = random.randint(1, 6)
        self.image = self.images[f'{self.roll_result}_DICE']

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Text:
    def __init__(self, text, color, cx, cy, font_size=36, font_family=None, angle=0):
        self.text = str(text)
        self.color = color
        self.cx = cx
        self.cy = cy
        self.font = pygame.font.SysFont(font_family, font_size)
        self.angle = angle
        self.image = self.font.render(self.text, 1, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = self.cx, self.cy
        self.update()

    def update(self):
        if self.angle != 0:
            self.image = pygame.transform.rotate(self.image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class Button:
    def __init__(self, text, text_color, background_color, cx, cy, width, height,
                 font_size=36, font_family=None):
        self.text = Text(text, text_color, cx, cy, font_size, font_family)
        self.background_color = background_color
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = self.text.rect.center

    def draw(self, surface):
        surface.fill(self.background_color, self.rect)
        self.text.update()
        self.text.draw(surface)


class Property(pygame.sprite.Sprite):
    def __init__(self, name, number, position, price=None, house_price=None, hotel_price=None):
        super().__init__()
        self.name = name
        self.number = number
        self.image = IMAGES['DOT']
        self.rect = self.image.get_rect()
        self.rect.topleft = position
        self.price = price
        self.house_price = house_price
        self.hotel_price = hotel_price
        self.buildings_owned = 0
        self.rent = 0
        self.players_on_place = []
        self.player_own = None
        self.images = IMAGES
        self.position_building = None
        self.player_color = None

    def draw(self, surface):
        if self.rect.topleft[1] > 700:
            if self.buildings_owned == 5:
                self.position_building = (self.rect.topleft[0], self.rect.topleft[1] - 60)
                surface.blit(IMAGES[f'{self.player_color}_HOTEL'], self.position_building)
            else:
                self.position_building = (self.rect.topleft[0] - 30, self.rect.topleft[1] - 60)
                for i in range(self.buildings_owned):
                    surface.blit(self.images[f'{self.player_color}_HOUSE'], [self.position_building[0] + i * 15, self.position_building[1]])

            rent_text = Text("" if self.rent == 0 else f"{self.rent / 1000}K", BLACK, self.rect.topleft[0], self.rect.topleft[1] + 55, 25, None)
            rent_text.draw(screen)

        if self.rect.topleft[0] < 100:
            if self.buildings_owned == 5:
                self.position_building = (self.rect.topleft[0] + 50, self.rect.topleft[1])
                surface.blit(IMAGES[f'{self.player_color}_HOTEL'], self.position_building)
            else:
                self.position_building = (self.rect.topleft[0] + 50, self.rect.topleft[1] - 30)
                for i in range(self.buildings_owned):
                    surface.blit(self.images[f'{self.player_color}_HOUSE'], [self.position_building[0], self.position_building[1] + i * 15])

            rent_text = Text("" if self.rent == 0 else f"{self.rent / 1000}K", BLACK, self.rect.topleft[0] - 60, self.rect.topleft[1], 25, None, 270)
            rent_text.draw(screen)

        if self.rect.topleft[1] < 100:
            if self.buildings_owned == 5:
                self.position_building = (self.rect.topleft[0], self.rect.topleft[1] + 55)
                surface.blit(IMAGES[f'{self.player_color}_HOTEL'], self.position_building)
            else:
                self.position_building = (self.rect.topleft[0] - 30, self.rect.topleft[1] + 55)
                for i in range(self.buildings_owned):
                    surface.blit(self.images[f'{self.player_color}_HOUSE'], [self.position_building[0] + i * 15, self.position_building[1]])

            rent_text = Text("" if self.rent == 0 else f"{self.rent / 1000}K", BLACK, self.rect.topleft[0], self.rect.topleft[1] - 50, 25, None)
            rent_text.draw(screen)

        if self.rect.topleft[0] > 700:
            if self.buildings_owned == 5:
                self.position_building = (self.rect.topleft[0] - 60, self.rect.topleft[1])
                surface.blit(IMAGES[f'{self.player_color}_HOTEL'], self.position_building)
            else:
                self.position_building = (self.rect.topleft[0] - 60, self.rect.topleft[1] - 30)
                for i in range(self.buildings_owned):
                    surface.blit(self.images[f'{self.player_color}_HOUSE'], [self.position_building[0], self.position_building[1] + i * 15])

            rent_text = Text("" if self.rent == 0 else f"{self.rent / 1000}K", BLACK, self.rect.topleft[0] + 55, self.rect.topleft[1], 25, None, 270)
            rent_text.draw(screen)

    def buy_without_owner(self, player, buildings_owned):

        if buildings_owned == 1:
            amount = self.price
            self.rent = 0.2 * self.hotel_price
        elif buildings_owned == 2:
            amount = self.price + self.house_price
            self.rent = 0.4 * self.hotel_price
        elif buildings_owned == 3:
            amount = self.price + 2 * self.house_price
            self.rent = 0.6 * self.hotel_price
        elif buildings_owned == 4:
            amount = self.price + 3 * self.house_price
            self.rent = 0.8 * self.hotel_price
        elif buildings_owned == 5:
            if self.number == 4 or self.number == 14 or self.number == 18 or self.number == 25:
                amount = self.price
                self.rent = 200000
            else:
                amount = self.price + 3 * self.house_price + self.hotel_price
                self.rent = self.hotel_price

        if player.money >= amount:
            self.player_own = player
            self.player_color = player.color
            self.buildings_owned = buildings_owned
            player.properties_owned.append(self)
            player.money = player.money - amount
            print("kupujemy")
            print(self.rent)
        else:
            self.rent = 0
            print("za mało pieniedzy")
            if player == red_player:
                rectangle.draw()
                text_za_malo_pieniedzy.draw(screen)
            print(self.rent)

    def buy_with_owner(self, player, buildings_owned):

        if self.buildings_owned == 1:
            amount = self.price
        elif self.buildings_owned == 2:
            amount = self.price + self.house_price
        elif self.buildings_owned == 3:
            amount = self.price + 2 * self.house_price
        elif self.buildings_owned == 4:
            amount = self.price + 3 * self.house_price
        else:
            amount = 0

        if buildings_owned == 1:
            amount2 = self.price
            rent = 0.2 * self.hotel_price
        elif buildings_owned == 2:
            amount2 = self.price + self.house_price
            rent = 0.4 * self.hotel_price
        elif buildings_owned == 3:
            amount2 = self.price + 2 * self.house_price
            rent = 0.6 * self.hotel_price
        elif buildings_owned == 4:
            amount2 = self.price + 3 * self.house_price
            rent = 0.8 * self.hotel_price
        elif buildings_owned == 5:
            amount2 = self.price + 3 * self.house_price + self.hotel_price
            rent = self.hotel_price
        else:
            rent = 0

        if player.money >= (amount2 - amount):
            self.player_own = player
            self.player_color = player.color
            self.buildings_owned = buildings_owned
            self.rent = rent
            player.properties_owned.append(self)
            player.money -= amount2 - amount
            print("kupujemy")
            print(self.rent)

        else:
            print("za mało pieniedzy")
            if player == red_player:
                rectangle.draw()
                text_za_malo_pieniedzy.draw(screen)
            pygame.time.delay(1000)
            print(self.rent)

    def add_player(self, player):
        self.players_on_place.append(player)

        len_list = len(self.players_on_place)
        if len_list == 1:
            return 1
        elif len_list == 2:
            return 2
        elif len_list == 3:
            return 3
        elif len_list == 4:
            return 4
        self.update()

    def remove_player(self, player):
        if player in self.players_on_place:
            self.players_on_place.remove(player)


class Board:
    def __init__(self, background, players, dice1, dice2, properties):
        self.background = background
        self.players = players
        self.dice1 = dice1
        self.dice2 = dice2
        self.properties = properties
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.dice1, self.dice2)

        for player in self.players:
            self.all_sprites.add(player)

    def draw(self, surface):
        surface.blit(self.background, (0, 0))
        self.all_sprites.draw(surface)


class Rectangle:
    def __init__(self, screen, color, x, y, width, height):
        self.screen = screen
        self.color = color
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self):
        pygame.draw.rect(self.screen, self.color, (self.x, self.y, self.width, self.height))


red_player = Player(1, IMAGES['RED_PLAYER'], 681.81, 681.81)
red_player.color = 'RED'
blue_player = Player(2, IMAGES['BLUE_PLAYER'], 754.53, 681.81)
blue_player.color = 'BLUE'
green_player = Player(3, IMAGES['GREEN_PLAYER'], 681.81, 754.53)
green_player.color = 'GREEN'
yellow_player = Player(4, IMAGES['YELLOW_PLAYER'], 754.53, 754.53)
yellow_player.color = 'YELLOW'

properties = [
    Property("Start", 0, (727.27, 727.27)),
    Property("Grenada", 1, (618.181, 727.27), 60000, 50000, 150000),
    Property("Sewilla", 2, (545.45, 727.27), 60000, 50000, 150000),
    Property("Madryt", 3, (472.72, 727.27), 60000, 50000, 150000),
    Property("Bali", 4, (400, 727.27), 200000),
    Property("Hongkong", 5, (327.27, 727.27), 60000, 50000, 150000),
    Property("Pekin", 6, (254.545, 727.27), 60000, 50000, 150000),
    Property("Szanghaj", 7, (181.82, 727.27), 60000, 50000, 150000),
    Property("Bezludna Wyspa", 8, (72.72, 727.27)),

    Property("Wenecja", 9, (72.72, 618.12), 140000, 100000, 250000),
    Property("Mediolan", 10, (72.72, 545.4), 140000, 100000, 250000),
    Property("Rzym", 11, (72.72, 472.68), 160000, 100000, 250000),
    Property("Szansa", 12, (72.72, 399.96)),
    Property("Hamburg", 13, (72.72, 327.24), 180000, 100000, 250000),
    Property("Cypr", 14, (72.72, 254.52), 200000),
    Property("Berlin", 15, (72.72, 181.8), 200000, 100000, 250000),
    Property("Mistrzostwa Świata", 16, (72.72, 72.72)),

    Property("Londyn", 17, (181.8, 72.72), 220000, 150000, 375000),
    Property("Dubaj", 18, (254.52, 72.72), 200000),
    Property("Sydney", 19, (327.24, 72.72), 240000, 150000, 375000),
    Property("Szansa", 20, (399.96, 72.72)),
    Property("Chicago", 21, (472.68, 72.72), 260000, 150000, 375000),
    Property("Las Vegas", 22, (545.4, 72.72), 260000, 150000, 375000),
    Property("Nowy Jork", 23, (618.12, 72.72), 280000, 150000, 375000),
    Property("Podroz", 24, (727.27, 72.72)),

    Property("Nicea", 25, (727.27, 181.8), 200000),
    Property("Lyon", 26, (727.27, 254.52), 300000, 200000, 500000),
    Property("Paryż", 27, (727.27, 327.24), 320000, 200000, 500000),
    Property("Szansa", 28, (727.27, 399.96)),
    Property("Kraków", 29, (727.27, 472.68), 350000, 200000, 500000),
    Property("Podatek", 30, (727.27, 545.4)),
    Property("Warszawa", 31, (727.27, 618.17), 400000, 200000, 500000)
]

properties[0].players_on_place.extend([red_player, blue_player, green_player, yellow_player])
properties[0].player_own = "Board"
properties[8].player_own = "Board"
properties[12].player_own = "Board"
properties[16].player_own = "Board"
properties[20].player_own = "Board"
properties[24].player_own = "Board"
properties[28].player_own = "Board"
properties[30].player_own = "Board"

dice1 = Dice(IMAGES, WIDTH // 2 - 16, HEIGHT // 2)
dice2 = Dice(IMAGES, WIDTH // 2 + 16, HEIGHT // 2)

button_width, button_height = 200, 50

start_button = Button("Start", BLACK, GRAY, WIDTH // 2, HEIGHT // 2 - 50, button_width, button_height)
quit_button = Button("Quit", BLACK, GRAY, WIDTH // 2, HEIGHT // 2 + 50, button_width, button_height)
roll_button = Button("Roll", BLACK, GRAY, WIDTH // 2, HEIGHT // 2 + 50, button_width, button_height)

kup_pole = Button("Kup pole", (255, 255, 255), GREEN, WIDTH // 2, 200, button_width, button_height)
kup_dom = Button("Kup 1 dom", (255, 255, 255), GREEN, WIDTH // 2, 280, button_width, button_height)
kup_2domy = Button("Kup 2 domy", (255, 255, 255), GREEN, WIDTH // 2, 360, button_width, button_height)
kup_3domy = Button("Kup 3 domy", (255, 255, 255), GREEN, WIDTH // 2, 440, button_width, button_height)
kup_hotel = Button("Kup hotel", (255, 255, 255), GREEN, WIDTH // 2, 520, button_width, button_height)
anuluj = Button("Anuluj", RED, WHITE, WIDTH // 2, 600, button_width, button_height)

rectangle = Rectangle(screen, RED, WIDTH // 2 - 120, HEIGHT // 2 - 240, 240, 480)
text_za_malo_pieniedzy = Text("Za mało środków", (255, 255, 255), WIDTH // 2, HEIGHT // 2, 36, None)

turn = 1
number_of_active_players = 4
players = [red_player, blue_player, green_player, yellow_player]

window_open = True

active_game = False
roll = False
roll_button_active = True

kup_pole_bool = False
kup_dom_bool = False
kup_2domy_bool = False
kup_3domy_bool = False
kup_hotel_bool = False
anuluj_bool = False

no_owner = False

kup_pole_active = False
kup_dom_active = False
kup_2domy_active = False
kup_3domy_active = False
kup_hotel_active = False
anuluj_active = False

owner_is_you = False

resort = False

loose = False
win = False

while window_open:
    screen.blit(BACKGROUND, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if active_game:
                    active_game = False
                else:
                    window_open = False
        if event.type == pygame.QUIT:
            window_open = False
        elif event.type == pygame.MOUSEBUTTONDOWN and not active_game:
            if start_button.rect.collidepoint(event.pos):
                active_game = True
                pygame.time.delay(200)
            elif quit_button.rect.collidepoint(event.pos):
                window_open = False
        elif event.type == pygame.MOUSEBUTTONDOWN and active_game:
            if roll_button_active and roll_button.rect.collidepoint(event.pos):
                roll = True
                roll_button_active = False
                pygame.time.delay(500)
            if kup_pole_active and kup_pole.rect.collidepoint(event.pos):
                kup_pole_bool = True
                kup_pole_active = False
                pygame.time.delay(500)
            if kup_dom_active and kup_dom.rect.collidepoint(event.pos):
                kup_dom_bool = True
                kup_dom_active = False
                pygame.time.delay(500)
            if kup_2domy_active and kup_2domy.rect.collidepoint(event.pos):
                kup_2domy_bool = True
                kup_2domy_active = False
                pygame.time.delay(500)
            if kup_3domy_active and kup_3domy.rect.collidepoint(event.pos):
                kup_3domy_bool = True
                kup_3domy_active = False
                pygame.time.delay(500)
            if kup_hotel_active and kup_hotel.rect.collidepoint(event.pos):
                kup_hotel_bool = True
                kup_hotel_active = False
                pygame.time.delay(500)
            if anuluj_active and anuluj.rect.collidepoint(event.pos):
                anuluj_bool = True
                anuluj_active = False
                pygame.time.delay(500)

    if active_game:
        board = Board(BACKGROUND, players, dice1, dice2, properties)
        if win or loose:
            active_game = False

        elif turn == 1:
            if roll_button.rect.collidepoint(pygame.mouse.get_pos()):
                roll_button.text.color = WHITE
                roll_button.background_color = GRAY
            else:
                roll_button.text.color = WHITE
                roll_button.background_color = GRAY
            if kup_pole.rect.collidepoint(pygame.mouse.get_pos()):
                kup_pole.text_color = WHITE
                kup_pole.background_color = GRAY
            else:
                kup_pole.text_color = WHITE
                kup_pole.background_color = GREEN

            if kup_dom.rect.collidepoint(pygame.mouse.get_pos()):
                kup_dom.text_color = WHITE
                kup_dom.background_color = GRAY
            else:
                kup_dom.text_color = WHITE
                kup_dom.background_color = GREEN
            if kup_2domy.rect.collidepoint(pygame.mouse.get_pos()):
                kup_2domy.text_color = WHITE
                kup_2domy.background_color = GRAY
            else:
                kup_2domy.text_color = WHITE
                kup_2domy.background_color = GREEN

            if kup_3domy.rect.collidepoint(pygame.mouse.get_pos()):
                kup_3domy.text_color = WHITE
                kup_3domy.background_color = GRAY
            else:
                kup_3domy.text_color = WHITE
                kup_3domy.background_color = GREEN

            if kup_hotel.rect.collidepoint(pygame.mouse.get_pos()):
                kup_hotel.text_color = WHITE
                kup_hotel.background_color = GRAY
            else:
                kup_hotel.text_color = WHITE
                kup_hotel.background_color = GREEN
            if anuluj.rect.collidepoint(pygame.mouse.get_pos()):
                anuluj.text_color = WHITE
                anuluj.background_color = (128, 0, 0)
            else:
                anuluj.text_color = WHITE
                anuluj.background_color = WHITE
            board.draw(screen)
            for property in properties:
                property.draw(screen)
            for player in players:
                player.money_draw()
            roll_button.draw(screen)
            if roll:
                board.draw(screen)
                for property in properties:
                    property.draw(screen)
                for player in players:
                    player.money_draw()
                player_turn = players[turn - 1]
                dice1.update()
                dice2.update()
                player_turn.update()
                board.draw(screen)
                for property in properties:
                    property.draw(screen)
                for player in players:
                    player.money_draw()

                if properties[player_turn.position_property].player_own:
                    print("ma wlasciciela")
                    if properties[player_turn.position_property].player_own == "Board":
                        roll_button_active = True
                        turn = (turn % number_of_active_players) + 1
                    else:
                        if properties[player_turn.position_property].player_own == player_turn:
                            if properties[player_turn.position_property].buildings_owned != 5:
                                owner_is_you = True
                            else:
                                print("ma juz hotel")
                                roll_button_active = True
                                turn = (turn % number_of_active_players) + 1
                        else:
                            print("plac")
                            bool_loose = player_turn.pay(properties[player_turn.position_property].player_own)
                            if bool_loose:
                                loose = True

                            roll_button_active = True
                            turn = (turn % number_of_active_players) + 1

                else:
                    print("Nie ma wlasciciela")
                    number_of_place = properties[player_turn.position_property].number
                    if number_of_place == 4 or number_of_place == 14 or number_of_place == 18 or number_of_place == 25:
                        resort = True
                    else:
                        no_owner = True
                print(player_turn.money)
                roll = False

            if no_owner:
                roll_button_active = False
                kup_pole_active = True
                kup_dom_active = True
                kup_2domy_active = True
                kup_3domy_active = True
                kup_hotel_active = True
                anuluj_active = True
                rectangle.draw()
                kup_pole.draw(screen)
                kup_dom.draw(screen)
                kup_2domy.draw(screen)
                kup_3domy.draw(screen)
                kup_hotel.draw(screen)
                anuluj.draw(screen)
                if anuluj_bool:
                    no_owner = False
                    anuluj_bool = False
                    kup_pole_active = False
                    kup_dom_active = False
                    kup_2domy_active = False
                    kup_3domy_active = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    turn = (turn % number_of_active_players) + 1
                if kup_pole_bool:
                    no_owner = False
                    kup_pole_bool = False
                    kup_pole_active = False
                    kup_dom_active = False
                    kup_2domy_active = False
                    kup_3domy_active = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    properties[player_turn.position_property].buy_without_owner(player_turn, 1)
                    turn = (turn % number_of_active_players) + 1
                if kup_dom_bool:
                    no_owner = False
                    kup_dom_bool = False
                    kup_pole_active = False
                    kup_dom_active = False
                    kup_2domy_active = False
                    kup_3domy_active = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    properties[player_turn.position_property].buy_without_owner(player_turn, 2)
                    turn = (turn % number_of_active_players) + 1
                if kup_2domy_bool:
                    no_owner = False
                    kup_2domy_bool = False
                    kup_pole_active = False
                    kup_dom_active = False
                    kup_2domy_active = False
                    kup_3domy_active = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    properties[player_turn.position_property].buy_without_owner(player_turn, 3)
                    turn = (turn % number_of_active_players) + 1
                if kup_3domy_bool:
                    no_owner = False
                    kup_3domy_bool = False
                    kup_pole_active = False
                    kup_dom_active = False
                    kup_2domy_active = False
                    kup_3domy_active = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    properties[player_turn.position_property].buy_without_owner(player_turn, 4)
                    turn = (turn % number_of_active_players) + 1
                if kup_hotel_bool:
                    no_owner = False
                    kup_hotel_bool = False
                    kup_pole_active = False
                    kup_dom_active = False
                    kup_2domy_active = False
                    kup_3domy_active = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    properties[player_turn.position_property].buy_without_owner(player_turn, 5)
                    turn = (turn % number_of_active_players) + 1
            if owner_is_you:
                roll_button_active = False
                if properties[player_turn.position_property].buildings_owned == 1:
                    kup_dom_active = True
                    kup_2domy_active = True
                    kup_3domy_active = True
                    kup_hotel_active = True
                    anuluj_active = True
                    rectangle.draw()
                    kup_dom.draw(screen)
                    kup_2domy.draw(screen)
                    kup_3domy.draw(screen)
                    kup_hotel.draw(screen)
                    anuluj.draw(screen)
                    if anuluj_bool:
                        owner_is_you = False
                        anuluj_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        turn = (turn % number_of_active_players) + 1
                    if kup_dom_bool:
                        owner_is_you = False
                        kup_dom_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 2)
                        turn = (turn % number_of_active_players) + 1
                    if kup_2domy_bool:
                        owner_is_you = False
                        kup_2domy_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 3)
                        turn = (turn % number_of_active_players) + 1
                    if kup_3domy_bool:
                        owner_is_you = False
                        kup_3domy_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 4)
                        turn = (turn % number_of_active_players) + 1
                    if kup_hotel_bool:
                        owner_is_you = False
                        kup_hotel_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 5)
                        turn = (turn % number_of_active_players) + 1
                elif properties[player_turn.position_property].buildings_owned == 2:
                    roll_button_active = False
                    kup_2domy_active = True
                    kup_3domy_active = True
                    kup_hotel_active = True
                    anuluj_active = True
                    rectangle.draw()
                    kup_2domy.draw(screen)
                    kup_3domy.draw(screen)
                    kup_hotel.draw(screen)
                    anuluj.draw(screen)
                    if anuluj_bool:
                        owner_is_you = False
                        anuluj_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        turn = (turn % number_of_active_players) + 1
                    if kup_2domy_bool:
                        owner_is_you = False
                        kup_2domy_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 3)
                        turn = (turn % number_of_active_players) + 1
                    if kup_3domy_bool:
                        owner_is_you = False
                        kup_3domy_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 4)
                        turn = (turn % number_of_active_players) + 1
                    if kup_hotel_bool:
                        owner_is_you = False
                        kup_hotel_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 5)
                        turn = (turn % number_of_active_players) + 1
                elif properties[player_turn.position_property].buildings_owned == 3:
                    roll_button_active = False
                    kup_3domy_active = True
                    kup_hotel_active = True
                    anuluj_active = True
                    rectangle.draw()
                    kup_3domy.draw(screen)
                    kup_hotel.draw(screen)
                    anuluj.draw(screen)
                    if anuluj_bool:
                        owner_is_you = False
                        anuluj_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        turn = (turn % number_of_active_players) + 1
                    if kup_3domy_bool:
                        owner_is_you = False
                        kup_3domy_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 4)
                        turn = (turn % number_of_active_players) + 1
                    if kup_hotel_bool:
                        owner_is_you = False
                        kup_hotel_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 5)
                        turn = (turn % number_of_active_players) + 1
                elif properties[player_turn.position_property].buildings_owned == 4:
                    roll_button_active = False
                    kup_hotel_active = True
                    anuluj_active = True
                    rectangle.draw()
                    kup_hotel.draw(screen)
                    anuluj.draw(screen)
                    if anuluj_bool:
                        owner_is_you = False
                        anuluj_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        turn = (turn % number_of_active_players) + 1
                    if kup_hotel_bool:
                        owner_is_you = False
                        kup_hotel_bool = False
                        kup_pole_active = False
                        kup_dom_active = False
                        kup_2domy_active = False
                        kup_3domy_active = False
                        kup_hotel_active = False
                        anuluj_active = False
                        roll_button_active = True
                        properties[player_turn.position_property].buy_with_owner(player_turn, 5)
                        turn = (turn % number_of_active_players) + 1
            if resort:
                roll_button_active = False
                kup_hotel_active = True
                anuluj_active = True
                rectangle.draw()
                kup_hotel.draw(screen)
                anuluj.draw(screen)
                if anuluj_bool:
                    resort = False
                    anuluj_bool = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    turn = (turn % number_of_active_players) + 1
                if kup_hotel_bool:
                    resort = False
                    kup_hotel_bool = False
                    kup_hotel_active = False
                    anuluj_active = False
                    roll_button_active = True
                    properties[player_turn.position_property].buy_without_owner(player_turn, 5)
                    turn = (turn % number_of_active_players) + 1



        else:
            player_turn = players[turn - 1]
            dice1.update()
            dice2.update()
            player_turn.update()
            board.draw(screen)
            for property in properties:
                property.draw(screen)
            for player in players:
                player.money_draw()

            if properties[player_turn.position_property].player_own:
                print("ma wlasciciela bot")
                if properties[player_turn.position_property].player_own == "Board":
                    pass
                else:
                    if properties[player_turn.position_property].player_own == player_turn:
                        if properties[player_turn.position_property].buildings_owned != 5:
                            buildings_owned = properties[player_turn.position_property].buildings_owned
                            switcher = {
                                2: lambda: properties[player_turn.position_property].buy_with_owner(player_turn, 2),
                                3: lambda: properties[player_turn.position_property].buy_with_owner(player_turn, 3),
                                4: lambda: properties[player_turn.position_property].buy_with_owner(player_turn, 4),
                                5: lambda: properties[player_turn.position_property].buy_with_owner(player_turn, 5)
                            }
                            result_function = switcher.get(random.randint(buildings_owned + 1, 5))
                            if result_function:
                                result_function()
                        else:
                            print("ma juz hotel bot")

                    else:
                        print("plac bot")
                        bool_loose = player_turn.pay(properties[player_turn.position_property].player_own)
                        if bool_loose:
                            players.remove(player_turn)
                            number_of_active_players = len(players)
                            if number_of_active_players == 1:
                                win = True

            else:
                print("Nie ma wlasciciela bot")
                number_of_place = properties[player_turn.position_property].number
                if number_of_place == 4 or number_of_place == 14 or number_of_place == 18 or number_of_place == 25:
                    properties[player_turn.position_property].buy_without_owner(player_turn, 5)
                else:
                    switcher = {
                        1: lambda: properties[player_turn.position_property].buy_without_owner(player_turn, 1),
                        2: lambda: properties[player_turn.position_property].buy_without_owner(player_turn, 2),
                        3: lambda: properties[player_turn.position_property].buy_without_owner(player_turn, 3),
                        4: lambda: properties[player_turn.position_property].buy_without_owner(player_turn, 4),
                        5: lambda: properties[player_turn.position_property].buy_without_owner(player_turn, 5),
                    }

                    result_function = switcher.get(random.randint(1, 5))
                    if result_function:
                        result_function()
            turn = (turn % number_of_active_players) + 1

            pygame.time.delay(2000)

    else:
        if win or loose:
            if loose:
                loose = Text("PRZEGRAŁEŚ!", BLACK, WIDTH // 2, HEIGHT // 2, 36, None)
                loose.draw(screen)
                pygame.time.delay(5000)
                window_open = False
            else:
                win = Text("WYGRAŁEŚ!", BLACK, WIDTH // 2, HEIGHT // 2, 36, None)
                win.draw(screen)
                pygame.time.delay(5000)
                window_open = False
        else:

            if start_button.rect.collidepoint(pygame.mouse.get_pos()):
                start_button.text.color = WHITE
                start_button.background_color = GRAY
            else:
                start_button.text.color = WHITE
                start_button.background_color = GRAY
            if quit_button.rect.collidepoint(pygame.mouse.get_pos()):
                quit_button.text.color = WHITE
                quit_button.background_color = GRAY
            else:
                quit_button.text.color = WHITE
                quit_button.background_color = GRAY
            start_button.draw(screen)
            quit_button.draw(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
