
from flask import Flask, request, jsonify

import math
import os
import uuid
import time

from BaseClass import Graph


def octile_heuristic(node_a, node_b):

    if not node_a.data or not node_b.data:

        return 0.0

    x1 = node_a.data.get("x")
    y1 = node_a.data.get("y")

    x2 = node_b.data.get("x")
    y2 = node_b.data.get("y")

    if None in (x1, y1, x2, y2):

        return 0.0

    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    # Cost of diagonal movement
    diagonal_cost = math.sqrt(2)

    return (

        max(dx, dy)

        +

        (diagonal_cost - 1)

        *

        min(dx, dy)

    )
def chebyshev_heuristic(node_a, node_b):

    if not node_a.data or not node_b.data:

        return 0.0

    x1 = node_a.data.get("x")
    y1 = node_a.data.get("y")

    x2 = node_b.data.get("x")
    y2 = node_b.data.get("y")

    if None in (x1, y1, x2, y2):

        return 0.0

    return max(

        abs(x2 - x1),

        abs(y2 - y1)

    )
def haversine_heuristic(node_a, node_b):

    # ====================================================
    # GET COORDINATES
    # ====================================================

    if not node_a.data or not node_b.data:

        return 0.0

    x1 = node_a.data.get("x")
    y1 = node_a.data.get("y")

    x2 = node_b.data.get("x")
    y2 = node_b.data.get("y")

    # Missing coordinates
    if None in (x1, y1, x2, y2):

        return 0.0

    # ====================================================
    # HAVERSINE
    #
    # Assumption:
    # x = longitude
    # y = latitude
    # ====================================================

    lat1 = math.radians(y1)
    lon1 = math.radians(x1)

    lat2 = math.radians(y2)
    lon2 = math.radians(x2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (

        math.sin(dlat / 2) ** 2

        +

        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2

    )

    c = (

        2
        *
        math.atan2(

            math.sqrt(a),

            math.sqrt(1 - a)

        )

    )

    # Earth radius in meters

    earth_radius = 6_371_000

    return earth_radius * c
# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# GRAPH STORAGE
# ============================================================

GRAPHS = {}


# ============================================================
# CONSTANTS
# ============================================================

ALGORITHMS = {
    "dijkstra",
    "a_star",
    "bidijkstra",
    "bi_a_star",
    "bfs",
    "ch",
}


GRAPH_TYPES = {
    "generic",
    "random",
    "geographical",
    "grid",
}


# ============================================================
# GRAPH GENERATION SCHEMA
# ============================================================
#
# This is used by the GUI.
#
# The GUI can request:
#
#     GET /graph-types
#
# and dynamically create the appropriate controls.
#
# ============================================================

GRAPH_SCHEMAS = {

    "generic": {

        "name": "Generic Graph",

        "description":
            "Graph containing isolated nodes. "
            "No edges are generated automatically.",

        "parameters": {

            "nodes": {
                "type": "integer",
                "label": "Nodes",
                "default": 100,
                "minimum": 1,
                "maximum": 100000,
            },

        },
    },

    "random": {

        "name": "Random Graph",

        "description":
            "Random graph generated using edge probability.",

        "parameters": {

            "nodes": {
                "type": "integer",
                "label": "Nodes",
                "default": 100,
                "minimum": 1,
                "maximum": 100000,
            },

            "probability": {
                "type": "float",
                "label": "Edge Probability",
                "default": 0.05,
                "minimum": 0.0,
                "maximum": 1.0,
                "step": 0.01,
            },

            "min_weight": {
                "type": "float",
                "label": "Minimum Weight",
                "default": 1.0,
                "minimum": 0.0,
                "step": 0.1,
            },

            "max_weight": {
                "type": "float",
                "label": "Maximum Weight",
                "default": 100.0,
                "minimum": 0.0,
                "step": 0.1,
            },

        },
    },

    "geographical": {

        "name": "Geographical Graph",

        "description":
            "Connected geographical graph using an MST "
            "and additional local edges.",

        "parameters": {

            "nodes": {
                "type": "integer",
                "label": "Nodes",
                "default": 100,
                "minimum": 2,
                "maximum": 10000,
            },

            "size": {
                "type": "float",
                "label": "Area Size",
                "default": 1000,
                "minimum": 1,
                "step": 10,
            },

            "min_dist": {
                "type": "float",
                "label": "Minimum Node Distance",
                "default": 10,
                "minimum": 0,
                "step": 1,
            },

            "radius": {
                "type": "float",
                "label": "Connection Radius",
                "default": 150,
                "minimum": 0,
                "step": 10,
            },

            "max_degree": {
                "type": "integer",
                "label": "Maximum Degree",
                "default": 4,
                "minimum": 1,
                "maximum": 100,
            },

        },
    },

    "grid": {

        "name": "Grid Graph",

        "description":
            "Rectangular grid graph.",

        "parameters": {

            "rows": {
                "type": "integer",
                "label": "Rows",
                "default": 10,
                "minimum": 1,
                "maximum": 1000,
            },

            "cols": {
                "type": "integer",
                "label": "Columns",
                "default": 10,
                "minimum": 1,
                "maximum": 1000,
            },

            "weight": {
                "type": "float",
                "label": "Edge Weight",
                "default": 1.0,
                "minimum": 0.0,
                "step": 0.1,
            },

            "diagonal": {
                "type": "boolean",
                "label": "Allow Diagonal Edges",
                "default": False,
            },

        },
    },
}


# ============================================================
# ALGORITHM SCHEMA
# ============================================================

ALGORITHM_SCHEMAS = {

    "dijkstra": {
        "name": "Dijkstra",
        "description": "Shortest path using Dijkstra's algorithm.",
        "requires_ch": False,
    },

    "a_star": {
        "name": "A*",
        "description": "A* shortest path search.",
        "requires_ch": False,
    },

    "bidijkstra": {
        "name": "Bidirectional Dijkstra",
        "description": "Bidirectional Dijkstra search.",
        "requires_ch": False,
    },

    "bi_a_star": {
        "name": "Bidirectional A*",
        "description": "Bidirectional A* search.",
        "requires_ch": False,
    },

    "bfs": {
        "name": "BFS",
        "description": "Breadth-first search.",
        "requires_ch": False,
    },

    "ch": {
        "name": "Contraction Hierarchy",
        "description": "Shortest path using Contraction Hierarchies.",
        "requires_ch": True,
    },
}


# ============================================================
# TYPE CONVERSION HELPERS
# ============================================================

def parse_bool(value, default=False):

    if value is None:
        return default

    if isinstance(value, bool):
        return value

    if isinstance(value, str):

        value = value.strip().lower()

        if value in {
            "true",
            "1",
            "yes",
            "on"
        }:
            return True

        if value in {
            "false",
            "0",
            "no",
            "off"
        }:
            return False

    if isinstance(value, int):
        return value != 0

    raise ValueError(
        f"Invalid boolean value: {value}"
    )


def get_int(
    data,
    name,
    default=None,
    minimum=None,
    maximum=None
):

    if name not in data:

        if default is None:
            raise ValueError(
                f"Missing '{name}'."
            )

        value = default

    else:

        try:
            value = int(data[name])

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"'{name}' must be an integer."
            )

    if minimum is not None and value < minimum:

        raise ValueError(
            f"'{name}' must be >= {minimum}."
        )

    if maximum is not None and value > maximum:

        raise ValueError(
            f"'{name}' must be <= {maximum}."
        )

    return value


