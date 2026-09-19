
from PyQt6.QtCore import *

from PyQt6.QtGui import *

from PyQt6.QtWidgets import *

import math


# ============================================================
# NODE ITEM
# ============================================================

class NodeItem(QGraphicsEllipseItem):

    NODE_RADIUS = 8

    def __init__(
        self,
        node_id,
        data=None,
        parent=None
    ):

        radius = self.NODE_RADIUS

        super().__init__(
            -radius,
            -radius,
            radius * 2,
            radius * 2,
            parent
        )

        self.node_id = node_id
        self.node_data = data or {}

        # ----------------------------------------------------
        # Graphics flags
        # ----------------------------------------------------

        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable,
            True
        )

        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable,
            False
        )

        # ----------------------------------------------------
        # Default style
        # ----------------------------------------------------

        self.normal_brush = QBrush(
            QColor(70, 130, 180)
        )

        self.normal_pen = QPen(
            QColor(30, 30, 30),
            1
        )

        # ----------------------------------------------------
        # Highlight style
        # ----------------------------------------------------

        self.highlight_brush = QBrush(
            QColor(255, 215, 0)
        )

        self.highlight_pen = QPen(
            QColor(180, 120, 0),
            2
        )

        # ----------------------------------------------------
        # Start style
        # ----------------------------------------------------

        self.start_brush = QBrush(
            QColor(50, 200, 80)
        )

        self.start_pen = QPen(
            QColor(20, 100, 40),
            3
        )

        # ----------------------------------------------------
        # Goal style
        # ----------------------------------------------------

        self.goal_brush = QBrush(
            QColor(220, 60, 60)
        )

        self.goal_pen = QPen(
            QColor(120, 20, 20),
            3
        )

        # ----------------------------------------------------
        # Apply default style
        # ----------------------------------------------------

        self.reset_style()

        self.setZValue(
            2
        )

        self.setToolTip(
            f"Node {node_id}"
        )

    # ========================================================
    # NORMAL STYLE
    # ========================================================

    def reset_style(self):

        self.setBrush(
            self.normal_brush
        )

        self.setPen(
            self.normal_pen
        )

        self.setZValue(
            2
        )

    # ========================================================
    # HIGHLIGHT
    # ========================================================

    def highlight(self):

        self.setBrush(
            self.highlight_brush
        )

        self.setPen(
            self.highlight_pen
        )

        self.setZValue(
            10
        )

    # ========================================================
    # START STYLE
    # ========================================================

    def set_start_style(self):

        self.setBrush(
            self.start_brush
        )

        self.setPen(
            self.start_pen
        )

        self.setZValue(
            20
        )

    # ========================================================
    # GOAL STYLE
    # ========================================================

    def set_goal_style(self):

        self.setBrush(
            self.goal_brush
        )

        self.setPen(
            self.goal_pen
        )

        self.setZValue(
            20
        )

    # ========================================================
    # MOUSE PRESS
    # ========================================================
    def mousePressEvent(
        self,
        event
     ):

        event.ignore()

# ============================================================
# EDGE ITEM
# ============================================================

