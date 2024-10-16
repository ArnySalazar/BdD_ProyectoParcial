import pygame
import time
import random
import threading
from tkinter import *

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

snake_speed = 10

# Window size
window_x = 720
window_y = 480

# Defining colors
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)

# Initialising pygame
pygame.init()

# Initialise game window
pygame.display.set_caption('Proyecto Game')
game_window = pygame.display.set_mode((window_x, window_y))

# FPS (frames per second) controller
fps = pygame.time.Clock()

# Defining snake default position
snake_position = [100, 50]

# Defining first 4 blocks of snake body
snake_body = [[100, 50],
              [90, 50],
              [80, 50],
              [70, 50]
              ]

# Fruit position (se genera desde el inicio)
fruit_position = [random.randrange(1, (window_x // 10)) * 10, 
                  random.randrange(1, (window_y // 10)) * 10]

fruit_spawn = True

# Initial score
score = 0

# Displaying Score function
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    game_window.blit(score_surface, score_rect)

# Game over function
def game_over():
    my_font = pygame.font.SysFont('times new roman', 50)
    game_over_surface = my_font.render('Your Score is : ' + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (window_x / 2, window_y / 4)
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()
    time.sleep(2)
    pygame.quit()
    quit()

# Main Function
if __name__ == "__main__":
    # Iniciar la interfaz de Tkinter en un hilo
    tkinter_thread = threading.Thread(target=tkinter_controls)
    tkinter_thread.start()

    direction = None  # Inicializar dirección como None

    # Mostrar la serpiente y la comida inicialmente
    game_window.fill(black)
    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))
    pygame.display.update()

    while True:
        # Manejar eventos de pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # Actualizar dirección según el botón presionado en Tkinter
        if move_direction:
            if direction is None:  # Solo establece la dirección si es None
                direction = move_direction
            else:
                if move_direction == 'UP' and direction != 'DOWN':
                    direction = 'UP'
                elif move_direction == 'DOWN' and direction != 'UP':
                    direction = 'DOWN'
                elif move_direction == 'LEFT' and direction != 'RIGHT':
                    direction = 'LEFT'
                elif move_direction == 'RIGHT' and direction != 'LEFT':
                    direction = 'RIGHT'

        # Mover la serpiente solo si se ha definido una dirección
        if direction:
            if direction == 'UP':
                snake_position[1] -= 10
            elif direction == 'DOWN':
                snake_position[1] += 10
            elif direction == 'LEFT':
                snake_position[0] -= 10
            elif direction == 'RIGHT':
                snake_position[0] += 10

            # Mecanismo de crecimiento de la serpiente
            snake_body.insert(0, list(snake_position))
            if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
                score += 10
                fruit_spawn = False
            else:
                snake_body.pop()

            if not fruit_spawn:
                fruit_position = [random.randrange(1, (window_x // 10)) * 10, 
                                  random.randrange(1, (window_y // 10)) * 10]

            fruit_spawn = True
            game_window.fill(black)

            for pos in snake_body:
                pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
            pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

            # Solo verificar condiciones de Game Over si la dirección ha sido definida
            if direction: 
                if snake_position[0] < 0 or snake_position[0] > window_x - 10 or snake_position[1] < 0 or snake_position[1] > window_y - 10:
                    game_over()
                
                for block in snake_body[1:]:
                    if snake_position[0] == block[0] and snake_position[1] == block[1]:
                        game_over()

            show_score(1, white, 'times new roman', 20)

            # Refresh game screen
            pygame.display.update()

            # Frame Per Second /Refresh Rate
            fps.tick(snake_speed)