def get_float(
    data,
    name,
    default=None,
    minimum=None,
    maximum=None
):

    if name not in data:

        if default is None:
            raise ValueError(
                f"Missing '{name}'."
            )

        value = default

    else:

        try:
            value = float(data[name])

        except (
            TypeError,
            ValueError
        ):

            raise ValueError(
                f"'{name}' must be a number."
            )

    if minimum is not None and value < minimum:

        raise ValueError(
            f"'{name}' must be >= {minimum}."
        )

    if maximum is not None and value > maximum:

        raise ValueError(
            f"'{name}' must be <= {maximum}."
        )

    return value


# ============================================================
# HEURISTICS
# ============================================================

def geographical_heuristic(a, b):

    data_a = a.data or {}
    data_b = b.data or {}

    xa = data_a.get("x")
    ya = data_a.get("y")

    xb = data_b.get("x")
    yb = data_b.get("y")

    if (
        xa is None
        or ya is None
        or xb is None
        or yb is None
    ):
        return 0.0

    return math.hypot(
        xa - xb,
        ya - yb
    )


def grid_heuristic(a, b):

    data_a = a.data or {}
    data_b = b.data or {}

    row_a = data_a.get("row")
    col_a = data_a.get("col")

    row_b = data_b.get("row")
    col_b = data_b.get("col")

    if (
        row_a is None
        or col_a is None
        or row_b is None
        or col_b is None
    ):
        return 0.0

    return (
        abs(row_a - row_b)
        +
        abs(col_a - col_b)
    )


