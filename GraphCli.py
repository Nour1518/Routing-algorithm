import argparse
import math
import sys

from BaseClass import Graph


# ============================================================
# HEURISTICS
# ============================================================

def zero_heuristic(a, b):
    return 0.0


def euclidean_heuristic(a, b):
    if not a.data or not b.data:
        return 0.0

    if "x" in a.data and "y" in a.data and "x" in b.data and "y" in b.data:
        return math.hypot(
            a.data["x"] - b.data["x"],
            a.data["y"] - b.data["y"],
        )

    return 0.0


def manhattan_heuristic(a, b):
    if not a.data or not b.data:
        return 0.0

    if "row" in a.data and "col" in a.data:
        return (
            abs(a.data["row"] - b.data["row"])
            + abs(a.data["col"] - b.data["col"])
        )

    if "x" in a.data and "y" in b.data:
        return (
            abs(a.data["x"] - b.data["x"])
            + abs(a.data["y"] - b.data["y"])
        )

    return 0.0


def octile_heuristic(a, b):
    if not a.data or not b.data:
        return 0.0

    # Grid coordinates
    if "row" in a.data and "col" in a.data:
        dx = abs(a.data["row"] - b.data["row"])
        dy = abs(a.data["col"] - b.data["col"])

        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

    # Geographical coordinates
    if "x" in a.data and "y" in a.data:
        dx = abs(a.data["x"] - b.data["x"])
        dy = abs(a.data["y"] - b.data["y"])

        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

    return 0.0


HEURISTICS = {
    "zero": zero_heuristic,
    "euclidean": euclidean_heuristic,
    "manhattan": manhattan_heuristic,
    "octile": octile_heuristic,
}


# ============================================================
# CLI
# ============================================================

