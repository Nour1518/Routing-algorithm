# GraphBenchmark.py

import argparse
import csv
import math
import random
import time

from BaseClass import Graph


# ============================================================
# HEURISTICS
# ============================================================

def zero_heuristic(node_a, node_b):
    return 0.0


def _xy(node):
    if not node or not getattr(node, "data", None):
        return None

    data = node.data

    x = data.get("x")
    y = data.get("y")

    if x is not None and y is not None:
        return float(x), float(y)

    row = data.get("row")
    col = data.get("col")

    if row is not None and col is not None:
        return float(col), float(row)

    return None


def euclidean_heuristic(node_a, node_b):
    a = _xy(node_a)
    b = _xy(node_b)

    if a is None or b is None:
        return 0.0

    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return math.hypot(dx, dy)


def manhattan_heuristic(node_a, node_b):
    a = _xy(node_a)
    b = _xy(node_b)

    if a is None or b is None:
        return 0.0

    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def chebyshev_heuristic(node_a, node_b):
    a = _xy(node_a)
    b = _xy(node_b)

    if a is None or b is None:
        return 0.0

    return max(
        abs(a[0] - b[0]),
        abs(a[1] - b[1])
    )


def octile_heuristic(node_a, node_b):
    a = _xy(node_a)
    b = _xy(node_b)

    if a is None or b is None:
        return 0.0

    dx = abs(a[0] - b[0])
    dy = abs(a[1] - b[1])

    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


def haversine_heuristic(node_a, node_b):
    if not node_a or not node_b:
        return 0.0

    data_a = getattr(node_a, "data", {}) or {}
    data_b = getattr(node_b, "data", {}) or {}

    lat1 = data_a.get("lat")
    lon1 = data_a.get("lon")

    lat2 = data_b.get("lat")
    lon2 = data_b.get("lon")

    if None in (lat1, lon1, lat2, lon2):
        return 0.0

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return 6371000 * c


HEURISTICS = {
    "zero": zero_heuristic,
    "euclidean": euclidean_heuristic,
    "manhattan": manhattan_heuristic,
    "chebyshev": chebyshev_heuristic,
    "octile": octile_heuristic,
    "haversine": haversine_heuristic,
}


# ============================================================
# ALGORITHMS
# ============================================================

ALGORITHMS = [
    ("dijkstra", None),

    ("a_star", "zero"),
    ("a_star", "euclidean"),
    ("a_star", "manhattan"),
    ("a_star", "octile"),

    ("bidijkstra", None),

    ("bi_a_star", "zero"),
    ("bi_a_star", "euclidean"),
    ("bi_a_star", "manhattan"),
    ("bi_a_star", "octile"),

    ("bfs", None),
]


# ============================================================
# GRAPH SCENARIOS
# ============================================================

def get_scenarios():
    """
    Maximum graph size = 1000 nodes.

    Random graph probability decreases as node count increases.
    """

    return [

        # ----------------------------------------------------
        # RANDOM GRAPHS
        # ----------------------------------------------------

        {
            "name": "random_100",
            "type": "random",
            "nodes": 100,
            "probability": 0.08,
            "directed": False,
            "condition": "sparse",
        },

        {
            "name": "random_250",
            "type": "random",
            "nodes": 250,
            "probability": 0.04,
            "directed": False,
            "condition": "sparse",
        },

        {
            "name": "random_500",
            "type": "random",
            "nodes": 500,
            "probability": 0.015,
            "directed": False,
            "condition": "sparse",
        },

        {
            "name": "random_1000",
            "type": "random",
            "nodes": 1000,
            "probability": 0.005,
            "directed": False,
            "condition": "sparse",
        },

        # ----------------------------------------------------
        # GRIDS
        # ----------------------------------------------------

        {
            "name": "grid_10x10",
            "type": "grid",
            "rows": 10,
            "cols": 10,
            "diagonal": False,
            "directed": False,
            "condition": "4-neighbor",
        },

        {
            "name": "grid_20x20",
            "type": "grid",
            "rows": 20,
            "cols": 20,
            "diagonal": False,
            "directed": False,
            "condition": "4-neighbor",
        },

        {
            "name": "grid_30x30",
            "type": "grid",
            "rows": 30,
            "cols": 30,
            "diagonal": False,
            "directed": False,
            "condition": "4-neighbor",
        },

        {
            "name": "grid_20x20_diagonal",
            "type": "grid",
            "rows": 20,
            "cols": 20,
            "diagonal": True,
            "directed": False,
            "condition": "8-neighbor",
        },

        # ----------------------------------------------------
        # GEOGRAPHICAL
        # ----------------------------------------------------

        {
            "name": "geo_100",
            "type": "geographical",
            "nodes": 100,
            "directed": False,
            "condition": "small",
        },

        {
            "name": "geo_500",
            "type": "geographical",
            "nodes": 500,
            "directed": False,
            "condition": "medium",
        },

        {
            "name": "geo_1000",
            "type": "geographical",
            "nodes": 1000,
            "directed": False,
            "condition": "large",
        },
    ]


