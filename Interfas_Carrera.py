# ==========================================
# 1. IMPORTACIÓN DE LIBRERÍAS
# ==========================================
import tkinter as tk           # Librería principal para crear la interfaz gráfica (Ventanas, botones, etiquetas)
from tkinter import messagebox # Submódulo de Tkinter para mostrar ventanas emergentes (alertas)
import random                  # Librería nativa para generar números aleatorios (usada para la velocidad de los caballos)
import time                    # Librería nativa para medir el tiempo real (usada para cronometrar a los caballos)

# ==========================================
# 2. DEFINICIÓN DE CLASES (Orientación a Objetos)
# ==========================================
# Aquí definimos la "plantilla" o "molde" para crear cada caballo.
class Caballo:
    def __init__(self, id_caballo, y_pos, ventana, img_caballo):
        # --- Atributos de Identificación y Posición ---
        self.id_caballo = id_caballo  # Número del caballo (0 al 9)
        self.y_pos = y_pos            # Coordenada 'y' fija en el carril
        self.ventana = ventana        # Referencia a la ventana de Tkinter para saber dónde dibujarse
        
        # --- Atributos de Estado de Movimiento ---
        self.x_inicial = 33           # Posición 'x' inicial (Punto de partida)
        self.x = self.x_inicial       # Posición 'x' actual que irá cambiando
        self.direccion = 1            # Dirección: 1 (Hacia adelante/derecha), -1 (Hacia atrás/izquierda)
        self.vueltas_completadas = 0  # Contador de idas y vueltas terminadas
        self.corriendo = False        # Bandera booleana: Indica si el caballo se está moviendo o no
        
        # --- Atributos de Tiempo y Velocidad ---
        self.tiempo_inicio = 0        # Guardará el timestamp (hora exacta) en la que arranca
        self.tiempo_fin = 0           # Guardará el timestamp (hora exacta) en la que cruza la meta
        self.velocidad_actual = random.randint(10, 40) # Genera un intervalo aleatorio inicial
        
        # --- Atributos Gráficos (Objeto Visual) ---
        # Creamos un widget tk.Label que contendrá la imagen del caballo
        self.label = tk.Label(ventana, image=img_caballo, bg="white")
        # Posicionamos la imagen en la pantalla usando .place()
        self.label.place(x=self.x, y=self.y_pos)

    def reiniciar(self):
        #Método para devolver al caballo a sus valores originales, listo para otra carrera.
        self.corriendo = False
        self.x = self.x_inicial
        self.direccion = 1
        self.vueltas_completadas = 0
        # Movemos físicamente la etiqueta de nuevo al inicio
        self.label.place(x=self.x, y=self.y_pos)

    def ciclo_movimiento(self, total_vueltas, slider_tiempo, callback_llegada):
        
        #Método recursivo: Funciona como un bucle "while", pero amigable con Tkinter.
        #Es el temporizador independiente del caballo.
        if not self.corriendo:
            return # Si no está corriendo, aborta la función inmediatamente

        # 1. ACTUALIZAR POSICIÓN FÍSICA
        paso_pixeles = 10 # Cuántos píxeles se mueve por ciclo
        self.x += paso_pixeles * self.direccion # Suma o resta dependiendo de la dirección

        # 2. DETECCIÓN DE BORDES (Rebotes)
        # Si llega a la meta derecha (x >= 800) yendo hacia adelante
        if self.x >= 800 and self.direccion == 1:
            self.direccion = -1 # Invierte la dirección para regresar
            self.velocidad_actual = random.randint(10, 40) # Asigna una nueva velocidad aleatoria al rebotar
        
        # Si llega a la meta izquierda (x <= 33) regresando
        elif self.x <= 33 and self.direccion == -1:
            self.direccion = 1 # Vuelve a mirar hacia adelante
            self.vueltas_completadas += 1 # Cuenta que terminó una ida y vuelta completa
            self.velocidad_actual = random.randint(10, 40) # Asigna una nueva velocidad

        # 3. DIBUJAR EN PANTALLA
        # Actualiza las coordenadas visuales del label
        self.label.place(x=self.x, y=self.y_pos)

        # 4. CONDICIÓN DE VICTORIA O CONTINUIDAD
        # Comprueba si el caballo ya alcanzó el número de vueltas solicitado
        if self.vueltas_completadas >= total_vueltas:
            self.corriendo = False # Detiene el movimiento
            # time.time() obtiene el tiempo actual del sistema en segundos
            self.tiempo_fin = time.time() 
            # Llama a la función 'registrar_llegada' y se envía a sí mismo (self)
            callback_llegada(self) 
        else:
            # 5. EL TEMPORIZADOR (Tk.after)
            # Calcula el tiempo de pausa antes del siguiente movimiento
            factor_slider = slider_tiempo.get() / 100.0 # Obtiene el valor del slider (ej: 100% = 1.0)
            tiempo_espera = int(self.velocidad_actual * factor_slider)
            
            # self.ventana.after(milisegundos, funcion, argumentos...)
            # Le dice a Tkinter que espera X milisegundos y vuelve a ejecutar esta misma función.
            # Es el equivalente a time.sleep() pero sin congelar la ventana gráfica.
            self.ventana.after(tiempo_espera, self.ciclo_movimiento, total_vueltas, slider_tiempo, callback_llegada)