def zero_heuristic(a, b):

    return 0.0

def get_heuristic(
    graph,
    heuristic_name=None
):

    # --------------------------------------------------------
    # USER SELECTED HEURISTIC
    # --------------------------------------------------------

    if heuristic_name:

        heuristics = {

            "zero": zero_heuristic,

            "euclidean": geographical_heuristic,

            "geographical": geographical_heuristic,

            "haversine": haversine_heuristic,

            "manhattan": grid_heuristic,

            "grid": grid_heuristic,
            "chebyshev": chebyshev_heuristic,
            "octile": octile_heuristic,


        }

        heuristic = heuristics.get(
            heuristic_name.lower()
        )

        if heuristic is None:

            raise ValueError(
                f"Unknown heuristic: {heuristic_name}"
            )

        return heuristic

    # --------------------------------------------------------
    # AUTOMATIC SELECTION
    # --------------------------------------------------------

    graph_type = getattr(
        graph,
        "graph_type",
        "generic"
    )

    if graph_type in {
        "geographical",
        "road"
    }:

        return geographical_heuristic

    if graph_type == "grid":

        return grid_heuristic

    return zero_heuristic
# ============================================================
# GRAPH STATISTICS
# ============================================================

def graph_statistics(graph):

    node_count = len(
        graph.nodes
    )

    directed = graph.directed

    adjacency_edges = sum(
        len(edges)
        for edges in graph.adjacency.values()
    )

    if directed:

        edge_count = adjacency_edges

    else:

        edge_count = adjacency_edges // 2

    max_degree = 0

    if graph.nodes:

        max_degree = max(
            len(
                graph.adjacency[node_id]
            )
            for node_id in graph.nodes
        )

    average_degree = (

        adjacency_edges / node_count

        if node_count

        else 0
    )

    return {

        "nodes": node_count,

        "edges": edge_count,

        "directed": directed,

        "graph_type":
            getattr(
                graph,
                "graph_type",
                "generic"
            ),

        "average_degree":
            average_degree,

        "max_degree":
            max_degree,

        "ch_ready":
            getattr(
                graph,
                "ch_ready",
                False
            ),

    }


# ============================================================
# PATH STATISTICS
# ============================================================

def path_statistics(
    graph,
    path
):

    if not path:

        return {

            "path_nodes": 0,

            "path_edges": 0,

            "path_length": None,

        }

    path_edges = max(
        0,
        len(path) - 1
    )

    path_length = 0.0

    for source, target in zip(
        path,
        path[1:]
    ):

        found = False

        for edge in graph.neighbors(
            source
        ):

            if edge.target.id == target:

                path_length += edge.weight

                found = True

                break

        if not found:

            # CH may contain shortcut edges.

            path_length = None

            break

    return {

        "path_nodes": len(path),

        "path_edges": path_edges,

        "path_length": path_length,

    }


