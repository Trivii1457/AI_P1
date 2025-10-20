---
title: "Proyecto 1 – Introducción a la Inteligencia Artificial"
subtitle: "Hormiga y el Hongo Mágico"
author: 
  - Juan Diego Escobar (2359393)
  - Julio David Cardona (2359654)
  - Daniel Camelo Castro (2477177)
university: "Universidad del Valle – Escuela de Ingeniería de Sistemas y Computación"
course: "Introducción a la Inteligencia Artificial"
date: "Periodo 2025–2"
---

## Descripción General

El objetivo del proyecto es implementar un agente inteligente —una **hormiga**— que debe encontrar el **hongo mágico** dentro de un tablero, evitando obstáculos y celdas con veneno.

El proyecto busca **comparar el desempeño** de dos algoritmos de búsqueda informada:
1. **Beam Search** (búsqueda con ancho limitado).  
2. **Dynamic Weighted A*** (versión adaptativa del algoritmo A*).  

La simulación se desarrolla con una **interfaz gráfica en Pygame**, donde se observa el recorrido de la hormiga sobre el mapa.

---

## Objetivos

- Implementar y visualizar algoritmos de búsqueda informada.  
- Analizar el impacto de los parámetros β (beam width) y ε (peso dinámico) sobre el rendimiento.  
- Desarrollar una interfaz visual intuitiva e interactiva.  
- Evaluar el comportamiento de los algoritmos frente a obstáculos y celdas de alto costo (veneno).

---

## Estructura del Proyecto

```
📂 Proyecto-Hormiga
│
├── src/
│   ├── Main.py              # Interfaz gráfica y lógica de simulación
│   ├── Search.py            # Implementación de Beam Search y Dynamic A*
│
├── map_example.json         # Mapa de ejemplo
├── requirements.txt         # Dependencias
└── README.md                # Informe / documentación
```

---

## Diseño del Sistema

### **1. Interfaz Gráfica (Main.py)**
Implementada en `pygame`, muestra un tablero interactivo donde el usuario puede:
- Dibujar obstáculos, venenos, inicio y meta.  
- Guardar/cargar mapas en formato JSON.  
- Seleccionar algoritmo (`Beam` o `Dynamic A*`).  
- Ajustar parámetros:
  - **β (Beam width)** → número de nodos a conservar por nivel.  
  - **ε (Epsilon)** → peso dinámico de la heurística.  
  - **Velocidad** → control de animación de la hormiga.  
- Visualizar estadísticas de la búsqueda:
  - Nodos expandidos y generados.  
  - Longitud y costo del camino.  
  - Tiempo de ejecución.

---

### **2. Mapa y Representación (GridMap)**
Definido en `Search.py`, representa la matriz del entorno.  
Cada celda puede ser:

| Tipo | Código | Color en GUI |
|------|---------|--------------|
| Vacío | 0 | Blanco |
| Obstáculo | 1 | Negro |
| Veneno | 2 | Púrpura |
| Inicio | 3 | Verde |
| Meta | 4 | Rojo |

El mapa puede modificarse dinámicamente y guardarse como `.json`.

---

### **3. Nodo y Estructura de Búsqueda**
Cada estado se representa con un objeto `Node`, que almacena:
- `position`: coordenadas (x, y).  
- `g`: costo acumulado.  
- `h`: heurística al objetivo.  
- `depth`: profundidad del nodo.  
- `parent`: referencia al nodo anterior.

---

## 🔍 Algoritmos Implementados

### **A. Beam Search**

**Idea principal:**  
Limitar la cantidad de nodos explorados por nivel (β).  
Solo los **β nodos más prometedores** (con menor `f = g + h`) se expanden.

**Ventajas:**
- Bajo consumo de memoria.  
- Búsqueda rápida.

**Desventajas:**
- Puede perder la solución óptima si la poda elimina el camino correcto.

**Pseudocódigo:**
```python
current_level = [start_node]
while current_level:
    next_level = []
    for node in current_level:
        expand(node)
        for child in successors(node):
            next_level.append(child)
    next_level.sort(by=f)
    current_level = next_level[:beta]
```

---

### **B. Dynamic Weighted A\***

**Idea principal:**  
Modificar dinámicamente el peso de la heurística según la profundidad.  
\[
f(n) = g(n) + h(n) + \varepsilon \cdot (1 - \frac{d(n)}{N}) \cdot h(n)
\]

Donde:
- `ε` → controla el grado de prioridad de la heurística.  
- `d(n)` → profundidad actual.  
- `N` → profundidad estimada total.

**Comportamiento:**
- Al inicio da más peso a `h(n)` → búsqueda más rápida.  
- Cerca del objetivo da más peso a `g(n)` → solución más óptima.

**Ventajas:**
- Equilibrio entre velocidad y precisión.  
- Reduce el sobrecoste de A* tradicional.

---

## 🧪 Pruebas y Resultados

### **Mapa utilizado (`map_example.json`)**
- Dimensiones: 20x15  
- Inicio: (1, 1)  
- Meta: (18, 13)  
- Zonas con obstáculos y venenos estratégicamente colocados.

**Configuraciones de prueba:**

| Prueba | Algoritmo | β / ε | Nodos Expandidos | Longitud Camino | Costo Total | Tiempo (s) |
|--------|------------|-------|------------------|------------------|--------------|-------------|
| 1 | Beam Search | β = 3 | 187 | 25 | 37 | 0.015 |
| 2 | Beam Search | β = 5 | 305 | 22 | 30 | 0.020 |
| 3 | Dynamic A* | ε = 1.0 | 242 | 21 | 29 | 0.030 |
| 4 | Dynamic A* | ε = 2.0 | 190 | 21 | 32 | 0.025 |

**Observaciones:**
- Con β bajo, Beam Search sacrifica precisión por velocidad.  
- Dynamic Weighted A* genera caminos más consistentes y evita venenos costosos.  
- Un ε demasiado grande puede sobreestimar `h` y desviar el camino.  

---

## 🎨 Interfaz y Experiencia de Usuario

- **Visualización del recorrido:** la hormiga se anima paso a paso con color naranja.  
- **Ruta trazada:** línea amarilla une las celdas del camino encontrado.  
- **Panel lateral:** controles, estadísticas y parámetros dinámicos.  
- **Edición manual:** clic izquierdo para colocar elementos, sliders para ajustar valores.  

---

## 🧠 Conclusiones

- Se logró implementar con éxito una simulación visual de búsqueda informada.  
- **Beam Search** es rápido pero no garantiza soluciones óptimas.  
- **Dynamic Weighted A\*** ofrece equilibrio entre rendimiento y calidad de la ruta.  
- La penalización de **veneno (costo = 5)** influyó de forma visible en las decisiones del agente.  
- La interfaz gráfica permite comprender de forma intuitiva cómo los algoritmos priorizan la expansión de nodos.

---

## 💻 Ejecución

### **Requisitos**
```bash
pip install pygame
```

### **Ejecución del simulador**
```bash
cd src
python Main.py
```

### **Controles**
- **Beam Search / Dynamic A\*** → selecciona algoritmo.  
- **Play / Pause / Step** → controla animación.  
- **Reset / Clear / Save / Load** → gestiona el mapa.  
- **Sliders:**  
  - *Velocidad*  
  - *Beta (β)*  
  - *Epsilon (ε)*  

---

## 📂 Referencias

- Russell, S. & Norvig, P. (2021). *Artificial Intelligence: A Modern Approach.* 4th Edition.  
- Universidad del Valle – Guía de proyecto “Hormiga y Hongo Mágico”.  
- Documentación oficial de [Pygame](https://www.pygame.org/docs/).  