class GraphCLI:

    def __init__(self, directed=False):
        self.graph = Graph(
            directed=directed,
            graph_type="generic"
        )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    def edge_count(self):
        count = sum(
            len(edges)
            for edges in self.graph.adjacency.values()
        )

        if not self.graph.directed:
            count //= 2

        return count

    def print_graph_info(self):
        print("\n========== GRAPH ==========")
        print(f"Type       : {self.graph.graph_type}")
        print(f"Directed   : {self.graph.directed}")
        print(f"Nodes      : {len(self.graph.nodes)}")
        print(f"Edges      : {self.edge_count()}")
        print(f"CH ready   : {self.graph.ch_ready}")

        if self.graph.ch_ready:
            ch_edges = sum(
                len(edges)
                for edges in self.graph.ch_adjacency.values()
            )

            shortcuts = 0

            for edges in self.graph.ch_adjacency.values():
                for edge in edges:
                    if edge.middle is not None:
                        shortcuts += 1

            print(f"CH edges   : {ch_edges}")
            print(f"CH ranks   : {len(self.graph.ch_rank)}")
            print(f"Shortcuts  : {shortcuts}")

        print("============================\n")

    def ask_int(self, prompt, default=None):
        while True:
            value = input(prompt).strip()

            if not value and default is not None:
                return default

            try:
                return int(value)
            except ValueError:
                print("Enter an integer.")

    def ask_float(self, prompt, default=None):
        while True:
            value = input(prompt).strip()

            if not value and default is not None:
                return default

            try:
                return float(value)
            except ValueError:
                print("Enter a number.")

    def ask_yes_no(self, prompt, default=False):
        suffix = " [Y/n]: " if default else " [y/N]: "

        value = input(prompt + suffix).strip().lower()

        if not value:
            return default

        return value in ("y", "yes")

    def ask_path(self, prompt):
        value = input(prompt).strip()

        if not value:
            print("Path cannot be empty.")
            return self.ask_path(prompt)

        return value

    def print_path(self, path, cost, max_nodes=30):
        if path is None:
            print("\nNo path found.")
            return

        print("\n========== ROUTE ==========")
        print(f"Cost       : {cost}")
        print(f"Nodes      : {len(path)}")
        print(f"Edges      : {max(0, len(path) - 1)}")

        if len(path) <= max_nodes:
            print("Path       :", " -> ".join(map(str, path)))
        else:
            head = path[:max_nodes // 2]
            tail = path[-max_nodes // 2:]

            print(
                "Path       :",
                " -> ".join(map(str, head)),
                " -> ... -> ",
                " -> ".join(map(str, tail)),
            )

        print("============================\n")

    def choose_heuristic(self):
        print("\nHeuristic:")
        print("1. zero")
        print("2. euclidean")
        print("3. manhattan")
        print("4. octile")

        choice = input("Choice [2]: ").strip() or "2"

        names = {
            "1": "zero",
            "2": "euclidean",
            "3": "manhattan",
            "4": "octile",
        }

        name = names.get(choice, "euclidean")

        print(f"Using heuristic: {name}")

        return HEURISTICS[name]

    # --------------------------------------------------------
    # Graph creation
    # --------------------------------------------------------

    def new_graph(self):
        directed = self.ask_yes_no(
            "Directed graph?",
            self.graph.directed
        )

        self.graph = Graph(
            directed=directed,
            graph_type="generic"
        )

        print("New empty graph created.")

    def generate_random(self):
        n = self.ask_int("Number of nodes [100]: ", 100)
        probability = self.ask_float(
            "Edge probability [0.05]: ",
            0.05
        )
        min_weight = self.ask_float(
            "Minimum weight [1]: ",
            1.0
        )
        max_weight = self.ask_float(
            "Maximum weight [100]: ",
            100.0
        )

        self.graph.generate_random(
            n=n,
            edge_probability=probability,
            min_weight=min_weight,
            max_weight=max_weight,
        )

        print("Random graph generated.")
        self.print_graph_info()

    def generate_grid(self):
        rows = self.ask_int("Rows [20]: ", 20)
        cols = self.ask_int("Columns [20]: ", 20)
        weight = self.ask_float("Edge weight [1]: ", 1.0)

        diagonal = self.ask_yes_no(
            "Allow diagonal movement?",
            False
        )

        directed = self.ask_yes_no(
            "Directed graph?",
            self.graph.directed
        )

        self.graph = Graph(
            directed=directed,
            graph_type="grid"
        )

        self.graph.build_grid(
            rows=rows,
            cols=cols,
            weight=weight,
            diagonal=diagonal,
        )

        print("Grid graph generated.")
        self.print_graph_info()

    def generate_geographical(self):
        n = self.ask_int("Number of nodes [100]: ", 100)
        size = self.ask_float("Area size [1000]: ", 1000.0)
        min_dist = self.ask_float(
            "Minimum node distance [10]: ",
            10.0
        )
        radius = self.ask_float(
            "Local edge radius [150]: ",
            150.0
        )
        max_degree = self.ask_int(
            "Maximum degree [4]: ",
            4
        )

        directed = self.ask_yes_no(
            "Directed graph?",
            False
        )

        self.graph = Graph(
            directed=directed,
            graph_type="geographical"
        )

        self.graph.build_geographical(
            n=n,
            size=size,
            min_dist=min_dist,
            radius=radius,
            max_degree=max_degree,
        )

        print("Geographical graph generated.")
        self.print_graph_info()

    # --------------------------------------------------------
    # File operations
    # --------------------------------------------------------

    def save_graph(self):
        filename = self.ask_path(
            "Filename (.json or .graph): "
        )

        try:
            self.graph.save(filename)
            print(f"Graph saved to: {filename}")
        except Exception as exc:
            print(f"Save error: {exc}")

    def load_graph(self):
        filename = self.ask_path(
            "Filename (.json or .graph): "
        )

        try:
            self.graph.load(filename)
            print(f"Graph loaded from: {filename}")
            self.print_graph_info()
        except Exception as exc:
            print(f"Load error: {exc}")

    # --------------------------------------------------------
    # CH
    # --------------------------------------------------------

    def build_ch(self):
        if not self.graph.nodes:
            print("Graph is empty.")
            return

        print("\nBuilding Contraction Hierarchy...")
        print("This can take time on large graphs.")

        try:
            result = self.graph.build_contraction_hierarchy()

            print("\nCH built successfully.")
            print(f"Nodes       : {result['nodes']}")
            print(f"Original    : {result['original_edges']}")
            print(f"CH edges    : {result['ch_edges']}")
            print(f"Shortcuts   : {result['shortcuts']}")

        except Exception as exc:
            print(f"CH error: {exc}")

    # --------------------------------------------------------
    # Routing
    # --------------------------------------------------------

    def route(self):
        if not self.graph.nodes:
            print("Graph is empty.")
            return

        start = self.ask_int("Start node: ")
        goal = self.ask_int("Goal node: ")

        if start not in self.graph.nodes:
            print(f"Node {start} does not exist.")
            return

        if goal not in self.graph.nodes:
            print(f"Node {goal} does not exist.")
            return

        print("\nAlgorithm:")
        print("1. Dijkstra")
        print("2. A*")
        print("3. Bidirectional Dijkstra")
        print("4. Bidirectional A*")
        print("5. BFS")
        print("6. Contraction Hierarchy")

        choice = input("Choice [1]: ").strip() or "1"

        try:
            if choice == "1":
                algorithm = "Dijkstra"
                path, cost = self.graph.dijkstra(
                    start,
                    goal
                )

            elif choice == "2":
                algorithm = "A*"
                heuristic = self.choose_heuristic()

                path, cost = self.graph.a_star(
                    start,
                    goal,
                    heuristic=heuristic
                )

            elif choice == "3":
                algorithm = "Bidirectional Dijkstra"

                path, cost = self.graph.bidirectional_dijkstra(
                    start,
                    goal
                )

            elif choice == "4":
                algorithm = "Bidirectional A*"
                heuristic = self.choose_heuristic()

                path, cost = self.graph.bidirectional_a_star(
                    start,
                    goal,
                    heuristic=heuristic
                )

            elif choice == "5":
                algorithm = "BFS"

                path, cost = self.graph.bfs(
                    start,
                    goal
                )

            elif choice == "6":
                algorithm = "Contraction Hierarchy"

                if not self.graph.ch_ready:
                    build = self.ask_yes_no(
                        "CH is not built. Build it now?",
                        True
                    )

                    if not build:
                        return

                    self.build_ch()

                    if not self.graph.ch_ready:
                        return

                path, cost = self.graph.contraction_hierarchy(
                    start,
                    goal
                )

            else:
                print("Invalid algorithm.")
                return

            print(f"\nAlgorithm  : {algorithm}")
            self.print_path(path, cost)

        except Exception as exc:
            print(f"Routing error: {exc}")

    # --------------------------------------------------------
    # Main menu
    # --------------------------------------------------------

    def menu(self):
        while True:
            print("\n")
            print("========================================")
            print("           GRAPH ROUTING CLI")
            print("========================================")
            print(f"Graph: {len(self.graph.nodes)} nodes, "
                  f"{self.edge_count()} edges")
            print("----------------------------------------")
            print("1. Graph information")
            print("2. New empty graph")
            print("3. Generate random graph")
            print("4. Generate grid graph")
            print("5. Generate geographical graph")
            print("6. Route")
            print("7. Build Contraction Hierarchy")
            print("8. Save graph")
            print("9. Load graph")
            print("0. Exit")
            print("----------------------------------------")

            choice = input("Choice: ").strip()

            if choice == "1":
                self.print_graph_info()

            elif choice == "2":
                self.new_graph()

            elif choice == "3":
                self.generate_random()

            elif choice == "4":
                self.generate_grid()

            elif choice == "5":
                self.generate_geographical()

            elif choice == "6":
                self.route()

            elif choice == "7":
                self.build_ch()

            elif choice == "8":
                self.save_graph()

            elif choice == "9":
                self.load_graph()

            elif choice == "0":
                print("Bye.")
                break

            else:
                print("Invalid choice.")


# ============================================================
# ARGUMENTS
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="CLI for the Graph class in BaseClass.py"
    )

    parser.add_argument(
        "--directed",
        action="store_true",
        help="Start with a directed graph"
    )

    parser.add_argument(
        "--load",
        metavar="FILE",
        help="Load a .json or .graph file at startup"
    )

    args = parser.parse_args()

    cli = GraphCLI(
        directed=args.directed
    )

    if args.load:
        try:
            cli.graph.load(args.load)
            print(f"Loaded: {args.load}")
            cli.print_graph_info()
        except Exception as exc:
            print(f"Load error: {exc}")
            sys.exit(1)

    cli.menu()


if __name__ == "__main__":
    main()
