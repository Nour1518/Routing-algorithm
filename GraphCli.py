
import argparse
import json
import math
import sys
import time
from pathlib import Path


# ============================================================
# IMPORT GRAPH
# ============================================================

# Change this if your Graph class is in another module.
#
# Example:
#     from Graph import Graph
#
from BaseClass import Graph


# ============================================================
# ALGORITHMS
# ============================================================

ALGORITHMS = {
    "dijkstra",
    "a_star",
    "bidijkstra",
    "bi_a_star",
    "bfs",
    "ch",
}


# ============================================================
# HEURISTICS
# ============================================================

def geographical_heuristic(a, b):
    """
    Euclidean heuristic for geographical graphs.

    Expected node.data:

        {
            "x": ...,
            "y": ...
        }
    """

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
    """
    Manhattan-distance heuristic for a grid.

    Expected node.data:

        {
            "row": ...,
            "col": ...
        }
    """

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
    """
    Zero heuristic.

    This makes A* behave like Dijkstra.
    """

    return 0.0


def get_heuristic(graph):
    """
    Select an appropriate heuristic based on graph type.
    """

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
    """
    Return basic graph statistics.
    """

    node_count = len(graph.nodes)

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
            len(graph.adjacency[node_id])
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
        "graph_type": getattr(
            graph,
            "graph_type",
            "generic"
        ),
        "average_degree": average_degree,
        "max_degree": max_degree,
        "ch_ready": getattr(
            graph,
            "ch_ready",
            False
        ),
    }


# ============================================================
# PATH STATISTICS
# ============================================================

def path_statistics(graph, path):
    """
    Calculate additional information about a resulting path.
    """

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

    # Cost is calculated independently from the algorithm result.
    #
    # This gives us a sanity check.

    path_length = 0.0

    for source, target in zip(
        path,
        path[1:]
    ):

        found = False

        for edge in graph.neighbors(source):

            if edge.target.id == target:

                path_length += edge.weight
                found = True
                break

        if not found:
            # This can happen for CH shortcuts.
            # The algorithm's returned cost remains authoritative.
            path_length = None
            break

    return {
        "path_nodes": len(path),
        "path_edges": path_edges,
        "path_length": path_length,
    }


# ============================================================
# SOLVE
# ============================================================

