from login import LoginPage
from juego import main_game

if __name__ == "__main__":
    login=LoginPage()
    user_id=login.user_id

    if login.inicio_correcto:
        main_game(user_id)