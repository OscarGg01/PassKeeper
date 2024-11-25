# gui.py
import tkinter as tk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
from src.database.database import agregar_contraseña, obtener_contraseñas, editar_contraseña, borrar_contraseña, obtener_historial, exportar_a_excel, importar_desde_excel
from src.logica.utils import copiar_al_portapapeles
from src.logica.security import desencriptar_contraseña
import random
import string
import pyperclip

#Si es necesario actaulizar pip: python.exe -m pip install --upgrade pip
# Instalar pillow para las imágenes
# Instalar openpyxl para exportar e importar
# Importar datetime
# Importar pandas

BG_COLOR = "#013161"
BTN_COLOR = {"Agregar": "#DAF7A6", "Ver": "#FFC300", "Historial": "#FF5733", "Exportar": "#C70039", "Importar": "#900C3F", "Salir": "#581845"}
FONT = ("Century Gothic", 10)

def centrar_ventana(ventana, ancho, alto):
    screen_width = ventana.winfo_screenwidth()
    screen_height = ventana.winfo_screenheight()
    x = (screen_width - ancho) // 2
    y = (screen_height - alto) // 2
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")
    ventana.resizable(False, False)

def generar_contraseña_aleatoria():
    longitud = 15
    caracteres = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(caracteres) for _ in range(longitud))

def ventana_principal():
    root = tk.Tk()
    root.title("Gestión de Contraseñas")
    root.geometry("600x500")
    centrar_ventana(root, 600, 500)
    root.config(bg="#013161")  # Cambiar el color de fondo

    try:
        imagen = Image.open("D:\\Proyectos\\PassKeeper\\seguridad.png")  # Cambia "seguridad.png" a la ruta correcta de tu imagen
        logo_img = ImageTk.PhotoImage(imagen)
        logo_label = tk.Label(root, image=logo_img, bg="#013161")  # Ajusta el color de fondo
        logo_label.pack(pady=10)
    except Exception as e:
        print(f"Error al cargar la imagen: {e}")

    def exportar():
        archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")])

        if archivo:
            exportar_a_excel(archivo)
            messagebox.showinfo("Éxito", f"Contraseñas exportadas a {archivo} correctamente.")

    # Función para importar contraseñas desde Excel
    def importar():
        archivo = filedialog.askopenfilename(
            filetypes=[("Excel Files", "*.xlsx"), ("All Files", "*.*")]
        )
        if archivo:
            importar_desde_excel(archivo)
            messagebox.showinfo("Éxito", f"Contraseñas importadas desde {archivo} correctamente.")

    botones = [
        ("Agregar Contraseña", ventana_agregar_contraseña, "Agregar"),
        ("Ver Contraseñas", ventana_ver_contraseñas, "Ver"),
        ("Ver Historial", ventana_historial, "Historial"),
        ("Exportar", exportar, "Exportar"),
        ("Importar", importar, "Importar"),
        ("Salir", root.quit, "Salir"),
    ]
    for texto, comando, tipo in botones:
        tk.Button(root, text=texto, command=comando, bg=BTN_COLOR[tipo], fg="black", font=FONT).pack(pady=10)

    root.mainloop()

def ventana_historial():
    ventana = tk.Toplevel()
    ventana.title("Historial de Contraseñas")
    centrar_ventana(ventana, 600, 700)

    tk.Label(ventana, text="Historial de acciones en contraseñas:").pack(pady=5)

    historial = obtener_historial()
    if historial:
        for cuenta, accion, fecha_hora in historial:
            tk.Label(ventana, text=f"Cuenta: {cuenta}, Acción: {accion}, Fecha y Hora: {fecha_hora}").pack()
    else:
        tk.Label(ventana, text="No hay registros en el historial.").pack()

def ventana_agregar_contraseña():
    ventana = tk.Toplevel()
    ventana.title("Agregar Contraseña")
    centrar_ventana(ventana, 400, 350)
    tk.Label(ventana, text="Cuenta:").pack()
    cuenta_entry = tk.Entry(ventana, width=30)
    cuenta_entry.pack()

    tk.Label(ventana, text="Contraseña:").pack()
    contraseña_entry = tk.Entry(ventana, show="*", width=30)
    contraseña_entry.pack()

    tk.Label(ventana, text="Categoría:").pack()
    categoria_entry = tk.Entry(ventana, width=30)
    categoria_entry.pack()

    def copiar_contraseña_aleatoria():
        contraseña_generada = generar_contraseña_aleatoria()
        contraseña_entry.delete(0, tk.END)
        contraseña_entry.insert(0, contraseña_generada)
        pyperclip.copy(contraseña_generada)

    def guardar_contraseña():
        cuenta = cuenta_entry.get()
        contraseña = contraseña_entry.get()
        categoria = categoria_entry.get()

        if len(contraseña) < 8:
            messagebox.showerror("Error", "La contraseña no es fuerte. Debe tener al menos 8 caracteres.")
            return

        agregar_contraseña(cuenta, contraseña, categoria)
        messagebox.showinfo("Éxito", "Contraseña guardada.")
        ventana.destroy()

    tk.Button(ventana, text="Guardar", command=guardar_contraseña).pack(pady=10)
    tk.Button(ventana, text="Generar Contraseña Aleatoria", command=copiar_contraseña_aleatoria).pack(pady=5)