# ==========================================
# 3. LÓGICA PRINCIPAL DEL JUEGO (Controlador)
# ==========================================
# Listas globales para administrar los datos
caballos_lista = []  # Guardará las 10 instancias (objetos) de los caballos
orden_llegada = []   # Guardará los caballos en el orden en que cruzan la meta final

def iniciar_carrera():
    global orden_llegada
    # Prevención de errores: No iniciar si la carrera ya está en curso
    if len(orden_llegada) > 0 and len(orden_llegada) < 10:
        return 
        
    orden_llegada = [] # Vaciamos la tabla de llegadas
    vueltas = int(spin_vueltas.get()) # Extrae el número de vueltas de la interfaz
    
    # time.time() marca el reloj en cero exacto para medir la duración de la carrera
    tiempo_arranque = time.time() 
    
    # Limpia la caja de texto (desde la línea 1.0 hasta el final)
    cuadro_resultados.delete("1.0", tk.END)
    
    # Iteramos sobre los 10 objetos Caballo creados para encenderlos
    for c in caballos_lista:
        c.tiempo_inicio = tiempo_arranque
        c.corriendo = True
        c.velocidad_actual = random.randint(10, 40)
        # Disparamos el temporizador de cada caballo de manera independiente
        c.ciclo_movimiento(vueltas, slider_velocidad, registrar_llegada)

def registrar_llegada(caballo_termino):
    #Función de retorno (Callback):
    #Cada caballo invoca esta función en el instante en que completa sus vueltas.
    orden_llegada.append(caballo_termino) # Agrega el caballo a la lista
    
    # Evalúa si la lista de llegadas ya tiene a los 10 caballos
    if len(orden_llegada) == 10:
        mostrar_tabla_y_apuesta() # Dispara el evento final

def mostrar_tabla_y_apuesta():
    #Se ejecuta únicamente cuando los 10 caballos terminaron.
    #Calcula duraciones, ordena la lista y muestra los mensajes.

    # .sort() ordena la lista. Usamos una función lambda para decirle que ordene
    # según el cálculo matemático de: tiempo_final - tiempo_inicial
    orden_llegada.sort(key=lambda c: (c.tiempo_fin - c.tiempo_inicio))
    
    # Insertar el título en la caja de texto (.insert)
    cuadro_resultados.insert(tk.END, " POSICIONES FINALES \n\n")
    
    # enumerate() extrae tanto la posición 'i' (0 al 9) como el objeto 'c' (Caballo)
    for i, c in enumerate(orden_llegada):
        tiempo_total = c.tiempo_fin - c.tiempo_inicio # Duración de la carrera en segundos
        # Se imprime formateando el texto (f-string)
        cuadro_resultados.insert(tk.END, f"{i+1}º - Caballo {c.id_caballo} ({tiempo_total:.2f} seg)\n")
    
    # Evaluar apuesta del usuario
    caballo_ganador = orden_llegada[0].id_caballo # El índice 0 es el más rápido
    mi_apuesta = int(spin_apuesta.get())          # Extrae la apuesta de la interfaz
    
    # messagebox genera las ventanas de alerta de Windows
    if mi_apuesta == caballo_ganador:
        messagebox.showinfo("¡Felicidades!", f"¡El caballo {caballo_ganador} ganó!\nTu apuesta fue correcta.")
    else:
        messagebox.showinfo("Fin de la carrera", f"Ganó el caballo {caballo_ganador}.\nSuerte en la próxima.")

