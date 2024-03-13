import tkinter as tk
from tkinter import messagebox
from threading import Thread
import subprocess

def execute_bot():
    # Función para ejecutar el bot de trading en un hilo separado
    def run_bot():
        # Ejecutar el bot de trading en otro proceso
        subprocess.call(["python", "tradingbot.py"])

    # Crear un hilo para ejecutar el bot de trading
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

def show_message():
    # Función para mostrar un mensaje de confirmación al usuario
    messagebox.showinfo("Bot de Trading", "El bot de trading se ha iniciado.")

def main():
    # Crea y configura la ventana principal de la interfaz de usuario
    root = tk.Tk()
    root.title("Interfaz de Usuario para Bot de Trading")

    # Agrega una etiqueta para mostrar un mensaje de bienvenida
    welcome_label = tk.Label(root, text="¡Bienvenido a la Interfaz de Usuario para el Bot de Trading!")
    welcome_label.pack(pady=10)

    # Agrega un botón para iniciar el bot de trading
    start_button = tk.Button(root, text="Iniciar Bot", command=lambda: [execute_bot(), show_message()])
    start_button.pack(pady=5)

    # Agrega un botón para salir de la aplicación
    exit_button = tk.Button(root, text="Salir", command=root.quit)
    exit_button.pack(pady=5)

    # Inicia el bucle principal de la interfaz de usuario
    root.mainloop()

if __name__ == "__main__":
    main()
