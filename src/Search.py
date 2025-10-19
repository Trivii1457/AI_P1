"""
Algoritmos de búsqueda: Beam Search y Dynamic Weighting A*
"""
import heapq
from collections import deque
import math


class Node:
    """Representa un nodo en el espacio de búsqueda"""
    def __init__(self, position, parent=None, g=0, h=0, depth=0):
        self.position = position  # (x, y)
        self.parent = parent
        self.g = g  # Costo desde el inicio
        self.h = h  # Heurística al objetivo
        self.depth = depth  # Profundidad del nodo
        
    def f(self, epsilon=0, N=1):
        """Calcula f(n) con peso dinámico opcional"""
        if epsilon > 0 and N > 0:
            # Dynamic Weighting: f(n) = g(n) + h(n) + ε * (1 - d(n)/N) * h(n)
            dynamic_weight = epsilon * (1 - self.depth / N) * self.h
            return self.g + self.h + dynamic_weight
        else:
            # A* estándar: f(n) = g(n) + h(n)
            return self.g + self.h
    
    def __lt__(self, other):
        """Para comparación en heapq"""
        return self.f() < other.f()
    
    def __eq__(self, other):
        return self.position == other.position
    
    def __hash__(self):
        return hash(self.position)


class GridMap:
    """Representa el mapa/matriz del problema"""
    
    # Tipos de celda
    EMPTY = 0
    OBSTACLE = 1
    POISON = 2
    START = 3
    GOAL = 4
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[self.EMPTY for _ in range(width)] for _ in range(height)]
        self.start = None
        self.goal = None
        self.poison_cost = 5  # Costo extra por pasar por veneno
        
    def set_cell(self, x, y, cell_type):
        """Establece el tipo de celda en posición (x, y)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = cell_type
            if cell_type == self.START:
                self.start = (x, y)
            elif cell_type == self.GOAL:
                self.goal = (x, y)
    
    def get_cell(self, x, y):
        """Obtiene el tipo de celda en posición (x, y)"""
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y][x]
        return self.OBSTACLE  # Fuera de límites = obstáculo
    
    def is_walkable(self, x, y):
        """Verifica si una celda es transitable"""
        cell = self.get_cell(x, y)
        return cell != self.OBSTACLE
    
    def get_cost(self, x, y):
        """Obtiene el costo de moverse a una celda"""
        cell = self.get_cell(x, y)
        if cell == self.OBSTACLE:
            return float('inf')
        elif cell == self.POISON:
            return self.poison_cost
        else:
            return 1  # Costo normal
    
    def get_neighbors(self, position):
        """Obtiene vecinos válidos de una posición (4-vecinos)"""
        x, y = position
        neighbors = []
        # Movimientos: arriba, derecha, abajo, izquierda
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if self.is_walkable(nx, ny):
                neighbors.append((nx, ny))
        
        return neighbors
    
    def heuristic(self, pos1, pos2, method='manhattan'):
        """Calcula la heurística entre dos posiciones"""
        x1, y1 = pos1
        x2, y2 = pos2
        
        if method == 'manhattan':
            return abs(x1 - x2) + abs(y1 - y2)
        elif method == 'euclidean':
            return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
        else:
            return 0


def beam_search(grid_map, beta=3, heuristic='manhattan'):
    """
    Beam Search: búsqueda que mantiene solo los β mejores nodos por nivel
    
    Args:
        grid_map: Objeto GridMap con el mapa
        beta: Ancho de la viga (número de nodos a mantener por nivel)
        heuristic: Tipo de heurística ('manhattan' o 'euclidean')
    
    Returns:
        tuple: (ruta, estadísticas)
    """
    if not grid_map.start or not grid_map.goal:
        return None, {"error": "Start o Goal no definido"}
    
    stats = {
        "nodes_expanded": 0,
        "nodes_generated": 0,
        "path_length": 0,
        "path_cost": 0,
        "beam_width": beta
    }
    
    # Inicializar con el nodo de inicio
    start_node = Node(
        position=grid_map.start,
        parent=None,
        g=0,
        h=grid_map.heuristic(grid_map.start, grid_map.goal, heuristic),
        depth=0
    )
    
    current_level = [start_node]
    visited = set()
    
    while current_level:
        next_level = []
        
        # Expandir todos los nodos del nivel actual
        for node in current_level:
            stats["nodes_expanded"] += 1
            
            # ¿Llegamos al objetivo?
            if node.position == grid_map.goal:
                path = reconstruct_path(node)
                stats["path_length"] = len(path)
                stats["path_cost"] = node.g
                return path, stats
            
            visited.add(node.position)
            
            # Generar sucesores
            for neighbor_pos in grid_map.get_neighbors(node.position):
                if neighbor_pos not in visited:
                    cost = grid_map.get_cost(neighbor_pos[0], neighbor_pos[1])
                    child = Node(
                        position=neighbor_pos,
                        parent=node,
                        g=node.g + cost,
                        h=grid_map.heuristic(neighbor_pos, grid_map.goal, heuristic),
                        depth=node.depth + 1
                    )
                    next_level.append(child)
                    stats["nodes_generated"] += 1
        
        # Mantener solo los β mejores nodos según f(n)
        if next_level:
            next_level.sort(key=lambda n: n.f())
            current_level = next_level[:beta]
        else:
            current_level = []
    
    # No se encontró solución
    return None, stats


def dynamic_weighted_astar(grid_map, epsilon=1.5, heuristic='manhattan'):
    """
    Dynamic Weighting A*: ajusta el peso de la heurística dinámicamente
    f(n) = g(n) + h(n) + ε * (1 - d(n)/N) * h(n)
    
    Args:
        grid_map: Objeto GridMap con el mapa
        epsilon: Peso inicial para la heurística
        heuristic: Tipo de heurística ('manhattan' o 'euclidean')
    
    Returns:
        tuple: (ruta, estadísticas)
    """
    if not grid_map.start or not grid_map.goal:
        return None, {"error": "Start o Goal no definido"}
    
    # Estimación de profundidad máxima N
    N = grid_map.heuristic(grid_map.start, grid_map.goal, heuristic) * 1.5
    if N == 0:
        N = max(grid_map.width, grid_map.height)
    
    stats = {
        "nodes_expanded": 0,
        "nodes_generated": 0,
        "path_length": 0,
        "path_cost": 0,
        "epsilon": epsilon,
        "N": N
    }
    
    # Nodo inicial
    start_node = Node(
        position=grid_map.start,
        parent=None,
        g=0,
        h=grid_map.heuristic(grid_map.start, grid_map.goal, heuristic),
        depth=0
    )
    
    # Priority queue (min-heap)
    open_set = []
    heapq.heappush(open_set, (start_node.f(epsilon, N), start_node))
    
    # Conjuntos de nodos
    open_dict = {start_node.position: start_node}
    closed_set = set()
    
    while open_set:
        _, current = heapq.heappop(open_set)
        
        # Ya procesado
        if current.position in closed_set:
            continue
        
        stats["nodes_expanded"] += 1
        
        # ¿Llegamos al objetivo?
        if current.position == grid_map.goal:
            path = reconstruct_path(current)
            stats["path_length"] = len(path)
            stats["path_cost"] = current.g
            return path, stats
        
        closed_set.add(current.position)
        open_dict.pop(current.position, None)
        
        # Expandir vecinos
        for neighbor_pos in grid_map.get_neighbors(current.position):
            if neighbor_pos in closed_set:
                continue
            
            cost = grid_map.get_cost(neighbor_pos[0], neighbor_pos[1])
            tentative_g = current.g + cost
            
            # Crear o actualizar nodo vecino
            if neighbor_pos in open_dict:
                neighbor = open_dict[neighbor_pos]
                if tentative_g < neighbor.g:
                    neighbor.g = tentative_g
                    neighbor.parent = current
                    neighbor.depth = current.depth + 1
                    heapq.heappush(open_set, (neighbor.f(epsilon, N), neighbor))
            else:
                neighbor = Node(
                    position=neighbor_pos,
                    parent=current,
                    g=tentative_g,
                    h=grid_map.heuristic(neighbor_pos, grid_map.goal, heuristic),
                    depth=current.depth + 1
                )
                heapq.heappush(open_set, (neighbor.f(epsilon, N), neighbor))
                open_dict[neighbor_pos] = neighbor
                stats["nodes_generated"] += 1
    
    # No se encontró solución
    return None, stats


def reconstruct_path(node):
    """Reconstruye la ruta desde el nodo objetivo hasta el inicio"""
    path = []
    current = node
    while current:
        path.append(current.position)
        current = current.parent
    return list(reversed(path))