# ============================================================
# SOLVE GRAPH
# ============================================================
def solve_graph(
    graph,
    start,
    goal,
    algorithm,
    heuristic_name=None,
    collect_trace=False
):

    if start not in graph.nodes:

        raise ValueError(
            f"Start node {start} does not exist."
        )

    if goal not in graph.nodes:

        raise ValueError(
            f"Goal node {goal} does not exist."
        )

    if algorithm not in ALGORITHMS:

        raise ValueError(
            f"Unknown algorithm: {algorithm}"
        )

    # ========================================================
    # HEURISTIC
    # ========================================================

    heuristic = None

    if algorithm in {
        "a_star",
        "bi_a_star",
    }:

        heuristic = get_heuristic(
            graph,
            heuristic_name
        )

    trace = None

    start_time = time.perf_counter()

    # --------------------------------------------------------
    # DIJKSTRA
    # --------------------------------------------------------

    if algorithm == "dijkstra":

        if (
            collect_trace
            and
            hasattr(
                graph,
                "dijkstra_visual"
            )
        ):

            path, cost, trace = (
                graph.dijkstra_visual(
                    start,
                    goal
                )
            )

        else:

            path, cost = graph.dijkstra(
                start,
                goal
            )

    # --------------------------------------------------------
    # A*
    # --------------------------------------------------------

    elif algorithm == "a_star":

        if (
            collect_trace
            and
            hasattr(
                graph,
                "a_star_visual"
            )
        ):

            path, cost, trace = (
                graph.a_star_visual(
                    start,
                    goal,
                    heuristic_name=heuristic,
                )
            )

        else:

            path, cost = graph.a_star(
                start,
                goal,
                heuristic=heuristic
            )

    # --------------------------------------------------------
    # BIDIRECTIONAL DIJKSTRA
    # --------------------------------------------------------

    elif algorithm == "bidijkstra":

        if (
            collect_trace
            and
            hasattr(
                graph,
                "bidirectional_dijkstra_visual"
            )
        ):

            path, cost, trace = (
                graph.bidirectional_dijkstra_visual(
                    start,
                    goal
                )
            )

        else:

            path, cost = (
                graph.bidirectional_dijkstra(
                    start,
                    goal
                )
            )

    # --------------------------------------------------------
    # BIDIRECTIONAL A*
    # --------------------------------------------------------

    elif algorithm == "bi_a_star":

        if (
            collect_trace
            and
            hasattr(
                graph,
                "bidirectional_a_star_visual"
            )
        ):

            path, cost, trace = (
                graph.bidirectional_a_star_visual(
                    start,
                    goal,
                    heuristic=heuristic
                )
            )

        else:

            path, cost = (
                graph.bidirectional_a_star(
                    start,
                    goal,
                    heuristic=heuristic
                )
            )

    # --------------------------------------------------------
    # BFS
    # --------------------------------------------------------

    elif algorithm == "bfs":

        path, cost = graph.bfs(
            start,
            goal
        )

    # --------------------------------------------------------
    # CH
    # --------------------------------------------------------

    elif algorithm == "ch":

        if not getattr(
            graph,
            "ch_ready",
            False
        ):

            raise RuntimeError(
                "CH is not ready. "
                "Build the contraction hierarchy first."
            )

        path, cost = (
            graph.contraction_hierarchy(
                start,
                goal
            )
        )

    else:

        raise ValueError(
            f"Unsupported algorithm: {algorithm}"
        )

    elapsed = (
        time.perf_counter()
        -
        start_time
    )

    return (
        path,
        cost,
        trace,
        elapsed
    )


# ============================================================
# GENERATE GRAPH
# ============================================================