# ============================================================
# GRAPH GENERATION
# ============================================================

def generate_graph(scenario):
    graph = Graph(
        directed=scenario.get("directed", False),
        graph_type=scenario["type"]
    )

    graph_type = scenario["type"]

    if graph_type == "random":

        graph.generate_random(
            scenario["nodes"],
            scenario["probability"]
        )

    elif graph_type == "grid":

        graph.build_grid(
            scenario["rows"],
            scenario["cols"],
            diagonal=scenario.get("diagonal", False)
        )

    elif graph_type == "geographical":

        graph.build_geographical(
            scenario["nodes"]
        )

    else:
        raise ValueError(
            f"Unknown graph type: {graph_type}"
        )

    return graph


# ============================================================
# GRAPH INFORMATION
# ============================================================

def get_node_ids(graph):
    """
    Supports the common Graph.nodes dictionary structure.
    """

    if hasattr(graph, "nodes"):

        nodes = graph.nodes

        if isinstance(nodes, dict):
            return list(nodes.keys())

        return [
            getattr(node, "id", i)
            for i, node in enumerate(nodes)
        ]

    raise AttributeError(
        "Graph object does not contain a 'nodes' attribute."
    )


def get_node(graph, node_id):
    return graph.nodes[node_id]


def get_graph_size(graph):
    node_count = 0
    edge_count = 0

    if hasattr(graph, "nodes"):
        try:
            node_count = len(graph.nodes)
        except Exception:
            pass

    if hasattr(graph, "edges"):

        try:
            edge_count = len(graph.edges)

        except Exception:

            try:
                edge_count = sum(
                    len(v)
                    for v in graph.edges.values()
                )

            except Exception:
                edge_count = 0

    elif hasattr(graph, "adjacency"):

        try:
            edge_count = sum(
                len(v)
                for v in graph.adjacency.values()
            )

            if not graph.directed:
                edge_count //= 2

        except Exception:
            pass

    return node_count, edge_count


# ============================================================
# ALGORITHM EXECUTION
# ============================================================

def run_algorithm(
    graph,
    algorithm,
    heuristic_name,
    start,
    goal
):
    if algorithm == "dijkstra":

        return graph.dijkstra(start, goal)

    if algorithm == "a_star":

        heuristic = HEURISTICS[heuristic_name]

        return graph.a_star(
            start,
            goal,
            heuristic=heuristic
        )

    if algorithm == "bidijkstra":

        return graph.bidirectional_dijkstra(
            start,
            goal
        )

    if algorithm == "bi_a_star":

        heuristic = HEURISTICS[heuristic_name]

        return graph.bidirectional_a_star(
            start,
            goal,
            heuristic=heuristic
        )

    if algorithm == "bfs":

        return graph.bfs(start, goal)

    raise ValueError(
        f"Unknown algorithm: {algorithm}"
    )


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_result(result):
    """
    Converts different possible Graph method return formats
    into:

        path, cost

    """

    if result is None:
        return None, math.inf

    if isinstance(result, tuple):

        if len(result) >= 2:
            return result[0], result[1]

        if len(result) == 1:
            return result[0], math.inf

    if isinstance(result, list):
        return result, math.inf

    return None, math.inf


