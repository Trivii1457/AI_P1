Universidad del Valle
Escuela de Ingeniería de Sistemas y Computación
Introducción a la Inteligencia Artificial

# Primer Proyecto: La hormiga y el hongo mágico

![Table](/img/Problem.png)

Descripción
-----------
Vamos a resolver un problema clásico: una hormiga debe encontrar el hongo mágico recorriendo una matriz. En el mapa habrá casillas libres, obstáculos y casillas con veneno. La hormiga puede pasar por venenos (con coste o riesgo), y el objetivo es encontrar una ruta válida hacia el hongo.

El agente deberá implementar y comparar dos variaciones de búsqueda informada vistas en clase:

1. Beam Search
	 - Búsqueda informada que limita la cantidad de nodos que se mantienen por nivel (ancho de viga β).
	 - En cada paso solo se expanden los β nodos más prometedores según la función de evaluación (por ejemplo h(n) o f(n)).
	 - El resto de nodos se descartan permanentemente.

2. Dynamic Weighting (peso dinámico)
	 - En lugar de usar un ε fijo (como en Weighted A*), se ajusta dinámicamente el peso de la heurística según la profundidad.
	 - Ejemplo de función: f(n) = g(n) + h(n) + ε * (1 - d(n)/N) * h(n)
		 - d(n): profundidad del nodo n
		 - N: profundidad máxima estimada o una cota del problema
		 - ε: parámetro de escala inicial. Esto da más peso a h(n) al inicio y menos cerca del objetivo.

Requisitos obligatorios
----------------------
- La matriz (mapa) debe ser configurable: tamaño variable y posiciones de inicio, hongo, obstáculos y venenos.
- Debe tener una interfaz gráfica donde se vea la hormiga moviéndose; no se acepta solución solo por consola.
- La interfaz debe permitir al menos: crear/cargar un mapa, iniciar/pausar la simulación, ajustar velocidad y visualizar la ruta encontrada.
- Entregar código fuente, un README con instrucciones para ejecutar y una breve guía de uso de la GUI.

Requisitos de evaluación y notas importantes
--------------------------------------------
- La nota del proyecto es grupal; la defensa/sustentación es individual. Si durante la sustentación no se demuestra dominio mínimo, la nota individual puede bajar hasta 0.
- Lenguaje recomendado: Python (por practicidad) — no obligatorio. Si usan otro lenguaje, asegúrense de incluir instrucciones claras para ejecutar la GUI.
- Tamaño de grupos: 3 o 4 personas. No se aceptan parejas ni proyectos individuales este semestre.

Entregables
-----------
- Repositorio con código fuente y recursos.
- `README.md` con requisitos, pasos de instalación y cómo usar la GUI.
- Archivo o interface para configurar mapas (puede ser un JSON, CSV o editor visual dentro de la GUI).
- Presentación / demostración en la sustentación donde cada integrante explique parte del trabajo.

Características mínimas recomendadas de la GUI
---------------------------------------------
- Vista de cuadrícula (cada celda muestra estado: libre, obstáculo, veneno, inicio, objetivo).
- Animación de la hormiga moviéndose paso a paso.
- Controles: ejecutar/pausar/reset, avance paso a paso, control de velocidad.
- Mostrar métricas durante/tras la búsqueda: número de nodos expandidos, longitud de la ruta, coste total, tiempo de ejecución.
- Visualizar el conjunto de nodos conservados en Beam Search (por ejemplo colorear los β candidatos).
- Opción para superponer la heurística/valores f(n) en las celdas (opcional pero útil).

Sugerencias técnicas
--------------------
- Heurísticas: Manhattan o Euclidiana según el modelo de movimiento (4‑vecinos o 8‑vecinos).
- Representación del mapa: matriz 2D, donde cada celda tiene coste y tipos (normal, veneno con coste extra, obstáculo inaccesible).
- Para Dynamic Weighting: definir una N razonable (p. ej. tamaño máximo del mapa o una cota heurística) y permitir experimentar con ε.
- Tecnologías recomendadas para la GUI en Python:
	- tkinter (simple, viene con Python) — suficiente para una interfaz funcional.
	- Pygame (mejor para animaciones fluidas y control de frames).
	- PyQt/PySide (más completa, pero más trabajo de setup).
	- Alternativa web: HTML5 + JavaScript (canvas) si prefieren interfaz web.

Propuesta de experimento y análisis
----------------------------------
- Ejecutar ambos algoritmos sobre varios mapas (pequeño, mediano, grande) y distintos valores de β y ε.
- Métricas a comparar: coste de la solución, longitud, nodos expandidos, tiempo, completitud y optimalidad (cuando aplique).
- Presentar tablas o gráficos con resultados y comentar los trade-offs.

Plan / Cronograma sugerido (4–6 semanas)
-----------------------------------------
1. Diseño y división de tareas (1 semana): definir formato del mapa, API interna, y boceto de la GUI.
2. Implementación de la representación del mapa y heurísticas (1 semana).
3. Implementación de Beam Search y Dynamic Weighting (1–2 semanas).
4. Desarrollo de la GUI y la animación (1–2 semanas).
5. Pruebas, documentación y preparación de la sustentación (1 semana).

Rúbrica de evaluación (sugerida)
-------------------------------
- Implementación correcta de ambos algoritmos y funcionamiento: 40%
- Interfaz gráfica funcional y animación: 25%
- Experimentos y análisis comparativo: 15%
- Calidad del código, documentación y facilidad de uso: 10%
- Defensa individual y dominio de la solución en la sustentación: 10% (puede reducir nota individual si no se demuestra dominio)

Notas finales
------------
- Pueden incluir mejoras opcionales como guardar mapas, exportar estadísticas, o añadir niveles de dificultad.
- Documenten claramente cualquier decisión de diseño y asunciones en el `README.md`.

Buen trabajo y cualquier duda sobre el alcance o el formato de entrega me la consultan antes de avanzar demasiado.