def generate_graph(data):

    graph_type = data.get(
        "type"
    )

    if not graph_type:

        raise ValueError(
            "Missing 'type'."
        )

    if graph_type not in GRAPH_TYPES:

        raise ValueError(
            f"Unsupported graph type: {graph_type}. "
            f"Available types: {sorted(GRAPH_TYPES)}"
        )

    directed = parse_bool(
        data.get(
            "directed",
            False
        )
    )

    # ========================================================
    # GENERIC
    # ========================================================

    if graph_type == "generic":

        nodes = get_int(
            data,
            "nodes",
            default=100,
            minimum=1,
            maximum=100000
        )

        graph = Graph(
            directed=directed,
            graph_type="generic"
        )

        for node_id in range(nodes):

            graph.add_node(
                node_id,
                {}
            )

        return graph

    # ========================================================
    # RANDOM
    # ========================================================

    if graph_type == "random":

        nodes = get_int(
            data,
            "nodes",
            default=100,
            minimum=1,
            maximum=100000
        )

        probability = get_float(
            data,
            "probability",
            default=0.05,
            minimum=0.0,
            maximum=1.0
        )

        min_weight = get_float(
            data,
            "min_weight",
            default=1.0,
            minimum=0.0
        )

        max_weight = get_float(
            data,
            "max_weight",
            default=100.0,
            minimum=0.0
        )

        if min_weight > max_weight:

            raise ValueError(
                "'min_weight' cannot be greater "
                "than 'max_weight'."
            )

        graph = Graph(
            directed=directed,
            graph_type="random"
        )

        graph.generate_random(
            n=nodes,
            edge_probability=probability,
            min_weight=min_weight,
            max_weight=max_weight
        )

        return graph

    # ========================================================
    # GEOGRAPHICAL
    # ========================================================

    if graph_type == "geographical":

        nodes = get_int(
            data,
            "nodes",
            default=100,
            minimum=2,
            maximum=10000
        )

        size = get_float(
            data,
            "size",
            default=1000,
            minimum=1
        )

        min_dist = get_float(
            data,
            "min_dist",
            default=10,
            minimum=0
        )

        radius = get_float(
            data,
            "radius",
            default=150,
            minimum=0
        )

        max_degree = get_int(
            data,
            "max_degree",
            default=4,
            minimum=1,
            maximum=100
        )

        graph = Graph(
            directed=directed,
            graph_type="geographical"
        )

        graph.build_geographical(
            n=nodes,
            size=size,
            min_dist=min_dist,
            radius=radius,
            max_degree=max_degree
        )

        return graph

    # ========================================================
    # GRID
    # ========================================================

    if graph_type == "grid":

        rows = get_int(
            data,
            "rows",
            default=10,
            minimum=1,
            maximum=1000
        )

        cols = get_int(
            data,
            "cols",
            default=10,
            minimum=1,
            maximum=1000
        )

        weight = get_float(
            data,
            "weight",
            default=1.0,
            minimum=0
        )

        diagonal = parse_bool(
            data.get(
                "diagonal",
                False
            )
        )

        graph = Graph(
            directed=directed,
            graph_type="grid"
        )

        graph.build_grid(
            rows=rows,
            cols=cols,
            weight=weight,
            diagonal=diagonal
        )

        return graph

    raise ValueError(
        f"Unsupported graph type: {graph_type}"
    )


# ============================================================
# BUILD CH
# ============================================================

def build_ch(graph):

    start_time = time.perf_counter()

    statistics = (
        graph.build_contraction_hierarchy()
    )

    elapsed = (
        time.perf_counter()
        -
        start_time
    )

    return {

        "time_seconds": elapsed,

        "statistics": statistics,

        "ch_ready":
            getattr(
                graph,
                "ch_ready",
                False
            ),

    }


# ============================================================
# CREATE GRAPH ID
# ============================================================

def create_graph_id():

    return uuid.uuid4().hex


