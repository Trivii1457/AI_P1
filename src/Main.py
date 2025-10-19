"""
GUI Principal para el proyecto de la Hormiga y el Hongo Mágico
Universidad del Valle - Introducción a la Inteligencia Artificial
"""
import pygame
import sys
import json
import time
from Search import GridMap, beam_search, dynamic_weighted_astar


# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (200, 0, 200)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (173, 216, 230)
DARK_GREEN = (0, 128, 0)


class Button:
    """Botón interactivo para la GUI"""
    def __init__(self, x, y, width, height, text, color=GRAY):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = LIGHT_BLUE
        self.is_hovered = False
        
    def draw(self, screen, font):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)
        
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Slider:
    """Control deslizante para ajustar velocidad"""
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        
    def draw(self, screen, font):
        # Línea del slider
        pygame.draw.rect(screen, DARK_GRAY, self.rect, 2)
        
        # Posición del handle
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        handle_x = self.rect.x + int(ratio * self.rect.width)
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 5, 10, 30)
        pygame.draw.rect(screen, BLUE, handle_rect)
        
        # Label
        text = font.render(f"{self.label}: {self.value:.1f}", True, BLACK)
        screen.blit(text, (self.rect.x, self.rect.y - 25))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
            handle_x = self.rect.x + int(ratio * self.rect.width)
            handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 5, 10, 30)
            if handle_rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = event.pos[0]
            ratio = (x - self.rect.x) / self.rect.width
            ratio = max(0, min(1, ratio))
            self.value = self.min_val + ratio * (self.max_val - self.min_val)