def solve_graph(
    graph,
    start,
    goal,
    algorithm,
    collect_trace=False
):
    """
    Execute one routing algorithm.

    Returns:

        path,
        cost,
        trace,
        elapsed_time
    """

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

    heuristic = get_heuristic(graph)

    trace = None

    # --------------------------------------------------------
    # Select algorithm
    # --------------------------------------------------------

    start_time = time.perf_counter()

    if algorithm == "dijkstra":

        if collect_trace and hasattr(
            graph,
            "dijkstra_visual"
        ):
            path, cost, trace = graph.dijkstra_visual(
                start,
                goal
            )
        else:
            path, cost = graph.dijkstra(
                start,
                goal
            )

    elif algorithm == "a_star":

        if collect_trace and hasattr(
            graph,
            "a_star_visual"
        ):
            path, cost, trace = graph.a_star_visual(
                start,
                goal,
                heuristic=heuristic
            )
        else:
            path, cost = graph.a_star(
                start,
                goal,
                heuristic=heuristic
            )

    elif algorithm == "bidijkstra":

        if collect_trace and hasattr(
            graph,
            "bidirectional_dijkstra_visual"
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

    elif algorithm == "bi_a_star":

        if collect_trace and hasattr(
            graph,
            "bidirectional_a_star_visual"
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

    elif algorithm == "bfs":

        path, cost = graph.bfs(
            start,
            goal
        )

    elif algorithm == "ch":

        if not graph.ch_ready:

            raise RuntimeError(
                "CH is not ready. "
                "Build the contraction hierarchy first."
            )

        path, cost = graph.contraction_hierarchy(
            start,
            goal
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


def generate_graph(args):
    """
    Generate a graph according to CLI parameters.

    Supported types:
        generic
        random
        grid
        geographical
    """

    graph_type = args.type

    # ========================================================
    # GENERIC
    # ========================================================

    if graph_type == "generic":

        graph = Graph(
            directed=args.directed,
            graph_type="generic"
        )

        # Generic graph starts with nodes only.
        #
        # This is useful when the user wants to construct
        # the graph manually or through another API.

        for node_id in range(args.nodes):

            graph.add_node(
                node_id,
                {}
            )

        return graph

    # ========================================================
    # RANDOM
    # ========================================================

    if graph_type == "random":

        graph = Graph(
            directed=args.directed,
            graph_type="random"
        )

        graph.generate_random(
            n=args.nodes,
            edge_probability=args.probability,
            min_weight=args.min_weight,
            max_weight=args.max_weight
        )

        return graph

    # ========================================================
    # GEOGRAPHICAL
    # ========================================================

    if graph_type == "geographical":

        graph = Graph(
            directed=args.directed,
            graph_type="geographical"
        )

        graph.build_geographical(
            n=args.nodes,
            size=args.size,
            min_dist=args.min_dist,
            radius=args.radius,
            max_degree=args.max_degree
        )

        return graph

    # ========================================================
    # GRID
    # ========================================================

    if graph_type == "grid":

        graph = Graph(
            directed=args.directed,
            graph_type="grid"
        )

        graph.build_grid(
            rows=args.rows,
            cols=args.cols,
            weight=args.weight,
            diagonal=args.diagonal
        )

        return graph

    # ========================================================
    # INVALID
    # ========================================================

    raise ValueError(
        f"Unsupported graph type: {graph_type}"
    )


# ============================================================
# BUILD CH
# ============================================================

def build_ch_if_requested(
    graph,
    build_ch
):
    """
    Build Contraction Hierarchy when requested.
    """

    if not build_ch:
        return None

    print()
    print("Building Contraction Hierarchy...")

    start_time = time.perf_counter()

    ch_stats = graph.build_contraction_hierarchy()

    elapsed = (
        time.perf_counter()
        -
        start_time
    )

    print(
        f"CH build time : {elapsed:.6f} s"
    )

    return {
        "time_seconds": elapsed,
        "statistics": ch_stats,
    }


# ============================================================
# PRINT GRAPH
# ============================================================

def print_graph_info(graph):

    stats = graph_statistics(graph)

    print()
    print("=" * 60)
    print("GRAPH")
    print("=" * 60)

    print(
        f"Type           : {stats['graph_type']}"
    )

    print(
        f"Directed       : {stats['directed']}"
    )

    print(
        f"Nodes          : {stats['nodes']:,}"
    )

    print(
        f"Edges          : {stats['edges']:,}"
    )

    print(
        f"Average degree : {stats['average_degree']:.2f}"
    )

    print(
        f"Maximum degree : {stats['max_degree']}"
    )

    print(
        f"CH ready       : {stats['ch_ready']}"
    )


# ============================================================
# PRINT RESULT
# ============================================================

def print_result(
    graph,
    start,
    goal,
    algorithm,
    path,
    cost,
    elapsed,
    trace=None
):

    print()
    print("=" * 60)
    print("ROUTING RESULT")
    print("=" * 60)

    print(
        f"Algorithm      : {algorithm}"
    )

    print(
        f"Start          : {start}"
    )

    print(
        f"Goal           : {goal}"
    )

    print(
        f"Time           : {elapsed:.6f} s"
    )

    if path is None:

        print(
            "Path           : NOT FOUND"
        )

        print(
            "Cost           : inf"
        )

        return

    print(
        f"Path nodes     : {len(path):,}"
    )

    print(
        f"Cost           : {cost}"
    )

    # --------------------------------------------------------
    # Path
    # --------------------------------------------------------

    print()
    print("Path:")

    if len(path) <= 100:

        print(
            " -> ".join(
                str(node)
                for node in path
            )
        )

    else:

        print(
            " -> ".join(
                str(node)
                for node in path[:20]
            )
        )

        print(
            f"... ({len(path) - 40:,} nodes omitted) ..."
        )

        print(
            " -> ".join(
                str(node)
                for node in path[-20:]
            )
        )

    # --------------------------------------------------------
    # Trace
    # --------------------------------------------------------

    if trace:

        print()
        print("Search statistics:")

        if "expansion_count" in trace:

            print(
                f"Expansions     : "
                f"{trace['expansion_count']:,}"
            )

        if "edge_check_count" in trace:

            print(
                f"Edge checks    : "
                f"{trace['edge_check_count']:,}"
            )

        if "meeting_node" in trace:

            print(
                f"Meeting node   : "
                f"{trace['meeting_node']}"
            )


# ============================================================
# SAVE RESULT
# ============================================================

def save_result(
    filename,
    graph,
    start,
    goal,
    algorithm,
    path,
    cost,
    elapsed,
    trace=None,
    ch_info=None
):
    """
    Save routing result and statistics as JSON.
    """

    result = {
        "format": "graph-routing-result",
        "version": 1,

        "graph": graph_statistics(graph),

        "query": {
            "start": start,
            "goal": goal,
            "algorithm": algorithm,
        },

        "result": {
            "found": path is not None,
            "cost": (
                cost
                if path is not None
                else None
            ),
            "time_seconds": elapsed,
            "path": path,
            "path_nodes": (
                len(path)
                if path is not None
                else 0
            ),
        },

        "trace": trace,

        "ch": ch_info,
    }

    # Remove data that JSON cannot represent.
    #
    # In normal use trace consists of JSON-compatible objects,
    # but this makes the CLI safer.

    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            indent=2,
            ensure_ascii=False,
            default=str
        )

    print()
    print(
        f"Result saved to: {filename}"
    )


# ============================================================
# SAVE GRAPH
# ============================================================

def save_graph(graph, filename):

    graph.save(filename)

    print(
        f"Graph saved to: {filename}"
    )


# ============================================================
# ARGUMENT PARSER
# ============================================================

def create_parser():
    """Create the command-line argument parser."""

    parser = argparse.ArgumentParser(
        description="Graph generation, loading and routing CLI"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # ========================================================
    # GENERATE
    # ========================================================

    generate = subparsers.add_parser(
        "generate",
        help="Generate a new graph"
    )

    generate.add_argument(
        "--type",
        choices=[
            "generic",
            "random",
            "grid",
            "geographical"
        ],
        required=True,
        help="Graph generation type"
    )

    generate.add_argument(
        "--directed",
        action="store_true",
        help="Create a directed graph"
    )

    # --------------------------------------------------------
    # Generic / Random
    # --------------------------------------------------------

    generate.add_argument(
        "--nodes",
        type=int,
        default=100,
        help="Number of nodes"
    )

    generate.add_argument(
        "--probability",
        type=float,
        default=0.05,
        help="Random graph edge probability"
    )

    generate.add_argument(
        "--min-weight",
        type=float,
        default=1.0,
        help="Minimum random edge weight"
    )

    generate.add_argument(
        "--max-weight",
        type=float,
        default=100.0,
        help="Maximum random edge weight"
    )

    # --------------------------------------------------------
    # Geographical
    # --------------------------------------------------------

    generate.add_argument(
        "--size",
        type=float,
        default=1000,
        help="Geographical area size"
    )

    generate.add_argument(
        "--min-dist",
        type=float,
        default=10,
        help="Minimum distance between geographical nodes"
    )

    generate.add_argument(
        "--radius",
        type=float,
        default=150,
        help="Maximum local connection radius"
    )

    generate.add_argument(
        "--max-degree",
        type=int,
        default=4,
        help="Maximum geographical node degree"
    )

    # --------------------------------------------------------
    # Grid
    # --------------------------------------------------------

    generate.add_argument(
        "--rows",
        type=int,
        default=10,
        help="Grid rows"
    )

    generate.add_argument(
        "--cols",
        type=int,
        default=10,
        help="Grid columns"
    )

    generate.add_argument(
        "--weight",
        type=float,
        default=1,
        help="Grid edge weight"
    )

    generate.add_argument(
        "--diagonal",
        action="store_true",
        help="Allow diagonal grid edges"
    )

    # --------------------------------------------------------
    # Generation actions
    # --------------------------------------------------------

    generate.add_argument(
        "--build-ch",
        action="store_true",
        help="Build Contraction Hierarchy after generation"
    )

    generate.add_argument(
        "--save",
        help="Save generated graph (.graph or .json)"
    )

    # ========================================================
    # LOAD + SOLVE
    # ========================================================

    load = subparsers.add_parser(
        "load",
        help="Load an existing graph and solve a query"
    )

    load.add_argument(
        "filename",
        help="Graph file (.graph or .json)"
    )

    add_routing_arguments(load)

    # ========================================================
    # SOLVE
    # ========================================================

    solve = subparsers.add_parser(
        "solve",
        help="Load a graph and solve a routing query"
    )

    solve.add_argument(
        "filename",
        help="Graph file (.graph or .json)"
    )

    add_routing_arguments(solve)

    return parser


# ============================================================
# COMMON ROUTING ARGUMENTS
# ============================================================

def add_routing_arguments(parser):
    """Add arguments required for a routing query."""

    parser.add_argument(
        "--start",
        type=int,
        required=True,
        help="Start node ID"
    )

    parser.add_argument(
        "--goal",
        type=int,
        required=True,
        help="Goal node ID"
    )

    parser.add_argument(
        "--algorithm",
        choices=sorted(ALGORITHMS),
        default="dijkstra",
        help="Routing algorithm"
    )

    parser.add_argument(
        "--build-ch",
        action="store_true",
        help="Build Contraction Hierarchy before solving"
    )

    parser.add_argument(
        "--trace",
        action="store_true",
        help="Collect visualization/search trace when available"
    )

    parser.add_argument(
        "--save",
        help="Save graph after loading"
    )

    parser.add_argument(
        "--result",
        help="Save routing result as JSON"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    parser = create_parser()
    args = parser.parse_args()

    try:

        # ====================================================
        # GENERATE
        # ====================================================

        if args.command == "generate":

            print(f"Generating {args.type} graph...")

            graph = generate_graph(args)

            print_graph_info(graph)

            # CH is optional during generation.
            ch_info = build_ch_if_requested(
                graph,
                args.build_ch
            )

            if args.save:
                save_graph(graph, args.save)

            print()
            print("Generation completed.")

            return 0

        # ====================================================
        # LOAD / SOLVE
        # ====================================================

        if args.command in ("load", "solve"):

            print(f"Loading graph: {args.filename}")

            graph = Graph()
            graph.load(args.filename)

            print_graph_info(graph)

            # CH may be requested before solving.
            ch_info = build_ch_if_requested(
                graph,
                args.build_ch
            )

            if args.save:
                save_graph(graph, args.save)

            print()
            print(f"Running {args.algorithm}...")

            (
                path,
                cost,
                trace,
                elapsed
            ) = solve_graph(
                graph=graph,
                start=args.start,
                goal=args.goal,
                algorithm=args.algorithm,
                collect_trace=args.trace
            )

            print_result(
                graph=graph,
                start=args.start,
                goal=args.goal,
                algorithm=args.algorithm,
                path=path,
                cost=cost,
                elapsed=elapsed,
                trace=trace
            )

            if args.result:
                save_result(
                    filename=args.result,
                    graph=graph,
                    start=args.start,
                    goal=args.goal,
                    algorithm=args.algorithm,
                    path=path,
                    cost=cost,
                    elapsed=elapsed,
                    trace=trace,
                    ch_info=ch_info
                )

            return 0

        raise RuntimeError("Unknown command.")

    except KeyboardInterrupt:

        print("\nInterrupted.")
        return 130

    except Exception as exc:

        print(
            f"\nERROR: {exc}",
            file=sys.stderr
        )
        return 1


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    sys.exit(
        main()
    )

    