
import heapq
from itertools import count
from collections import deque
import json
import pickle
import random
import math

class Node:
    def __init__(self, node_id, data=None):
        self.id = node_id
        self.data = data

    def __repr__(self):
        return f"Node({self.id})"
class Edge:
    def __init__(self, source, target, weight=1):
        self.source = source
        self.target = target
        self.weight = weight

    def __repr__(self):
        return (
            f"Edge({self.source.id} -> "
            f"{self.target.id}, weight={self.weight})"
        )
class CHEdge:
    def __init__(
        self,
        source,
        target,
        weight,
        middle=None
    ):
        self.source = source
        self.target = target
        self.weight = weight

        # Node used to create the shortcut
        self.middle = middle

    def __repr__(self):
        if self.middle is None:
            return (
                f"CHEdge("
                f"{self.source} -> "
                f"{self.target}, "
                f"weight={self.weight}"
                f")"
            )

        return (
            f"CHEdge("
            f"{self.source} -> "
            f"{self.target}, "
            f"weight={self.weight}, "
            f"middle={self.middle}"
            f")"
        )
class Graph:
    def __init__(self, directed=False,graph_type="generic"):
        self.directed = directed

        self.nodes = {}
        self.adjacency = {}
        self.reverse_adjacency = {}
        self.graph_type = graph_type
        # CH data
        self.ch_ready = False

        self.ch_rank = {}
        self.ch_order = []

        self.ch_adjacency = {}
        self.ch_reverse_adjacency = {}

    # ============================================================
    # GRAPH CONSTRUCTION
    # ============================================================

    def add_node(self, node_id, data=None):
        if node_id not in self.nodes:
            node = Node(node_id, data)

            self.nodes[node_id] = node
            self.adjacency[node_id] = []
            self.reverse_adjacency[node_id] = []

        return self.nodes[node_id]

    def add_edge(self, source_id, target_id, weight=1):
        source = self.add_node(source_id)
        target = self.add_node(target_id)

        # source -> target
        edge = Edge(source, target, weight)

        self.adjacency[source_id].append(edge)
        self.reverse_adjacency[target_id].append(edge)

        if not self.directed:

            # target -> source
            reverse_edge = Edge(
                target,
                source,
                weight
            )

            self.adjacency[target_id].append(
                reverse_edge
            )

            self.reverse_adjacency[source_id].append(
                reverse_edge
            )
    def reverse_neighbors(self, node_id):
        return self.reverse_adjacency.get(node_id, [])
    def neighbors(self, node_id):
        return self.adjacency.get(node_id, [])

    def get_node(self, node_id):
        return self.nodes.get(node_id)

    def __len__(self):
        return len(self.nodes)

    # ============================================================
    # PATH RECONSTRUCTION
    # ============================================================

    def _reconstruct_path(self, parent, start, goal):
        path = []

        current = goal

        while current is not None:
            path.append(current)

            if current == start:
                break

            current = parent.get(current)

        path.reverse()

        if not path or path[0] != start:
            return None

        return path

    # ============================================================
    # DIJKSTRA
    # ============================================================

    def dijkstra(self, start, goal):

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf")

        distances = {
            node_id: float("inf")
            for node_id in self.nodes
        }

        distances[start] = 0

        parent = {
            start: None
        }

        # counter avoids comparison problems between Node objects
        counter = count()

        queue = [
            (0, next(counter), start)
        ]

        visited = set()

        while queue:

            current_distance, _, current = heapq.heappop(queue)

            if current in visited:
                continue

            visited.add(current)

            if current == goal:
                path = self._reconstruct_path(
                    parent,
                    start,
                    goal
                )

                return path, current_distance

            for edge in self.neighbors(current):

                neighbor = edge.target.id

                new_distance = (
                    current_distance +
                    edge.weight
                )

                if new_distance < distances[neighbor]:

                    distances[neighbor] = new_distance

                    parent[neighbor] = current

                    heapq.heappush(
                        queue,
                        (
                            new_distance,
                            next(counter),
                            neighbor
                        )
                    )

        return None, float("inf")
    def dijkstra_visual(
        self,
        start,
        goal,
        record_frontier=False
    ):

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf"), {
                "expanded": [],
                "discovered": [],
                "edges_checked": [],
                "frontier": [],
                "expansion_count": 0,
                "edge_check_count": 0,
            }

        distances = {
            node_id: float("inf")
            for node_id in self.nodes
        }

        distances[start] = 0

        parent = {
            start: None
        }

        counter = count()

        queue = [
            (0, next(counter), start)
        ]

        visited = set()

        # ============================================================
        # TRACE
        # ============================================================

        expanded = []
        discovered = [start]
        edges_checked = []
        frontier_history = []

        # ============================================================
        # SEARCH
        # ============================================================

        while queue:

            current_distance, _, current = heapq.heappop(
                queue
            )

            if current in visited:
                continue

            visited.add(current)

            # --------------------------------------------------------
            # Record node expansion
            # --------------------------------------------------------

            expanded.append({
                "node": current,
                "distance": current_distance
            })

            # --------------------------------------------------------
            # Record frontier
            # --------------------------------------------------------

            if record_frontier:

                frontier_history.append([
                    item[2]
                    for item in queue
                ])

            # --------------------------------------------------------
            # Goal reached
            # --------------------------------------------------------

            if current == goal:

                path = self._reconstruct_path(
                    parent,
                    start,
                    goal
                )

                trace = {
                    "expanded": expanded,
                    "discovered": discovered,
                    "edges_checked": edges_checked,
                    "frontier": frontier_history,

                    "expansion_count": len(expanded),
                    "edge_check_count": len(edges_checked),

                    "visited": list(visited),
                }

                return path, current_distance, trace

            # --------------------------------------------------------
            # Expand neighbors
            # --------------------------------------------------------

            for edge in self.neighbors(current):

                neighbor = edge.target.id

                # Record edge examination
                edges_checked.append({
                    "source": current,
                    "target": neighbor,
                    "weight": edge.weight
                })

                new_distance = (
                    current_distance +
                    edge.weight
                )

                if new_distance < distances[neighbor]:

                    distances[neighbor] = new_distance

                    parent[neighbor] = current

                    discovered.append(neighbor)

                    heapq.heappush(
                        queue,
                        (
                            new_distance,
                            next(counter),
                            neighbor
                        )
                    )

        # ============================================================
        # NO PATH
        # ============================================================

        trace = {
            "expanded": expanded,
            "discovered": discovered,
            "edges_checked": edges_checked,
            "frontier": frontier_history,

            "expansion_count": len(expanded),
            "edge_check_count": len(edges_checked),

            "visited": list(visited),
        }

        return None, float("inf"), trace
    # ============================================================
    # A*
    # ============================================================

    def a_star(self, start, goal, heuristic=None):

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf")

        if heuristic is None:

            heuristic = lambda a, b: 0

        g_score = {
            node_id: float("inf")
            for node_id in self.nodes
        }

        g_score[start] = 0

        parent = {
            start: None
        }

        counter = count()

        start_f = heuristic(
            self.nodes[start],
            self.nodes[goal]
        )

        queue = [
            (
                start_f,
                next(counter),
                start
            )
        ]

        closed = set()

        while queue:

            _, _, current = heapq.heappop(queue)

            if current in closed:
                continue

            if current == goal:

                path = self._reconstruct_path(
                    parent,
                    start,
                    goal
                )

                return path, g_score[goal]

            closed.add(current)

            for edge in self.neighbors(current):

                neighbor = edge.target.id

                tentative_g = (
                    g_score[current] +
                    edge.weight
                )

                if tentative_g < g_score[neighbor]:

                    parent[neighbor] = current

                    g_score[neighbor] = tentative_g

                    f_score = (
                        tentative_g +
                        heuristic(
                            self.nodes[neighbor],
                            self.nodes[goal]
                        )
                    )

                    heapq.heappush(
                        queue,
                        (
                            f_score,
                            next(counter),
                            neighbor
                        )
                    )

        return None, float("inf")
    def a_star_visual(
        self,
        start,
        goal,
        heuristic=None,
        record_frontier=False
    ):

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf"), {
                "expanded": [],
                "discovered": [],
                "edges_checked": [],
                "frontier": [],
                "expansion_count": 0,
                "edge_check_count": 0,
                "visited": []
            }

        if heuristic is None:
            heuristic = lambda a, b: 0

        # ============================================================
        # SCORES
        # ============================================================

        g_score = {
            node_id: float("inf")
            for node_id in self.nodes
        }

        g_score[start] = 0

        parent = {
            start: None
        }

        # ============================================================
        # PRIORITY QUEUE
        # ============================================================

        counter = count()

        start_f = heuristic(
            self.nodes[start],
            self.nodes[goal]
        )

        queue = [
            (
                start_f,
                next(counter),
                start
            )
        ]

        closed = set()

        # ============================================================
        # TRACE
        # ============================================================

        expanded = []

        discovered = [
            {
                "node": start,
                "g": 0,
                "f": start_f
            }
        ]

        edges_checked = []

        frontier_history = []

        # ============================================================
        # SEARCH
        # ============================================================

        while queue:

            current_f, _, current = heapq.heappop(
                queue
            )

            if current in closed:
                continue

            # --------------------------------------------------------
            # Record expansion
            # --------------------------------------------------------

            expanded.append({
                "node": current,
                "g": g_score[current],
                "f": current_f
            })

            # --------------------------------------------------------
            # Record frontier
            # --------------------------------------------------------

            if record_frontier:

                frontier_history.append([
                    item[2]
                    for item in queue
                ])

            # --------------------------------------------------------
            # Goal reached
            # --------------------------------------------------------

            if current == goal:

                path = self._reconstruct_path(
                    parent,
                    start,
                    goal
                )

                trace = {
                    "expanded": expanded,
                    "discovered": discovered,
                    "edges_checked": edges_checked,
                    "frontier": frontier_history,

                    "expansion_count": len(expanded),
                    "edge_check_count": len(edges_checked),

                    "visited": list(closed)
                }

                return path, g_score[goal], trace

            closed.add(current)

            # --------------------------------------------------------
            # Expand neighbors
            # --------------------------------------------------------

            for edge in self.neighbors(current):

                neighbor = edge.target.id

                # Record edge examination
                edges_checked.append({
                    "source": current,
                    "target": neighbor,
                    "weight": edge.weight
                })

                tentative_g = (
                    g_score[current] +
                    edge.weight
                )

                # ----------------------------------------------------
                # Better route found
                # ----------------------------------------------------

                if tentative_g < g_score[neighbor]:

                    parent[neighbor] = current

                    g_score[neighbor] = tentative_g

                    h = heuristic(
                        self.nodes[neighbor],
                        self.nodes[goal]
                    )

                    f_score = (
                        tentative_g +
                        h
                    )

                    discovered.append({
                        "node": neighbor,
                        "g": tentative_g,
                        "h": h,
                        "f": f_score
                    })

                    heapq.heappush(
                        queue,
                        (
                            f_score,
                            next(counter),
                            neighbor
                        )
                    )

        # ============================================================
        # NO PATH
        # ============================================================

        trace = {
            "expanded": expanded,
            "discovered": discovered,
            "edges_checked": edges_checked,
            "frontier": frontier_history,

            "expansion_count": len(expanded),
            "edge_check_count": len(edges_checked),

            "visited": list(closed)
        }

        return None, float("inf"), trace
    # ============================================================
    # BIDIRECTIONAL DIJKSTRA
    # ============================================================

    def bidirectional_dijkstra(self, start, goal):

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf")

        if start == goal:
            return [start], 0

        inf = float("inf")
        counter = count()

        # ============================================================
        # FORWARD SEARCH
        # ============================================================

        dist_f = {
            node_id: inf
            for node_id in self.nodes
        }

        dist_f[start] = 0

        parent_f = {
            start: None
        }

        queue_f = [
            (0, next(counter), start)
        ]

        settled_f = set()

        # ============================================================
        # BACKWARD SEARCH
        # ============================================================

        dist_b = {
            node_id: inf
            for node_id in self.nodes
        }

        dist_b[goal] = 0

        parent_b = {
            goal: None
        }

        queue_b = [
            (0, next(counter), goal)
        ]

        settled_b = set()

        # ============================================================
        # BEST PATH FOUND SO FAR
        # ============================================================

        best_cost = inf
        meeting_node = None

        # ============================================================
        # SEARCH
        # ============================================================

        while queue_f and queue_b:

            # Remove outdated entries
            while queue_f and queue_f[0][2] in settled_f:
                heapq.heappop(queue_f)

            while queue_b and queue_b[0][2] in settled_b:
                heapq.heappop(queue_b)

            if not queue_f or not queue_b:
                break

            min_f = queue_f[0][0]
            min_b = queue_b[0][0]

            # Correct termination condition
            if min_f + min_b >= best_cost:
                break

            # ========================================================
            # Expand the side with the smaller minimum distance
            # ========================================================

            if min_f <= min_b:

                current_dist, _, current = heapq.heappop(
                    queue_f
                )

                if current in settled_f:
                    continue

                settled_f.add(current)

                # If backward search has reached this node,
                # we have a complete candidate path
                if dist_b[current] < inf:

                    total_cost = (
                        dist_f[current] +
                        dist_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # Expand forward
                for edge in self.neighbors(current):

                    neighbor = edge.target.id

                    new_dist = (
                        dist_f[current] +
                        edge.weight
                    )

                    if new_dist < dist_f[neighbor]:

                        dist_f[neighbor] = new_dist
                        parent_f[neighbor] = current

                        heapq.heappush(
                            queue_f,
                            (
                                new_dist,
                                next(counter),
                                neighbor
                            )
                        )

                        # Check possible connection
                        if dist_b[neighbor] < inf:

                            total_cost = (
                                new_dist +
                                dist_b[neighbor]
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

            else:

                current_dist, _, current = heapq.heappop(
                    queue_b
                )

                if current in settled_b:
                    continue

                settled_b.add(current)

                # Candidate path
                if dist_f[current] < inf:

                    total_cost = (
                        dist_f[current] +
                        dist_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # Expand backward using reverse edges
                for edge in self.reverse_neighbors(current):

                    neighbor = edge.source.id

                    new_dist = (
                        dist_b[current] +
                        edge.weight
                    )

                    if new_dist < dist_b[neighbor]:

                        dist_b[neighbor] = new_dist
                        parent_b[neighbor] = current

                        heapq.heappush(
                            queue_b,
                            (
                                new_dist,
                                next(counter),
                                neighbor
                            )
                        )

                        # Check possible connection
                        if dist_f[neighbor] < inf:

                            total_cost = (
                                dist_f[neighbor] +
                                new_dist
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

        # ============================================================
        # NO PATH
        # ============================================================

        if meeting_node is None:
            return None, inf

        # ============================================================
        # RECONSTRUCT START -> MEETING
        # ============================================================

        path_forward = self._reconstruct_path(
            parent_f,
            start,
            meeting_node
        )

        # ============================================================
        # RECONSTRUCT MEETING -> GOAL
        # ============================================================

        path_backward = []

        current = meeting_node

        while current != goal:

            current = parent_b.get(current)

            if current is None:
                return None, inf

            path_backward.append(current)

        path = path_forward + path_backward

        return path, best_cost
    def bidirectional_dijkstra_visual(
        self,
        start,
        goal,
        record_frontier=False
    ):

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf"), {
                "expanded_forward": [],
                "expanded_backward": [],
                "discovered_forward": [],
                "discovered_backward": [],
                "edges_checked_forward": [],
                "edges_checked_backward": [],
                "frontier_forward": [],
                "frontier_backward": [],
                "meeting_node": None,
                "best_cost": float("inf"),
                "expansion_count": 0,
                "edge_check_count": 0
            }

        if start == goal:

            return [start], 0, {
                "expanded_forward": [],
                "expanded_backward": [],
                "discovered_forward": [start],
                "discovered_backward": [goal],
                "edges_checked_forward": [],
                "edges_checked_backward": [],
                "frontier_forward": [],
                "frontier_backward": [],
                "meeting_node": start,
                "best_cost": 0,
                "expansion_count": 0,
                "edge_check_count": 0
            }

        inf = float("inf")
        counter = count()

        # ============================================================
        # FORWARD SEARCH
        # ============================================================

        dist_f = {
            node_id: inf
            for node_id in self.nodes
        }

        dist_f[start] = 0

        parent_f = {
            start: None
        }

        queue_f = [
            (0, next(counter), start)
        ]

        settled_f = set()

        # ============================================================
        # BACKWARD SEARCH
        # ============================================================

        dist_b = {
            node_id: inf
            for node_id in self.nodes
        }

        dist_b[goal] = 0

        parent_b = {
            goal: None
        }

        queue_b = [
            (0, next(counter), goal)
        ]

        settled_b = set()

        # ============================================================
        # TRACE
        # ============================================================

        expanded_forward = []
        expanded_backward = []

        discovered_forward = [
            {
                "node": start,
                "distance": 0
            }
        ]

        discovered_backward = [
            {
                "node": goal,
                "distance": 0
            }
        ]

        edges_checked_forward = []
        edges_checked_backward = []

        frontier_forward = []
        frontier_backward = []

        # ============================================================
        # BEST PATH
        # ============================================================

        best_cost = inf
        meeting_node = None

        # ============================================================
        # SEARCH
        # ============================================================

        while queue_f and queue_b:

            # --------------------------------------------------------
            # Remove outdated entries
            # --------------------------------------------------------

            while queue_f and queue_f[0][2] in settled_f:
                heapq.heappop(queue_f)

            while queue_b and queue_b[0][2] in settled_b:
                heapq.heappop(queue_b)

            if not queue_f or not queue_b:
                break

            min_f = queue_f[0][0]
            min_b = queue_b[0][0]

            # --------------------------------------------------------
            # Termination
            # --------------------------------------------------------

            if min_f + min_b >= best_cost:
                break

            # ========================================================
            # FORWARD SEARCH
            # ========================================================

            if min_f <= min_b:

                current_dist, _, current = heapq.heappop(
                    queue_f
                )

                if current in settled_f:
                    continue

                settled_f.add(current)

                # Record expansion
                expanded_forward.append({
                    "node": current,
                    "distance": current_dist
                })

                # Record frontier
                if record_frontier:

                    frontier_forward.append([
                        item[2]
                        for item in queue_f
                    ])

                # ----------------------------------------------------
                # Check meeting
                # ----------------------------------------------------

                if dist_b[current] < inf:

                    total_cost = (
                        dist_f[current] +
                        dist_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # ----------------------------------------------------
                # Expand edges
                # ----------------------------------------------------

                for edge in self.neighbors(current):

                    neighbor = edge.target.id

                    edges_checked_forward.append({
                        "source": current,
                        "target": neighbor,
                        "weight": edge.weight
                    })

                    new_dist = (
                        dist_f[current] +
                        edge.weight
                    )

                    if new_dist < dist_f[neighbor]:

                        dist_f[neighbor] = new_dist

                        parent_f[neighbor] = current

                        discovered_forward.append({
                            "node": neighbor,
                            "distance": new_dist
                        })

                        heapq.heappush(
                            queue_f,
                            (
                                new_dist,
                                next(counter),
                                neighbor
                            )
                        )

                        # Check connection
                        if dist_b[neighbor] < inf:

                            total_cost = (
                                new_dist +
                                dist_b[neighbor]
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

            # ========================================================
            # BACKWARD SEARCH
            # ========================================================

            else:

                current_dist, _, current = heapq.heappop(
                    queue_b
                )

                if current in settled_b:
                    continue

                settled_b.add(current)

                # Record expansion
                expanded_backward.append({
                    "node": current,
                    "distance": current_dist
                })

                # Record frontier
                if record_frontier:

                    frontier_backward.append([
                        item[2]
                        for item in queue_b
                    ])

                # ----------------------------------------------------
                # Check meeting
                # ----------------------------------------------------

                if dist_f[current] < inf:

                    total_cost = (
                        dist_f[current] +
                        dist_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # ----------------------------------------------------
                # Expand reverse edges
                # ----------------------------------------------------

                for edge in self.reverse_neighbors(current):

                    neighbor = edge.source.id

                    edges_checked_backward.append({
                        "source": neighbor,
                        "target": current,
                        "weight": edge.weight
                    })

                    new_dist = (
                        dist_b[current] +
                        edge.weight
                    )

                    if new_dist < dist_b[neighbor]:

                        dist_b[neighbor] = new_dist

                        parent_b[neighbor] = current

                        discovered_backward.append({
                            "node": neighbor,
                            "distance": new_dist
                        })

                        heapq.heappush(
                            queue_b,
                            (
                                new_dist,
                                next(counter),
                                neighbor
                            )
                        )

                        # Check connection
                        if dist_f[neighbor] < inf:

                            total_cost = (
                                dist_f[neighbor] +
                                new_dist
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

        # ============================================================
        # NO PATH
        # ============================================================

        if meeting_node is None:

            trace = {
                "expanded_forward": expanded_forward,
                "expanded_backward": expanded_backward,

                "discovered_forward": discovered_forward,
                "discovered_backward": discovered_backward,

                "edges_checked_forward": edges_checked_forward,
                "edges_checked_backward": edges_checked_backward,

                "frontier_forward": frontier_forward,
                "frontier_backward": frontier_backward,

                "meeting_node": None,
                "best_cost": inf,

                "expansion_count": (
                    len(expanded_forward) +
                    len(expanded_backward)
                ),

                "edge_check_count": (
                    len(edges_checked_forward) +
                    len(edges_checked_backward)
                )
            }

            return None, inf, trace

        # ============================================================
        # PATH RECONSTRUCTION
        # ============================================================

        path_forward = self._reconstruct_path(
            parent_f,
            start,
            meeting_node
        )

        path_backward = []

        current = meeting_node

        while current != goal:

            current = parent_b.get(current)

            if current is None:

                return None, inf, {
                    "expanded_forward": expanded_forward,
                    "expanded_backward": expanded_backward,
                    "discovered_forward": discovered_forward,
                    "discovered_backward": discovered_backward,
                    "edges_checked_forward": edges_checked_forward,
                    "edges_checked_backward": edges_checked_backward,
                    "frontier_forward": frontier_forward,
                    "frontier_backward": frontier_backward,
                    "meeting_node": None,
                    "best_cost": inf,
                    "expansion_count": (
                        len(expanded_forward) +
                        len(expanded_backward)
                    ),
                    "edge_check_count": (
                        len(edges_checked_forward) +
                        len(edges_checked_backward)
                    )
                }

            path_backward.append(current)

        path = path_forward + path_backward

        # ============================================================
        # TRACE
        # ============================================================

        trace = {
            "expanded_forward": expanded_forward,
            "expanded_backward": expanded_backward,

            "discovered_forward": discovered_forward,
            "discovered_backward": discovered_backward,

            "edges_checked_forward": edges_checked_forward,
            "edges_checked_backward": edges_checked_backward,

            "frontier_forward": frontier_forward,
            "frontier_backward": frontier_backward,

            "meeting_node": meeting_node,
            "best_cost": best_cost,

            "expansion_count": (
                len(expanded_forward) +
                len(expanded_backward)
            ),

            "edge_check_count": (
                len(edges_checked_forward) +
                len(edges_checked_backward)
            ),

            "visited_forward": list(set(
                expanded_forward_item["node"]
                for expanded_forward_item
                in expanded_forward
            )),

            "visited_backward": list(set(
                expanded_backward_item["node"]
                for expanded_backward_item
                in expanded_backward
            ))
        }

        return path, best_cost, trace
    # ============================================================
    # BIDIRECTIONAL A*
    # ============================================================
    def bidirectional_a_star(
        self,
        start,
        goal,
        heuristic=None
    ):

        # ============================================================
        # VALIDATION
        # ============================================================

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf")

        if start == goal:
            return [start], 0

        if heuristic is None:
            heuristic = lambda a, b: 0.0

        inf = float("inf")

        # ============================================================
        # FORWARD SEARCH
        # ============================================================

        g_f = {
            node_id: inf
            for node_id in self.nodes
        }

        g_f[start] = 0.0

        parent_f = {
            start: None
        }

        # ============================================================
        # BACKWARD SEARCH
        # ============================================================

        g_b = {
            node_id: inf
            for node_id in self.nodes
        }

        g_b[goal] = 0.0

        # parent_b[node] = next node toward goal
        parent_b = {
            goal: None
        }

        # ============================================================
        # PRIORITY QUEUES
        # ============================================================

        counter = count()

        h_start = heuristic(
            self.nodes[start],
            self.nodes[goal]
        )

        h_goal = heuristic(
            self.nodes[goal],
            self.nodes[start]
        )

        queue_f = [
            (
                h_start,
                next(counter),
                start
            )
        ]

        queue_b = [
            (
                h_goal,
                next(counter),
                goal
            )
        ]

        # ============================================================
        # CLOSED SETS
        # ============================================================

        closed_f = set()
        closed_b = set()

        # ============================================================
        # BEST COMPLETE PATH
        # ============================================================

        best_cost = inf
        meeting_node = None

        # ============================================================
        # REMOVE STALE ENTRIES
        # ============================================================

        def clean_forward_queue():

            while queue_f:

                f, _, node = queue_f[0]

                # Already expanded
                if node in closed_f:

                    heapq.heappop(queue_f)
                    continue

                h = heuristic(
                    self.nodes[node],
                    self.nodes[goal]
                )

                expected_f = g_f[node] + h

                # Old entry produced before g[node] improved
                if f > expected_f + 1e-12:

                    heapq.heappop(queue_f)
                    continue

                break

        def clean_backward_queue():

            while queue_b:

                f, _, node = queue_b[0]

                # Already expanded
                if node in closed_b:

                    heapq.heappop(queue_b)
                    continue

                h = heuristic(
                    self.nodes[node],
                    self.nodes[start]
                )

                expected_f = g_b[node] + h

                # Old entry produced before g[node] improved
                if f > expected_f + 1e-12:

                    heapq.heappop(queue_b)
                    continue

                break

        # ============================================================
        # SEARCH
        # ============================================================

        while queue_f and queue_b:

            # --------------------------------------------------------
            # Clean queues
            # --------------------------------------------------------

            clean_forward_queue()
            clean_backward_queue()

            if not queue_f or not queue_b:
                break

            # --------------------------------------------------------
            # Current lower bounds
            # --------------------------------------------------------

            min_f = queue_f[0][0]
            min_b = queue_b[0][0]

            # ========================================================
            # CORRECT TERMINATION CONDITION
            #
            # Once both frontier lower bounds are >= the best complete
            # path we have found, no better path can exist.
            # ========================================================

            if (
                best_cost < inf
                and
                min_f >= best_cost
                and
                min_b >= best_cost
            ):
                break

            # ========================================================
            # SELECT DIRECTION
            # ========================================================

            if min_f <= min_b:

                # ====================================================
                # FORWARD EXPANSION
                # ====================================================

                _, _, current = heapq.heappop(
                    queue_f
                )

                if current in closed_f:
                    continue

                closed_f.add(current)

                # ----------------------------------------------------
                # Check connection
                #
                # The backward search does NOT need to have closed
                # this node. A finite g_b is already enough to create
                # a complete candidate path.
                # ----------------------------------------------------

                if g_b[current] < inf:

                    total_cost = (
                        g_f[current] +
                        g_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # ----------------------------------------------------
                # Expand forward edges
                # ----------------------------------------------------

                for edge in self.neighbors(current):

                    neighbor = edge.target.id

                    tentative_g = (
                        g_f[current] +
                        edge.weight
                    )

                    if tentative_g < g_f[neighbor]:

                        g_f[neighbor] = tentative_g

                        parent_f[neighbor] = current

                        h = heuristic(
                            self.nodes[neighbor],
                            self.nodes[goal]
                        )

                        f_score = (
                            tentative_g +
                            h
                        )

                        heapq.heappush(
                            queue_f,
                            (
                                f_score,
                                next(counter),
                                neighbor
                            )
                        )

                        # ------------------------------------------------
                        # Check connection immediately
                        # ------------------------------------------------

                        if g_b[neighbor] < inf:

                            total_cost = (
                                tentative_g +
                                g_b[neighbor]
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

            else:

                # ====================================================
                # BACKWARD EXPANSION
                # ====================================================

                _, _, current = heapq.heappop(
                    queue_b
                )

                if current in closed_b:
                    continue

                closed_b.add(current)

                # ----------------------------------------------------
                # Check connection
                # ----------------------------------------------------

                if g_f[current] < inf:

                    total_cost = (
                        g_f[current] +
                        g_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # ----------------------------------------------------
                # Expand reverse edges
                # ----------------------------------------------------

                for edge in self.reverse_neighbors(current):

                    # Original edge:
                    #
                    # neighbor ----> current

                    neighbor = edge.source.id

                    tentative_g = (
                        g_b[current] +
                        edge.weight
                    )

                    if tentative_g < g_b[neighbor]:

                        g_b[neighbor] = tentative_g

                        # neighbor -> current -> ... -> goal
                        parent_b[neighbor] = current

                        h = heuristic(
                            self.nodes[neighbor],
                            self.nodes[start]
                        )

                        f_score = (
                            tentative_g +
                            h
                        )

                        heapq.heappush(
                            queue_b,
                            (
                                f_score,
                                next(counter),
                                neighbor
                            )
                        )

                        # ------------------------------------------------
                        # Check connection immediately
                        # ------------------------------------------------

                        if g_f[neighbor] < inf:

                            total_cost = (
                                g_f[neighbor] +
                                tentative_g
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

        # ============================================================
        # NO PATH
        # ============================================================

        if meeting_node is None:
            return None, inf

        # ============================================================
        # RECONSTRUCT START -> MEETING
        # ============================================================

        path_forward = self._reconstruct_path(
            parent_f,
            start,
            meeting_node
        )

        if path_forward is None:
            return None, inf

        # ============================================================
        # RECONSTRUCT MEETING -> GOAL
        # ============================================================

        path_backward = []

        current = meeting_node

        while current != goal:

            current = parent_b.get(current)

            if current is None:
                return None, inf

            path_backward.append(current)

        # ============================================================
        # COMPLETE PATH
        # ============================================================

        path = (
            path_forward +
            path_backward
        )

        return path, best_cost

    def bidirectional_a_star_visual(
        self,
        start,
        goal,
        heuristic=None,
        record_frontier=False
    ):

        # ============================================================
        # INVALID NODES
        # ============================================================

        if start not in self.nodes or goal not in self.nodes:

            trace = {
                "expanded_forward": [],
                "expanded_backward": [],
                "discovered_forward": [],
                "discovered_backward": [],
                "edges_checked_forward": [],
                "edges_checked_backward": [],
                "frontier_forward": [],
                "frontier_backward": [],
                "meeting_node": None,
                "best_cost": float("inf"),
                "expansion_count": 0,
                "edge_check_count": 0,
                "visited_forward": [],
                "visited_backward": []
            }

            return None, float("inf"), trace

        # ============================================================
        # START == GOAL
        # ============================================================

        if start == goal:

            trace = {
                "expanded_forward": [],
                "expanded_backward": [],
                "discovered_forward": [],
                "discovered_backward": [],
                "edges_checked_forward": [],
                "edges_checked_backward": [],
                "frontier_forward": [],
                "frontier_backward": [],
                "meeting_node": start,
                "best_cost": 0,
                "expansion_count": 0,
                "edge_check_count": 0,
                "visited_forward": [],
                "visited_backward": []
            }

            return [start], 0, trace

        # ============================================================
        # DEFAULT HEURISTIC
        # ============================================================

        if heuristic is None:
            heuristic = lambda a, b: 0.0

        inf = float("inf")

        # ============================================================
        # FORWARD SEARCH
        # ============================================================

        g_f = {
            node_id: inf
            for node_id in self.nodes
        }

        g_f[start] = 0.0

        parent_f = {
            start: None
        }

        # ============================================================
        # BACKWARD SEARCH
        # ============================================================

        g_b = {
            node_id: inf
            for node_id in self.nodes
        }

        g_b[goal] = 0.0

        # parent_b[node] = next node toward goal
        parent_b = {
            goal: None
        }

        # ============================================================
        # PRIORITY QUEUES
        # ============================================================

        counter = count()

        h_start = heuristic(
            self.nodes[start],
            self.nodes[goal]
        )

        h_goal = heuristic(
            self.nodes[goal],
            self.nodes[start]
        )

        queue_f = [
            (
                h_start,
                next(counter),
                start
            )
        ]

        queue_b = [
            (
                h_goal,
                next(counter),
                goal
            )
        ]

        # ============================================================
        # CLOSED SETS
        # ============================================================

        closed_f = set()
        closed_b = set()

        # ============================================================
        # TRACE
        # ============================================================

        expanded_forward = []
        expanded_backward = []

        discovered_forward = [
            {
                "node": start,
                "g": 0.0,
                "h": h_start,
                "f": h_start
            }
        ]

        discovered_backward = [
            {
                "node": goal,
                "g": 0.0,
                "h": h_goal,
                "f": h_goal
            }
        ]

        edges_checked_forward = []
        edges_checked_backward = []

        frontier_forward = []
        frontier_backward = []

        # ============================================================
        # BEST COMPLETE PATH FOUND
        # ============================================================

        best_cost = inf
        meeting_node = None

        # ============================================================
        # HELPER:
        # REMOVE STALE ENTRIES
        # ============================================================

        def clean_forward_queue():

            while queue_f:

                f, _, node = queue_f[0]

                if node in closed_f:
                    heapq.heappop(queue_f)
                    continue

                # This queue entry may be stale because g[node]
                # has subsequently been improved.
                h = heuristic(
                    self.nodes[node],
                    self.nodes[goal]
                )

                expected_f = g_f[node] + h

                if f > expected_f + 1e-12:
                    heapq.heappop(queue_f)
                    continue

                break

        def clean_backward_queue():

            while queue_b:

                f, _, node = queue_b[0]

                if node in closed_b:
                    heapq.heappop(queue_b)
                    continue

                h = heuristic(
                    self.nodes[node],
                    self.nodes[start]
                )

                expected_f = g_b[node] + h

                if f > expected_f + 1e-12:
                    heapq.heappop(queue_b)
                    continue

                break

        # ============================================================
        # SEARCH
        # ============================================================

        while queue_f and queue_b:

            # --------------------------------------------------------
            # Remove stale entries
            # --------------------------------------------------------

            clean_forward_queue()
            clean_backward_queue()

            if not queue_f or not queue_b:
                break

            # --------------------------------------------------------
            # CURRENT LOWER BOUNDS
            #
            # min f in each A* frontier is a lower bound on a
            # complete path through that direction.
            # --------------------------------------------------------

            min_f = queue_f[0][0]
            min_b = queue_b[0][0]

            # ========================================================
            # IMPORTANT TERMINATION CONDITION
            #
            # If BOTH searches have lower bounds >= best_cost,
            # no cheaper complete path can exist.
            # ========================================================

            if (
                best_cost < inf
                and
                min_f >= best_cost
                and
                min_b >= best_cost
            ):
                break

            # ========================================================
            # SELECT SEARCH DIRECTION
            # ========================================================

            if min_f <= min_b:

                # ====================================================
                # FORWARD
                # ====================================================

                current_f, _, current = heapq.heappop(
                    queue_f
                )

                if current in closed_f:
                    continue

                closed_f.add(current)

                current_g = g_f[current]

                current_h = heuristic(
                    self.nodes[current],
                    self.nodes[goal]
                )

                # ----------------------------------------------------
                # TRACE EXPANSION
                # ----------------------------------------------------

                expanded_forward.append({
                    "node": current,
                    "g": current_g,
                    "h": current_h,
                    "f": current_g + current_h
                })

                if record_frontier:

                    frontier_forward.append([
                        item[2]
                        for item in queue_f
                    ])

                # ----------------------------------------------------
                # MEETING / CONNECTION
                #
                # The other search does NOT need to have closed
                # the node. Discovery is enough to form a valid
                # candidate path.
                # ----------------------------------------------------

                if g_b[current] < inf:

                    total_cost = (
                        g_f[current] +
                        g_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # ----------------------------------------------------
                # EXPAND FORWARD EDGES
                # ----------------------------------------------------

                for edge in self.neighbors(current):

                    neighbor = edge.target.id

                    edges_checked_forward.append({
                        "source": current,
                        "target": neighbor,
                        "weight": edge.weight
                    })

                    tentative_g = (
                        g_f[current] +
                        edge.weight
                    )

                    if tentative_g < g_f[neighbor]:

                        g_f[neighbor] = tentative_g

                        parent_f[neighbor] = current

                        h = heuristic(
                            self.nodes[neighbor],
                            self.nodes[goal]
                        )

                        f = tentative_g + h

                        discovered_forward.append({
                            "node": neighbor,
                            "g": tentative_g,
                            "h": h,
                            "f": f
                        })

                        heapq.heappush(
                            queue_f,
                            (
                                f,
                                next(counter),
                                neighbor
                            )
                        )

                        # ------------------------------------------------
                        # Candidate path through neighbor
                        # ------------------------------------------------

                        if g_b[neighbor] < inf:

                            total_cost = (
                                tentative_g +
                                g_b[neighbor]
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

            else:

                # ====================================================
                # BACKWARD
                # ====================================================

                current_f, _, current = heapq.heappop(
                    queue_b
                )

                if current in closed_b:
                    continue

                closed_b.add(current)

                current_g = g_b[current]

                current_h = heuristic(
                    self.nodes[current],
                    self.nodes[start]
                )

                # ----------------------------------------------------
                # TRACE EXPANSION
                # ----------------------------------------------------

                expanded_backward.append({
                    "node": current,
                    "g": current_g,
                    "h": current_h,
                    "f": current_g + current_h
                })

                if record_frontier:

                    frontier_backward.append([
                        item[2]
                        for item in queue_b
                    ])

                # ----------------------------------------------------
                # MEETING / CONNECTION
                # ----------------------------------------------------

                if g_f[current] < inf:

                    total_cost = (
                        g_f[current] +
                        g_b[current]
                    )

                    if total_cost < best_cost:

                        best_cost = total_cost
                        meeting_node = current

                # ----------------------------------------------------
                # REVERSE EDGES
                # ----------------------------------------------------

                for edge in self.reverse_neighbors(current):

                    # Original edge:

                    # neighbor -----> current

                    neighbor = edge.source.id

                    edges_checked_backward.append({
                        "source": neighbor,
                        "target": current,
                        "weight": edge.weight
                    })

                    tentative_g = (
                        g_b[current] +
                        edge.weight
                    )

                    if tentative_g < g_b[neighbor]:

                        g_b[neighbor] = tentative_g

                        parent_b[neighbor] = current

                        h = heuristic(
                            self.nodes[neighbor],
                            self.nodes[start]
                        )

                        f = tentative_g + h

                        discovered_backward.append({
                            "node": neighbor,
                            "g": tentative_g,
                            "h": h,
                            "f": f
                        })

                        heapq.heappush(
                            queue_b,
                            (
                                f,
                                next(counter),
                                neighbor
                            )
                        )

                        # ------------------------------------------------
                        # Candidate path through neighbor
                        # ------------------------------------------------

                        if g_f[neighbor] < inf:

                            total_cost = (
                                g_f[neighbor] +
                                tentative_g
                            )

                            if total_cost < best_cost:

                                best_cost = total_cost
                                meeting_node = neighbor

        # ============================================================
        # NO PATH
        # ============================================================

        if meeting_node is None:

            trace = {
                "expanded_forward": expanded_forward,
                "expanded_backward": expanded_backward,

                "discovered_forward": discovered_forward,
                "discovered_backward": discovered_backward,

                "edges_checked_forward": edges_checked_forward,
                "edges_checked_backward": edges_checked_backward,

                "frontier_forward": frontier_forward,
                "frontier_backward": frontier_backward,

                "meeting_node": None,
                "best_cost": inf,

                "expansion_count": (
                    len(expanded_forward) +
                    len(expanded_backward)
                ),

                "edge_check_count": (
                    len(edges_checked_forward) +
                    len(edges_checked_backward)
                ),

                "visited_forward": list(closed_f),
                "visited_backward": list(closed_b)
            }

            return None, inf, trace

        # ============================================================
        # RECONSTRUCT FORWARD PATH
        # ============================================================

        path_forward = self._reconstruct_path(
            parent_f,
            start,
            meeting_node
        )

        if path_forward is None:

            return None, inf, {
                "expanded_forward": expanded_forward,
                "expanded_backward": expanded_backward,
                "discovered_forward": discovered_forward,
                "discovered_backward": discovered_backward,
                "edges_checked_forward": edges_checked_forward,
                "edges_checked_backward": edges_checked_backward,
                "frontier_forward": frontier_forward,
                "frontier_backward": frontier_backward,
                "meeting_node": None,
                "best_cost": inf,
                "expansion_count": (
                    len(expanded_forward) +
                    len(expanded_backward)
                ),
                "edge_check_count": (
                    len(edges_checked_forward) +
                    len(edges_checked_backward)
                ),
                "visited_forward": list(closed_f),
                "visited_backward": list(closed_b)
            }

        # ============================================================
        # RECONSTRUCT BACKWARD PATH
        # ============================================================

        path_backward = []

        current = meeting_node

        while current != goal:

            current = parent_b.get(current)

            if current is None:

                return None, inf, {
                    "expanded_forward": expanded_forward,
                    "expanded_backward": expanded_backward,
                    "discovered_forward": discovered_forward,
                    "discovered_backward": discovered_backward,
                    "edges_checked_forward": edges_checked_forward,
                    "edges_checked_backward": edges_checked_backward,
                    "frontier_forward": frontier_forward,
                    "frontier_backward": frontier_backward,
                    "meeting_node": None,
                    "best_cost": inf,
                    "expansion_count": (
                        len(expanded_forward) +
                        len(expanded_backward)
                    ),
                    "edge_check_count": (
                        len(edges_checked_forward) +
                        len(edges_checked_backward)
                    ),
                    "visited_forward": list(closed_f),
                    "visited_backward": list(closed_b)
                }

            path_backward.append(current)

        # ============================================================
        # COMPLETE PATH
        # ============================================================

        path = (
            path_forward +
            path_backward
        )

        # ============================================================
        # FINAL TRACE
        # ============================================================

        trace = {
            "expanded_forward": expanded_forward,
            "expanded_backward": expanded_backward,

            "discovered_forward": discovered_forward,
            "discovered_backward": discovered_backward,

            "edges_checked_forward": edges_checked_forward,
            "edges_checked_backward": edges_checked_backward,

            "frontier_forward": frontier_forward,
            "frontier_backward": frontier_backward,

            "meeting_node": meeting_node,
            "best_cost": best_cost,

            "expansion_count": (
                len(expanded_forward) +
                len(expanded_backward)
            ),

            "edge_check_count": (
                len(edges_checked_forward) +
                len(edges_checked_backward)
            ),

            "visited_forward": list(closed_f),
            "visited_backward": list(closed_b)
        }

        return path, best_cost, trace

    def bfs(self, start, goal):

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf")

        if start == goal:
            return [start], 0

        queue = deque([start])

        parent = {
            start: None
        }

        visited = {
            start
        }

        while queue:

            current = queue.popleft()

            if current == goal:

                path = self._reconstruct_path(
                    parent,
                    start,
                    goal
                )

                # In an unweighted graph,
                # shortest-path cost = number of edges
                return path, len(path) - 1

            for edge in self.neighbors(current):

                neighbor = edge.target.id

                if neighbor in visited:
                    continue

                visited.add(neighbor)

                parent[neighbor] = current

                queue.append(neighbor)

        return None, float("inf")
    def __repr__(self):

        edge_count = sum(
            len(edges)
            for edges in self.adjacency.values()
        )

        if not self.directed:
            edge_count //= 2

        return (
            f"Graph(nodes={len(self.nodes)}, "
            f"edges={edge_count}, "
            f"directed={self.directed})"
        )
    def build_contraction_hierarchy(self):

            # ============================================================
            # RESET
            # ============================================================

            self.ch_rank = {}
            self.ch_order = []

            self.ch_adjacency = {
                node_id: []
                for node_id in self.nodes
            }

            self.ch_reverse_adjacency = {
                node_id: []
                for node_id in self.nodes
            }

            self.ch_ready = False

            # ============================================================
            # WORKING GRAPH
            #
            # working_edges[source] = CHEdge(...)
            #
            # This contains original edges + shortcuts.
            # ============================================================

            working_edges = {
                node_id: []
                for node_id in self.nodes
            }

            for source, edges in self.adjacency.items():

                for edge in edges:

                    working_edges[source].append(
                        CHEdge(
                            source=edge.source.id,
                            target=edge.target.id,
                            weight=edge.weight,
                            middle=None
                        )
                    )

            # ============================================================
            # ACTIVE NODES
            # ============================================================

            remaining = set(self.nodes.keys())

            # ============================================================
            # INCOMING EDGES
            # ============================================================

            def get_incoming(node_id):

                incoming = []

                for source in remaining:

                    for edge in working_edges[source]:

                        if edge.target in remaining:
                            if edge.target == node_id:
                                incoming.append(edge)

                return incoming

            # ============================================================
            # OUTGOING EDGES
            # ============================================================

            def get_outgoing(node_id):

                return [
                    edge
                    for edge in working_edges[node_id]
                    if edge.target in remaining
                    and edge.target != node_id
                ]

            # ============================================================
            # WITNESS SEARCH
            # ============================================================

            def witness_search(
                source,
                target,
                max_cost,
                forbidden_node
            ):

                if source == target:
                    return True

                distances = {
                    source: 0
                }

                counter = count()

                queue = [
                    (0, next(counter), source)
                ]

                settled = set()

                while queue:

                    distance, _, current = heapq.heappop(queue)

                    if current in settled:
                        continue

                    settled.add(current)

                    if distance >= max_cost:
                        continue

                    if current == target:
                        return True

                    for edge in working_edges[current]:

                        neighbor = edge.target

                        # Only active nodes
                        if neighbor not in remaining:
                            continue

                        # Cannot use the node being contracted
                        if neighbor == forbidden_node:
                            continue

                        new_distance = (
                            distance +
                            edge.weight
                        )

                        if new_distance >= max_cost:
                            continue

                        if new_distance < distances.get(
                            neighbor,
                            float("inf")
                        ):

                            distances[neighbor] = new_distance

                            heapq.heappush(
                                queue,
                                (
                                    new_distance,
                                    next(counter),
                                    neighbor
                                )
                            )

                return False

            # ============================================================
            # CONTRACTION PRIORITY
            # ============================================================

            def contraction_priority(node_id):

                incoming = get_incoming(node_id)
                outgoing = get_outgoing(node_id)

                # Simple degree-based priority.
                #
                # For now we intentionally don't use a sophisticated
                # edge-difference metric.

                return len(incoming) + len(outgoing)

            # ============================================================
            # CONTRACTION
            # ============================================================

            rank = 0

            while remaining:

                # --------------------------------------------------------
                # Select node
                # --------------------------------------------------------

                node_id = min(
                    remaining,
                    key=contraction_priority
                )

                # --------------------------------------------------------
                # Current active edges
                # --------------------------------------------------------

                incoming = get_incoming(node_id)
                outgoing = get_outgoing(node_id)

                # --------------------------------------------------------
                # Generate shortcuts
                # --------------------------------------------------------

                shortcuts = []

                for in_edge in incoming:

                    source = in_edge.source

                    if source == node_id:
                        continue

                    if source not in remaining:
                        continue

                    for out_edge in outgoing:

                        target = out_edge.target

                        if target == node_id:
                            continue

                        if target not in remaining:
                            continue

                        if source == target:
                            continue

                        shortcut_weight = (
                            in_edge.weight +
                            out_edge.weight
                        )

                        # ------------------------------------------------
                        # Is there already a path that avoids node_id?
                        # ------------------------------------------------

                        witness_exists = witness_search(
                            source,
                            target,
                            shortcut_weight,
                            node_id
                        )

                        if witness_exists:
                            continue

                        # ------------------------------------------------
                        # Check existing active edge
                        # ------------------------------------------------

                        already_exists = False

                        for existing in working_edges[source]:

                            if existing.target != target:
                                continue

                            if existing.target not in remaining:
                                continue

                            if existing.weight <= shortcut_weight:

                                already_exists = True
                                break

                        if already_exists:
                            continue

                        shortcuts.append(
                            CHEdge(
                                source=source,
                                target=target,
                                weight=shortcut_weight,
                                middle=node_id
                            )
                        )

                # --------------------------------------------------------
                # Add shortcuts
                # --------------------------------------------------------

                for shortcut in shortcuts:

                    working_edges[
                        shortcut.source
                    ].append(shortcut)

                # --------------------------------------------------------
                # Assign rank
                # --------------------------------------------------------

                self.ch_rank[node_id] = rank

                self.ch_order.append(node_id)

                rank += 1

                # --------------------------------------------------------
                # Remove node from active graph
                # --------------------------------------------------------

                remaining.remove(node_id)

            # ============================================================
            # BUILD FINAL UPWARD GRAPH
            # ============================================================

            for source in self.nodes:

                for edge in working_edges[source]:

                    target = edge.target

                    if source not in self.ch_rank:
                        continue

                    if target not in self.ch_rank:
                        continue

                    if (
                        self.ch_rank[source]
                        <
                        self.ch_rank[target]
                    ):

                        self.ch_adjacency[source].append(edge)

                        self.ch_reverse_adjacency[target].append(edge)

            # ============================================================
            # READY
            # ============================================================

            self.ch_ready = True

            original_edges = sum(
                len(edges)
                for edges in self.adjacency.values()
            )

            ch_edges = sum(
                len(edges)
                for edges in self.ch_adjacency.values()
            )

            shortcuts = sum(
                1
                for edges in working_edges.values()
                for edge in edges
                if edge.middle is not None
            )

            return {
                "nodes": len(self.nodes),
                "original_edges": original_edges,
                "ch_edges": ch_edges,
                "shortcuts": shortcuts,
                "order": self.ch_order.copy(),
                "rank": self.ch_rank.copy()
            }

    def contraction_hierarchy(self, start, goal):
        """
        Contraction Hierarchy shortest-path query.

        Returns:
            path, cost
        """

        # ============================================================
        # VALIDATION
        # ============================================================

        if start not in self.nodes or goal not in self.nodes:
            return None, float("inf")

        if not self.ch_ready:
            raise RuntimeError(
                "Contraction Hierarchy has not been built. "
                "Call build_contraction_hierarchy() first."
            )

        if start == goal:
            return [start], 0

        inf = float("inf")
        counter = count()

        # ============================================================
        # FORWARD SEARCH
        #
        # Only upward edges:
        #
        # rank(source) < rank(target)
        # ============================================================

        dist_f = {
            node_id: inf
            for node_id in self.nodes
        }

        dist_f[start] = 0

        parent_f = {
            start: None
        }

        queue_f = [
            (0, next(counter), start)
        ]

        settled_f = set()

        # ============================================================
        # BACKWARD SEARCH
        #
        # Reverse of upward CH edges.
        # ============================================================

        dist_b = {
            node_id: inf
            for node_id in self.nodes
        }

        dist_b[goal] = 0

        parent_b = {
            goal: None
        }

        queue_b = [
            (0, next(counter), goal)
        ]

        settled_b = set()

        # ============================================================
        # BEST COMPLETE PATH
        # ============================================================

        best_cost = inf
        meeting_node = None

        # ============================================================
        # SEARCH
        # ============================================================

        while queue_f or queue_b:

            # --------------------------------------------------------
            # FORWARD
            # --------------------------------------------------------

            if queue_f:

                current_dist, _, current = heapq.heappop(queue_f)

                if current not in settled_f:

                    settled_f.add(current)

                    # If backward search already reached this node
                    if dist_b[current] < inf:

                        total = (
                            dist_f[current] +
                            dist_b[current]
                        )

                        if total < best_cost:

                            best_cost = total
                            meeting_node = current

                    # Expand upward edges
                    for edge in self.ch_adjacency[current]:

                        neighbor = edge.target

                        new_distance = (
                            dist_f[current] +
                            edge.weight
                        )

                        if new_distance < dist_f[neighbor]:

                            dist_f[neighbor] = new_distance

                            parent_f[neighbor] = current

                            heapq.heappush(
                                queue_f,
                                (
                                    new_distance,
                                    next(counter),
                                    neighbor
                                )
                            )

            # --------------------------------------------------------
            # BACKWARD
            # --------------------------------------------------------

            if queue_b:

                current_dist, _, current = heapq.heappop(queue_b)

                if current not in settled_b:

                    settled_b.add(current)

                    # If forward search already reached this node
                    if dist_f[current] < inf:

                        total = (
                            dist_f[current] +
                            dist_b[current]
                        )

                        if total < best_cost:

                            best_cost = total
                            meeting_node = current

                    # Follow reverse upward edges
                    for edge in self.ch_reverse_adjacency[current]:

                        neighbor = edge.source

                        new_distance = (
                            dist_b[current] +
                            edge.weight
                        )

                        if new_distance < dist_b[neighbor]:

                            dist_b[neighbor] = new_distance

                            # Actual path direction:
                            #
                            # neighbor -> current
                            #
                            parent_b[neighbor] = current

                            heapq.heappush(
                                queue_b,
                                (
                                    new_distance,
                                    next(counter),
                                    neighbor
                                )
                            )

        # ============================================================
        # NO PATH
        # ============================================================

        if meeting_node is None:
            return None, inf

        # ============================================================
        # START -> MEETING
        # ============================================================

        path_forward = self._reconstruct_path(
            parent_f,
            start,
            meeting_node
        )

        if path_forward is None:
            return None, inf

        # ============================================================
        # MEETING -> GOAL
        # ============================================================

        path_backward = []

        current = meeting_node

        while current != goal:

            current = parent_b.get(current)

            if current is None:
                return None, inf

            path_backward.append(current)

        # ============================================================
        # COMPLETE PATH
        # ============================================================

        path = (
            path_forward +
            path_backward
        )

        return path, best_cost

    def build_grid(
        self,
        rows,
        cols,
        weight=1,
        diagonal=False
    ):
        """
        Build a rectangular grid graph.

        Node IDs are:
            0 ... rows*cols-1

        Coordinates are stored in node.data:
            {"row": r, "col": c}
        """

        # ------------------------------------------------------------
        # Create nodes
        # ------------------------------------------------------------

        for r in range(rows):

            for c in range(cols):

                node_id = r * cols + c

                self.add_node(
                    node_id,
                    {
                        "row": r,
                        "col": c
                    }
                )

        # ------------------------------------------------------------
        # Add edges
        # ------------------------------------------------------------

        directions = [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1)
        ]

        if diagonal:

            directions += [
                (-1, -1),
                (-1, 1),
                (1, -1),
                (1, 1)
            ]

        for r in range(rows):

            for c in range(cols):

                source = r * cols + c

                for dr, dc in directions:

                    nr = r + dr
                    nc = c + dc

                    if (
                        0 <= nr < rows
                        and
                        0 <= nc < cols
                    ):

                        target = nr * cols + nc

                        # For undirected graphs, only add each
                        # connection once.
                        if not self.directed:

                            if target <= source:
                                continue

                        self.add_edge(
                            source,
                            target,
                            weight
                        )

        return self
    def _ch_witness_search(
        self,
        source,
        target,
        max_cost,
        forbidden_node
    ):
        """
        Determine whether there is a path from source to target
        cheaper than max_cost without using forbidden_node.

        Returns:
            True  -> witness path exists
            False -> no sufficiently cheap witness exists
        """

        if source == target:
            return True

        distances = {
            source: 0
        }

        counter = count()

        queue = [
            (0, next(counter), source)
        ]

        visited = set()

        while queue:

            distance, _, current = heapq.heappop(queue)

            if current in visited:
                continue

            visited.add(current)

            # No need to continue once the candidate
            # shortcut is already worse.
            if distance >= max_cost:
                continue

            if current == target:
                return True

            for edge in self.adjacency[current]:

                neighbor = edge.target.id

                # Never pass through the node being contracted.
                if neighbor == forbidden_node:
                    continue

                new_distance = (
                    distance +
                    edge.weight
                )

                if new_distance >= max_cost:
                    continue

                if (
                    neighbor not in distances
                    or
                    new_distance < distances[neighbor]
                ):

                    distances[neighbor] = new_distance

                    heapq.heappush(
                        queue,
                        (
                            new_distance,
                            next(counter),
                            neighbor
                        )
                    )

        return False
    def _contract_node(self, node_id, rank):

        incoming = []

        outgoing = []

        # ------------------------------------------------------------
        # Incoming edges
        # ------------------------------------------------------------

        for source, edges in self.adjacency.items():

            if source == node_id:
                continue

            for edge in edges:

                if edge.target.id == node_id:

                    incoming.append(edge)

        # ------------------------------------------------------------
        # Outgoing edges
        # ------------------------------------------------------------

        for edge in self.adjacency[node_id]:

            if edge.target.id == node_id:
                continue

            outgoing.append(edge)

        # ------------------------------------------------------------
        # Create shortcuts
        # ------------------------------------------------------------

        shortcuts = []

        for in_edge in incoming:

            for out_edge in outgoing:

                source = in_edge.source.id
                target = out_edge.target.id

                if source == target:
                    continue

                shortcut_weight = (
                    in_edge.weight +
                    out_edge.weight
                )

                # ----------------------------------------------------
                # Check whether a witness already exists
                # ----------------------------------------------------

                witness_exists = self._ch_witness_search(
                    source,
                    target,
                    shortcut_weight,
                    node_id
                )

                if witness_exists:
                    continue

                shortcuts.append(
                    CHEdge(
                        source=source,
                        target=target,
                        weight=shortcut_weight,
                        middle=node_id
                    )
                )

        # ------------------------------------------------------------
        # Assign rank
        # ------------------------------------------------------------

        self.ch_rank[node_id] = rank

        return shortcuts

    # ============================================================
    # SERIALIZATION
    # ============================================================

    def save(self, filename):
        """
        Save the graph.

        Supported formats:
            .json   -> JSON
            .graph  -> pickle

        The .graph format preserves the complete Python object
        structure and is recommended for fast save/load.

        The JSON format is human-readable and portable.
        """

        filename = str(filename)

        if filename.lower().endswith(".json"):
            self._save_json(filename)

        elif filename.lower().endswith(".graph"):
            self._save_pickle(filename)

        else:
            raise ValueError(
                "Unsupported graph format. "
                "Use '.json' or '.graph'."
            )

    def load(self, filename):
        """
        Load graph data into this Graph instance.

        Supported formats:
            .json   -> JSON
            .graph  -> pickle

        Returns:
            self
        """

        filename = str(filename)

        if filename.lower().endswith(".json"):
            loaded = self._load_json(filename)

        elif filename.lower().endswith(".graph"):
            loaded = self._load_pickle(filename)

        else:
            raise ValueError(
                "Unsupported graph format. "
                "Use '.json' or '.graph'."
            )

        self.__dict__.clear()
        self.__dict__.update(loaded.__dict__)

        return self

    # ============================================================
    # PICKLE
    # ============================================================

    def _save_pickle(self, filename):
        """
        Save the complete Graph object using pickle.
        """

        with open(filename, "wb") as f:
            pickle.dump(
                self,
                f,
                protocol=pickle.HIGHEST_PROTOCOL
            )

    @staticmethod
    def _load_pickle(filename):
        """
        Load a complete Graph object from pickle.
        """

        with open(filename, "rb") as f:
            graph = pickle.load(f)

        if not isinstance(graph, Graph):
            raise TypeError(
                "The file does not contain a Graph object."
            )

        return graph

    # ============================================================
    # JSON
    # ============================================================

    def _save_json(self, filename):
        """
        Save graph to a JSON representation.

        Stores:
            - graph type
            - directed state
            - nodes + node.data
            - original edges
            - CH ready state
            - CH ranks
            - CH order
            - CH edges
            - CH shortcut middle nodes
        """

        data = {
            "format": "graph",
            "version": 1,

            # Graph properties
            "type": self.graph_type,
            "directed": self.directed,

            # Main graph
            "nodes": [],
            "edges": [],

            # Contraction Hierarchy
            "ch": {
                "ready": self.ch_ready,
                "rank": [],
                "order": self.ch_order,
                "edges": []
            }
        }

        # --------------------------------------------------------
        # NODES
        # --------------------------------------------------------

        for node_id, node in self.nodes.items():

            data["nodes"].append({
                "id": node_id,
                "data": node.data
            })

        # --------------------------------------------------------
        # ORIGINAL EDGES
        # --------------------------------------------------------

        for source_id, edges in self.adjacency.items():

            for edge in edges:

                data["edges"].append({
                    "source": edge.source.id,
                    "target": edge.target.id,
                    "weight": edge.weight
                })

        # --------------------------------------------------------
        # CH RANK
        # --------------------------------------------------------

        # Do NOT store ch_rank directly as a dictionary.
        #
        # JSON converts integer dictionary keys into strings.
        #
        # Instead:
        #
        #     {"node": ..., "rank": ...}
        #
        # This preserves the original node ID type.

        for node_id, rank in self.ch_rank.items():

            data["ch"]["rank"].append({
                "node": node_id,
                "rank": rank
            })

        # --------------------------------------------------------
        # CH EDGES
        # --------------------------------------------------------

        if self.ch_ready:

            for source_id, edges in self.ch_adjacency.items():

                for edge in edges:

                    data["ch"]["edges"].append({
                        "source": edge.source,
                        "target": edge.target,
                        "weight": edge.weight,
                        "middle": edge.middle
                    })

        # --------------------------------------------------------
        # WRITE
        # --------------------------------------------------------

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

    @staticmethod
    def _load_json(filename):
        """
        Load a Graph from JSON.
        """

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        # --------------------------------------------------------
        # VALIDATE FILE
        # --------------------------------------------------------

        if data.get("format") != "graph":

            raise ValueError(
                "Invalid graph JSON file."
            )

        # --------------------------------------------------------
        # CREATE GRAPH
        # --------------------------------------------------------

        graph = Graph(
            directed=data.get(
                "directed",
                False
            ),
            graph_type=data.get(
                "type",
                "generic"
            )
        )

        # --------------------------------------------------------
        # NODES
        # --------------------------------------------------------

        for node_data in data.get(
            "nodes",
            []
        ):

            graph.add_node(
                node_data["id"],
                node_data.get("data")
            )

        # --------------------------------------------------------
        # ORIGINAL EDGES
        # --------------------------------------------------------

        edges = data.get(
            "edges",
            []
        )

        if graph.directed:

            # Directed graph:
            # every stored edge is an actual edge.

            for edge in edges:

                graph.add_edge(
                    edge["source"],
                    edge["target"],
                    edge["weight"]
                )

        else:

            # Undirected graph:
            #
            # add_edge() automatically creates the reverse edge.
            #
            # Therefore avoid adding the same connection twice.

            seen = set()

            for edge in edges:

                source = edge["source"]
                target = edge["target"]
                weight = edge["weight"]

                key = (
                    min(source, target),
                    max(source, target),
                    weight
                )

                if key in seen:
                    continue

                seen.add(key)

                graph.add_edge(
                    source,
                    target,
                    weight
                )

        # --------------------------------------------------------
        # CH DATA
        # --------------------------------------------------------

        ch_data = data.get(
            "ch",
            {}
        )

        graph.ch_ready = ch_data.get(
            "ready",
            False
        )

        # --------------------------------------------------------
        # CH RANK
        # --------------------------------------------------------

        graph.ch_rank = {}

        for rank_data in ch_data.get(
            "rank",
            []
        ):

            node_id = rank_data["node"]
            rank = rank_data["rank"]

            graph.ch_rank[node_id] = rank

        # --------------------------------------------------------
        # CH ORDER
        # --------------------------------------------------------

        graph.ch_order = ch_data.get(
            "order",
            []
        )

        # --------------------------------------------------------
        # CH ADJACENCY
        # --------------------------------------------------------

        graph.ch_adjacency = {
            node_id: []
            for node_id in graph.nodes
        }

        graph.ch_reverse_adjacency = {
            node_id: []
            for node_id in graph.nodes
        }

        # --------------------------------------------------------
        # CH EDGES
        # --------------------------------------------------------

        for edge_data in ch_data.get(
            "edges",
            []
        ):

            source = edge_data["source"]
            target = edge_data["target"]
            weight = edge_data["weight"]
            middle = edge_data.get(
                "middle"
            )

            edge = CHEdge(
                source=source,
                target=target,
                weight=weight,
                middle=middle
            )

            graph.ch_adjacency[source].append(
                edge
            )

            graph.ch_reverse_adjacency[target].append(
                edge
            )

        return graph
    # ============================================================
    # GEOGRAPHICAL GRAPH GENERATION
    # ============================================================

    def generate_geographical_nodes(
        self,
        n,
        size,
        min_dist=0
    ):
        """
        Generate n random geographical nodes.

        Coordinates are stored in node.data:

            {
                "x": ...,
                "y": ...
            }

        Parameters:
            n:
                Number of nodes.

            size:
                Size of the geographical area.

            min_dist:
                Minimum distance allowed between nodes.

        Existing graph content is cleared.
        """

        # --------------------------------------------------------
        # CLEAR GRAPH
        # --------------------------------------------------------

        self.nodes.clear()
        self.adjacency.clear()
        self.reverse_adjacency.clear()

        # CH data must also be cleared
        self.ch_ready = False
        self.ch_rank.clear()
        self.ch_order.clear()
        self.ch_adjacency.clear()
        self.ch_reverse_adjacency.clear()

        # --------------------------------------------------------
        # GENERATE POINTS
        # --------------------------------------------------------

        points = []

        max_attempts = n * 50

        for _ in range(max_attempts):

            if len(points) >= n:
                break

            x = random.uniform(0, size)
            y = random.uniform(0, size)

            valid = all(
                math.hypot(
                    x - px,
                    y - py
                ) >= min_dist
                for px, py in points
            )

            if not valid:
                continue

            node_id = len(points)

            points.append((x, y))

            self.add_node(
                node_id,
                {
                    "x": x,
                    "y": y
                }
            )

        if len(points) < n:
            raise ValueError(
                "Could not place all nodes. "
                "Try increasing 'size' or decreasing "
                "'min_dist'."
            )

    # ============================================================
    # GEOGRAPHICAL MST
    # ============================================================

    def build_geographical_mst(self):
        """
        Build a Euclidean Minimum Spanning Tree.

        The MST guarantees that the generated graph is connected.
        Edge weights are Euclidean distances between nodes.
        """

        node_ids = list(self.nodes.keys())

        n = len(node_ids)

        if n <= 1:
            return

        # --------------------------------------------------------
        # UNION-FIND
        # --------------------------------------------------------

        parent = {
            node_id: node_id
            for node_id in node_ids
        }

        def find(x):

            while parent[x] != x:

                parent[x] = parent[parent[x]]
                x = parent[x]

            return x

        def union(a, b):

            root_a = find(a)
            root_b = find(b)

            if root_a == root_b:
                return False

            parent[root_b] = root_a

            return True

        # --------------------------------------------------------
        # GENERATE ALL POSSIBLE EDGES
        # --------------------------------------------------------

        edges = []

        for i in range(n):

            for j in range(i + 1, n):

                a = node_ids[i]
                b = node_ids[j]

                node_a = self.nodes[a]
                node_b = self.nodes[b]

                xa = node_a.data["x"]
                ya = node_a.data["y"]

                xb = node_b.data["x"]
                yb = node_b.data["y"]

                distance = math.hypot(
                    xa - xb,
                    ya - yb
                )

                edges.append(
                    (
                        distance,
                        a,
                        b
                    )
                )

        # --------------------------------------------------------
        # KRUSKAL
        # --------------------------------------------------------

        edges.sort(
            key=lambda edge: edge[0]
        )

        for distance, a, b in edges:

            if union(a, b):

                self.add_edge(
                    a,
                    b,
                    distance
                )

    # ============================================================
    # ADD LOCAL GEOGRAPHICAL EDGES
    # ============================================================

    def add_geographical_edges(
        self,
        max_degree=4,
        radius=200
    ):
        """
        Add additional local edges.

        An edge is added when:

            distance <= radius

        while respecting:

            degree <= max_degree

        Existing edges are ignored.
        """

        # --------------------------------------------------------
        # CURRENT DEGREE
        # --------------------------------------------------------

        degree = {
            node_id: len(
                self.adjacency[node_id]
            )
            for node_id in self.nodes
        }

        node_ids = list(
            self.nodes.keys()
        )

        # --------------------------------------------------------
        # SEARCH LOCAL NEIGHBORS
        # --------------------------------------------------------

        for a in node_ids:

            if degree[a] >= max_degree:
                continue

            node_a = self.nodes[a]

            xa = node_a.data["x"]
            ya = node_a.data["y"]

            candidates = []

            for b in node_ids:

                if a == b:
                    continue

                if degree[b] >= max_degree:
                    continue

                node_b = self.nodes[b]

                xb = node_b.data["x"]
                yb = node_b.data["y"]

                distance = math.hypot(
                    xa - xb,
                    ya - yb
                )

                if distance <= radius:

                    candidates.append(
                        (
                            distance,
                            b
                        )
                    )

            # Closest nodes first
            candidates.sort(
                key=lambda item: item[0]
            )

            # ----------------------------------------------------
            # ADD EDGES
            # ----------------------------------------------------

            for distance, b in candidates:

                if degree[a] >= max_degree:
                    break

                if degree[b] >= max_degree:
                    continue

                if self.has_edge(a, b):
                    continue

                self.add_edge(
                    a,
                    b,
                    distance
                )

                degree[a] += 1
                degree[b] += 1

    # ============================================================
    # COMPLETE GEOGRAPHICAL GRAPH GENERATOR
    # ============================================================

    def build_geographical(
        self,
        n=100,
        size=1000,
        min_dist=10,
        radius=150,
        max_degree=4
    ):
        """
        Generate a connected random geographical graph.

        Generation process:

            1. Generate random node positions.
            2. Enforce minimum node distance.
            3. Build an MST to guarantee connectivity.
            4. Add additional local edges.
            5. Respect maximum node degree.

        Node coordinates are stored in:

            node.data["x"]
            node.data["y"]

        The graph type is automatically set to:

            "geographical"
        """

        # --------------------------------------------------------
        # GRAPH TYPE
        # --------------------------------------------------------

        self.graph_type = "geographical"

        # --------------------------------------------------------
        # GENERATE NODES
        # --------------------------------------------------------

        self.generate_geographical_nodes(
            n=n,
            size=size,
            min_dist=min_dist
        )

        # --------------------------------------------------------
        # GUARANTEE CONNECTIVITY
        # --------------------------------------------------------

        self.build_geographical_mst()

        # --------------------------------------------------------
        # ADD LOCAL EDGES
        # --------------------------------------------------------

        self.add_geographical_edges(
            max_degree=max_degree,
            radius=radius
        )

        return self
    def has_edge(self, source_id, target_id):
        """
        Return True if an edge from source_id to target_id exists.
        """

        for edge in self.adjacency.get(source_id, []):
            if edge.target.id == target_id:
                return True

        return False
# ============================================================
# RANDOM GRAPH GENERATION
# ============================================================

    def generate_random(
        self,
        n=100,
        edge_probability=0.05,
        min_weight=1.0,
        max_weight=100.0
    ):
        """
        Generate a random weighted graph.

        Parameters:
            n:
                Number of nodes.

            edge_probability:
                Probability of creating an edge between
                two nodes.

            min_weight:
                Minimum random edge weight.

            max_weight:
                Maximum random edge weight.
        """

        # --------------------------------------------------------
        # VALIDATION
        # --------------------------------------------------------

        if n < 1:
            raise ValueError(
                "Number of nodes must be at least 1."
            )

        if not 0.0 <= edge_probability <= 1.0:
            raise ValueError(
                "edge_probability must be between 0 and 1."
            )

        if min_weight > max_weight:
            raise ValueError(
                "min_weight cannot be greater than max_weight."
            )

        # --------------------------------------------------------
        # RESET GRAPH DATA
        # --------------------------------------------------------

        self.nodes.clear()
        self.adjacency.clear()
        self.reverse_adjacency.clear()

        # Random graph invalidates CH

        self.ch_ready = False
        self.ch_rank.clear()
        self.ch_order.clear()
        self.ch_adjacency.clear()
        self.ch_reverse_adjacency.clear()

        self.graph_type = "random"

        # --------------------------------------------------------
        # CREATE NODES
        # --------------------------------------------------------

        for node_id in range(n):

            self.add_node(
                node_id,
                {}
            )

        # --------------------------------------------------------
        # CREATE RANDOM EDGES
        # --------------------------------------------------------

        if self.directed:

            # Directed graph
            for source in range(n):

                for target in range(n):

                    if source == target:
                        continue

                    if random.random() <= edge_probability:

                        weight = random.uniform(
                            min_weight,
                            max_weight
                        )

                        self.add_edge(
                            source,
                            target,
                            weight
                        )

        else:

            # Undirected graph
            #
            # Only test each pair once.
            # add_edge() automatically adds the reverse edge.

            for source in range(n):

                for target in range(
                    source + 1,
                    n
                ):

                    if random.random() <= edge_probability:

                        weight = random.uniform(
                            min_weight,
                            max_weight
                        )

                        self.add_edge(
                            source,
                            target,
                            weight
                        )

        return self