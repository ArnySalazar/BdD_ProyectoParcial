import pymysql
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
from conexion import crear_conexion

# Variables globales
partida_id = 1  # Game ID or session ID

class LoginPage:
    def __init__(self):
        self.root = Tk()
        self.root.title("GameHarryPotter - Login")
        self.root.geometry("580x400")
        self.root.configure(bg="#fff")
        self.root.resizable(False, False)

        # Configura la imagen y los elementos de la interfaz
        self.interfaz()

    def interfaz(self):
        # Carga y redimensiona la imagen
        img = Image.open("Version9\Version9\PotterLogin.png")  # Ruta de la imagen
        img_resized = img.resize((220, 300))
        self.img_tk = ImageTk.PhotoImage(img_resized)

        # Coloca la imagen en la ventana
        Label(self.root, image=self.img_tk, border=0, bg="white").place(x=36, y=42)

        # Crea el frame para el formulario
        frame = Frame(self.root, width=280, height=370, bg='white')
        frame.place(x=290, y=10)

        # Título del formulario
        heading = Label(frame, text="Sign up", fg="#57a1f8", bg="white", font=("Microsoft Yahei UI Light", 23, "bold"))
        heading.place(x=75, y=80)

        # Campo de entrada de usuario
        self.user = Entry(frame, width=25, fg="black", border=0, bg="white", font=("Microsoft Yahei UI Ligth", 11))
        self.user.place(x=40, y=165)

        Frame(frame, width=204, height=2, bg="black").place(x=38, y=185)

        # Botón de login
        Button(frame, width=25, pady=7, text="Login", bg="#57a1f8", fg="white", border=0, command=self.login).place(
            x=49, y=220)

        # Mensaje de creación de cuenta
        label = Label(frame, text="¿No tiene una cuenta?", fg="black", bg="white", font=("MIcrosoft Yahei UI Ligth", 9))
        label.place(x=48, y=272)

        # Botón de registro
        signin = Button(frame, width=6, text="Cree una", border=0, bg="white", cursor="hand2", fg="#57a1f8",
                        command=self.open_register)
        signin.place(x=180, y=272)

        self.inicio_correcto = False
        self.user_id = None
        self.root.mainloop()

    def login(self):
        username = self.user.get().strip()  # Eliminamos espacios en blanco adicionales
        # Verificamos si el campo está vacío o contiene el texto predeterminado
        if not username:
            messagebox.showwarning("Login", "Por favor ingrese un nombre de usuario válido.")
        if username:
            self.verificar_login(username)

    # User login verification
    def verificar_login(self, nombre_usuario):
        conexion = crear_conexion()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    query = "SELECT ID_usuario FROM usuarios WHERE nombre_usuario = %s"
                    cursor.execute(query, (nombre_usuario,))
                    resultado = cursor.fetchone()
                    if resultado:
                        self.user_id = resultado[0]
                        messagebox.showinfo("Login", f"Bienvenido, {nombre_usuario}!")
                        self.root.destroy()
                        self.inicio_correcto = True
                    else:
                        messagebox.showerror("Error", "Usuario no encontrado.")
            except pymysql.MySQLError as e:
                messagebox.showerror("Error", f"Error en el login: {e}")
            finally:
                conexion.close()

    def open_register(self):
        self.root.withdraw()  # Oculta la ventana actual
        register_window = Toplevel(self.root)  # Crea una nueva ventana
        RegisterApp(register_window, self.root)

# GUI for user registration
class RegisterApp:
    def __init__(self, root, main_window):
        self.root = root
        self.main_window = main_window
        self.root.title("GameHarryPotter - Register")
        self.root.geometry("580x400")
        self.root.configure(bg="#fff")
        self.root.resizable(False, False)

        # Configura la imagen y los elementos de la interfaz de registro
        self.interfaz()

    def interfaz(self):
        img = Image.open("Version9\Version9\PotterLogin.png")  # Ruta de la imagen
        img_resized = img.resize((220, 300))
        self.img_tk = ImageTk.PhotoImage(img_resized)

        Label(self.root, image=self.img_tk, border=0, bg="white").place(x=36, y=42)

        frame = Frame(self.root, width=280, height=370, bg='white')
        frame.place(x=290, y=10)

        heading = Label(frame, text="Register", fg="#57a1f8", bg="white", font=("Microsoft Yahei UI Light", 23, "bold"))
        heading.place(x=75, y=80)

        self.new_user = Entry(frame, width=25, fg="black", border=0, bg="white", font=("Microsoft Yahei UI Ligth", 11))
        self.new_user.place(x=40, y=165)

        Frame(frame, width=204, height=2, bg="black").place(x=38, y=185)

        Button(frame, width=25, pady=7, text="Registrar Sesión", bg="#57a1f8", fg="white", border=0,
               command=self.register).place(x=49, y=220)

    def register(self):
        username = self.new_user.get().strip()  # Eliminamos espacios en blanco adicionales
        # Verificamos si el campo está vacío o contiene el texto predeterminado
        if not username:
            messagebox.showwarning("Login", "Por favor ingrese un nombre de usuario válido.")
        if username:
            self.registrar_usuario(username)
            self.root.destroy()  # Cierra la ventana de registro
            self.main_window.deiconify()  # Muestra de nuevo la ventana principal

    # User registration
    def registrar_usuario(self, nombre_usuario):
        conexion = crear_conexion()
        if conexion:
            try:
                with conexion.cursor() as cursor:
                    cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
                    resultado = cursor.fetchone()
                    if resultado:
                        messagebox.showerror("Error", "El usuario ya existe.")
                    else:
                        query = "INSERT INTO usuarios (nombre_usuario) VALUES (%s)"
                        cursor.execute(query, (nombre_usuario,))
                        conexion.commit()
                        messagebox.showinfo("Registro", f"Usuario '{nombre_usuario}' registrado correctamente.")
            except pymysql.MySQLError as e:
                messagebox.showerror("Error", f"Error al registrar el usuario: {e}")
            finally:
                conexion.close()