# ============================================================
# HEALTH
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def index():

    return jsonify({

        "service":
            "Graph Routing API",

        "status":
            "running",

        "graphs_loaded":
            len(GRAPHS),

        "algorithms":
            sorted(ALGORITHMS),

        "graph_types":
            sorted(GRAPH_TYPES),

    })


# ============================================================
# GRAPH TYPES
# ============================================================
#
# GUI uses this endpoint to build the generation controls.
#
# ============================================================

@app.route(
    "/graph-types",
    methods=["GET"]
)
def graph_types():

    return jsonify({

        "success": True,

        "types":
            GRAPH_SCHEMAS,

        "directed_supported":
            True,

    })


# ============================================================
# ALGORITHMS
# ============================================================

@app.route(
    "/algorithms",
    methods=["GET"]
)
def algorithms():

    return jsonify({

        "success": True,

        "algorithms":
            ALGORITHM_SCHEMAS,

    })


# ============================================================
# LIST GRAPHS
# ============================================================

@app.route(
    "/graphs",
    methods=["GET"]
)
def list_graphs():

    result = []

    for graph_id, graph in GRAPHS.items():

        result.append({

            "id": graph_id,

            **graph_statistics(graph)

        })

    return jsonify({

        "count": len(result),

        "graphs": result

    })


# ============================================================
# GENERATE GRAPH
# ============================================================

@app.route(
    "/graphs/generate",
    methods=["POST"]
)
def api_generate_graph():

    try:

        data = request.get_json(
            silent=True
        )

        if not isinstance(
            data,
            dict
        ):

            return jsonify({

                "success": False,

                "error":
                    "Request body must be a JSON object."

            }), 400

        graph = generate_graph(
            data
        )

        # ----------------------------------------------------
        # OPTIONAL CH
        # ----------------------------------------------------

        ch_info = None

        if parse_bool(
            data.get(
                "build_ch",
                False
            )
        ):

            ch_info = build_ch(
                graph
            )

        graph_id = create_graph_id()

        GRAPHS[graph_id] = graph

        return jsonify({

            "success": True,

            "id": graph_id,

            "graph":
                graph_statistics(graph),

            "ch":
                ch_info

        }), 201

    except Exception as exc:

        return jsonify({

            "success": False,

            "error": str(exc)

        }), 400


# ============================================================
# LOAD GRAPH
# ============================================================

@app.route(
    "/graphs/load",
    methods=["POST"]
)
def api_load_graph():

    try:

        data = request.get_json(
            silent=True
        )

        if not isinstance(
            data,
            dict
        ):

            return jsonify({

                "success": False,

                "error":
                    "Request body must be a JSON object."

            }), 400

        filename = data.get(
            "filename"
        )

        if not filename:

            return jsonify({

                "success": False,

                "error":
                    "Missing 'filename'."

            }), 400

        if not os.path.exists(
            filename
        ):

            return jsonify({

                "success": False,

                "error":
                    f"File not found: {filename}"

            }), 404

        graph = Graph()

        graph.load(
            filename
        )

        # ----------------------------------------------------
        # OPTIONAL CH
        # ----------------------------------------------------

        ch_info = None

        if parse_bool(
            data.get(
                "build_ch",
                False
            )
        ):

            ch_info = build_ch(
                graph
            )

        graph_id = create_graph_id()

        GRAPHS[graph_id] = graph

        return jsonify({

            "success": True,

            "id": graph_id,

            "graph":
                graph_statistics(graph),

            "ch":
                ch_info

        }), 201

    except Exception as exc:

        return jsonify({

            "success": False,

            "error": str(exc)

        }), 400


# ============================================================
# GET GRAPH INFORMATION
# ============================================================

@app.route(
    "/graphs/<graph_id>",
    methods=["GET"]
)
def api_graph_info(
    graph_id
):

    graph = GRAPHS.get(
        graph_id
    )

    if graph is None:

        return jsonify({

            "success": False,

            "error":
                "Graph not found."

        }), 404

    return jsonify({

        "success": True,

        "id": graph_id,

        "graph":
            graph_statistics(graph)

    })