# ============================================================
# RANDOM SOURCE / GOAL PAIRS
# ============================================================

def choose_pairs(
    graph,
    count,
    rng
):
    node_ids = get_node_ids(graph)

    if len(node_ids) < 2:
        return []

    pairs = []

    max_attempts = max(
        50,
        count * 20
    )

    attempts = 0

    while (
        len(pairs) < count
        and attempts < max_attempts
    ):

        attempts += 1

        start, goal = rng.sample(
            node_ids,
            2
        )

        try:

            path, cost = normalize_result(
                graph.dijkstra(
                    start,
                    goal
                )
            )

            if path:
                pairs.append(
                    {
                        "start": start,
                        "goal": goal,
                        "reference_path": path,
                        "reference_cost": cost,
                    }
                )

        except Exception:
            continue

    return pairs


# ============================================================
# SINGLE ROUTE BENCHMARK
# ============================================================

def benchmark_route(
    graph,
    algorithm,
    heuristic,
    pair,
):
    start = pair["start"]
    goal = pair["goal"]

    reference_cost = pair["reference_cost"]

    start_time = time.perf_counter()

    try:

        result = run_algorithm(
            graph,
            algorithm,
            heuristic,
            start,
            goal
        )

        elapsed = (
            time.perf_counter()
            - start_time
        ) * 1000.0

        path, cost = normalize_result(result)

    except Exception as exc:

        elapsed = (
            time.perf_counter()
            - start_time
        ) * 1000.0

        return {
            "success": False,
            "time_ms": elapsed,
            "cost": math.inf,
            "path_nodes": 0,
            "cost_error": math.inf,
            "exact": False,
            "error": str(exc),
        }

    if not path:

        return {
            "success": False,
            "time_ms": elapsed,
            "cost": math.inf,
            "path_nodes": 0,
            "cost_error": math.inf,
            "exact": False,
            "error": "",
        }

    try:

        cost_error = abs(
            float(cost)
            - float(reference_cost)
        )

        exact = math.isclose(
            float(cost),
            float(reference_cost),
            rel_tol=1e-9,
            abs_tol=1e-7
        )

    except Exception:

        cost_error = math.inf
        exact = False

    return {
        "success": True,
        "time_ms": elapsed,
        "cost": cost,
        "path_nodes": len(path),
        "cost_error": cost_error,
        "exact": exact,
        "error": "",
    }


# ============================================================
# AGGREGATION
# ============================================================

def create_accumulator():
    return {
        "total_queries": 0,
        "successful": 0,
        "exact": 0,

        "total_time_ms": 0.0,
        "total_cost": 0.0,
        "total_path_nodes": 0.0,
        "total_cost_error": 0.0,

        "errors": 0,
    }


def add_result(acc, result):

    acc["total_queries"] += 1

    if not result["success"]:

        acc["errors"] += 1
        return

    acc["successful"] += 1

    if result["exact"]:
        acc["exact"] += 1

    acc["total_time_ms"] += result["time_ms"]

    acc["total_cost"] += float(
        result["cost"]
    )

    acc["total_path_nodes"] += result[
        "path_nodes"
    ]

    acc["total_cost_error"] += result[
        "cost_error"
    ]


