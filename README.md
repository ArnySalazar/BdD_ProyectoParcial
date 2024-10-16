# Juego del Laberinto

Este proyecto es una implementación inspirada en **TwitchPlaysPokémon**, donde múltiples usuarios pueden votar para decidir las acciones de un personaje en un juego de laberinto. Los votos se registran en una base de datos, y el juego se actualiza en tiempo real según los comandos ganadores.

## Características

- **Modo Jugador**: Un jugador controla el personaje directamente.
- **Modo Espectador**: Los espectadores pueden votar por los movimientos del personaje.
- **Votación en Tiempo Real**: Los comandos de movimiento se votan y el comando ganador se ejecuta tras un intervalo de tiempo.
- **Interfaz Gráfica**: El juego utiliza Pygame para renderizar el laberinto y el movimiento del personaje.

## Tecnologías Utilizadas

- **Python 3**
- **Pygame**: Para el renderizado gráfico del juego.
- **Tkinter**: Para la interfaz de votación.
- **MySQL (Pymysql)**: Para gestionar las votaciones y almacenar los resultados en la base de datos.

## Instalación

1. Clona este repositorio en tu máquina local:
   ```bash
   git clone https://github.com/tu_usuario/twitch-plays-maze-game.git
   cd twitch-plays-maze-game