def ventana_ver_contraseñas():
    ventana = tk.Toplevel()
    ventana.title("Ver Contraseñas")
    centrar_ventana(ventana, 500, 400)

    tk.Label(ventana, text="Contraseñas almacenadas:").pack(pady=5)

    lista_frame = tk.Frame(ventana)
    lista_frame.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(lista_frame)
    scrollbar.pack(side="right", fill="y")

    lista_contraseñas = tk.Listbox(lista_frame, yscrollcommand=scrollbar.set, selectmode="single", width=80)
    lista_contraseñas.pack(fill="both", expand=True)
    scrollbar.config(command=lista_contraseñas.yview)

    contraseñas = obtener_contraseñas()

    def mostrar_contraseñas(lista):
        lista_contraseñas.delete(0, tk.END)
        for cuenta, _, categoria in lista:
            lista_contraseñas.insert(tk.END, f"Cuenta: {cuenta} | Categoría: {categoria}")

    mostrar_contraseñas(contraseñas)

    def actualizar_lista():
        contraseñas_actualizadas = obtener_contraseñas()
        mostrar_contraseñas(contraseñas_actualizadas)

    def ordenar_por_categoria():
        contraseñas_ordenadas = sorted(contraseñas, key=lambda x: x[2])
        mostrar_contraseñas(contraseñas_ordenadas)

    def copiar_contraseña():
        seleccion = lista_contraseñas.curselection()
        if seleccion:
            cuenta = contraseñas[seleccion[0]][0]
            contraseña_encriptada = contraseñas[seleccion[0]][1]

            try:
                from src.logica.security import desencriptar_contraseña  # Asegúrate de importar la función desencriptar_contraseña
                contraseña_desencriptada = desencriptar_contraseña(contraseña_encriptada)  # Desencripta la contraseña
                copiar_al_portapapeles(contraseña_desencriptada)  # Copia la contraseña desencriptada al portapapeles
                messagebox.showinfo("Copiado", f"Contraseña de '{cuenta}' copiada al portapapeles.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo copiar la contraseña: {e}")
        else:
            messagebox.showwarning("Selección", "Por favor, selecciona una cuenta para copiar la contraseña.")

    
    def editar_seleccion():
        seleccion = lista_contraseñas.curselection()
        if seleccion:
            cuenta = contraseñas[seleccion[0]][0]
            ventana_editar_contraseña(cuenta)
        else:
            messagebox.showwarning("Selección", "Por favor, selecciona una cuenta para editar.")

    def borrar_seleccion():
        seleccion = lista_contraseñas.curselection()
        if seleccion:
            cuenta = contraseñas[seleccion[0]][0]
            if messagebox.askyesno("Confirmación", f"¿Seguro que deseas borrar la contraseña para '{cuenta}'?"):
                borrar_contraseña(cuenta)
                lista_contraseñas.delete(seleccion)
                messagebox.showinfo("Éxito", f"Contraseña de '{cuenta}' eliminada.")
        else:
            messagebox.showwarning("Selección", "Por favor, selecciona una cuenta para borrar.")

    def importar_y_actualizar():
        importar_desde_excel(actualizar_lista=actualizar_lista)

    tk.Button(ventana, text="Ordenar por Categoría", command=ordenar_por_categoria).pack(pady=5)
    tk.Button(ventana, text="Copiar Contraseña", command=copiar_contraseña).pack(pady=5)
    tk.Button(ventana, text="Editar Cuenta", command=editar_seleccion).pack(pady=5)
    tk.Button(ventana, text="Borrar Cuenta", command=borrar_seleccion).pack(pady=5)
    ventana.mainloop()

def ventana_editar_contraseña(cuenta):
    ventana = tk.Toplevel()
    ventana.title(f"Editar Contraseña: {cuenta}")
    centrar_ventana(ventana, 200, 150)

    tk.Label(ventana, text="Nueva Contraseña:").pack()
    nueva_contraseña_entry = tk.Entry(ventana, show="*", width=30)
    nueva_contraseña_entry.pack(pady=5)

    def guardar_cambios():
        nueva_contraseña = nueva_contraseña_entry.get()
        if len(nueva_contraseña) < 8:
            messagebox.showerror("Error", "La contraseña no es fuerte. Debe tener por lo menos 8 caracteres.")
            return
        editar_contraseña(cuenta, nueva_contraseña)
        messagebox.showinfo("Éxito", "Contraseña actualizada.")
        ventana.destroy()

    tk.Button(ventana, text="Guardar Cambios", command=guardar_cambios).pack(pady=10)