class EdgeItem(QGraphicsLineItem):

    def __init__(
        self,
        source_item,
        target_item,
        weight=1.0,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.source_item = source_item
        self.target_item = target_item

        # Keep IDs directly on the edge.
        # This will be useful for route highlighting later.
        self.source_id = source_item.node_id
        self.target_id = target_item.node_id

        self.weight = weight

        # ----------------------------------------------------
        # Pens
        # ----------------------------------------------------

        self.normal_pen = QPen(
            QColor(150, 150, 150),
            1
        )

        self.route_pen = QPen(
            QColor(255, 80, 30),
            4
        )

        self.setZValue(
            1
        )

        self.setPen(
            self.normal_pen
        )

        self.update_position()

    # ========================================================
    # UPDATE POSITION
    # ========================================================

    def update_position(self):

        source_pos = (
            self.source_item.pos()
        )

        target_pos = (
            self.target_item.pos()
        )

        self.setLine(
            source_pos.x(),
            source_pos.y(),
            target_pos.x(),
            target_pos.y()
        )

    # ========================================================
    # HIGHLIGHT ROUTE
    # ========================================================

    def highlight(self):

        self.setPen(
            self.route_pen
        )

        self.setZValue(
            10
        )

    # ========================================================
    # RESET STYLE
    # ========================================================

    def reset_style(self):

        self.setPen(
            self.normal_pen
        )

        self.setZValue(
            1
        )


# ============================================================
# GRAPH VIEW
# ============================================================

class GraphView(QGraphicsView):

    # ========================================================
    # SIGNALS
    # ========================================================

    node_selected = pyqtSignal(
        int,
        dict
    )

    graph_loaded = pyqtSignal(
        str
    )

    graph_load_failed = pyqtSignal(
        str
    )

    # --------------------------------------------------------
    # NEW
    # --------------------------------------------------------

    route_nodes_selected = pyqtSignal(
        int,
        int
    )

    node_highlighted = pyqtSignal(
        int,
        bool
    )

    mode_changed = pyqtSignal(
        str
    )

    # ========================================================
    # INIT
    # ========================================================

    def __init__(
        self,
        api_client=None,
        parent=None
    ):

        super().__init__(
            parent
        )

        self.api_client = api_client

        self.current_graph_id = None

        self.scene = QGraphicsScene(
            self
        )

        self.setScene(
            self.scene
        )

        self.node_items = {}

        self.edge_items = []
        self.route_nodes = []
        self.route_edges = []
        self.graph_data = None

        # ====================================================
        # INTERACTION STATE
        # ====================================================

        self.view_mode = "view"

        self.start_node_id = None

        self.goal_node_id = None

        self.highlighted_nodes = set()
        # ====================================================
        # PAN / CLICK DETECTION
        # ====================================================

        self._mouse_press_pos = None
        self._dragging_view = False
        self._drag_start_pos = None
        # ====================================================
        # GRAPHICS
        # ====================================================

        self.setRenderHint(
            QPainter.RenderHint.Antialiasing
        )

        self.setRenderHint(
            QPainter.RenderHint.TextAntialiasing
        )

        self.setDragMode(
            QGraphicsView.DragMode.ScrollHandDrag
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorViewCenter
        )

        self.setBackgroundBrush(
            QColor(245, 245, 245)
        )

        # ====================================================
        # MODE BAR
        # ====================================================

        self.create_mode_bar()

        # ====================================================
        # SIGNALS
        # ====================================================

        self.scene.selectionChanged.connect(
            self.on_selection_changed
        )

    # ========================================================
    # MODE BAR
    # ========================================================

    def create_mode_bar(self):

        self.mode_bar = QFrame(
            self
        )

        self.mode_bar.setObjectName(
            "GraphModeBar"
        )

        self.mode_bar.setStyleSheet(
            """
            QFrame#GraphModeBar {
                background-color: white;
                border: 1px solid #cccccc;
                border-radius: 6px;
            }

            QPushButton {
                padding: 6px 12px;
                border: none;
                border-radius: 4px;
                background-color: #eeeeee;
            }

            QPushButton:hover {
                background-color: #dddddd;
            }

            QPushButton:checked {
                background-color: #4a90e2;
                color: white;
            }
            """
        )

        layout = QHBoxLayout(
            self.mode_bar
        )

        layout.setContentsMargins(
            6,
            4,
            6,
            4
        )

        layout.setSpacing(
            5
        )

        # ----------------------------------------------------
        # Label
        # ----------------------------------------------------

        label = QLabel(
            "Mode:"
        )

        layout.addWidget(
            label
        )

        # ----------------------------------------------------
        # View
        # ----------------------------------------------------

        self.view_mode_button = QPushButton(
            "View"
        )

        self.view_mode_button.setCheckable(
            True
        )

        self.view_mode_button.clicked.connect(
            lambda:
            self.set_mode("view")
        )

        layout.addWidget(
            self.view_mode_button
        )

        # ----------------------------------------------------
        # Route
        # ----------------------------------------------------

        self.route_mode_button = QPushButton(
            "Select Route"
        )

        self.route_mode_button.setCheckable(
            True
        )

        self.route_mode_button.clicked.connect(
            lambda:
            self.set_mode("route")
        )

        layout.addWidget(
            self.route_mode_button
        )

        # ----------------------------------------------------
        # Highlight
        # ----------------------------------------------------

        self.highlight_mode_button = QPushButton(
            "Highlight Nodes"
        )

        self.highlight_mode_button.setCheckable(
            True
        )

        self.highlight_mode_button.clicked.connect(
            lambda:
            self.set_mode("highlight")
        )

        layout.addWidget(
            self.highlight_mode_button
        )

        # ----------------------------------------------------
        # Route status
        # ----------------------------------------------------

        self.route_status_label = QLabel(
            "Start: —   Goal: —"
        )

        layout.addWidget(
            self.route_status_label
        )

        layout.addStretch()

        # ----------------------------------------------------
        # Button group
        # ----------------------------------------------------

        self.mode_button_group = QButtonGroup(
            self
        )

        self.mode_button_group.setExclusive(
            True
        )

        self.mode_button_group.addButton(
            self.view_mode_button
        )

        self.mode_button_group.addButton(
            self.route_mode_button
        )

        self.mode_button_group.addButton(
            self.highlight_mode_button
        )

        # ----------------------------------------------------
        # Default mode
        # ----------------------------------------------------

        self.view_mode_button.setChecked(
            True
        )

        # ----------------------------------------------------
        # Position
        # ----------------------------------------------------

        self.mode_bar.adjustSize()

        self.mode_bar.raise_()

    # ========================================================
    # RESIZE EVENT
    # ========================================================

    def resizeEvent(
        self,
        event
    ):

        super().resizeEvent(
            event
        )

        if hasattr(
            self,
            "mode_bar"
        ):

            margin = 10

            self.mode_bar.adjustSize()

            self.mode_bar.move(
                margin,
                margin
            )

            self.mode_bar.raise_()

    # ========================================================
    # SET MODE
    # ========================================================

    def set_mode(
        self,
        mode
    ):

        valid_modes = {
            "view",
            "route",
            "highlight"
        }

        if mode not in valid_modes:
            return

        self.view_mode = mode

        # ----------------------------------------------------
        # Update buttons
        # ----------------------------------------------------

        self.view_mode_button.setChecked(
            mode == "view"
        )

        self.route_mode_button.setChecked(
            mode == "route"
        )

        self.highlight_mode_button.setChecked(
            mode == "highlight"
        )

        # ----------------------------------------------------
        # Configure mouse behavior
        # ----------------------------------------------------

        if mode == "view":

            self.setDragMode(
                QGraphicsView.DragMode.ScrollHandDrag
            )

        else:

            self.setDragMode(
                QGraphicsView.DragMode.NoDrag
            )

        # ----------------------------------------------------
        # Notify outside
        # ----------------------------------------------------

        self.mode_changed.emit(
            mode
        )

    # ========================================================
    # NODE CLICKED
    # ========================================================

    def node_clicked(
        self,
        node_item
    ):

        node_id = node_item.node_id

        # ====================================================
        # VIEW MODE
        # ====================================================

        if self.view_mode == "view":

            node_item.setSelected(
                True
            )

            return

        # ====================================================
        # HIGHLIGHT MODE
        # ====================================================

        if self.view_mode == "highlight":

            self.toggle_node_highlight(
                node_id
            )

            return

        # ====================================================
        # ROUTE MODE
        # ====================================================

        if self.view_mode == "route":

            self.select_route_node(
                node_id
            )

    # ========================================================
    # TOGGLE NODE HIGHLIGHT
    # ========================================================

    def toggle_node_highlight(
        self,
        node_id
    ):

        item = self.node_items.get(
            node_id
        )

        if item is None:
            return

        # ----------------------------------------------------
        # Remove highlight
        # ----------------------------------------------------

        if node_id in self.highlighted_nodes:

            self.highlighted_nodes.remove(
                node_id
            )

            # Don't reset a route node incorrectly.
            if node_id == self.start_node_id:

                item.set_start_style()

            elif node_id == self.goal_node_id:

                item.set_goal_style()

            else:

                item.reset_style()

            self.node_highlighted.emit(
                node_id,
                False
            )

        # ----------------------------------------------------
        # Add highlight
        # ----------------------------------------------------

        else:

            self.highlighted_nodes.add(
                node_id
            )

            item.highlight()

            self.node_highlighted.emit(
                node_id,
                True
            )

    # ========================================================
    # SELECT ROUTE NODE
    # ========================================================

    def select_route_node(
        self,
        node_id
    ):

        # ====================================================
        # FIRST CLICK = START
        # ====================================================

        if self.start_node_id is None:

            self.start_node_id = node_id

            self.set_start_node_style(
                node_id
            )

            self.update_route_status()

            return

        # ====================================================
        # SAME NODE
        # ====================================================

        if node_id == self.start_node_id:

            return

        # ====================================================
        # SECOND CLICK = GOAL
        # ====================================================

        if self.goal_node_id is None:

            self.goal_node_id = node_id

            self.set_goal_node_style(
                node_id
            )

            self.update_route_status()

            # ------------------------------------------------
            # Both nodes are now available.
            # ------------------------------------------------

            self.route_nodes_selected.emit(
                self.start_node_id,
                self.goal_node_id
            )

            return

        # ====================================================
        # THIRD CLICK
        #
        # Start a completely new selection.
        # ====================================================

        self.clear_route_selection()

        self.start_node_id = node_id

        self.set_start_node_style(
            node_id
        )

        self.update_route_status()

    # ========================================================
    # START NODE STYLE
    # ========================================================

    def set_start_node_style(
        self,
        node_id
    ):

        item = self.node_items.get(
            node_id
        )

        if item is None:
            return

        item.set_start_style()

    # ========================================================
    # GOAL NODE STYLE
    # ========================================================

    def set_goal_node_style(
        self,
        node_id
    ):

        item = self.node_items.get(
            node_id
        )

        if item is None:
            return

        item.set_goal_style()

    # ========================================================
    # CLEAR ROUTE SELECTION
    # ========================================================

    def clear_route_selection(self):

        # ----------------------------------------------------
        # Start
        # ----------------------------------------------------

        if self.start_node_id is not None:

            item = self.node_items.get(
                self.start_node_id
            )

            if item is not None:

                if (
                    self.start_node_id
                    in self.highlighted_nodes
                ):

                    item.highlight()

                else:

                    item.reset_style()

        # ----------------------------------------------------
        # Goal
        # ----------------------------------------------------

        if self.goal_node_id is not None:

            item = self.node_items.get(
                self.goal_node_id
            )

            if item is not None:

                if (
                    self.goal_node_id
                    in self.highlighted_nodes
                ):

                    item.highlight()

                else:

                    item.reset_style()

        # ----------------------------------------------------
        # Clear state
        # ----------------------------------------------------

        self.start_node_id = None

        self.goal_node_id = None

        self.update_route_status()

    # ========================================================
    # UPDATE ROUTE STATUS
    # ========================================================

    def update_route_status(self):

        start_text = (
            str(self.start_node_id)
            if self.start_node_id is not None
            else "—"
        )

        goal_text = (
            str(self.goal_node_id)
            if self.goal_node_id is not None
            else "—"
        )

        self.route_status_label.setText(
            f"Start: {start_text}   Goal: {goal_text}"
        )

    # ========================================================
    # GET START NODE
    # ========================================================

    def get_start_node(self):

        return self.start_node_id

    # ========================================================
    # GET GOAL NODE
    # ========================================================

    def get_goal_node(self):

        return self.goal_node_id

    # ========================================================
    # GET ROUTE
    # ========================================================

    def get_selected_route(self):

        return (
            self.start_node_id,
            self.goal_node_id
        )

    # ========================================================
    # CLEAR GRAPH
    # ========================================================

    def clear_graph(self):

        self.scene.clear()

        self.node_items.clear()

        self.edge_items.clear()

        self.graph_data = None

        self.current_graph_id = None

        self.start_node_id = None

        self.goal_node_id = None

        self.highlighted_nodes.clear()

        self.update_route_status()

    # ========================================================
    # LOAD GRAPH DATA
    # ========================================================

    def load_graph(
        self,
        graph_data
    ):

        """
        Expected format:

        {
            "nodes": [
                {
                    "id": 0,
                    "data": {
                        "x": 10,
                        "y": 20
                    }
                }
            ],

            "edges": [
                {
                    "source": 0,
                    "target": 1,
                    "weight": 5
                }
            ]
        }
        """

        self.clear_graph()

        self.graph_data = graph_data

        nodes = graph_data.get(
            "nodes",
            []
        )

        edges = graph_data.get(
            "edges",
            []
        )

        # ----------------------------------------------------
        # CREATE NODES
        # ----------------------------------------------------

        self.create_nodes(
            nodes
        )

        # ----------------------------------------------------
        # CREATE EDGES
        # ----------------------------------------------------

        self.create_edges(
            edges
        )

        # ----------------------------------------------------
        # FIT GRAPH
        # ----------------------------------------------------

        self.fit_graph()

    # ========================================================
    # CREATE NODES
    # ========================================================

    def create_nodes(
        self,
        nodes
    ):

        positions = self.calculate_positions(
            nodes
        )

        for node in nodes:

            node_id = node.get(
                "id"
            )

            data = node.get(
                "data",
                {}
            )

            position = positions.get(
                node_id,
                QPointF(0, 0)
            )

            item = NodeItem(
                node_id=node_id,
                data=data
            )

            item.setPos(
                position
            )

            self.scene.addItem(
                item
            )

            self.node_items[
                node_id
            ] = item

    # ========================================================
    # CREATE EDGES
    # ========================================================

    def create_edges(
        self,
        edges
    ):

        for edge in edges:

            source_id = edge.get(
                "source"
            )

            target_id = edge.get(
                "target"
            )

            weight = edge.get(
                "weight",
                1.0
            )

            source_item = (
                self.node_items.get(
                    source_id
                )
            )

            target_item = (
                self.node_items.get(
                    target_id
                )
            )

            if (
                source_item is None
                or
                target_item is None
            ):

                continue

            edge_item = EdgeItem(
                source_item,
                target_item,
                weight
            )

            self.scene.addItem(
                edge_item
            )

            self.edge_items.append(
                edge_item
            )

    # ========================================================
    # CALCULATE POSITIONS
    # ========================================================

    def calculate_positions(
        self,
        nodes
    ):

        positions = {}

        # ----------------------------------------------------
        # USE EXISTING X/Y
        # ----------------------------------------------------

        has_positions = False

        for node in nodes:

            data = node.get(
                "data",
                {}
            )

            if (
                "x" in data
                and
                "y" in data
            ):

                has_positions = True

                break

        if has_positions:

            for node in nodes:

                node_id = node.get(
                    "id"
                )

                data = node.get(
                    "data",
                    {}
                )

                x = data.get(
                    "x",
                    0
                )

                y = data.get(
                    "y",
                    0
                )

                positions[
                    node_id
                ] = QPointF(
                    float(x),
                    float(y)
                )

            return positions

        # ----------------------------------------------------
        # DEFAULT GRID LAYOUT
        # ----------------------------------------------------

        count = len(
            nodes
        )

        if count == 0:

            return positions

        columns = int(
            math.ceil(
                math.sqrt(count)
            )
        )

        spacing = 50

        for index, node in enumerate(nodes):

            row = index // columns

            column = index % columns

            positions[
                node.get("id")
            ] = QPointF(
                column * spacing,
                row * spacing
            )

        return positions

    # ========================================================
    # FIT GRAPH
    # ========================================================

    def fit_graph(self):

        rect = (
            self.scene.itemsBoundingRect()
        )

        if not rect.isNull():

            self.fitInView(
                rect,
                Qt.AspectRatioMode.KeepAspectRatio
            )

    # ========================================================
    # ZOOM
    # ========================================================

    def wheelEvent(
        self,
        event
    ):

        zoom_factor = 1.15

        if (
            event.angleDelta().y()
            > 0
        ):

            self.scale(
                zoom_factor,
                zoom_factor
            )

        else:

            self.scale(
                1 / zoom_factor,
                1 / zoom_factor
            )

    # ========================================================
    # RESET VIEW
    # ========================================================

    def reset_view(self):

        self.resetTransform()

        self.fit_graph()

    # ========================================================
    # SELECTION
    # ========================================================

    def on_selection_changed(self):

        selected = (
            self.scene.selectedItems()
        )

        if not selected:

            return

        item = selected[0]

        if isinstance(
            item,
            NodeItem
        ):

            self.node_selected.emit(
                item.node_id,
                item.node_data
            )

    # ========================================================
    # LOAD GRAPH FROM API
    # ========================================================

    def load_graph_from_api(
        self,
        graph_id
    ):

        """
        Download graph structure from API
        and display it.
        """

        if self.api_client is None:

            error = (
                "Graph API client is not configured."
            )

            self.graph_load_failed.emit(
                error
            )

            return False

        try:

            graph_data = (
                self.api_client.get_graph_data(
                    graph_id
                )
            )

            self.load_graph(
                graph_data
            )

            self.current_graph_id = (
                graph_id
            )

            self.graph_loaded.emit(
                graph_id
            )

            return True

        except Exception as exc:

            error = str(
                exc
            )

            self.graph_load_failed.emit(
                error
            )

            return False





    # ========================================================
    # SHOW ROUTE
    # ========================================================

    def show_route(self, path):

        """
        Highlight a computed route.

        The route start/end nodes are taken from:
            self.start_node_id
            self.goal_node_id

        The path is a list of node IDs.
        """

        # ----------------------------------------------------
        # Clear previous route visualization ONLY
        # ----------------------------------------------------

        self.clear_route()

        if not path:
            return

        # ----------------------------------------------------
        # Existing start / goal IDs
        # ----------------------------------------------------

        start_node_id = self.get_start_node()
        goal_node_id = self.get_goal_node()

        # ----------------------------------------------------
        # Highlight route nodes
        # ----------------------------------------------------

        self.route_nodes = []

        for node_id in path:

            node_item = self.node_items.get(
                node_id
            )

            if node_item is None:
                continue

            self.route_nodes.append(
                node_item
            )

            # ----------------------------------------------
            # Don't overwrite start style
            # ----------------------------------------------

            if node_id == start_node_id:
                continue

            # ----------------------------------------------
            # Don't overwrite goal style
            # ----------------------------------------------

            if node_id == goal_node_id:
                continue

            node_item.setBrush(
                QBrush(
                    QColor(255, 193, 7)
                )
            )

            node_item.setPen(
                QPen(
                    QColor(255, 87, 34),
                    2
                )
            )

            node_item.setZValue(
                4
            )

        # ----------------------------------------------------
        # Highlight route edges
        # ----------------------------------------------------

        self.route_edges = []

        for i in range(
            len(path) - 1
        ):

            source_id = path[i]
            target_id = path[i + 1]

            for edge_item in self.edge_items:

                source = edge_item.source_id
                target = edge_item.target_id

                # ------------------------------------------
                # Directed OR undirected matching
                # ------------------------------------------

                if (
                    (
                        source == source_id
                        and
                        target == target_id
                    )
                    or
                    (
                        source == target_id
                        and
                        target == source_id
                    )
                ):

                    edge_item.highlight()

                    self.route_edges.append(
                        edge_item
                    )

                    break

    # ========================================================
    # CLEAR ROUTE
    # ========================================================

    def clear_route(self):

        """
        Remove the visual route highlighting.

        Does NOT remove the selected start/goal nodes.
        Does NOT remove manually highlighted nodes.
        """

        # ----------------------------------------------------
        # Restore route edges
        # ----------------------------------------------------

        for edge_item in self.route_edges:

            edge_item.reset_style()

        # ----------------------------------------------------
        # Restore route nodes
        # ----------------------------------------------------

        start_node_id = self.get_start_node()
        goal_node_id = self.get_goal_node()

        for node_item in self.route_nodes:

            node_id = node_item.node_id

            # ----------------------------------------------
            # Start node keeps its style
            # ----------------------------------------------

            if node_id == start_node_id:

                node_item.set_start_style()

                continue

            # ----------------------------------------------
            # Goal node keeps its style
            # ----------------------------------------------

            if node_id == goal_node_id:

                node_item.set_goal_style()

                continue

            # ----------------------------------------------
            # Manually highlighted node keeps highlight
            # ----------------------------------------------

            if node_id in self.highlighted_nodes:

                node_item.highlight()

                continue

            # ----------------------------------------------
            # Otherwise normal
            # ----------------------------------------------

            node_item.reset_style()

        # ----------------------------------------------------
        # Clear route visualization state
        # ----------------------------------------------------

        self.route_nodes = []

        self.route_edges = []
    # ========================================================
    # MOUSE PRESS
    # ========================================================

    def mousePressEvent(
        self,
        event
    ):

        if event.button() == Qt.MouseButton.LeftButton:

            self._mouse_press_pos = event.position()
            self._drag_start_pos = event.position()

            self._dragging_view = False

        super().mousePressEvent(
            event
        )


    # ========================================================
    # MOUSE MOVE
    # ========================================================

    def mouseMoveEvent(
        self,
        event
    ):

        if (
            self._mouse_press_pos is not None
            and
            event.buttons()
            & Qt.MouseButton.LeftButton
        ):

            distance = (
                event.position()
                - self._mouse_press_pos
            )

            # Small movement is still considered a click.
            if distance.manhattanLength() > 5:

                self._dragging_view = True

        super().mouseMoveEvent(
            event
        )


    # ========================================================
    # MOUSE RELEASE
    # ========================================================

    def mouseReleaseEvent(
        self,
        event
    ):

        # First let QGraphicsView finish dragging.
        super().mouseReleaseEvent(
            event
        )

        # ----------------------------------------------------
        # LEFT BUTTON ONLY
        # ----------------------------------------------------

        if (
            event.button()
            != Qt.MouseButton.LeftButton
        ):

            return

        # ----------------------------------------------------
        # If the mouse moved significantly,
        # this was navigation, NOT a click.
        # ----------------------------------------------------

        if self._dragging_view:

            self._mouse_press_pos = None
            self._drag_start_pos = None
            self._dragging_view = False

            return

        # ----------------------------------------------------
        # This was a click
        # ----------------------------------------------------

        scene_pos = self.mapToScene(
            event.position().toPoint()
        )

        item = self.scene.itemAt(
            scene_pos,
            self.transform()
        )

        # ----------------------------------------------------
        # Find clicked node
        # ----------------------------------------------------

        if isinstance(
            item,
            NodeItem
        ):

            self.node_clicked(
                item
            )

        # ----------------------------------------------------
        # Clear mouse state
        # ----------------------------------------------------

        self._mouse_press_pos = None
        self._drag_start_pos = None
        self._dragging_view = False