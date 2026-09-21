This project was developed in collaboration with ESSE Lab (Sfax) as part of an internship project. The work focuses on the development and experimental evaluation of a modular graph-routing framework, with support for multiple graph structures, routing algorithms, heuristics, and interfaces



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






# Benchmark Results

The routing framework was tested with several graph structures and routing algorithms in order to evaluate execution time, path optimality, and the influence of heuristics.

## Tested Algorithms

| Algorithm              | Description                                       |
| ---------------------- | ------------------------------------------------- |
| Dijkstra               | Weighted shortest-path search                     |
| A*                     | Dijkstra guided by a heuristic                    |
| Bidirectional Dijkstra | Search performed from both source and destination |
| Bidirectional A*       | Bidirectional search using heuristics             |
| BFS                    | Breadth-first search                              |

### A* Heuristics

| Heuristic | Main use                             |
| --------- | ------------------------------------ |
| Zero      | Reference without heuristic guidance |
| Euclidean | Geometric graphs                     |
| Manhattan | Grid-like movement                   |
| Octile    | Grids allowing diagonal movement     |

---

## Graphs Tested

Three main graph families were used.

| Graph type   |   Sizes tested | Purpose                    |
| ------------ | -------------: | -------------------------- |
| Random       | 100–1000 nodes | General graph performance  |
| Grid         |  100–900 nodes | Heuristic evaluation       |
| Geographical | 100–1000 nodes | Spatial routing evaluation |

For random graphs, the edge probability was reduced as the number of nodes increased to keep the graph size manageable.

| Graph       | Nodes | Approx. edges |
| ----------- | ----: | ------------: |
| Random 100  |   100 |          ~400 |
| Random 250  |   250 |         ~1280 |
| Random 500  |   500 |         ~1880 |
| Random 1000 |  1000 |         ~2540 |

---

## Main Results

### Random Graphs

The random graphs do not have a meaningful relationship between node coordinates and edge costs.

| Algorithm              | Observed behavior                                       |
| ---------------------- | ------------------------------------------------------- |
| Dijkstra               | Stable and predictable performance                      |
| A* Zero                | Similar principle to Dijkstra, with additional overhead |
| A* Euclidean           | Limited benefit                                         |
| A* Manhattan           | Limited benefit                                         |
| A* Octile              | Limited benefit                                         |
| Bidirectional Dijkstra | Very good performance in the tested cases               |
| Bidirectional A*       | Higher execution time in several tests                  |
| BFS                    | Very fast, but not optimal for weighted graphs          |

Example execution times:

| Nodes |    Dijkstra | Bidirectional Dijkstra |         BFS |
| ----: | ----------: | ---------------------: | ----------: |
|   100 | ~0.4–0.8 ms |            ~0.2–0.5 ms | ~0.2–0.3 ms |
|   500 |     ~1–2 ms |            ~0.5–0.8 ms | ~0.5–0.8 ms |
|  1000 | ~3.3–4.5 ms |                ~0.8 ms |       ~1 ms |

**Observation:** geometric heuristics do not necessarily improve A* on random graphs because the coordinates do not necessarily represent the actual routing cost.

---

## Grid Graphs

Grid graphs provide a more suitable environment for evaluating geometric heuristics.

| Grid    | Nodes |
| ------- | ----: |
| 10 × 10 |   100 |
| 20 × 20 |   400 |
| 30 × 30 |   900 |

The results show that heuristic selection has a stronger effect on regular grids.

| Heuristic | Suitable structure                |
| --------- | --------------------------------- |
| Manhattan | Horizontal/vertical grid movement |
| Euclidean | Geometric movement                |
| Octile    | Grid movement with diagonals      |
| Zero      | Baseline/reference                |

For diagonal grids, **Euclidean and Octile heuristics** showed better behavior than A* without heuristic guidance in several tests.

---

## Geographical Graphs

Geographical graphs contain spatial coordinates, making geometric heuristics more meaningful.

| Heuristic | Observed behavior                          |
| --------- | ------------------------------------------ |
| Zero      | Optimal, but behaves similarly to Dijkstra |
| Euclidean | Optimal in the tested cases                |
| Octile    | Optimal in the tested cases                |
| Manhattan | Can produce non-optimal paths              |

Manhattan produced different optimality rates in some tests:

| Observed optimality |
| ------------------: |
|              66.67% |
|              33.33% |
|                  0% |

This demonstrates that **an inappropriate heuristic can reduce the search effort while producing a non-optimal path**.

---

## BFS

BFS does not consider edge weights and instead minimizes the number of edges.

| Graph type             | Observed optimality |
| ---------------------- | ------------------: |
| Uniform-weight grids   |                100% |
| Weighted random graphs |                  0% |

This behavior is expected:

* With equal edge weights, minimizing the number of edges also minimizes the total cost.
* With different edge weights, the path with fewer edges is not necessarily the cheapest path.

---

## Overall Comparison

| Algorithm              | Speed                     | Optimality               | Dependency on graph structure |
| ---------------------- | ------------------------- | ------------------------ | ----------------------------- |
| Dijkstra               | Good                      | Yes                      | Low                           |
| A* Zero                | Moderate                  | Yes                      | Low                           |
| A* Euclidean           | Variable                  | If heuristic is suitable | High                          |
| A* Manhattan           | Variable                  | Depends on graph         | High                          |
| A* Octile              | Variable                  | If heuristic is suitable | High                          |
| Bidirectional Dijkstra | Very good in tested cases | Yes                      | Medium                        |
| Bidirectional A*       | Variable                  | Depends on heuristic     | High                          |
| BFS                    | Very fast                 | Conditional              | High                          |

---

## Key Findings

1. **Dijkstra provides a reliable reference** for weighted shortest-path problems.
2. **A* performance strongly depends on the heuristic.**
3. Geometric heuristics are more useful on **grid and geographical graphs** than on random graphs.
4. **Octile is particularly suitable for grids with diagonal movement.**
5. **BFS is very fast**, but it is not suitable for general weighted shortest-path problems.
6. **Bidirectional Dijkstra performed very well** in several of the tested scenarios.
7. Increasing graph size generally increases execution time, but the number and structure of edges also have a significant influence.
8. No single algorithm consistently provides the same behavior on every graph type.

> These results are specific to the tested graph structures, sizes, edge distributions, and implementation. They are intended to demonstrate the behavior of the framework rather than establish a universal ranking of routing algorithms.


                 
