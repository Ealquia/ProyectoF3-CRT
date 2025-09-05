import pygame
import numpy as np

# --- CONSTANTES FÍSICAS Y DE SIMULACIÓN ---
E_CHARGE = 1.602e-19 # carga del electrón
E_MASS = 9.109e-31 # masa del electrón 

pygame.init()
# --- PARÁMETROS GEOMÉTRICOS DEL CRT (en metros) ---
# Se ajustaron ligeramente para una mejor proporción visual
GUN_TO_PLATES_DIST = 0.05 # Distancia del cañón a las placas de deflexión
DEFLECT_PLATE_LENGTH = 0.05 # Longitud de las placas de deflexión
PLATE_TO_SCREEN_DIST = 0.25 # Distancia de las placas a la pantalla
PLATE_SEPARATION = 0.01 # Separación entre las placas
TOTAL_LENGTH = GUN_TO_PLATES_DIST + DEFLECT_PLATE_LENGTH + PLATE_TO_SCREEN_DIST

# --- CONFIGURACIÓN DE LA PANTALLA Y LA INTERFAZ ---
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h # Aumentada la altura para mejor espaciado
UI_X_START = int(SCREEN_WIDTH * 0.65)
UI_WIDTH = SCREEN_WIDTH - UI_X_START - 50
BG_COLOR = (10, 10, 30)
TEXT_COLOR = (220, 220, 255)
VIEW_BG_COLOR = (0, 0, 0)
VIEW_BORDER_COLOR = (50, 50, 80)
BEAM_COLOR = (50, 255, 50)
PLATE_COLOR = (200, 200, 0)
CURRENT_IMPACT_COLOR = (255, 255, 150)

class CRT:
    """
    Clase que encapsula la física del CRT.
    Calcula la trayectoria completa del electrón y la deflexión máxima posible.
    """
    def _calculate_final_deflection(self, Va, V_deflect):
        """
        Calcula la deflexión final en un eje (Y o Z) en la pantalla.
        Esta es una implementación precisa basada en cinemática.
        """
        if Va <= 0: return 0

        if Va <= 0 or Va < 1e-3:
            return 0
        # Velocidad inicial del electrón debida al voltaje de aceleración
        v_x = np.sqrt(2 * E_CHARGE * Va / E_MASS)
        
        # Tiempo que el electrón pasa entre las placas de deflexión
        time_in_plates = DEFLECT_PLATE_LENGTH / v_x
        
        # Aceleración transversal (vertical o horizontal) dentro de las placas
        a_deflect = (E_CHARGE * (V_deflect / PLATE_SEPARATION)) / E_MASS
        
        # Deflexión y velocidad al salir de las placas
        d_at_exit = 0.5 * a_deflect * time_in_plates**2
        v_at_exit = a_deflect * time_in_plates
        
        # Tiempo que el electrón viaja desde las placas hasta la pantalla
        time_drift = PLATE_TO_SCREEN_DIST / v_x
        
        # Deflexión total = deflexión dentro de las placas + deflexión en la región de deriva
        return d_at_exit + v_at_exit * time_drift

    def calculate_max_deflection(self, Va, V_max_deflect):
        """Calcula la máxima deflexión en metros que se puede lograr con los voltajes dados."""
        return self._calculate_final_deflection(Va, V_max_deflect)

    def calculate_trajectory(self, Va, Vh, Vv, num_points=100):
        """Calcula la trayectoria completa del electrón (puntos x, y, z) a través del tubo."""
        if Va <= 0: return [(x, 0, 0) for x in np.linspace(0, TOTAL_LENGTH, num_points)]

        if Va <= 0 or Va < 1e-3:
            return [(x, 0, 0) for x in np.linspace(0, TOTAL_LENGTH, num_points)]
        
        v_x = np.sqrt(2 * E_CHARGE * Va / E_MASS)
        a_vertical = (E_CHARGE * (Vv / PLATE_SEPARATION)) / E_MASS 
        a_horizontal = (E_CHARGE * (Vh / PLATE_SEPARATION)) / E_MASS

        trajectory = [] # lista de para las coordenadas (x, y, z)
        x_coords = np.linspace(0, TOTAL_LENGTH, num_points)

        # Tiempos y posiciones/velocidades clave
        t_exit_plates = DEFLECT_PLATE_LENGTH / v_x
        y_exit = 0.5 * a_vertical * t_exit_plates**2
        z_exit = 0.5 * a_horizontal * t_exit_plates**2
        vy_exit = a_vertical * t_exit_plates
        vz_exit = a_horizontal * t_exit_plates

        for x in x_coords:
            y, z = 0, 0
            if x <= GUN_TO_PLATES_DIST:
                # Antes de las placas, no hay deflexión
                pass
            elif x <= GUN_TO_PLATES_DIST + DEFLECT_PLATE_LENGTH:
                # Dentro de las placas, movimiento parabólico
                t_in_plates = (x - GUN_TO_PLATES_DIST) / v_x # timpo dentro de las placas
                y = 0.5 * a_vertical * t_in_plates**2 # deflexión vertical
                z = 0.5 * a_horizontal * t_in_plates**2 # deflexión horizontal
            else:
                # Después de las placas, movimiento rectilíneo
                t_drift = (x - (GUN_TO_PLATES_DIST + DEFLECT_PLATE_LENGTH)) / v_x # tiempo en llegar a la pantalla
                y = y_exit + vy_exit * t_drift # coordenada final vertical
                z = z_exit + vz_exit * t_drift # coordenada final horizontal
            trajectory.append((x, y, z))
        return trajectory

