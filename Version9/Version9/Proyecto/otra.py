import pygame as pg
import pygame_menu as pgm
from random import randrange, choice
import threading
from tkinter import *

pg.init()
H = pg.display.Info().current_h
W = pg.display.Info().current_w
CLOCK = pg.time.Clock()

pg.display.set_mode((W//2,H//2), pg.RESIZABLE) 
pg.display.set_caption("Proyecto")

listColorName = ["Azul", "Azul Oscuro", "Amarillo", "Blanco", "Celeste", "Colmena 1", "Colmena 2", "Colmena 3", "Gris", "Rosado", "Rojo", "Morado", "Negro", "Naranja", "Verde Oscuro", "Verde"]
listColor = ["#0079B0", "#003AB0", "#EBF41C","#FFFFFF", "#00BEBF", "#F4BE2E", "#35AEDC", "#047732", "#808080", "#FF63A8", "#952121", "#7E228A", "#000000", "#FF8614","#10BD3E","#01DF3C"]
configColors = {
    "marco": "#FFFFFF",
    "background": "#000000",
    "head": "#10BD3E",
    "body": "#01DF3C",
    "head2": "#F4BE2E",
    "body2": "#EBF41C",
    "food": "#952121",
    "ui": "#FFFFFF",
}
configNumbers = {
    "dimention": 25,
    "numManzanas": 1,
    "longManzana": 1,
    "speed": 250,
    "multiSnake": False,
}

move_direction = None

# Funciones para mover desde Tkinter
def move_up():
    global move_direction
    move_direction = "UP"

def move_down():
    global move_direction
    move_direction = "DOWN"

def move_left():
    global move_direction
    move_direction = "LEFT"

def move_right():
    global move_direction
    move_direction = "RIGHT"

# Función para iniciar la interfaz de Tkinter
def tkinter_controls():
    ventana = Tk()
    ventana.title("Control del juego")
    ventana.geometry("400x200")

    # Botones de dirección
    btn_up = Button(ventana, text="↑", command=move_up, width=5, height=2)
    btn_up.pack(side=TOP, pady=5)

    btn_down = Button(ventana, text="↓", command=move_down, width=5, height=2)
    btn_down.pack(side=BOTTOM, pady=5)

    btn_left = Button(ventana, text="←", command=move_left, width=5, height=2)
    btn_left.pack(side=LEFT, padx=5)

    btn_right = Button(ventana, text="→", command=move_right, width=5, height=2)
    btn_right.pack(side=RIGHT, padx=5)

    ventana.mainloop()

class Intro():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.alpha = -5
        self.imgLogo = pg.image.load("Proyecto/images/logo.png")
        
    def bucle(self, events:list):
        global page
        for event in events:
            if event.type == pg.KEYDOWN: page = 1

        self.screen.fill("#000000")
        width, height = self.screen.get_size()

        imgLogo_copy = self.imgLogo.copy()
        imgLogo_copy = pg.transform.scale(imgLogo_copy, (height,height))
        imgSize = imgLogo_copy.get_size()
        imgLogo_copy.set_alpha(self.alpha)
        self.screen.blit(imgLogo_copy, ((width-imgSize[0])/2,0))
        self.alpha += 1

        if self.alpha > 155:
            page = 1

class Start():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.multi = False
        sound = pgm.sound.Sound()
        sound.load_example_sounds()
        self.imgWin = pg.image.load("Proyecto/images/win.png")

        mytheme = pgm.Theme()
        mytheme.title_bar_style = pgm.widgets.MENUBAR_STYLE_SIMPLE
        mytheme.widget_font_color = "#70888C"
        mytheme.selection_color = "#6E2A48"
        mytheme.background_color = "#DAEBEE"
        mytheme.title_font_color = "#DAEBEE"
        mytheme.title_background_color = "#6E2A48"

        screenW, screenH = self.screen.get_size()
        self.menuColors = pgm.pygame_menu.Menu('Colores', screenW, screenH,theme=mytheme, center_content=True)
        self.menuColors.set_sound(sound, False)
        
        def changeColor(*args, **kwargs):
            configColors.update({kwargs["kwargs"]: listColor[args[0][1]]})
        
        self.menuColors.add.dropselect('Marco = ', items=[(i, "") for i in listColorName], default=listColor.index(configColors["marco"]) ,onchange=changeColor, kwargs="marco", font_color="#375D64")
        self.menuColors.add.dropselect('Texto = ', items=[(i, "") for i in listColorName], default=listColor.index(configColors["ui"]) ,onchange=changeColor, kwargs="ui", font_color="#56929D")
        self.menuColors.add.dropselect('Fondo = ', items=[(i, "") for i in listColorName], default=listColor.index(configColors["background"]) ,onchange=changeColor, kwargs="background", font_color="#375D64")
        self.menuColors.add.dropselect('Comida = ', items=[(i, "") for i in listColorName], default=listColor.index(configColors["food"]) ,onchange=changeColor, kwargs="food", font_color="#56929D")
        self.menuColors.add.vertical_margin(10)
        self.menuColors.add.label("Jugador")
        self.menuColors.add.dropselect('Cabeza = ', items=[(i, "") for i in listColorName], default=listColor.index(configColors["head"]) ,onchange=changeColor, kwargs="head", font_color="#375D64")
        self.menuColors.add.dropselect('Cuerpo = ', items=[(i, "") for i in listColorName], default=listColor.index(configColors["body"]) ,onchange=changeColor, kwargs="body", font_color="#56929D")

        self.menuNumber = pgm.pygame_menu.Menu('Parametros de juego', screenW, screenH,theme=mytheme, center_content=True)
        self.menuNumber.set_sound(sound, False)
        
        def changeNumber(*args, **kwargs):
            if (num := args[0]) < 2: num = 2
            configNumbers.update({kwargs["kwargs"]: num})
        
        def changeSpeed(*args, **kwargs):
            if (num := args[0]) < 1: num = 1
            num = 1000-num*10
            if (args[0]) == 99: num = 1
            configNumbers.update({"speed": num})

        self.menuNumber.add.text_input('Tamaño del tablero = ', default=str(configNumbers["dimention"]), input_type=pgm.locals.INPUT_INT, maxchar=3, onchange=changeNumber, kwargs="dimention", font_color="#375D64")
        self.menuNumber.add.text_input('Cantidad de comida en pantalla = ', default=str(configNumbers["numManzanas"]), input_type=pgm.locals.INPUT_INT, maxchar=3, onchange=changeNumber, kwargs="numManzanas", font_color="#56929D")
        self.menuNumber.add.text_input('Aumento por comida = ', default=str(configNumbers["longManzana"]), input_type=pgm.locals.INPUT_INT, maxchar=3, onchange=changeNumber, kwargs="longManzana", font_color="#375D64")
        self.menuNumber.add.text_input('Velocidad = ', default=str(100-configNumbers["speed"]//10), input_type=pgm.locals.INPUT_INT, maxchar=2, onchange=changeSpeed, font_color="#56929D")

        self.menu = pgm.pygame_menu.Menu('Configuracion', screenW, screenH,theme=mytheme, columns=1, rows=4, center_content=True)
        self.menu.set_sound(sound, False)
        
        def next(): global page; page = 2
        self.menu.add.button('Iniciar', next, font_color='#467780')
        self.menu.add.button('Parametros de juego', self.menuNumber)
        self.menu.add.button('Colores', self.menuColors)
        self.menu.add.button('Salir', pgm.events.EXIT)
        
    def bucle(self, events:list):
        if self.menu.is_enabled():
            for event in events:
                if event.type == pg.VIDEORESIZE:
                    screenW, screenH = self.screen.get_size()
                    self.menu.resize(screenW, screenH)
                    self.menuColors.resize(screenW, screenH)
                    self.menuNumber.resize(screenW, screenH)
                if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                    self.menu.reset(1)

            if configNumbers["multiSnake"] and not self.multi:
                self.multi = True
                self.menuNumber.add.selector('Multiplayer', items=["N", "S"], default=0, onchange=lambda x, _: configNumbers.update({"multiSnake": True if x[0][1] == "S" else False}))
            self.menu.mainloop(self.screen)

class Game():
    def __init__(self):
        self.screen = pg.display.get_surface()
        self.x = 0
        self.y = 0
        self.manzanas = []
        self.points = 0
        self.snake = [(0, 0)]
        self.running = True
        self.drawFood()
        
    def reset(self):
        self.x = 0
        self.y = 0
        self.points = 0
        self.snake = [(0, 0)]
        self.drawFood()

    def drawFood(self):
        self.manzanas.clear()
        for _ in range(configNumbers["numManzanas"]):
            self.manzanas.append((randrange(0, (W//2)//configNumbers["dimention"]) * configNumbers["dimention"], randrange(0, (H//2)//configNumbers["dimention"]) * configNumbers["dimention"]))

    def checkCollision(self):
        if len(self.snake) > 1:
            if (self.x, self.y) in self.snake[1:]:
                self.running = False
        
        if self.x < 0 or self.x >= W//2 or self.y < 0 or self.y >= H//2:
            self.running = False

    def bucle(self, events:list):
        global move_direction
        for event in events:
            if event.type == pg.QUIT:
                self.running = False

        if move_direction == "UP":
            self.y -= configNumbers["dimention"]
        elif move_direction == "DOWN":
            self.y += configNumbers["dimention"]
        elif move_direction == "LEFT":
            self.x -= configNumbers["dimention"]
        elif move_direction == "RIGHT":
            self.x += configNumbers["dimention"]

        self.checkCollision()

        if (self.x, self.y) in self.manzanas:
            self.points += configNumbers["longManzana"]
            self.manzanas.remove((self.x, self.y))
            self.drawFood()
            self.snake.append((self.x, self.y))
        else:
            self.snake.append((self.x, self.y))
            if len(self.snake) > self.points+1:
                del self.snake[0]

        self.screen.fill(configColors["background"])
        for seg in self.snake:
            pg.draw.rect(self.screen, configColors["body"], pg.Rect(seg[0], seg[1], configNumbers["dimention"], configNumbers["dimention"]))
        for manzana in self.manzanas:
            pg.draw.rect(self.screen, configColors["food"], pg.Rect(manzana[0], manzana[1], configNumbers["dimention"], configNumbers["dimention"]))
        pg.draw.rect(self.screen, configColors["head"], pg.Rect(self.x, self.y, configNumbers["dimention"], configNumbers["dimention"]))

        pg.display.flip()
        CLOCK.tick(1000 // configNumbers["speed"])

def main():
    global page
    page = 0
    intro = Intro()
    start = Start()
    game = Game()

    # Iniciar el hilo para Tkinter
    threading.Thread(target=tkinter_controls, daemon=True).start()

    while True:
        events = pg.event.get()
        if page == 0:
            intro.bucle(events)
        elif page == 1:
            start.bucle(events)
        elif page == 2:
            game.bucle(events)
            if not game.running:
                page = 1
                game.reset()

if __name__ == "__main__":
    main()
