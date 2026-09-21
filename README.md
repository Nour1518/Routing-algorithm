# Multi-Algorithm Graph Routing Engine & GUI

A modular Python framework for graph generation, algorithmic pathfinding, and interactive visualization. The system combines a core graph processing engine, a stateless Flask REST API, a command-line interface (CLI), and a PyQt6 desktop client with a 2D graphics canvas.

---

## Architecture Overview

The system follows a strict **Separation of Concerns (SoC)** model, separating core graph computations, web delivery, and client interface layers:

                    PyQt6 APPLICATION
                             │
                     GraphVisualizer
                      (Coordinator)
                             │
            ┌────────────────┴────────────────┐
            │                                 │
      ControlPanel                        GraphView
  (UI Controls & Logic)              (2D Canvas / Items)
            │                                 │
      GraphAPIClient                          │
            │                                 │
            └────────────────┬────────────────┘
                             │
                       Flask REST API
                             │
                        Graph Engine
                 (Dijkstra, A*, BFS, CH)


---

## Key Features

* **Core Engine:**
  * Support for Generic, Random, Grid, and Geographical graph topologies.
  * Shortest-path algorithms: **Dijkstra**, **A\*** (Euclidean, Manhattan, Octile heuristics), **Bi-Dijkstra**, **Bi-A\***, and **BFS**.
  * Experimental **Contraction Hierarchies (CH)** module for accelerated preprocessing and routing.
* **Flask REST API:** Stateless HTTP JSON API isolating graph management and algorithm execution.
* **PyQt6 GUI Client:**
  * Interactive `QGraphicsView`/`QGraphicsScene` canvas supporting zoom, pan, and direct node selection.
  * Real-time route highlighting and execution metric displays.
* **CLI Interface:** Scriptable command-line tools for automated benchmarking and testing.


                 
