import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
QApplication,
QFrame,
QHBoxLayout,
QLabel,
QMainWindow,
QSplitter,
QStatusBar,
QVBoxLayout,
QWidget,
)

from model.ControlPanel import ControlPanel
from model.GraphView import GraphView

# ============================================================

# MAIN WINDOW

# ============================================================

class GraphVisualizer(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "Graph Routing Visualizer"
        )

        self.resize(
            1400,
            850
        )

        self.setMinimumSize(
            1000,
            650
        )

        self.setup_ui()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        self.create_menu_bar()

        self.create_central_widget()

        self.create_status_bar()

        self.connect_signals()

    # ========================================================
    # MENU BAR
    # ========================================================

    def create_menu_bar(self):

        menu_bar = self.menuBar()

        # ====================================================
        # FILE
        # ====================================================

        file_menu = menu_bar.addMenu(
            "File"
        )

        self.open_graph_action = (
            file_menu.addAction(
                "Open Graph"
            )
        )

        self.save_graph_action = (
            file_menu.addAction(
                "Save Graph"
            )
        )

        file_menu.addSeparator()

        self.exit_action = (
            file_menu.addAction(
                "Exit"
            )
        )

        self.exit_action.triggered.connect(
            self.close
        )

        # ====================================================
        # GRAPH
        # ====================================================

        graph_menu = menu_bar.addMenu(
            "Graph"
        )

        self.generate_graph_action = (
            graph_menu.addAction(
                "Generate Graph"
            )
        )

        self.graph_information_action = (
            graph_menu.addAction(
                "Graph Information"
            )
        )

        # ====================================================
        # ROUTING
        # ====================================================

        routing_menu = menu_bar.addMenu(
            "Routing"
        )

        self.run_routing_action = (
            routing_menu.addAction(
                "Run Routing"
            )
        )

        self.clear_route_action = (
            routing_menu.addAction(
                "Clear Route"
            )
        )

        # ====================================================
        # VIEW
        # ====================================================

        view_menu = menu_bar.addMenu(
            "View"
        )

        self.fit_graph_action = (
            view_menu.addAction(
                "Fit Graph"
            )
        )

        self.zoom_in_action = (
            view_menu.addAction(
                "Zoom In"
            )
        )

        self.zoom_out_action = (
            view_menu.addAction(
                "Zoom Out"
            )
        )

        self.reset_view_action = (
            view_menu.addAction(
                "Reset View"
            )
        )

        # ====================================================
        # HELP
        # ====================================================

        help_menu = menu_bar.addMenu(
            "Help"
        )

        self.about_action = (
            help_menu.addAction(
                "About"
            )
        )

    # ========================================================
    # CENTRAL WIDGET
    # ========================================================

    def create_central_widget(self):

        central = QWidget()

        self.setCentralWidget(
            central
        )

        layout = QHBoxLayout(
            central
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            0
        )

        # ====================================================
        # SPLITTER
        # ====================================================

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )

        layout.addWidget(
            splitter
        )

        # ====================================================
        # CONTROL PANEL
        # ====================================================

        self.control_panel = ControlPanel()

        splitter.addWidget(
            self.control_panel
        )

        # ====================================================
        # GRAPH AREA
        # ====================================================

        self.graph_area = (
            self.create_graph_area()
        )

        splitter.addWidget(
            self.graph_area
        )

        # ====================================================
        # INITIAL SIZE
        # ====================================================

        splitter.setSizes(
            [
                320,
                1080
            ]
        )

    # ========================================================
    # GRAPH AREA
    # ========================================================

    def create_graph_area(self):

        frame = QFrame()

        frame.setFrameShape(
            QFrame.Shape.StyledPanel
        )

        layout = QVBoxLayout(
            frame
        )

        layout.setContentsMargins(
            0,
            0,
            0,
            0
        )

        layout.setSpacing(
            0
        )

        # ====================================================
        # GRAPH VIEW
        # ====================================================

        self.graph_view = GraphView()

        layout.addWidget(
            self.graph_view
        )

        return frame

    # ========================================================
    # STATUS BAR
    # ========================================================

    def create_status_bar(self):

        status_bar = QStatusBar()

        self.setStatusBar(
            status_bar
        )

        self.status_label = QLabel(
            "Ready"
        )

        self.api_status_label = QLabel(
            "API: Disconnected"
        )

        status_bar.addWidget(
            self.status_label
        )

        status_bar.addPermanentWidget(
            self.api_status_label
        )

    # ========================================================
    # SIGNALS
    # ========================================================

    def connect_signals(self):

        # ====================================================
        # CONTROL PANEL
        # ====================================================

        self.control_panel.graph_loaded.connect(
            self.on_graph_loaded
        )

        self.control_panel.route_completed.connect(
            self.on_route_completed
        )

        self.control_panel.api_connection_changed.connect(
            self.on_api_connection_changed
        )

        # ====================================================
        # GRAPH VIEW
        # ====================================================

        self.graph_view.node_selected.connect(
            self.on_node_selected
        )

        self.graph_view.route_nodes_selected.connect(
            self.on_route_nodes_selected
        )

        # ====================================================
        # MENU -> CONTROL PANEL
        # ====================================================

        self.generate_graph_action.triggered.connect(
            self.control_panel.generate_graph
        )

        self.open_graph_action.triggered.connect(
            self.control_panel.load_graph
        )

        self.run_routing_action.triggered.connect(
            self.control_panel.run_routing
        )

        self.clear_route_action.triggered.connect(
            self.on_clear_route
        )

        self.save_graph_action.triggered.connect(
            self.on_save_graph
        )

        # ====================================================
        # VIEW ACTIONS
        # ====================================================

        self.fit_graph_action.triggered.connect(
            self.graph_view.fit_graph
        )

        self.reset_view_action.triggered.connect(
            self.graph_view.reset_view
        )

        self.zoom_in_action.triggered.connect(
            self.zoom_in
        )

        self.zoom_out_action.triggered.connect(
            self.zoom_out
        )

    # ========================================================
    # GRAPH LOADED
    # ========================================================

    def on_graph_loaded(
        self,
        result
    ):

        graph_id = result.get(
            "id"
        )

        graph_info = result.get(
            "graph",
            {}
        )

        graph_type = graph_info.get(
            "graph_type",
            "unknown"
        )

        nodes = graph_info.get(
            "nodes",
            0
        )

        edges = graph_info.get(
            "edges",
            0
        )

        # ----------------------------------------------------
        # UPDATE STATUS
        # ----------------------------------------------------

        self.status_label.setText(
            f"Loading graph | "
            f"Type: {graph_type} | "
            f"Nodes: {nodes} | "
            f"Edges: {edges}"
        )

        # ----------------------------------------------------
        # VALIDATE GRAPH ID
        # ----------------------------------------------------

        if not graph_id:

            self.status_label.setText(
                "Graph loading failed: missing graph ID"
            )

            return

        # ----------------------------------------------------
        # GET GRAPH STRUCTURE FROM API
        # ----------------------------------------------------

        try:

            client = self.control_panel.api

            graph_response = (
                client.get_graph_structure(
                    graph_id
                )
            )

            graph_data = graph_response.get(
                "graph",
                graph_response
            )

            # ------------------------------------------------
            # LOAD INTO GRAPH VIEW
            # ------------------------------------------------

            self.graph_view.load_graph(
                graph_data
            )

            self.status_label.setText(
                f"Graph loaded | "
                f"Type: {graph_type} | "
                f"Nodes: {nodes} | "
                f"Edges: {edges}"
            )

        except Exception as exc:

            print(
                "Failed to load graph structure:",
                exc
            )

            self.status_label.setText(
                f"Graph loaded but visualization failed: {exc}"
            )

    # ========================================================
    # ROUTE NODES SELECTED
    # ========================================================

    def on_route_nodes_selected(
        self,
        start_node,
        goal_node
    ):

        # ----------------------------------------------------
        # UPDATE CONTROL PANEL
        # ----------------------------------------------------

        if start_node is not None:

            self.control_panel.start_input.setValue(
                start_node
            )

        if goal_node is not None:

            self.control_panel.goal_input.setValue(
                goal_node
            )

        # ----------------------------------------------------
        # STATUS
        # ----------------------------------------------------

        if start_node is None:

            self.status_label.setText(
                "Select a start node."
            )

        elif goal_node is None:

            self.status_label.setText(
                f"Start node selected: {start_node} | "
                f"Select goal node."
            )

        else:

            self.status_label.setText(
                f"Route selected | "
                f"Start: {start_node} | "
                f"Goal: {goal_node}"
            )

    # ========================================================
    # NODE SELECTED
    # ========================================================

    def on_node_selected(
        self,
        node_id,
        data
    ):

        self.status_label.setText(
            f"Selected node: {node_id}"
        )

        print(
            "Selected node:",
            node_id
        )

        print(
            "Node data:",
            data
        )

    # ========================================================
    # ROUTING COMPLETED
    # ========================================================

    def on_route_completed(
        self,
        result
    ):

        route = result.get(
            "result",
            {}
        )

        found = route.get(
            "found",
            False
        )

        if found:

            algorithm = (
                result.get(
                    "query",
                    {}
                ).get(
                    "algorithm",
                    "unknown"
                )
            )

            path = route.get(
                "path",
                []
            )

            cost = route.get(
                "cost",
                None
            )

            self.status_label.setText(
                f"Routing completed | "
                f"Algorithm: {algorithm} | "
                f"Cost: {cost}"
            )

            self.graph_view.show_route(
                path
            )

        else:

            self.status_label.setText(
                "Routing completed | No route found"
            )

            self.graph_view.clear_route()

    # ========================================================
    # API CONNECTION
    # ========================================================

    def on_api_connection_changed(
        self,
        connected
    ):

        if connected:

            self.api_status_label.setText(
                "API: Connected"
            )

        else:

            self.api_status_label.setText(
                "API: Disconnected"
            )

    # ========================================================
    # CLEAR ROUTE
    # ========================================================

    def on_clear_route(self):

        self.graph_view.clear_route()

        self.graph_view.clear_route_selection()

        self.status_label.setText(
            "Route cleared"
        )

    # ========================================================
    # ZOOM IN
    # ========================================================

    def zoom_in(self):

        self.graph_view.scale(
            1.2,
            1.2
        )

    # ========================================================
    # ZOOM OUT
    # ========================================================

    def zoom_out(self):

        self.graph_view.scale(
            1 / 1.2,
            1 / 1.2
        )

    # ========================================================
    # SAVE GRAPH
    # ========================================================

    def on_save_graph(self):

        if not self.control_panel.current_graph_id:

            self.status_label.setText(
                "No graph to save"
            )

            return

        self.status_label.setText(
            "Save Graph requested"
        )

    # ========================================================
    # CLOSE
    # ========================================================

    def closeEvent(
        self,
        event
    ):

        event.accept()

# ============================================================

# APPLICATION

# ============================================================

def main():

    app = QApplication(
        sys.argv
    )

    window = GraphVisualizer()

    window.show()

    sys.exit(
        app.exec()
    )


# ============================================================

# ENTRY POINT

# ============================================================


main()