# ============================================================
# ROUTE QUERY
# ============================================================
@app.route(
    "/graphs/<graph_id>/route",
    methods=["POST"]
)
def api_route(
    graph_id
):

    graph = GRAPHS.get(
        graph_id
    )

    if graph is None:

        return jsonify({

            "success": False,

            "error":
                "Graph not found."

        }), 404

    # ====================================================
    # REQUEST DATA
    # ====================================================

    data = request.get_json(
        silent=True
    )

    print("\n========== ROUTE REQUEST ==========")
    print("Graph ID:", graph_id)
    print("Request data:", data)
    print("===================================\n")

    if not isinstance(
        data,
        dict
    ):

        raise ValueError(
            "Request body must be a JSON object."
        )

    # ====================================================
    # VALIDATE START
    # ====================================================

    if "start" not in data:

        raise ValueError(
            "Missing 'start'."
        )

    # ====================================================
    # VALIDATE GOAL
    # ====================================================

    if "goal" not in data:

        raise ValueError(
            "Missing 'goal'."
        )

    start = int(
        data["start"]
    )

    goal = int(
        data["goal"]
    )

    # ====================================================
    # ALGORITHM
    # ====================================================

    algorithm = data.get(
        "algorithm",
        "dijkstra"
    )

    # ====================================================
    # TRACE
    # ====================================================

    trace_requested = parse_bool(
        data.get(
            "trace",
            False
        )
    )

    # ====================================================
    # OPTIONAL HEURISTIC
    # ====================================================

    heuristic = None

    if algorithm in {

        "a_star",
        "bi_a_star",

    }:

        heuristic = data.get(
            "heuristic",
            "zero"
        )

    print("Start:", start)
    print("Goal:", goal)
    print("Algorithm:", algorithm)
    print("Heuristic:", heuristic)
    print("Trace:", trace_requested)

    # ====================================================
    # SOLVE GRAPH
    # ====================================================

    (
        path,
        cost,
        trace,
        elapsed
    ) = solve_graph(

        graph=graph,

        start=start,

        goal=goal,

        algorithm=algorithm,

        # IMPORTANT:
        # This must match solve_graph parameter name
        heuristic_name=heuristic,

        collect_trace=trace_requested

    )

    # ====================================================
    # PATH STATISTICS
    # ====================================================

    statistics = path_statistics(

        graph,
        path

    )

    # ====================================================
    # RESPONSE QUERY
    # ====================================================

    query = {

        "start": start,

        "goal": goal,

        "algorithm": algorithm,

    }

    if heuristic is not None:

        query["heuristic"] = heuristic

    # ====================================================
    # RESPONSE
    # ====================================================

    return jsonify({

        "success": True,

        "graph_id":
            graph_id,

        "query":
            query,

        "result": {

            "found":
                path is not None,

            "cost": (

                cost

                if path is not None

                else None

            ),

            "time_seconds":
                elapsed,

            "path":
                path,

            **statistics

        },

        "trace":
            trace

    })


# ============================================================
# BUILD CH
# ============================================================

@app.route(
    "/graphs/<graph_id>/ch",
    methods=["POST"]
)
def api_build_ch(
    graph_id
):

    graph = GRAPHS.get(
        graph_id
    )

    if graph is None:

        return jsonify({

            "success": False,

            "error":
                "Graph not found."

        }), 404

    try:

        result = build_ch(
            graph
        )

        return jsonify({

            "success": True,

            "graph_id":
                graph_id,

            "ch":
                result

        })

    except Exception as exc:

        return jsonify({

            "success": False,

            "error":
                str(exc)

        }), 400


# ============================================================
# SAVE GRAPH
# ============================================================

