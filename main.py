import numpy as np
import matplotlib.pyplot as plt

# -----Constantes físicas----
ELECTRON_CHARGE = 1.602e-19  # Carga del electrón (C)
ELECTRON_MASS = 9.109e-31    # Masa del electrón (kg)

# -----Variables físicas fijas del CRT (no controlables por el usuario)-----
SCREEN_SIZE = 0.30  # metros (pantalla cuadrada de 30 cm x 30 cm)
PLATE_LENGTH = 0.05  # metros (longitud de las placas de deflexión, 5 cm)
PLATE_WIDTH = 0.02   # metros (ancho de las placas de deflexión, 2 cm)
PLATE_SEPARATION = 0.01 # metros (separación entre placas, 1 cm)
GUN_TO_PLATES = 0.02 # metros (distancia del cañón a las placas, 2 cm)
PLATES_TO_SCREEN = 0.23 # metros (distancia de las placas a la pantalla, 23 cm)
DIST_BETWEEN_PLATES = 0.01 # metros (distancia entre placas verticales y horizontales, 1 cm)

# -----Variables físicas controlables por el usuario-----
# Voltaje de aceleración de los electrones (V)
V_ACCEL_MIN = 100    # Voltaje mínimo de aceleración (V)
V_ACCEL_MAX = 2000   # Voltaje máximo de aceleración (V)
V_accel = 1000       # Valor inicial (puede ser modificado por el usuario)

# Voltaje de placas de deflexión verticales (V)
V_PLATE_Y_MIN = -100 # Voltaje mínimo placas verticales (V)
V_PLATE_Y_MAX = 100  # Voltaje máximo placas verticales (V)
V_plate_y = 0        # Valor inicial

# Voltaje de placas de deflexión horizontales (V)
V_PLATE_X_MIN = -100 # Voltaje mínimo placas horizontales (V)
V_PLATE_X_MAX = 100  # Voltaje máximo placas horizontales (V)
V_plate_x = 0        # Valor inicial

# Parámetros de señal sinusoidal para Figuras de Lissajous
FREQ_X_MIN = 1       # Hz
FREQ_X_MAX = 1000    # Hz
freq_x = 100         # Valor inicial

FREQ_Y_MIN = 1       # Hz
FREQ_Y_MAX = 1000    # Hz
freq_y = 100         # Valor inicial

PHASE_X_MIN = 0      # rad
PHASE_X_MAX = 2*np.pi # rad
phase_x = 0          # Valor inicial

PHASE_Y_MIN = 0      # rad
PHASE_Y_MAX = 2*np.pi # rad
phase_y = 0          # Valor inicial

# Tiempo de persistencia/latencia del punto en pantalla (s)
PERSISTENCE_MIN = 0.01
PERSISTENCE_MAX = 1.0
persistence = 0.1     # Valor inicial


def main():
    print(".")

if __name__ == "__main__":
    main()