def finalize_accumulator(acc):

    total = acc["total_queries"]
    successful = acc["successful"]

    if total > 0:
        success_rate = (
            acc["successful"] / total
        ) * 100.0

    else:
        success_rate = 0.0

    if successful > 0:

        accuracy = (
            acc["exact"] / successful
        ) * 100.0

        avg_time = (
            acc["total_time_ms"]
            / successful
        )

        avg_cost = (
            acc["total_cost"]
            / successful
        )

        avg_path_nodes = (
            acc["total_path_nodes"]
            / successful
        )

        avg_cost_error = (
            acc["total_cost_error"]
            / successful
        )

    else:

        accuracy = 0.0
        avg_time = 0.0
        avg_cost = 0.0
        avg_path_nodes = 0.0
        avg_cost_error = 0.0

    return {
        "total_queries": total,
        "success_rate_percent": success_rate,
        "accuracy_percent": accuracy,
        "avg_time_ms": avg_time,
        "avg_cost": avg_cost,
        "avg_path_nodes": avg_path_nodes,
        "avg_cost_error": avg_cost_error,
    }


# ============================================================
# BENCHMARK ONE SCENARIO
# ============================================================

def benchmark_scenario(
    scenario,
    tests_per_scenario,
    queries_per_graph,
    rng,
):
    rows = []

    print()
    print("=" * 70)
    print(
        f"SCENARIO: {scenario['name']}"
    )
    print("=" * 70)

    print(
        f"Type: {scenario['type']}"
    )

    if scenario["type"] == "random":
        print(
            f"Nodes: {scenario['nodes']}"
        )
        print(
            f"Edge probability: "
            f"{scenario['probability']}"
        )

    elif scenario["type"] == "grid":
        print(
            f"Grid: "
            f"{scenario['rows']}x"
            f"{scenario['cols']}"
        )

    elif scenario["type"] == "geographical":
        print(
            f"Nodes: {scenario['nodes']}"
        )

    print(
        f"Tests: {tests_per_scenario}"
    )

    print(
        f"Queries per graph: "
        f"{queries_per_graph}"
    )

    for test_index in range(
        tests_per_scenario
    ):

        print()
        print(
            f"Generating graph "
            f"{test_index + 1}/"
            f"{tests_per_scenario}..."
        )

        try:

            graph = generate_graph(
                scenario
            )

        except Exception as exc:

            print(
                f"Graph generation failed: "
                f"{exc}"
            )

            continue

        nodes, edges = get_graph_size(
            graph
        )

        print(
            f"Graph generated: "
            f"{nodes} nodes, "
            f"{edges} edges"
        )

        # Safety limit
        if nodes > 1000:

            print(
                "Graph exceeds 1000 nodes. "
                "Skipping."
            )

            continue

        print("Selecting routes...")

        pairs = choose_pairs(
            graph,
            queries_per_graph,
            rng
        )

        if not pairs:

            print(
                "No reachable source/goal "
                "pairs found."
            )

            continue

        print(
            f"Selected {len(pairs)} routes."
        )

        for algorithm, heuristic in ALGORITHMS:

            label = algorithm

            if heuristic:
                label += f" ({heuristic})"

            print(
                f"  Testing {label}..."
            )

            acc = create_accumulator()

            for pair in pairs:

                result = benchmark_route(
                    graph,
                    algorithm,
                    heuristic,
                    pair
                )

                add_result(
                    acc,
                    result
                )

            metrics = finalize_accumulator(
                acc
            )

            rows.append({

                "scenario":
                    scenario["name"],

                "graph_type":
                    scenario["type"],

                "directed":
                    scenario.get(
                        "directed",
                        False
                    ),

                "nodes":
                    nodes,

                "edges":
                    edges,

                "condition":
                    scenario.get(
                        "condition",
                        ""
                    ),

                "algorithm":
                    algorithm,

                "heuristic":
                    heuristic or "",

                "graph_tests":
                    tests_per_scenario,

                "queries_per_graph":
                    queries_per_graph,

                "total_queries":
                    metrics[
                        "total_queries"
                    ],

                "success_rate_percent":
                    metrics[
                        "success_rate_percent"
                    ],

                "accuracy_percent":
                    metrics[
                        "accuracy_percent"
                    ],

                "avg_time_ms":
                    metrics[
                        "avg_time_ms"
                    ],

                "avg_cost":
                    metrics[
                        "avg_cost"
                    ],

                "avg_path_nodes":
                    metrics[
                        "avg_path_nodes"
                    ],

                "avg_cost_error":
                    metrics[
                        "avg_cost_error"
                    ],
            })

    return rows