@app.route(
    "/graphs/<graph_id>/save",
    methods=["POST"]
)
def api_save_graph(
    graph_id
):

    graph = GRAPHS.get(
        graph_id
    )

    if graph is None:

        return jsonify({

            "success": False,

            "error":
                "Graph not found."

        }), 404

    try:

        data = request.get_json(
            silent=True
        )

        if not isinstance(
            data,
            dict
        ):

            return jsonify({

                "success": False,

                "error":
                    "Request body must be a JSON object."

            }), 400

        filename = data.get(
            "filename"
        )

        if not filename:

            return jsonify({

                "success": False,

                "error":
                    "Missing 'filename'."

            }), 400

        graph.save(
            filename
        )

        return jsonify({

            "success": True,

            "graph_id":
                graph_id,

            "filename":
                filename,

            "graph":
                graph_statistics(graph)

        })

    except Exception as exc:

        return jsonify({

            "success": False,

            "error":
                str(exc)

        }), 400


# ============================================================
# DELETE GRAPH
# ============================================================

@app.route(
    "/graphs/<graph_id>",
    methods=["DELETE"]
)
def api_delete_graph(
    graph_id
):

    if graph_id not in GRAPHS:

        return jsonify({

            "success": False,

            "error":
                "Graph not found."

        }), 404

    del GRAPHS[
        graph_id
    ]

    return jsonify({

        "success": True,

        "deleted":
            graph_id

    })


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(404)
def not_found(error):

    return jsonify({

        "success": False,

        "error":
            "Endpoint not found."

    }), 404


@app.errorhandler(405)
def method_not_allowed(error):

    return jsonify({

        "success": False,

        "error":
            "HTTP method not allowed."

    }), 405










# ============================================================
# GRAPH SERIALIZATION
# ============================================================

def graph_structure(graph):

    nodes = []

    edges = []

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    for node_id, node in graph.nodes.items():

        nodes.append({

            "id": node_id,

            "data": node.data or {}

        })

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    seen_edges = set()

    for source_id, edge_list in graph.adjacency.items():

        for edge in edge_list:

            source = edge.source.id
            target = edge.target.id

            # ------------------------------------------------
            # UNDIRECTED GRAPH
            #
            # add_edge() creates:
            #
            # A -> B
            # B -> A
            #
            # We only want to send one visual edge.
            # ------------------------------------------------

            if not graph.directed:

                edge_key = tuple(
                    sorted(
                        (source, target)
                    )
                )

                if edge_key in seen_edges:
                    continue

                seen_edges.add(
                    edge_key
                )

            edges.append({

                "source": source,

                "target": target,

                "weight": edge.weight

            })

    return {

        "nodes": nodes,

        "edges": edges

    }





# ============================================================
# GET GRAPH STRUCTURE
# ============================================================
@app.route(
    "/graphs/<graph_id>/structure",
    methods=["GET"]
)
def api_graph_structure(
    graph_id
):

    graph = GRAPHS.get(
        graph_id
    )

    if graph is None:

        return jsonify({

            "success": False,

            "error":
                "Graph not found."

        }), 404

    nodes = []

    for node_id, node in graph.nodes.items():

        nodes.append({

            "id":
                node_id,

            "data":
                node.data or {}

        })

    edges = []

    seen = set()

    for source_id, edge_list in graph.adjacency.items():

        for edge in edge_list:

            source = edge.source.id

            target = edge.target.id

            # ------------------------------------------------
            # Avoid duplicate edges in undirected graphs
            # ------------------------------------------------

            if not graph.directed:

                edge_key = tuple(
                    sorted(
                        (
                            source,
                            target
                        )
                    )
                )

                if edge_key in seen:

                    continue

                seen.add(
                    edge_key
                )

            edges.append({

                "source":
                    source,

                "target":
                    target,

                "weight":
                    edge.weight

            })

    return jsonify({

        "success": True,

        "id":
            graph_id,

        "graph": {

            "nodes":
                nodes,

            "edges":
                edges

        }

    })

# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    app.run(

        host="0.0.0.0",

        port=5000,

        debug=True

    )