def reiniciar_carrera():
    #Función vinculada al botón Reiniciar.
    #Devuelve todo el sistema al estado por defecto.
    
    global orden_llegada
    orden_llegada = []
    cuadro_resultados.delete("1.0", tk.END)
    
    # Itera sobre los objetos para llamar al método de la clase que reinicia posiciones
    for c in caballos_lista:
        c.reiniciar()

# ==========================================
# 4. CONFIGURACIÓN DE LA INTERFAZ (Tkinter GUI)
# ==========================================
ventana = tk.Tk()
ventana.title("Simulador de Carrera - Temporizadores")
# Agrandamos la ventana para dar espacio al panel lateral (ancho x alto)
ventana.geometry("1150x644") 

# --- SECCIÓN IZQUIERDA: PISTA Y CABALLOS ---
# Carga las imágenes en variables tk.PhotoImage (solo admite .png o .gif)
try:
    imagenPista = tk.PhotoImage(file="Camino.png")
    pista = tk.Label(ventana, image=imagenPista)
    pista.place(x=0, y=0)
    imagencaballo = tk.PhotoImage(file="Caballo.png")
except:
    print("Advertencia: Asegúrate de tener 'Camino.png' y 'Caballo.png' en la misma ruta del script.")
    imagencaballo = None

# Bucle for: Crea automáticamente 10 objetos Caballo en memoria RAM
# en lugar de escribir caballo_0, caballo_1, etc.
y_posiciones = [0, 64, 128, 192, 256, 320, 384, 448, 512, 576] # Posición 'Y' de cada carril
for i in range(10):
    # Instanciamos la clase pasando los atributos iniciales
    nuevo_caballo = Caballo(id_caballo=i, y_pos=y_posiciones[i], ventana=ventana, img_caballo=imagencaballo)
    caballos_lista.append(nuevo_caballo) # Guardamos el objeto en la lista para controlarlo luego

# --- SECCIÓN DERECHA: PANEL DE CONTROLES ---
# tk.Frame funciona como una "sub-ventana" para agrupar elementos ordenadamente
panel_controles = tk.Frame(ventana, width=250, bg="lightgray")
panel_controles.place(x=900, y=0, height=644, width=250)

# Etiqueta de Título
tk.Label(panel_controles, text="--- PANEL DE CONTROL ---", bg="lightgray", font=("Arial", 10, "bold")).pack(pady=10)

# Herramienta de Apuestas: tk.Spinbox crea una caja de texto con flechitas numéricas
tk.Label(panel_controles, text="Caballo al que apuestas (0-9):", bg="lightgray").pack(pady=5)
spin_apuesta = tk.Spinbox(panel_controles, from_=0, to=9, width=10)
spin_apuesta.pack()

# Herramienta de Vueltas
tk.Label(panel_controles, text="Nº de idas y vueltas (Rondas):", bg="lightgray").pack(pady=5)
spin_vueltas = tk.Spinbox(panel_controles, from_=1, to=10, width=10)
spin_vueltas.pack()

# Herramienta de Tiempo general: tk.Scale crea una barra deslizable (slider)
tk.Label(panel_controles, text="Modificador del Tiempo general:\n(Menos % = Más veloz)", bg="lightgray").pack(pady=10)
slider_velocidad = tk.Scale(panel_controles, from_=10, to=200, orient="horizontal", bg="lightgray", length=150)
slider_velocidad.set(100) # Configuramos el slider al 100% por defecto
slider_velocidad.pack()

# Botones con ejecución de comandos (funciones)
btn_iniciar = tk.Button(panel_controles, text="INICIAR CARRERA", bg="lightgreen", command=iniciar_carrera)
btn_iniciar.pack(pady=15, fill="x", padx=20)

btn_reiniciar = tk.Button(panel_controles, text="REINICIAR TABLERO", bg="lightcoral", command=reiniciar_carrera)
btn_reiniciar.pack(pady=5, fill="x", padx=20)

# Caja de Resultados: tk.Text crea un área grande para texto multilinea
tk.Label(panel_controles, text="Tabla de Posiciones:", bg="lightgray").pack(pady=10)
cuadro_resultados = tk.Text(panel_controles, width=25, height=12)
cuadro_resultados.pack(padx=10)

# ==========================================
# 5. BUCLE DE EJECUCIÓN (Mainloop)
# ==========================================
ventana.mainloop()