# ============================================================
# CSV
# ============================================================

CSV_FIELDS = [

    "scenario",
    "graph_type",
    "directed",

    "nodes",
    "edges",
    "condition",

    "algorithm",
    "heuristic",

    "graph_tests",
    "queries_per_graph",
    "total_queries",

    "success_rate_percent",
    "accuracy_percent",

    "avg_time_ms",
    "avg_cost",
    "avg_path_nodes",
    "avg_cost_error",
]


def save_csv(rows, filename):

    if not rows:
        print(
            "No benchmark results to save."
        )
        return

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=CSV_FIELDS
        )

        writer.writeheader()

        for row in rows:
            writer.writerow(row)

    print()
    print(
        f"Results saved to: {filename}"
    )


# ============================================================
# COMMAND LINE
# ============================================================

def parse_arguments():

    parser = argparse.ArgumentParser(
        description=(
            "Benchmark graph routing "
            "algorithms."
        )
    )

    parser.add_argument(
        "--tests",
        type=int,
        default=2,
        help=(
            "Number of graphs generated "
            "per scenario "
            "(default: 2)"
        )
    )

    parser.add_argument(
        "--queries",
        type=int,
        default=3,
        help=(
            "Number of source/goal pairs "
            "per graph "
            "(default: 3)"
        )
    )

    parser.add_argument(
        "--output",
        type=str,
        default="benchmark_results.csv",
        help=(
            "CSV output filename "
            "(default: benchmark_results.csv)"
        )
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help=(
            "Random seed "
            "(default: 42)"
        )
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():

    args = parse_arguments()

    if args.tests < 1:
        print(
            "--tests must be at least 1"
        )
        return

    if args.queries < 1:
        print(
            "--queries must be at least 1"
        )
        return

    rng = random.Random(
        args.seed
    )

    scenarios = get_scenarios()

    # Extra safety check
    scenarios = [
        scenario
        for scenario in scenarios
        if scenario.get(
            "nodes",
            scenario.get(
                "rows",
                0
            ) * scenario.get(
                "cols",
                0
            )
        ) <= 1000
    ]

    print()
    print("=" * 70)
    print("GRAPH ROUTING BENCHMARK")
    print("=" * 70)

    print(
        f"Scenarios: {len(scenarios)}"
    )

    print(
        f"Tests per scenario: "
        f"{args.tests}"
    )

    print(
        f"Queries per graph: "
        f"{args.queries}"
    )

    print(
        "Maximum graph size: 1000 nodes"
    )

    print(
        "Contraction Hierarchy: DISABLED"
    )

    print(
        f"Random seed: {args.seed}"
    )

    total_rows = 0

    all_rows = []

    benchmark_start = time.perf_counter()

    for index, scenario in enumerate(
        scenarios,
        start=1
    ):

        print()
        print(
            f"[{index}/{len(scenarios)}]"
        )

        rows = benchmark_scenario(
            scenario,
            args.tests,
            args.queries,
            rng
        )

        all_rows.extend(rows)

        total_rows += len(rows)

    benchmark_time = (
        time.perf_counter()
        - benchmark_start
    )

    save_csv(
        all_rows,
        args.output
    )

    print()
    print("=" * 70)
    print("BENCHMARK FINISHED")
    print("=" * 70)

    print(
        f"Result rows: {total_rows}"
    )

    print(
        f"Total execution time: "
        f"{benchmark_time:.2f} seconds"
    )

    print(
        f"CSV: {args.output}"
    )


if __name__ == "__main__":
    main()