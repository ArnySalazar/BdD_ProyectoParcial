import pygame
import pymysql
from pymysql import Error
import sys
from tkinter import *
from conexion import crear_conexion
from flechas_votacion import votar, lock_table_votos, contar_y_registrar_resultado, unlock_table_votos,limpiar_votos
import threading
from datetime import datetime
import time

id_usuario=None
id_game=42
screen_width = 400
screen_height = 400
screen =None
page = None
move_direction=None
modo_jugador=False

votacion_activa=False
tiempo_voto = 20  # Duración de votación
interval = 20000  # 20 segundos
tiempo_inicio_votacion = None
inicio_partida_esclavo=None

# Colores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)

class Intro:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.imgLogo = pygame.image.load("Version9\Version9\hogwarts.jpg")

        # Definir los colores
        self.white = (255, 255, 255)
        self.yellow = (255, 237, 146)
        self.black = (0, 0, 0)

        # Definir fuente
        self.font = pygame.font.Font('Version9\Version9\OverpassMono-SemiBold.ttf', 30)

        # Definir rectángulos para los botones
        self.jugador_button = pygame.Rect((self.screen.get_width() // 2) - 150, 120, 300, 50)
        self.espectador_button = pygame.Rect((self.screen.get_width() // 2) - 150, 200, 300, 50)
        self.quit_button = pygame.Rect((self.screen.get_width() // 2) - 150, 280,300, 50)

    def draw_text(self, text, font, color, rect):
        """Función para dibujar texto en los botones."""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def bucle(self, events:list):
        global page, modo_jugador
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if self.jugador_button.collidepoint(mouse_pos):
                    page = 1  # Cambia a la siguiente página/juego
                    modo_jugador = True  # Establece el modo jugador
                    tkinter_thread = threading.Thread(target=tkinter_controls)
                    tkinter_thread.start()
                if self.espectador_button.collidepoint(mouse_pos):
                    page = 1  # Cambia a la siguiente página/juego
                    modo_jugador = False  # Modo espectador
                if self.quit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        width, height = self.screen.get_size()
        img_logo_copy = pygame.transform.scale(self.imgLogo, (height,height))
        self.screen.blit(img_logo_copy, (0,0))

        # Dibujar los botones
        pygame.draw.rect(self.screen,
                         self.yellow if self.jugador_button.collidepoint(pygame.mouse.get_pos()) else self.white,
                         self.jugador_button)
        pygame.draw.rect(self.screen,
                         self.yellow if self.espectador_button.collidepoint(pygame.mouse.get_pos()) else self.white,
                         self.espectador_button)
        pygame.draw.rect(self.screen,
                         self.yellow if self.quit_button.collidepoint(pygame.mouse.get_pos()) else self.white,
                         self.quit_button)

        # Dibujar texto en los botones
        self.draw_text("Modo Jugador", self.font, self.black, self.jugador_button)
        self.draw_text("Modo Espectador", self.font, self.black, self.espectador_button)
        self.draw_text("Salir", self.font, self.black, self.quit_button)

        pygame.display.flip()

class MazeGame:
    def __init__(self):
        self.screen=pygame.display.get_surface()
        self.current_level=1
        self.maze=self.cargar_maze(self.current_level)
        #Definir el tamaño del bloque y velocidad
        self.block_size = 20
        self.player_speed = self.block_size
        self.player_pos=[self.block_size, self.block_size]
        self.player_image = pygame.image.load("Version9\Version9\playerH.png")  # Cargar la imagen
        # Escalar la imagen al tamaño del bloque si es necesario
        self.player_image_scale = pygame.transform.scale(self.player_image, (self.block_size, self.block_size))

        # Definir datos para el temporizador
        self.time_left = 50  # segundos
        self.start_time = pygame.time.get_ticks()
        self.game_started = False  # Indica si el juego ha comenzado
        self.guardado=False

    def cargar_maze(self,level):
        # Definir el laberinto (1 = pared, 0 = camino, 2 = meta)
        if level==1:
            return [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
            [1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1],
            [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 2, 1],  # '2' es la meta
            [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]
        return []

    def next_level(self):
        self.current_level += 1
        self.update_game(level=self.current_level)
        self.maze = self.cargar_maze(self.current_level)
        self.player_pos=[self.block_size, self.block_size] # Definir el jugador (un punto)

    # Función para dibujar el laberinto
    def draw_maze(self):
        for row in range(len(self.maze)):
            for col in range(len(self.maze[0])):
                if self.maze[row][col] == 1:
                    pygame.draw.rect(self.screen, BLUE, (col * self.block_size, row * self.block_size, self.block_size, self.block_size))
                elif self.maze[row][col] == 2:
                    pygame.draw.rect(self.screen, GREEN, (col * self.block_size, row * self.block_size, self.block_size, self.block_size))

    # Función para dibujar al jugador
    def draw_player(self):
        pygame.draw.rect(self.screen, RED, (self.player_pos[0], self.player_pos[1], self.block_size, self.block_size))

    # Función para verificar si el movimiento es válido
    def is_valid_move(self,x, y):
        row = y // self.block_size
        col = x // self.block_size
        if self.maze[row][col] == 0 or self.maze[row][col] == 2:  # Permite moverse al camino y a la meta
            return True
        return False

    # Función para verificar si el jugador ha ganado
    def check_win(self):
        row = self.player_pos[1] // self.block_size
        col = self.player_pos[0] // self.block_size
        if self.maze[row][col] == 2:  # Si llega a la meta
            return True
        return False

    def comprobar_partida(self,id_partida):
        connection = crear_conexion()
        if connection:
            try:
                cursor = connection.cursor()
                # Consulta para verificar si la partida ya existe
                cursor.execute("SELECT * FROM juego WHERE id_partida = %s", (id_partida,))
                partida = cursor.fetchone()
                if partida:
                    return True
                else:
                    return False
            except Error as e:
                print(f"Error al comprobar partida: {e}")

    def recuperar_juego(self, id_partida):
        connection = crear_conexion()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT pos_x, pos_y, nivel FROM juego WHERE id_partida = %s", (id_partida,))
                row = cursor.fetchone()
                if row:
                    return row
                else:
                    return None
            except Error as e:
                print(f"Error al recuperar la partida: {e}")

    def guardar_juego(self,id_user, inicio, pos_x, pos_y, level, terminado):
        global id_game
        connection = crear_conexion()
        if connection:
            try:
                cursor = connection.cursor()
                # Guarda los datos del juego
                cursor.execute(
                    "INSERT INTO juego (id_user, inicio_partida, pos_x, pos_y, nivel,terminado) VALUES (%s, %s, %s, %s, %s, %s)",
                    (id_user, inicio, pos_x, pos_y, level, terminado))
                connection.commit()

                # Obtener el ID del juego recién insertado
                id_game = cursor.lastrowid

                cursor.close()
                print("Se guardaron correctamente los datos iniciales del juego")
                return True
            except Error as e:
                print(f"Error al guardar el juego: {e}")

    def update_game(self, pos_x=-1, pos_y=-1, level=-1, terminado=""):
        connection = crear_conexion()
        # Actualizar posicion X
        if pos_x!=-1:
            if connection:
                try:
                    cursor = connection.cursor()
                    # Guarda los datos del juego
                    cursor.execute(
                        "UPDATE juego SET pos_x=%s WHERE id_partida=%s",(pos_x, id_game)
                    )
                    connection.commit()
                    cursor.close()
                    print("Se actualizo la posición X del juego")
                except Error as e:
                    print(f"Error al actualizar el juego: {e}")
        #actualizar posición Y
        if pos_y!=-1:
            if connection:
                try:
                    cursor = connection.cursor()
                    # Guarda los datos del juego
                    cursor.execute(
                        "UPDATE juego SET pos_y=%s WHERE id_partida=%s", (pos_y, id_game)
                    )
                    connection.commit()
                    cursor.close()
                    print("Se actualizo la posición Y del juego")
                except Error as e:
                    print(f"Error al actualizar el juego: {e}")
        # Actualizar nivel
        if level!=-1:
            if connection:
                try:
                    cursor = connection.cursor()
                    # Guarda los datos del juego
                    cursor.execute(
                        "UPDATE juego SET nivel=%s WHERE id_partida=%s", (level, id_game)
                    )
                    connection.commit()
                    cursor.close()
                    print("Se actualizo el nivel del juego")
                except Error as e:
                    print(f"Error al actualizar el juego: {e}")
        #Actualizar si el juego ha terminado
        if terminado!="":
            if connection:
                try:
                    cursor = connection.cursor()
                    # Guarda los datos del juego
                    cursor.execute(
                        "UPDATE juego SET terminado=%s WHERE id_partida=%s", (terminado, id_game)
                    )
                    connection.commit()
                    cursor.close()
                    print("Se actualizo el estado del juego")
                except Error as e:
                    print(f"Error al actualizar el juego: {e}")

    def bucle(self, events):
        # Lógica para la pantalla del juego
        screen.fill(WHITE)
        self.draw_maze()
        self.draw_player()
        #Si el juego ha iniciado

        inicio=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #Inicio de la partida
        if id_usuario and self.guardado==False:
            # Comprobamos si se quiere guardar nueva partida o se quiere recuperar una existente
            existe_partida= self.comprobar_partida(id_game)
            if existe_partida:
                #Recuperamos partida
                partida_recuperada=self.recuperar_juego(id_game)
                if partida_recuperada:
                    # si se obtienen correctamente los datos de la base
                    self.player_pos[0] = int(partida_recuperada[0])
                    self.player_pos[1] = int(partida_recuperada[1])
                    self.current_level = int(partida_recuperada[2])
                    self.guardado=True
            else:
                #Guardamos nueva partida
                self.guardado=self.guardar_juego(id_usuario,inicio,self.player_pos[0],self.player_pos[1],self.current_level, 'No')
                # Comprobamos si hay una votacion abierta

        tiempo_restante = (pygame.time.get_ticks() - self.start_time) / 1000
        self.time_left = 210 - int(tiempo_restante)

        font = pygame.font.Font(None, 30)
        time_text = font.render(f"Tiempo: {self.time_left}", True, BLACK)
        screen.blit(time_text, (6, 6))

        if self.time_left <= 0:
            self.update_game(terminado="Si")
            font = pygame.font.Font('Version9\Version9\OverpassMono-Regular.ttf', 50)
            game_over_text = font.render("Game Over", True, RED)
            screen.blit(game_over_text, (screen_width // 2 - 80, screen_height // 2))
            pygame.display.flip()
            pygame.time.wait(2000)
            pygame.quit()
            sys.exit()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                global page
                page = 0  # Regresar a login


def actualizar_juego():
    global move_direction
    conexion = crear_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT comando_ganador FROM resultados ORDER BY ID_resultado DESC LIMIT 1;")
                resultado = cursor.fetchone()
                print("obtener de tabla resultados: ", resultado[0])
                move_direction = resultado[0]
        except pymysql.MySQLError as e:
            print(f"Error al obtener resultado: {e}")
        finally:
            conexion.close()

# Voting timer and reset mechanism
def iniciar_votacion(id_usuario,label_tiempo):
    global votacion_activa, tiempo_inicio_votacion, user_id
    user_id=id_usuario

    votacion_activa = True
    tiempo_inicio_votacion = datetime.now()
    print(tiempo_inicio_votacion)
    # actualizar la tabla votacion
    connection = crear_conexion()
    if connection:
        try:
            cursor = connection.cursor()
            # Consulta para verificar si la partida ya existe
            cursor.execute("UPDATE votacion SET inicio_votacion = %s WHERE id_votacion=1", (tiempo_inicio_votacion,))
            connection.commit()
        except Error as e:
            print(f"Error al actualizar votacion: {e}")
    # Como actualizo el countdown para el esclavo
    countdown(20, label_tiempo)
    print("Inicia la votación. Los usuarios tienen 20 segundos para votar.")

    time.sleep(tiempo_voto)
    votacion_activa = False
    print("Tiempo de votación finalizado. Contando votos...")
    lock_table_votos()
    result=contar_y_registrar_resultado()
    if result:
        actualizar_juego()
    unlock_table_votos()
    limpiar_votos()
    reset_votacion(id_usuario, label_tiempo)

def reset_votacion(id_user, label_tiempo):
    print("Preparando la próxima votación...")
    time.sleep(5)
    iniciar_votacion(id_user, label_tiempo)

# Función de cuenta regresiva
def countdown(time_remaining, label):
    global votacion_activa
    if time_remaining > 0:
        label.config(text=f"Tiempo restante:\n{time_remaining} segundos")
        label.after(1000, countdown, time_remaining - 1, label)
    else:
        label.config(text="¡Votación finalizada!")
        votacion_activa=False
        if id_usuario!=1:
            actualizar_juego()
            label.after(11000, restart_voting, label)

def restart_voting(label):
    global votacion_activa
    votacion_activa = True  # Cambia el estado de votación activa
    countdown(20, label)  # Reinicia el temporizador de 20 segundos

def iniciar_countdown(label, tiempo_esclavo):
    global votacion_activa, inicio_partida_esclavo
    tiempo_restante = obtener_tiempo_restante(tiempo_esclavo)
    if tiempo_restante is not None:
        votacion_activa=True
        inicio_partida_esclavo=tiempo_restante
        countdown(tiempo_restante, label)
    else:
        label.config(text="Votación no activa.")
        time.sleep(11)
        if id_usuario!=1:
            votacion_activa = True
            countdown(20, label)

def obtener_tiempo_restante(tiempo_esclavo):
    conexion = crear_conexion()
    if conexion:
        try:
            with conexion.cursor() as cursor:
                cursor.execute("SELECT inicio_votacion FROM votacion WHERE id_votacion = 1")
                resultado = cursor.fetchone()
                if resultado:
                    tiempo_inicio = resultado[0]
                    tiempo_transcurrido = (tiempo_esclavo - tiempo_inicio).total_seconds()
                    tiempo_restante = tiempo_voto - tiempo_transcurrido
                    return max(0, int(tiempo_restante))  # No puede ser negativo
                else:
                    return None
        except pymysql.MySQLError as e:
            print(f"Error al obtener el tiempo restante: {e}")
        finally:
            conexion.close()
    return None

maze_game = MazeGame()

# Panel de flechas para votación
def tkinter_controls():
    ventana = Tk()
    ventana.title("Votación del Juego")
    ventana.geometry("200x200")

    # Etiqueta para mostrar el temporizador
    label_tiempo = Label(ventana, text="Tiempo restante de votación: 20 segundos", font=("Helvetica", 12), wraplength=200)
    label_tiempo.pack(pady=10)

    btn_up = Button(ventana, text="↑", command=lambda: votar('up',id_usuario, votacion_activa), width=5, height=2)
    btn_up.pack(side=TOP, pady=5)

    btn_down = Button(ventana, text="↓", command=lambda: votar('down',id_usuario, votacion_activa), width=5, height=2)
    btn_down.pack(side=BOTTOM, pady=5)

    btn_left = Button(ventana, text="←", command=lambda: votar('left',id_usuario, votacion_activa), width=5, height=2)
    btn_left.pack(side=LEFT, padx=5)

    btn_right = Button(ventana, text="→", command=lambda: votar('right',id_usuario, votacion_activa), width=5, height=2)
    btn_right.pack(side=RIGHT, padx=5)

    # verifica que el juego continue
    if id_usuario==1:
        threading.Thread(target=iniciar_votacion, args=(id_usuario, label_tiempo)).start()
    else:
        tiempo_esclavo=datetime.now()
        iniciar_countdown(label_tiempo,tiempo_esclavo)
    ventana.mainloop()


start_time = pygame.time.get_ticks()

def main_game(user_id):
    global screen, page, id_usuario, move_direction
    id_usuario=user_id
    pygame.init()

    screen=pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Juego de Laberinto")

    intro, game = Intro(), MazeGame()
    pages = [intro, game]

    # Bucle del juego
    clock = pygame.time.Clock()
    win = False
    page = 0
    running = True

    while running:
        events = pygame.event.get()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if not modo_jugador:
            current_time = pygame.time.get_ticks()
            # Verifica si han pasado 20 segundos
            print(game.start_time)
            if current_time - game.start_time >= interval:
                actualizar_juego() # Llama a la función
                game.start_time = current_time  # Reinicia el temporizador

        if not win:
            # Obtener el movimiento ganador de move_direction
            if move_direction=='left' or move_direction==3:
                new_x = game.player_pos[0] - game.player_speed
                if game.is_valid_move(new_x, game.player_pos[1]):
                    game.player_pos[0] = new_x
                    # Actualizar posición X en base de datos
                    if id_usuario == 1:
                        game.update_game(pos_x=new_x)
            if move_direction=='right' or move_direction==4:
                new_x = game.player_pos[0] + game.player_speed
                if game.is_valid_move(new_x, game.player_pos[1]):
                    game.player_pos[0] = new_x
                    # Actualizar posición X en base de datos
                    if id_usuario == 1:
                        game.update_game(pos_x=new_x)
            if move_direction=='up' or move_direction==1:
                new_y = game.player_pos[1] - game.player_speed
                if game.is_valid_move(game.player_pos[0], new_y):
                    game.player_pos[1] = new_y
                    # Actualizar posición Y en base de datos
                    if id_usuario == 1:
                        game.update_game(pos_y=new_y)
            if move_direction=='down' or move_direction==2:
                new_y = game.player_pos[1] + game.player_speed
                if game.is_valid_move(game.player_pos[0], new_y):
                    game.player_pos[1] = new_y
                    # Actualizar posición y en base de datos
                    if id_usuario==1:
                        game.update_game(pos_y=new_y)

            move_direction = None
            # Verificar si el jugador ganó
            if game.check_win():
                win = True
        else:
            # Mostrar mensaje de ganaste
            font = pygame.font.Font('OverpassMono-Regular.ttf', 40)
            text = font.render("¡Ganaste!", True, BLACK)
            screen.blit(text, (100, 150))
            # Salir de pygame
            pygame.quit()
            sys.exit()

        # Actualizar la pantalla
        pages[page].bucle(events)
        pygame.display.flip()
        clock.tick(10)