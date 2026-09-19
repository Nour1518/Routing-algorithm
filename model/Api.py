import requests


class GraphAPIClient:

    def __init__(
        self,
        base_url="http://127.0.0.1:5000"
    ):
        self.base_url = base_url.rstrip("/")

    # ========================================================
    # INTERNAL REQUEST HELPERS
    # ========================================================

    def _get(self, endpoint, timeout=5):

        response = requests.get(
            f"{self.base_url}{endpoint}",
            timeout=timeout
        )

        response.raise_for_status()

        return response.json()

    def _post(
        self,
        endpoint,
        data=None,
        timeout=30
    ):

        response = requests.post(
            f"{self.base_url}{endpoint}",
            json=data,
            timeout=timeout
        )

        response.raise_for_status()

        return response.json()

    def _delete(
        self,
        endpoint,
        timeout=5
    ):

        response = requests.delete(
            f"{self.base_url}{endpoint}",
            timeout=timeout
        )

        response.raise_for_status()

        return response.json()

    # ========================================================
    # CONNECTION
    # ========================================================

    def health(self):

        return self._get(
            "/",
            timeout=2
        )

    def is_connected(self):

        try:

            self.health()

            return True

        except requests.RequestException:

            return False

    # ========================================================
    # GRAPH LIST
    # ========================================================

    def list_graphs(self):

        return self._get(
            "/graphs",
            timeout=5
        )

    def get_graph(
        self,
        graph_id
    ):

        return self._get(
            f"/graphs/{graph_id}",
            timeout=5
        )

    # ========================================================
    # GENERIC GRAPH GENERATION
    # ========================================================

    def generate_graph(
        self,
        graph_type,
        directed=False,
        build_ch=False,
        **parameters
    ):
        """
        Generate a graph through the API.

        Example:

            client.generate_graph(
                "random",
                nodes=500,
                probability=0.05,
                min_weight=1,
                max_weight=100
            )

        The parameters depend on graph_type.
        """

        data = {
            "type": graph_type,
            "directed": directed,
            "build_ch": build_ch,
        }

        data.update(parameters)

        return self._post(
            "/graphs/generate",
            data=data,
            timeout=300
        )

    # ========================================================
    # GENERIC
    # ========================================================

    def generate_generic(
        self,
        nodes=100,
        directed=False,
        build_ch=False
    ):
        """
        Generate a generic graph.

        Parameters:
            nodes
            directed
            build_ch
        """

        return self.generate_graph(
            graph_type="generic",
            nodes=nodes,
            directed=directed,
            build_ch=build_ch
        )

    # ========================================================
    # RANDOM
    # ========================================================

    def generate_random(
        self,
        nodes=100,
        probability=0.05,
        min_weight=1.0,
        max_weight=100.0,
        directed=False,
        build_ch=False
    ):
        """
        Generate a random graph.

        Parameters:
            nodes:
                Number of nodes.

            probability:
                Probability of creating an edge.

            min_weight:
                Minimum edge weight.

            max_weight:
                Maximum edge weight.

            directed:
                Directed or undirected graph.

            build_ch:
                Build Contraction Hierarchy after generation.
        """

        return self.generate_graph(
            graph_type="random",

            nodes=nodes,

            probability=probability,

            min_weight=min_weight,

            max_weight=max_weight,

            directed=directed,

            build_ch=build_ch
        )

    # ========================================================
    # GEOGRAPHICAL
    # ========================================================

    def generate_geographical(
        self,
        nodes=100,
        size=1000,
        min_dist=10,
        radius=150,
        max_degree=4,
        directed=False,
        build_ch=False
    ):
        """
        Generate a geographical graph.

        Generation:

            random nodes
                ↓
            minimum distance
                ↓
            MST
                ↓
            local edges

        Parameters:
            nodes:
                Number of nodes.

            size:
                Size of the geographical area.

            min_dist:
                Minimum distance between nodes.

            radius:
                Maximum distance for local edges.

            max_degree:
                Maximum node degree.

            directed:
                Directed or undirected graph.

            build_ch:
                Build CH after generation.
        """

        return self.generate_graph(
            graph_type="geographical",

            nodes=nodes,

            size=size,

            min_dist=min_dist,

            radius=radius,

            max_degree=max_degree,

            directed=directed,

            build_ch=build_ch
        )

    # ========================================================
    # GRID
    # ========================================================

    def generate_grid(
        self,
        rows=10,
        cols=10,
        weight=1.0,
        diagonal=False,
        directed=False,
        build_ch=False
    ):
        """
        Generate a rectangular grid graph.

        Parameters:
            rows
            cols
            weight
            diagonal
            directed
            build_ch
        """

        return self.generate_graph(
            graph_type="grid",

            rows=rows,

            cols=cols,

            weight=weight,

            diagonal=diagonal,

            directed=directed,

            build_ch=build_ch
        )

    # ========================================================
    # LOAD GRAPH
    # ========================================================

    def load_graph(
        self,
        filename,
        build_ch=False
    ):
        """
        Load a graph from a file.
        """

        data = {
            "filename": filename,
            "build_ch": build_ch
        }

        return self._post(
            "/graphs/load",
            data=data,
            timeout=300
        )

        # ========================================================
        # ROUTING
        # ========================================================
    
    def route(
        self,
        graph_id,
        start,
        goal,
        algorithm="dijkstra",
        heuristic=None,
        trace=False
    ):
        """
        Execute a routing query.

        The heuristic is only sent when explicitly provided.
        """

        data = {
            "start": int(start),

            "goal": int(goal),

            "algorithm": algorithm,

            "trace": trace
        }

        # ========================================================
        # OPTIONAL HEURISTIC
        # ========================================================

        if heuristic is not None:

            data["heuristic"] = heuristic

        return self._post(
            f"/graphs/{graph_id}/route",
            data=data,
            timeout=300
        )
    

    # ========================================================
    # BUILD CH
    # ========================================================

    def build_ch(
        self,
        graph_id
    ):
        """
        Build Contraction Hierarchy for a loaded graph.
        """

        return self._post(
            f"/graphs/{graph_id}/ch",
            timeout=300
        )

    # ========================================================
    # SAVE GRAPH
    # ========================================================

    def save_graph(
        self,
        graph_id,
        filename
    ):
        """
        Save a graph on the server.
        """

        data = {
            "filename": filename
        }

        return self._post(
            f"/graphs/{graph_id}/save",
            data=data,
            timeout=300
        )

    # ========================================================
    # DELETE GRAPH
    # ========================================================

    def delete_graph(
        self,
        graph_id
    ):
        """
        Delete a graph from server memory.
        """

        return self._delete(
            f"/graphs/{graph_id}",
            timeout=5
        )

    # ========================================================
    # GRAPH INFORMATION
    # ========================================================

    def graph_statistics(
        self,
        graph_id
    ):
        """
        Convenience method returning only graph statistics.
        """

        result = self.get_graph(
            graph_id
        )

        return result.get(
            "graph",
            {}
        )

    # ========================================================
    # ALGORITHMS
    # ========================================================

    @staticmethod
    def algorithms():

        return [
            "dijkstra",
            "a_star",
            "bidijkstra",
            "bi_a_star",
            "bfs",
            "ch"
        ]

    # ========================================================
    # GRAPH TYPES
    # ========================================================

    @staticmethod
    def graph_types():

        return [
            "generic",
            "random",
            "geographical",
            "grid"
        ]
    # ========================================================
    # GET GRAPH DATA
    # ========================================================
# ========================================================
# GET GRAPH STRUCTURE
# ========================================================
# ========================================================
# GET GRAPH STRUCTURE
# ========================================================

    def get_graph_structure(
        self,
        graph_id,
        timeout=300
    ):
        """
        Get the complete graph nodes and edges.
        """

        return self._get(
            f"/graphs/{graph_id}/structure",
            timeout=timeout
        )


    # ========================================================
    # GET GRAPH DATA
    # ========================================================

    def get_graph_data(
        self,
        graph_id,
        timeout=300
    ):
        """
        Return only nodes and edges.
        """

        response = self.get_graph_structure(
            graph_id,
            timeout=timeout
        )

        return response.get(
            "graph",
            {
                "nodes": [],
                "edges": []
            }
        )