# --- CLASES DE UI (Slider, Button) ---
class Slider:
    def __init__(self, x, y, w, h, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, w, h); self.min_val, self.max_val, self.val = min_val, max_val, initial_val
        self.label = label; self.handle_rect = pygame.Rect(0, y - h//2, 10, h*2); self.update_handle_pos(); self.dragging = False
    def update_handle_pos(self): self.handle_rect.centerx = self.rect.x + (self.val - self.min_val) / (self.max_val - self.min_val) * self.rect.w
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.handle_rect.collidepoint(event.pos): self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP: self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            pos_x = max(self.rect.left, min(event.pos[0], self.rect.right))
            self.val = self.min_val + (pos_x - self.rect.x) / self.rect.w * (self.max_val - self.min_val); self.update_handle_pos()
    def draw(self, screen, font):
        pygame.draw.rect(screen, (50, 50, 80), self.rect); pygame.draw.rect(screen, (100, 100, 200), self.handle_rect)
        label_surf = font.render(f"{self.label}: {self.val:.2f}", True, TEXT_COLOR); screen.blit(label_surf, (self.rect.x, self.rect.y - 25))

class Button:
    def __init__(self, x, y, w, h, text, color): self.rect = pygame.Rect(x, y, w, h); self.text, self.color, self.is_active = text, color, False
    def draw(self, screen, font):
        draw_color = tuple(min(int(c * 1.5), 255) for c in self.color) if self.is_active else self.color; pygame.draw.rect(screen, draw_color, self.rect)
        text_surf = font.render(self.text, True, (255,255,255)); screen.blit(text_surf, text_surf.get_rect(center=self.rect.center))
    def handle_event(self, event): return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

# --- FUNCIONES DE DIBUJO ---
def draw_side_view(screen, font, title, rect, trajectory, view_type, max_deflection_m):
    """
    Dibuja la vista superior o lateral del CRT.
    USA UNA ESCALA FIJA para evitar el molesto parpadeo/zoom.
    """
    pygame.draw.rect(screen, VIEW_BG_COLOR, rect); pygame.draw.rect(screen, VIEW_BORDER_COLOR, rect, 2)
    screen.blit(font.render(title, True, TEXT_COLOR), (rect.x + 10, rect.y + 5))
    
    x_scale = rect.width / TOTAL_LENGTH
    # CORRECCIÓN: Usar la máxima deflexión posible para una escala vertical fija y estable.
    y_scale = (rect.height / 2) * 0.9 / max_deflection_m 
    
    # Dibuja las placas de deflexión
    plate_start_x = rect.x + GUN_TO_PLATES_DIST * x_scale
    plate_width = DEFLECT_PLATE_LENGTH * x_scale
    plate_pixel_separation = PLATE_SEPARATION * y_scale
    pygame.draw.rect(screen, PLATE_COLOR, (plate_start_x, rect.centery - plate_pixel_separation/2 - 5, plate_width, 5))
    pygame.draw.rect(screen, PLATE_COLOR, (plate_start_x, rect.centery + plate_pixel_separation/2, plate_width, 5))

    # Dibuja la trayectoria del haz de electrones
    deflection_index = 1 if view_type == 'side' else 2 # 1 para 'y', 2 para 'z'
    points_to_draw = [(rect.x + p[0] * x_scale, rect.centery - p[deflection_index] * y_scale) for p in trajectory]
    if len(points_to_draw) > 1: pygame.draw.aalines(screen, BEAM_COLOR, False, points_to_draw)

def draw_front_view(screen, font, title, rect, points_on_screen, current_point, Va):
    """Dibuja la pantalla del CRT con el rastro de persistencia."""
    pygame.draw.rect(screen, VIEW_BG_COLOR, rect, border_radius=60); pygame.draw.rect(screen, VIEW_BORDER_COLOR, rect, 2, border_radius=60)
    screen.blit(font.render(title, True, TEXT_COLOR), (rect.x + 10, rect.y + 5))
    
    # Dibuja los puntos antiguos (la persistencia)
    for point, va_at_impact in points_on_screen:
        final_pos = (point[0] + rect.x, point[1] + rect.y)
        if rect.collidepoint(final_pos):
            # Normaliza el brillo según el rango del slider
            Va_min = 2000
            Va_max = 3000
            r = int((va_at_impact - Va_min) / (Va_max - Va_min) * 255)
            b = int((va_at_impact - Va_min) / (Va_max - Va_min) * 150)
            r = max(0, min(r, 255))
            b = max(0, min(b, 255))
            trail_color = (r, 255, b)
            pygame.draw.circle(screen, trail_color, final_pos, 2)
    
    # Dibuja el punto de impacto actual más brillante
    if current_point:
        current_pos = (current_point[0] + rect.x, current_point[1] + rect.y)
        if rect.collidepoint(current_pos):
            # Obtener rango dinámico del slider
            Va_min = 2000
            Va_max = 3000

            # Normalizar y limitar los valores de color
            r = int((Va - Va_min) / (Va_max - Va_min) * 255)
            b = int((Va - Va_min) / (Va_max - Va_min) * 150)
            r = max(0, min(r, 255))
            b = max(0, min(b, 255))

            impact_color = (r, 255, b)
            pygame.draw.circle(screen, impact_color, current_pos, 4)

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulador de Tubo de Rayos Catódicos (CRT) - Versión Verificada")
    font = pygame.font.SysFont("sans", 20)
    clock = pygame.time.Clock()
    
    crt_physics = CRT()
    
    # Definición de las áreas de dibujo
    side_rect = pygame.Rect(50, 50, int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.2))
    top_rect = pygame.Rect(50, side_rect.bottom + 20, int(SCREEN_WIDTH * 0.6), int(SCREEN_HEIGHT * 0.2))
    front_rect = pygame.Rect(50, top_rect.bottom + 20, float(SCREEN_WIDTH * 0.3), float(SCREEN_HEIGHT * 0.4))

    # Controles de la UI (Interfaz de Usuario)
    sliders = {
        "Va": Slider(UI_X_START, SCREEN_HEIGHT*0.1, UI_WIDTH, 10, 2000, 3000, 2000, "Voltaje Aceleración (V)"), # Valor inicial es 2000V
        "V_amp": Slider(UI_X_START, SCREEN_HEIGHT*0.2, UI_WIDTH, 10, 0, 140, 100, "Amplitud Voltaje (V)"), 
        "freq_h": Slider(UI_X_START, SCREEN_HEIGHT*0.3, UI_WIDTH, 10, 1.0, 5.0, 1.0, "Frecuencia Horizontal (a)"),
        "freq_v": Slider(UI_X_START, SCREEN_HEIGHT*0.4, UI_WIDTH, 10, 1.0, 5.0, 1.0, "Frecuencia Vertical (b)"),
        "phase": Slider(UI_X_START, SCREEN_HEIGHT*0.5, UI_WIDTH, 10, 0, 2*np.pi, 0.0, "Desfase (δ)"), # Valor inicial es 0.0
        "persistence": Slider(UI_X_START, SCREEN_HEIGHT*0.6, UI_WIDTH, 10, 10, 500, 250, "Persistencia (puntos)"),
        "Vv_manual": Slider(UI_X_START, SCREEN_HEIGHT*0.7, UI_WIDTH, 10, -150, 150, 0, "Voltaje Vertical (Manual)"),
        "Vh_manual": Slider(UI_X_START, SCREEN_HEIGHT*0.8, UI_WIDTH, 10, -150, 150, 0, "Voltaje Horizontal (Manual)"),
    }
    btn_manual = Button(UI_X_START, int(SCREEN_HEIGHT*0.9), 120, 40, "Manual", (0, 100, 200))
    btn_sinusoidal = Button(UI_X_START + 140, int(SCREEN_HEIGHT*0.9), 120, 40, "Sinusoidal", (200, 50, 0))
    mode = "Sinusoidal"

    points_on_screen = []
    running = True

    while running:
        sim_time = pygame.time.get_ticks() / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            for s in sliders.values(): s.handle_event(event)
            if btn_manual.handle_event(event): mode = "Manual"
            if btn_sinusoidal.handle_event(event): mode = "Sinusoidal"
        
        btn_manual.is_active, btn_sinusoidal.is_active = (mode == "Manual"), (mode == "Sinusoidal")

        Va = sliders["Va"].val
        Va_min = sliders["Va"].min_val
        Va_max = sliders["Va"].max_val
        if mode == "Manual":
            Vh, Vv = sliders["Vh_manual"].val, sliders["Vv_manual"].val
        else: # Modo Sinusoidal
            # --- LÓGICA DE ECUACIONES DE LISSAJOUS - VERSIÓN FINAL CORREGIDA ---
            # La convención que coincide con la tabla de referencia es:
            # Horizontal (Vh) -> sin(a*t)
            # Vertical   (Vv) -> sin(b*t + δ)
            
            amp = sliders["V_amp"].val
            freq_h = sliders["freq_h"].val # Frecuencia 'a'
            freq_v = sliders["freq_v"].val # Frecuencia 'b'
            phase = sliders["phase"].val  # Desfase 'δ'

            Vh = amp * np.cos(2 * np.pi * freq_h * sim_time )
            Vv = amp * np.cos(2 * np.pi * freq_v * sim_time + phase)

        # --- CÁLCULOS FÍSICOS Y DE ESCALA ---
        trajectory = crt_physics.calculate_trajectory(Va, Vh, Vv)
        
        max_deflect_m = crt_physics.calculate_max_deflection(Va, sliders["V_amp"].max_val)
        if max_deflect_m < 1e-9: max_deflect_m = PLATE_SEPARATION
        
        front_view_scale = (front_rect.width / 2) * 0.9 / max_deflect_m
        
        final_point_m = trajectory[-1]
        pixel_z = front_rect.width / 2 + final_point_m[2] * front_view_scale
        pixel_y = front_rect.height / 2 - final_point_m[1] * front_view_scale
        
        current_point = (pixel_z, pixel_y)
        points_on_screen.append((current_point, Va))
        
        max_points = int(sliders["persistence"].val)
        if len(points_on_screen) > max_points:
            points_on_screen.pop(0)

        # --- DIBUJO EN PANTALLA ---
        screen.fill(BG_COLOR)
        draw_side_view(screen, font, "Vista Superior (Deflexión Horizontal Z)", top_rect, trajectory, 'top', max_deflect_m)
        draw_side_view(screen, font, "Vista Lateral (Deflexión Vertical Y)", side_rect, trajectory, 'side', max_deflect_m)
        draw_front_view(screen, font, "Pantalla (Vista Frontal)", front_rect, points_on_screen, current_point, Va)
        for s in sliders.values(): s.draw(screen, font)
        btn_manual.draw(screen, font); btn_sinusoidal.draw(screen, font)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()