class AntPathfinderGUI:
    """GUI principal del simulador"""
    
    def __init__(self, width=1200, height=700):
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Hormiga y Hongo Mágico - IA Proyecto 1")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        
        # Dimensiones del grid
        self.grid_width = 20
        self.grid_height = 15
        self.cell_size = 30
        
        # Mapa y algoritmos
        self.grid_map = GridMap(self.grid_width, self.grid_height)
        self.path = None
        self.stats = None
        self.algorithm = "beam"  # "beam" o "dynamic"
        
        # Estado de la animación
        self.animating = False
        self.ant_position = None
        self.path_index = 0
        self.animation_speed = 5  # FPS
        self.last_move_time = 0
        
        # Modo de edición
        self.edit_mode = GridMap.EMPTY
        self.edit_mode_names = {
            GridMap.EMPTY: "Vacío",
            GridMap.OBSTACLE: "Obstáculo",
            GridMap.POISON: "Veneno",
            GridMap.START: "Inicio",
            GridMap.GOAL: "Objetivo"
        }
        
        # Crear mapa por defecto
        self.create_default_map()
        
        # UI Elements
        self.create_ui_elements()
        
        self.running = True
    
    def create_default_map(self):
        """Crea un mapa de ejemplo"""
        # Inicio y objetivo
        self.grid_map.set_cell(1, 1, GridMap.START)
        self.grid_map.set_cell(18, 13, GridMap.GOAL)
        
        # Algunos obstáculos
        for x in range(5, 15):
            self.grid_map.set_cell(x, 7, GridMap.OBSTACLE)
        
        for y in range(3, 10):
            self.grid_map.set_cell(10, y, GridMap.OBSTACLE)
        
        # Venenos
        self.grid_map.set_cell(3, 5, GridMap.POISON)
        self.grid_map.set_cell(4, 5, GridMap.POISON)
        self.grid_map.set_cell(15, 10, GridMap.POISON)
        self.grid_map.set_cell(16, 10, GridMap.POISON)
    
    def create_ui_elements(self):
        """Crea botones y controles"""
        panel_x = self.grid_width * self.cell_size + 20
        
        self.buttons = {
            "beam": Button(panel_x, 50, 150, 40, "Beam Search"),
            "dynamic": Button(panel_x, 100, 150, 40, "Dynamic A*"),
            "play": Button(panel_x, 160, 70, 40, "Play"),
            "pause": Button(panel_x + 80, 160, 70, 40, "Pause"),
            "reset": Button(panel_x, 210, 150, 40, "Reset"),
            "step": Button(panel_x, 260, 150, 40, "Step"),
            "clear": Button(panel_x, 310, 150, 40, "Clear Map"),
            "save": Button(panel_x, 360, 70, 40, "Save"),
            "load": Button(panel_x + 80, 360, 70, 40, "Load")
        }
        
        # Botones de modo de edición
        y_offset = 420
        self.edit_buttons = {
            GridMap.EMPTY: Button(panel_x, y_offset, 150, 30, "Vacío", WHITE),
            GridMap.OBSTACLE: Button(panel_x, y_offset + 35, 150, 30, "Obstáculo", BLACK),
            GridMap.POISON: Button(panel_x, y_offset + 70, 150, 30, "Veneno", PURPLE),
            GridMap.START: Button(panel_x, y_offset + 105, 150, 30, "Inicio", GREEN),
            GridMap.GOAL: Button(panel_x, y_offset + 140, 150, 30, "Objetivo", RED)
        }
        
        # Sliders
        self.sliders = {
            "speed": Slider(panel_x, 600, 150, 1, 20, 5, "Velocidad"),
            "beta": Slider(panel_x, 650, 150, 1, 10, 3, "Beta (β)"),
            "epsilon": Slider(panel_x, 680, 150, 0.5, 3, 1.5, "Epsilon (ε)")
        }
    
    def handle_events(self):
        """Maneja eventos de pygame"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            # Botones principales
            if self.buttons["beam"].handle_event(event):
                self.algorithm = "beam"
                self.run_search()
            
            if self.buttons["dynamic"].handle_event(event):
                self.algorithm = "dynamic"
                self.run_search()
            
            if self.buttons["play"].handle_event(event):
                if self.path:
                    self.animating = True
            
            if self.buttons["pause"].handle_event(event):
                self.animating = False
            
            if self.buttons["reset"].handle_event(event):
                self.reset_animation()
            
            if self.buttons["step"].handle_event(event):
                self.step_animation()
            
            if self.buttons["clear"].handle_event(event):
                self.clear_map()
            
            if self.buttons["save"].handle_event(event):
                self.save_map()
            
            if self.buttons["load"].handle_event(event):
                self.load_map()
            
            # Botones de modo de edición
            for mode, button in self.edit_buttons.items():
                if button.handle_event(event):
                    self.edit_mode = mode
            
            # Sliders
            for slider in self.sliders.values():
                slider.handle_event(event)
            
            # Click en el grid para editar
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Click izquierdo
                    self.handle_grid_click(event.pos)
    
    def handle_grid_click(self, pos):
        """Maneja clicks en el grid para editar"""
        x, y = pos
        grid_x = x // self.cell_size
        grid_y = y // self.cell_size
        
        if 0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height:
            # Limpiar start/goal previos si se está colocando uno nuevo
            if self.edit_mode == GridMap.START:
                for i in range(self.grid_height):
                    for j in range(self.grid_width):
                        if self.grid_map.get_cell(j, i) == GridMap.START:
                            self.grid_map.set_cell(j, i, GridMap.EMPTY)
            
            elif self.edit_mode == GridMap.GOAL:
                for i in range(self.grid_height):
                    for j in range(self.grid_width):
                        if self.grid_map.get_cell(j, i) == GridMap.GOAL:
                            self.grid_map.set_cell(j, i, GridMap.EMPTY)
            
            self.grid_map.set_cell(grid_x, grid_y, self.edit_mode)
            self.reset_animation()
    
    def run_search(self):
        """Ejecuta el algoritmo de búsqueda seleccionado"""
        self.reset_animation()
        
        start_time = time.time()
        
        if self.algorithm == "beam":
            beta = int(self.sliders["beta"].value)
            self.path, self.stats = beam_search(self.grid_map, beta=beta)
        else:  # dynamic
            epsilon = self.sliders["epsilon"].value
            self.path, self.stats = dynamic_weighted_astar(self.grid_map, epsilon=epsilon)
        
        end_time = time.time()
        
        if self.stats:
            self.stats["time"] = end_time - start_time
        
        if self.path:
            self.ant_position = self.path[0]
    
    def reset_animation(self):
        """Reinicia la animación"""
        self.animating = False
        self.path_index = 0
        if self.path:
            self.ant_position = self.path[0]
    
    def step_animation(self):
        """Avanza un paso en la animación"""
        if self.path and self.path_index < len(self.path) - 1:
            self.path_index += 1
            self.ant_position = self.path[self.path_index]
    
    def update_animation(self):
        """Actualiza la animación automática"""
        if self.animating and self.path:
            current_time = time.time()
            if current_time - self.last_move_time > 1.0 / self.sliders["speed"].value:
                self.last_move_time = current_time
                if self.path_index < len(self.path) - 1:
                    self.path_index += 1
                    self.ant_position = self.path[self.path_index]
                else:
                    self.animating = False
    
    def clear_map(self):
        """Limpia el mapa"""
        self.grid_map = GridMap(self.grid_width, self.grid_height)
        self.path = None
        self.stats = None
        self.reset_animation()
    
    def save_map(self):
        """Guarda el mapa en un archivo JSON"""
        data = {
            "width": self.grid_width,
            "height": self.grid_height,
            "grid": self.grid_map.grid,
            "start": self.grid_map.start,
            "goal": self.grid_map.goal
        }
        with open("map.json", "w") as f:
            json.dump(data, f)
        print("Mapa guardado en map.json")
    
    def load_map(self):
        """Carga el mapa desde un archivo JSON"""
        try:
            with open("map.json", "r") as f:
                data = json.load(f)
            
            self.grid_width = data["width"]
            self.grid_height = data["height"]
            self.grid_map = GridMap(self.grid_width, self.grid_height)
            self.grid_map.grid = data["grid"]
            self.grid_map.start = tuple(data["start"]) if data["start"] else None
            self.grid_map.goal = tuple(data["goal"]) if data["goal"] else None
            
            self.reset_animation()
            print("Mapa cargado desde map.json")
        except FileNotFoundError:
            print("Archivo map.json no encontrado")
    
    def draw(self):
        """Dibuja toda la interfaz"""
        self.screen.fill(WHITE)
        
        # Dibujar grid
        self.draw_grid()
        
        # Dibujar path
        if self.path:
            self.draw_path()
        
        # Dibujar hormiga
        if self.ant_position:
            self.draw_ant()
        
        # Dibujar UI
        self.draw_ui()
        
        pygame.display.flip()
    
    def draw_grid(self):
        """Dibuja la cuadrícula"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size,
                                  self.cell_size, self.cell_size)
                
                cell = self.grid_map.get_cell(x, y)
                
                if cell == GridMap.EMPTY:
                    color = WHITE
                elif cell == GridMap.OBSTACLE:
                    color = BLACK
                elif cell == GridMap.POISON:
                    color = PURPLE
                elif cell == GridMap.START:
                    color = GREEN
                elif cell == GridMap.GOAL:
                    color = RED
                else:
                    color = WHITE
                
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, GRAY, rect, 1)
    
    def draw_path(self):
        """Dibuja el camino encontrado"""
        if len(self.path) > 1:
            for i in range(len(self.path) - 1):
                x1, y1 = self.path[i]
                x2, y2 = self.path[i + 1]
                
                center1 = (x1 * self.cell_size + self.cell_size // 2,
                          y1 * self.cell_size + self.cell_size // 2)
                center2 = (x2 * self.cell_size + self.cell_size // 2,
                          y2 * self.cell_size + self.cell_size // 2)
                
                pygame.draw.line(self.screen, YELLOW, center1, center2, 3)
    
    def draw_ant(self):
        """Dibuja la hormiga"""
        x, y = self.ant_position
        center = (x * self.cell_size + self.cell_size // 2,
                 y * self.cell_size + self.cell_size // 2)
        pygame.draw.circle(self.screen, ORANGE, center, self.cell_size // 3)
        # Dibujar "antenas"
        pygame.draw.line(self.screen, BLACK, center,
                        (center[0] - 5, center[1] - 10), 2)
        pygame.draw.line(self.screen, BLACK, center,
                        (center[0] + 5, center[1] - 10), 2)
    
    def draw_ui(self):
        """Dibuja la interfaz de usuario"""
        # Título
        title = self.font.render("Hormiga y Hongo Mágico", True, BLACK)
        self.screen.blit(title, (self.grid_width * self.cell_size + 20, 10))
        
        # Botones
        for button in self.buttons.values():
            button.draw(self.screen, self.small_font)
        
        # Botones de edición
        y_offset = 420
        edit_title = self.small_font.render("Modo de Edición:", True, BLACK)
        self.screen.blit(edit_title, (self.grid_width * self.cell_size + 20, y_offset - 25))
        
        for mode, button in self.edit_buttons.items():
            button.draw(self.screen, self.small_font)
            if mode == self.edit_mode:
                pygame.draw.rect(self.screen, BLUE, button.rect, 3)
        
        # Sliders
        for slider in self.sliders.values():
            slider.draw(self.screen, self.small_font)
        
        # Estadísticas
        if self.stats:
            stats_y = 200
            stats_x = self.grid_width * self.cell_size + 20
            
            stats_title = self.small_font.render("Estadísticas:", True, BLACK)
            self.screen.blit(stats_title, (stats_x, stats_y - 20))
            
            algo_name = "Beam Search" if self.algorithm == "beam" else "Dynamic Weighting A*"
            texts = [
                f"Algoritmo: {algo_name}",
                f"Nodos expandidos: {self.stats.get('nodes_expanded', 0)}",
                f"Nodos generados: {self.stats.get('nodes_generated', 0)}",
                f"Longitud camino: {self.stats.get('path_length', 0)}",
                f"Costo camino: {self.stats.get('path_cost', 0):.1f}",
                f"Tiempo: {self.stats.get('time', 0):.4f}s"
            ]
            
            for i, text in enumerate(texts):
                surface = self.small_font.render(text, True, BLACK)
                self.screen.blit(surface, (stats_x, stats_y + i * 20))
    
    def run(self):
        """Loop principal"""
        while self.running:
            self.handle_events()
            self.update_animation()
            self.draw()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()


def main():
    """Función principal"""
    app = AntPathfinderGUI()
    app.run()


if __name__ == "__main__":
    main()