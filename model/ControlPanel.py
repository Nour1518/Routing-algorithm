from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QCheckBox,
    QTabWidget,
    QWidget,
    QFileDialog,
    QMessageBox,
    QLineEdit,
    QTextEdit,
    QProgressBar,
)

from model.Api import GraphAPIClient


# ============================================================
# CONTROL PANEL
# ============================================================

class ControlPanel(QFrame):

    # ========================================================
    # SIGNALS
    # ========================================================

    graph_loaded = pyqtSignal(dict)
    route_completed = pyqtSignal(dict)
    api_connection_changed = pyqtSignal(bool)

    # ========================================================
    # INIT
    # ========================================================

    def __init__(self, parent=None):

        super().__init__(parent)

        self.api = GraphAPIClient()

        self.current_graph_id = None
        self.current_graph = None
        self.last_route_result = None

        self.setup_ui()

        self.check_api()

    # ========================================================
    # UI
    # ========================================================

    def setup_ui(self):

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            10,
            10,
            10,
            10
        )

        layout.setSpacing(8)

        # ====================================================
        # TITLE
        # ====================================================

        title = QLabel("GRAPH ROUTING CONTROL PANEL")

        title.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        layout.addWidget(title)

        # ====================================================
        # TABS
        # ====================================================

        self.tabs = QTabWidget()

        # ----------------------------------------------------
        # GRAPH TAB
        # ----------------------------------------------------

        self.graph_tab = self.create_graph_tab()

        self.tabs.addTab(
            self.graph_tab,
            "Graph"
        )

        # ----------------------------------------------------
        # ROUTING TAB
        # ----------------------------------------------------

        self.routing_tab = self.create_routing_tab()

        self.tabs.addTab(
            self.routing_tab,
            "Routing"
        )

        # ----------------------------------------------------
        # VISUALISATION TAB
        # ----------------------------------------------------

        self.visualisation_tab = (
            self.create_visualisation_tab()
        )

        self.tabs.addTab(
            self.visualisation_tab,
            "Visualisation"
        )

        # ----------------------------------------------------
        # SERVER TAB
        # ----------------------------------------------------

        self.server_tab = self.create_server_tab()

        self.tabs.addTab(
            self.server_tab,
            "Server"
        )

        layout.addWidget(
            self.tabs
        )

    # ========================================================
    # GRAPH TAB
    # ========================================================

    def create_graph_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        # ====================================================
        # GENERATION
        # ====================================================

        generation_group = QGroupBox(
            "Generate Graph"
        )

        generation_layout = QVBoxLayout(
            generation_group
        )

        # ----------------------------------------------------
        # TYPE
        # ----------------------------------------------------

        type_form = QFormLayout()

        self.graph_type_combo = QComboBox()

        self.graph_type_combo.addItems([
            "generic",
            "random",
            "geographical",
            "grid",
        ])

        self.graph_type_combo.currentTextChanged.connect(
            self.on_graph_type_changed
        )

        type_form.addRow(
            "Graph type:",
            self.graph_type_combo
        )

        generation_layout.addLayout(
            type_form
        )

        # ----------------------------------------------------
        # PARAMETERS
        # ----------------------------------------------------

        self.parameter_stack = QTabWidget()

        self.parameter_stack.setTabPosition(
            QTabWidget.TabPosition.North
        )

        # We use a stacked widget behavior but hide the tabs.
        self.parameter_stack.tabBar().hide()

        # Generic
        self.generic_page = (
            self.create_generic_page()
        )

        self.parameter_stack.addTab(
            self.generic_page,
            ""
        )

        # Random
        self.random_page = (
            self.create_random_page()
        )

        self.parameter_stack.addTab(
            self.random_page,
            ""
        )

        # Geographical
        self.geographical_page = (
            self.create_geographical_page()
        )

        self.parameter_stack.addTab(
            self.geographical_page,
            ""
        )

        # Grid
        self.grid_page = (
            self.create_grid_page()
        )

        self.parameter_stack.addTab(
            self.grid_page,
            ""
        )

        generation_layout.addWidget(
            self.parameter_stack
        )

        # ----------------------------------------------------
        # CH
        # ----------------------------------------------------

        self.build_ch_checkbox = QCheckBox(
            "Build Contraction Hierarchy after generation"
        )

        generation_layout.addWidget(
            self.build_ch_checkbox
        )

        # ----------------------------------------------------
        # GENERATE
        # ----------------------------------------------------

        self.generate_button = QPushButton(
            "Generate Graph"
        )

        self.generate_button.clicked.connect(
            self.generate_graph
        )

        generation_layout.addWidget(
            self.generate_button
        )

        layout.addWidget(
            generation_group
        )

        # ====================================================
        # GRAPH ACTIONS
        # ====================================================

        actions_group = QGroupBox(
            "Graph Actions"
        )

        actions_layout = QHBoxLayout(
            actions_group
        )

        self.load_button = QPushButton(
            "Load"
        )

        self.load_button.clicked.connect(
            self.load_graph
        )

        actions_layout.addWidget(
            self.load_button
        )

        self.save_button = QPushButton(
            "Save"
        )

        self.save_button.clicked.connect(
            self.save_graph
        )

        actions_layout.addWidget(
            self.save_button
        )

        self.refresh_graph_button = QPushButton(
            "Refresh"
        )

        self.refresh_graph_button.clicked.connect(
            self.refresh_graph
        )

        actions_layout.addWidget(
            self.refresh_graph_button
        )

        self.delete_button = QPushButton(
            "Delete"
        )

        self.delete_button.clicked.connect(
            self.delete_graph
        )

        actions_layout.addWidget(
            self.delete_button
        )

        layout.addWidget(
            actions_group
        )

        # ====================================================
        # GRAPH INFORMATION
        # ====================================================

        graph_group = QGroupBox(
            "Current Graph"
        )

        graph_layout = QFormLayout(
            graph_group
        )

        self.graph_id_label = QLabel("—")
        self.graph_type_label = QLabel("—")
        self.node_count_label = QLabel("—")
        self.edge_count_label = QLabel("—")
        self.directed_label = QLabel("—")
        self.average_degree_label = QLabel("—")
        self.max_degree_label = QLabel("—")
        self.ch_label = QLabel("—")

        graph_layout.addRow(
            "ID:",
            self.graph_id_label
        )

        graph_layout.addRow(
            "Type:",
            self.graph_type_label
        )

        graph_layout.addRow(
            "Nodes:",
            self.node_count_label
        )

        graph_layout.addRow(
            "Edges:",
            self.edge_count_label
        )

        graph_layout.addRow(
            "Directed:",
            self.directed_label
        )

        graph_layout.addRow(
            "Average degree:",
            self.average_degree_label
        )

        graph_layout.addRow(
            "Max degree:",
            self.max_degree_label
        )

        graph_layout.addRow(
            "CH:",
            self.ch_label
        )

        layout.addWidget(
            graph_group
        )

        layout.addStretch()

        return page

    # ========================================================
    # GENERIC PAGE
    # ========================================================

    def create_generic_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        form = QFormLayout()

        self.generic_nodes = QSpinBox()

        self.generic_nodes.setRange(
            1,
            1_000_000
        )

        self.generic_nodes.setValue(
            100
        )

        form.addRow(
            "Node count:",
            self.generic_nodes
        )

        self.generic_directed = QCheckBox(
            "Directed graph"
        )

        form.addRow(
            "",
            self.generic_directed
        )

        layout.addLayout(form)

        return page

    # ========================================================
    # RANDOM PAGE
    # ========================================================

    def create_random_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        form = QFormLayout()

        self.random_nodes = QSpinBox()

        self.random_nodes.setRange(
            1,
            1_000_000
        )

        self.random_nodes.setValue(
            100
        )

        form.addRow(
            "Node count:",
            self.random_nodes
        )

        self.random_probability = QDoubleSpinBox()

        self.random_probability.setRange(
            0.0,
            1.0
        )

        self.random_probability.setSingleStep(
            0.01
        )

        self.random_probability.setDecimals(
            3
        )

        self.random_probability.setValue(
            0.05
        )

        form.addRow(
            "Edge probability:",
            self.random_probability
        )

        self.random_min_weight = QDoubleSpinBox()

        self.random_min_weight.setRange(
            0.0,
            1_000_000_000.0
        )

        self.random_min_weight.setDecimals(
            3
        )

        self.random_min_weight.setValue(
            1.0
        )

        form.addRow(
            "Minimum weight:",
            self.random_min_weight
        )

        self.random_max_weight = QDoubleSpinBox()

        self.random_max_weight.setRange(
            0.0,
            1_000_000_000.0
        )

        self.random_max_weight.setDecimals(
            3
        )

        self.random_max_weight.setValue(
            100.0
        )

        form.addRow(
            "Maximum weight:",
            self.random_max_weight
        )

        self.random_directed = QCheckBox(
            "Directed graph"
        )

        form.addRow(
            "",
            self.random_directed
        )

        layout.addLayout(form)

        return page

    # ========================================================
    # GEOGRAPHICAL PAGE
    # ========================================================

    def create_geographical_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        form = QFormLayout()

        self.geo_nodes = QSpinBox()

        self.geo_nodes.setRange(
            1,
            1_000_000
        )

        self.geo_nodes.setValue(
            100
        )

        form.addRow(
            "Node count:",
            self.geo_nodes
        )

        self.geo_size = QDoubleSpinBox()

        self.geo_size.setRange(
            1.0,
            1_000_000_000.0
        )

        self.geo_size.setDecimals(
            2
        )

        self.geo_size.setValue(
            1000.0
        )

        form.addRow(
            "Area size:",
            self.geo_size
        )

        self.geo_min_dist = QDoubleSpinBox()

        self.geo_min_dist.setRange(
            0.0,
            1_000_000_000.0
        )

        self.geo_min_dist.setDecimals(
            2
        )

        self.geo_min_dist.setValue(
            10.0
        )

        form.addRow(
            "Minimum distance:",
            self.geo_min_dist
        )

        self.geo_radius = QDoubleSpinBox()

        self.geo_radius.setRange(
            0.0,
            1_000_000_000.0
        )

        self.geo_radius.setDecimals(
            2
        )

        self.geo_radius.setValue(
            150.0
        )

        form.addRow(
            "Connection radius:",
            self.geo_radius
        )

        self.geo_max_degree = QSpinBox()

        self.geo_max_degree.setRange(
            1,
            1_000_000
        )

        self.geo_max_degree.setValue(
            4
        )

        form.addRow(
            "Maximum degree:",
            self.geo_max_degree
        )

        self.geo_directed = QCheckBox(
            "Directed graph"
        )

        form.addRow(
            "",
            self.geo_directed
        )

        layout.addLayout(form)

        return page

    # ========================================================
    # GRID PAGE
    # ========================================================

    def create_grid_page(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        form = QFormLayout()

        # ----------------------------------------------------
        # ROWS
        # ----------------------------------------------------

        self.grid_rows = QSpinBox()

        self.grid_rows.setRange(
            1,
            10_000
        )

        self.grid_rows.setValue(
            10
        )

        self.grid_rows.valueChanged.connect(
            self.update_grid_node_preview
        )

        form.addRow(
            "Rows:",
            self.grid_rows
        )

        # ----------------------------------------------------
        # COLUMNS
        # ----------------------------------------------------

        self.grid_cols = QSpinBox()

        self.grid_cols.setRange(
            1,
            10_000
        )

        self.grid_cols.setValue(
            10
        )

        self.grid_cols.valueChanged.connect(
            self.update_grid_node_preview
        )

        form.addRow(
            "Columns:",
            self.grid_cols
        )

        # ----------------------------------------------------
        # CALCULATED NODE COUNT
        # ----------------------------------------------------

        self.grid_nodes_label = QLabel(
            "100"
        )

        form.addRow(
            "Total nodes:",
            self.grid_nodes_label
        )

        # ----------------------------------------------------
        # WEIGHT
        # ----------------------------------------------------

        self.grid_weight = QDoubleSpinBox()

        self.grid_weight.setRange(
            0.0,
            1_000_000_000.0
        )

        self.grid_weight.setDecimals(
            3
        )

        self.grid_weight.setValue(
            1.0
        )

        form.addRow(
            "Edge weight:",
            self.grid_weight
        )

        # ----------------------------------------------------
        # DIAGONAL
        # ----------------------------------------------------

        self.grid_diagonal = QCheckBox(
            "Allow diagonal edges"
        )

        form.addRow(
            "",
            self.grid_diagonal
        )

        # ----------------------------------------------------
        # DIRECTED
        # ----------------------------------------------------

        self.grid_directed = QCheckBox(
            "Directed graph"
        )

        form.addRow(
            "",
            self.grid_directed
        )

        layout.addLayout(form)

        return page

    # ========================================================
    # ROUTING TAB
    # ========================================================

    def create_routing_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        # ====================================================
        # QUERY
        # ====================================================

        routing_group = QGroupBox(
            "Routing Query"
        )

        routing_layout = QFormLayout(
            routing_group
        )

        # ----------------------------------------------------
        # START
        # ----------------------------------------------------

        self.start_input = QSpinBox()

        self.start_input.setRange(
            0,
            2_147_483_647
        )

        self.start_input.setValue(
            0
        )

        routing_layout.addRow(
            "Start node:",
            self.start_input
        )

        # ----------------------------------------------------
        # GOAL
        # ----------------------------------------------------

        self.goal_input = QSpinBox()

        self.goal_input.setRange(
            0,
            2_147_483_647
        )

        self.goal_input.setValue(
            0
        )

        routing_layout.addRow(
            "Goal node:",
            self.goal_input
        )

        # ----------------------------------------------------
        # ALGORITHM
        # ----------------------------------------------------

        self.algorithm_combo = QComboBox()

        self.algorithm_combo.addItems([
            "dijkstra",
            "a_star",
            "bidijkstra",
            "bi_a_star",
            "bfs",
            "ch",
        ])

        self.algorithm_combo.currentTextChanged.connect(
            self.on_algorithm_changed
        )

        routing_layout.addRow(
            "Algorithm:",
            self.algorithm_combo
        )

        layout.addWidget(
            routing_group
        )
        # ----------------------------------------------------
        # HEURISTIC
        # ----------------------------------------------------

        self.heuristic_combo = QComboBox()

        self.heuristic_combo.addItems([

            "zero",

            "euclidean",

            "manhattan",

            "chebyshev",

            "octile",

            "haversine",

            "geographical",
        ])

        routing_layout.addRow(
            "Heuristic:",
            self.heuristic_combo
        )

        # Update visibility depending on algorithm
        self.update_heuristic_state(
            self.algorithm_combo.currentText()
        )
        # ====================================================
        # ROUTING OPTIONS
        # ====================================================

        options_group = QGroupBox(
            "Options"
        )

        options_layout = QVBoxLayout(
            options_group
        )

        self.trace_checkbox = QCheckBox(
            "Collect routing trace"
        )

        self.trace_checkbox.setToolTip(
            "Request the API to return the algorithm exploration trace "
            "when visual tracing is supported."
        )

        options_layout.addWidget(
            self.trace_checkbox
        )

        layout.addWidget(
            options_group
        )

        # ====================================================
        # RUN
        # ====================================================

        self.route_button = QPushButton(
            "Run Routing"
        )

        self.route_button.setMinimumHeight(
            35
        )

        self.route_button.clicked.connect(
            self.run_routing
        )

        layout.addWidget(
            self.route_button
        )

        # ====================================================
        # CH
        # ====================================================

        self.ch_button = QPushButton(
            "Build Contraction Hierarchy"
        )

        self.ch_button.clicked.connect(
            self.build_ch
        )

        layout.addWidget(
            self.ch_button
        )

        # ====================================================
        # RESULT
        # ====================================================

        result_group = QGroupBox(
            "Routing Result"
        )

        result_layout = QFormLayout(
            result_group
        )

        self.routing_status = QLabel(
            "No routing query"
        )

        self.time_label = QLabel(
            "—"
        )

        self.cost_label = QLabel(
            "—"
        )

        self.path_nodes_label = QLabel(
            "—"
        )

        self.path_edges_label = QLabel(
            "—"
        )

        self.path_length_label = QLabel(
            "—"
        )

        result_layout.addRow(
            "Status:",
            self.routing_status
        )

        result_layout.addRow(
            "Time:",
            self.time_label
        )

        result_layout.addRow(
            "Cost:",
            self.cost_label
        )

        result_layout.addRow(
            "Path nodes:",
            self.path_nodes_label
        )

        result_layout.addRow(
            "Path edges:",
            self.path_edges_label
        )

        result_layout.addRow(
            "Path length:",
            self.path_length_label
        )

        layout.addWidget(
            result_group
        )

        layout.addStretch()

        return page

    # ========================================================
    # VISUALISATION TAB
    # ========================================================

    def create_visualisation_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        # ====================================================
        # TRACE INFORMATION
        # ====================================================

        trace_group = QGroupBox(
            "Routing Trace"
        )

        trace_layout = QVBoxLayout(
            trace_group
        )

        self.trace_status_label = QLabel(
            "No trace available."
        )

        trace_layout.addWidget(
            self.trace_status_label
        )

        self.trace_progress = QProgressBar()

        self.trace_progress.setRange(
            0,
            0
        )

        self.trace_progress.setVisible(
            False
        )

        trace_layout.addWidget(
            self.trace_progress
        )

        self.trace_view = QTextEdit()

        self.trace_view.setReadOnly(
            True
        )

        self.trace_view.setPlaceholderText(
            "Routing trace will appear here..."
        )

        trace_layout.addWidget(
            self.trace_view
        )

        layout.addWidget(
            trace_group
        )

        # ====================================================
        # PATH
        # ====================================================

        path_group = QGroupBox(
            "Current Path"
        )

        path_layout = QVBoxLayout(
            path_group
        )

        self.path_view = QTextEdit()

        self.path_view.setReadOnly(
            True
        )

        self.path_view.setPlaceholderText(
            "Calculated path will appear here..."
        )

        path_layout.addWidget(
            self.path_view
        )

        layout.addWidget(
            path_group
        )

        layout.addStretch()

        return page

    # ========================================================
    # SERVER TAB
    # ========================================================

    def create_server_tab(self):

        page = QWidget()

        layout = QVBoxLayout(page)

        layout.setContentsMargins(
            8,
            8,
            8,
            8
        )

        # ====================================================
        # CONNECTION
        # ====================================================

        connection_group = QGroupBox(
            "API Server"
        )

        connection_layout = QFormLayout(
            connection_group
        )

        self.server_url_input = QLineEdit(
            self.api.base_url
        )

        self.server_url_input.setPlaceholderText(
            "http://127.0.0.1:5000"
        )

        connection_layout.addRow(
            "Server URL:",
            self.server_url_input
        )

        self.server_status_label = QLabel(
            "Unknown"
        )

        connection_layout.addRow(
            "Status:",
            self.server_status_label
        )

        layout.addWidget(
            connection_group
        )

        # ====================================================
        # SERVER BUTTONS
        # ====================================================

        server_buttons = QHBoxLayout()

        self.connect_button = QPushButton(
            "Connect"
        )

        self.connect_button.clicked.connect(
            self.connect_to_server
        )

        server_buttons.addWidget(
            self.connect_button
        )

        self.refresh_server_button = QPushButton(
            "Refresh"
        )

        self.refresh_server_button.clicked.connect(
            self.check_api
        )

        server_buttons.addWidget(
            self.refresh_server_button
        )

        layout.addLayout(
            server_buttons
        )

        # ====================================================
        # SERVER INFORMATION
        # ====================================================

        server_info_group = QGroupBox(
            "Server Information"
        )

        server_info_layout = QVBoxLayout(
            server_info_group
        )

        self.server_info_view = QTextEdit()

        self.server_info_view.setReadOnly(
            True
        )

        server_info_layout.addWidget(
            self.server_info_view
        )

        layout.addWidget(
            server_info_group
        )

        layout.addStretch()

        return page

    # ========================================================
    # GRAPH TYPE CHANGED
    # ========================================================

    def on_graph_type_changed(self, graph_type):

        index = {
            "generic": 0,
            "random": 1,
            "geographical": 2,
            "grid": 3,
        }.get(
            graph_type,
            0
        )

        self.parameter_stack.setCurrentIndex(
            index
        )

        # Grid does not have a user-entered node count.
        if graph_type == "grid":
            self.update_grid_node_preview()

    # ========================================================
    # GRID NODE PREVIEW
    # ========================================================

    def update_grid_node_preview(self):

        rows = self.grid_rows.value()
        cols = self.grid_cols.value()

        nodes = rows * cols

        self.grid_nodes_label.setText(
            f"{nodes:,}"
        )

    # ========================================================
    # GENERATION DATA
    # ========================================================

    def get_generation_data(self):

        graph_type = (
            self.graph_type_combo.currentText()
        )

        data = {
            "type": graph_type,
            "build_ch": (
                self.build_ch_checkbox.isChecked()
            )
        }

        # ====================================================
        # GENERIC
        # ====================================================

        if graph_type == "generic":

            data.update({
                "nodes": self.generic_nodes.value(),

                "directed": (
                    self.generic_directed.isChecked()
                )
            })

        # ====================================================
        # RANDOM
        # ====================================================

        elif graph_type == "random":

            min_weight = (
                self.random_min_weight.value()
            )

            max_weight = (
                self.random_max_weight.value()
            )

            if min_weight > max_weight:

                raise ValueError(
                    "Minimum weight cannot be greater "
                    "than maximum weight."
                )

            data.update({
                "nodes": self.random_nodes.value(),

                "probability": (
                    self.random_probability.value()
                ),

                "min_weight": min_weight,

                "max_weight": max_weight,

                "directed": (
                    self.random_directed.isChecked()
                )
            })

        # ====================================================
        # GEOGRAPHICAL
        # ====================================================

        elif graph_type == "geographical":

            data.update({
                "nodes": self.geo_nodes.value(),

                "size": self.geo_size.value(),

                "min_dist": (
                    self.geo_min_dist.value()
                ),

                "radius": (
                    self.geo_radius.value()
                ),

                "max_degree": (
                    self.geo_max_degree.value()
                ),

                "directed": (
                    self.geo_directed.isChecked()
                )
            })

        # ====================================================
        # GRID
        # ====================================================

        elif graph_type == "grid":

            rows = self.grid_rows.value()
            cols = self.grid_cols.value()

            data.update({
                "rows": rows,

                "cols": cols,

                "weight": (
                    self.grid_weight.value()
                ),

                "diagonal": (
                    self.grid_diagonal.isChecked()
                ),

                "directed": (
                    self.grid_directed.isChecked()
                )
            })

        return data

    # ========================================================
# GENERATE GRAPH
# ========================================================

    def generate_graph(self):

        try:

            data = self.get_generation_data()

            # -----------------------------------------------
            # Extract common parameters
            # -----------------------------------------------

            graph_type = data.pop("type")

            directed = data.pop(
                "directed",
                False
            )

            build_ch = data.pop(
                "build_ch",
                False
            )

            self.generate_button.setEnabled(
                False
            )

            # -----------------------------------------------
            # Call the new API client correctly
            # -----------------------------------------------

            result = self.api.generate_graph(
                graph_type=graph_type,
                directed=directed,
                build_ch=build_ch,
                **data
            )

            self.set_graph(
                result
            )

        except Exception as exc:

            self.show_error(
                "Generate Graph",
                str(exc)
            )

        finally:

            self.generate_button.setEnabled(
                True
            )
    # ========================================================
    # LOAD GRAPH
    # ========================================================

    def load_graph(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Open Graph"
        )

        if not filename:
            return

        try:

            self.load_button.setEnabled(
                False
            )

            result = self.api.load_graph(
                filename
            )

            self.set_graph(
                result
            )

        except Exception as exc:

            self.show_error(
                "Load Graph",
                str(exc)
            )

        finally:

            self.load_button.setEnabled(
                True
            )

    # ========================================================
    # SET GRAPH
    # ========================================================

    def set_graph(self, result):

        self.current_graph_id = result.get(
            "id"
        )

        self.current_graph = result.get(
            "graph",
            {}
        )

        graph = self.current_graph

        # ----------------------------------------------------
        # INFORMATION
        # ----------------------------------------------------

        self.graph_id_label.setText(
            str(
                self.current_graph_id
                or "—"
            )
        )

        self.graph_type_label.setText(
            str(
                graph.get(
                    "graph_type",
                    "—"
                )
            )
        )

        self.node_count_label.setText(
            f"{graph.get('nodes', '—'):,}"
            if isinstance(
                graph.get("nodes"),
                int
            )
            else str(
                graph.get(
                    "nodes",
                    "—"
                )
            )
        )

        self.edge_count_label.setText(
            f"{graph.get('edges', '—'):,}"
            if isinstance(
                graph.get("edges"),
                int
            )
            else str(
                graph.get(
                    "edges",
                    "—"
                )
            )
        )

        self.directed_label.setText(
            str(
                graph.get(
                    "directed",
                    "—"
                )
            )
        )

        average_degree = graph.get(
            "average_degree"
        )

        if average_degree is not None:

            self.average_degree_label.setText(
                f"{average_degree:.3f}"
            )

        else:

            self.average_degree_label.setText(
                "—"
            )

        self.max_degree_label.setText(
            str(
                graph.get(
                    "max_degree",
                    "—"
                )
            )
        )

        self.ch_label.setText(
            "Ready"
            if graph.get(
                "ch_ready",
                False
            )
            else "Not built"
        )

        # ----------------------------------------------------
        # ROUTING INPUTS
        # ----------------------------------------------------

        node_count = graph.get(
            "nodes",
            0
        )

        if isinstance(
            node_count,
            int
        ) and node_count > 0:

            self.start_input.setRange(
                0,
                node_count - 1
            )

            self.goal_input.setRange(
                0,
                node_count - 1
            )

            self.start_input.setValue(
                0
            )

            self.goal_input.setValue(
                node_count - 1
            )

        # ----------------------------------------------------
        # RESET ROUTING RESULT
        # ----------------------------------------------------

        self.clear_route_result()

        self.graph_loaded.emit(
            result
        )

    # ========================================================
    # REFRESH GRAPH
    # ========================================================

    def refresh_graph(self):

        if not self.current_graph_id:
            return

        try:

            result = self.api.get_graph(
                self.current_graph_id
            )

            self.set_graph(
                result
            )

        except Exception as exc:

            self.show_error(
                "Refresh Graph",
                str(exc)
            )

    # ========================================================
    # DELETE GRAPH
    # ========================================================

    def delete_graph(self):

        if not self.current_graph_id:

            self.show_error(
                "Delete Graph",
                "No graph is loaded."
            )

            return

        answer = QMessageBox.question(
            self,
            "Delete Graph",
            "Delete the current graph?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        try:

            self.delete_button.setEnabled(
                False
            )

            self.api.delete_graph(
                self.current_graph_id
            )

            self.current_graph_id = None
            self.current_graph = None

            self.clear_graph_information()
            self.clear_route_result()

            self.graph_loaded.emit({
                "id": None,
                "graph": {}
            })

        except Exception as exc:

            self.show_error(
                "Delete Graph",
                str(exc)
            )

        finally:

            self.delete_button.setEnabled(
                True
            )

    # ========================================================
    # CLEAR GRAPH INFORMATION
    # ========================================================

    def clear_graph_information(self):

        self.graph_id_label.setText("—")
        self.graph_type_label.setText("—")
        self.node_count_label.setText("—")
        self.edge_count_label.setText("—")
        self.directed_label.setText("—")
        self.average_degree_label.setText("—")
        self.max_degree_label.setText("—")
        self.ch_label.setText("—")

        self.start_input.setRange(
            0,
            2_147_483_647
        )

        self.goal_input.setRange(
            0,
            2_147_483_647
        )

        self.start_input.setValue(0)
        self.goal_input.setValue(0)

    # ========================================================
    # ROUTING
    # ========================================================


    def run_routing(self):

        if not self.current_graph_id:

            self.show_error(
                "Routing",
                "No graph is loaded."
            )

            return

        # ========================================================
        # ROUTING PARAMETERS
        # ========================================================

        start = self.start_input.value()

        goal = self.goal_input.value()

        algorithm = (
            self.algorithm_combo.currentText()
        )

        trace = (
            self.trace_checkbox.isChecked()
        )

        # ========================================================
        # OPTIONAL HEURISTIC
        # ========================================================

        heuristic = None

        if algorithm in {
            "a_star",
            "bi_a_star",
        }:

            heuristic = (
                self.heuristic_combo.currentText()
            )

        # ========================================================
        # BUILD API REQUEST
        # ========================================================

        route_data = {

            "graph_id": self.current_graph_id,

            "start": start,

            "goal": goal,

            "algorithm": algorithm,

            "trace": trace,
        }

        # Only send heuristic for algorithms that use it.

        if heuristic is not None:

            route_data["heuristic"] = heuristic

        try:

            self.route_button.setEnabled(
                False
            )

            self.trace_progress.setVisible(
                trace
            )

            self.routing_status.setText(
                "Running..."
            )

            # ====================================================
            # API CALL
            # ====================================================

            result = self.api.route(
                **route_data
            )

            self.last_route_result = result

            self.display_route_result(
                result
            )

            self.display_visualisation_data(
                result
            )

            self.route_completed.emit(
                result
            )

            # ====================================================
            # SWITCH TO VISUALISATION
            # ====================================================

            if trace:

                self.tabs.setCurrentWidget(
                    self.visualisation_tab
                )

        except Exception as exc:

            self.show_error(
                "Routing",
                str(exc)
            )

        finally:

            self.trace_progress.setVisible(
                False
            )

            self.route_button.setEnabled(
                True
            )

    # ========================================================
    # DISPLAY ROUTE RESULT
    # ========================================================

    def display_route_result(self, result):

        route = result.get(
            "result",
            {}
        )

        found = route.get(
            "found",
            False
        )

        if not found:

            self.routing_status.setText(
                "No route found"
            )

            self.time_label.setText(
                "—"
            )

            self.cost_label.setText(
                "—"
            )

            self.path_nodes_label.setText(
                "0"
            )

            self.path_edges_label.setText(
                "0"
            )

            self.path_length_label.setText(
                "—"
            )

            return

        self.routing_status.setText(
            "Route found"
        )

        time_seconds = route.get(
            "time_seconds"
        )

        cost = route.get(
            "cost"
        )

        path_nodes = route.get(
            "path_nodes",
            0
        )

        path_edges = route.get(
            "path_edges",
            0
        )

        path_length = route.get(
            "path_length"
        )

        if time_seconds is not None:

            self.time_label.setText(
                f"{time_seconds:.6f} s"
            )

        else:

            self.time_label.setText(
                "—"
            )

        if cost is not None:

            self.cost_label.setText(
                f"{cost}"
            )

        else:

            self.cost_label.setText(
                "—"
            )

        self.path_nodes_label.setText(
            str(path_nodes)
        )

        self.path_edges_label.setText(
            str(path_edges)
        )

        if path_length is not None:

            self.path_length_label.setText(
                str(path_length)
            )

        else:

            self.path_length_label.setText(
                "—"
            )

    # ========================================================
    # VISUALISATION DATA
    # ========================================================

    def display_visualisation_data(self, result):

        route = result.get(
            "result",
            {}
        )

        path = route.get(
            "path"
        )

        trace = result.get(
            "trace"
        )

        # ----------------------------------------------------
        # PATH
        # ----------------------------------------------------

        if path:

            path_text = " → ".join(
                str(node)
                for node in path
            )

            self.path_view.setPlainText(
                path_text
            )

        else:

            self.path_view.clear()

        # ----------------------------------------------------
        # TRACE
        # ----------------------------------------------------

        if trace is None:

            self.trace_status_label.setText(
                "No trace returned by the API."
            )

            self.trace_view.clear()

            return

        self.trace_status_label.setText(
            f"Trace available: "
            f"{len(trace) if hasattr(trace, '__len__') else 'unknown'} entries"
        )

        try:

            import json

            self.trace_view.setPlainText(
                json.dumps(
                    trace,
                    indent=2,
                    ensure_ascii=False
                )
            )

        except Exception:

            self.trace_view.setPlainText(
                str(trace)
            )

    # ========================================================
    # CLEAR ROUTE RESULT
    # ========================================================

    def clear_route_result(self):

        self.routing_status.setText(
            "No routing query"
        )

        self.time_label.setText(
            "—"
        )

        self.cost_label.setText(
            "—"
        )

        self.path_nodes_label.setText(
            "—"
        )

        self.path_edges_label.setText(
            "—"
        )

        self.path_length_label.setText(
            "—"
        )

        self.trace_status_label.setText(
            "No trace available."
        )

        self.trace_view.clear()
        self.path_view.clear()

        self.last_route_result = None

    # ========================================================
    # ALGORITHM CHANGED
    # ========================================================
    def on_algorithm_changed(self, algorithm):

        self.update_heuristic_state(
            algorithm
        )

        # CH requires a prepared contraction hierarchy.
        if algorithm == "ch":

            ch_ready = False

            if self.current_graph:

                ch_ready = self.current_graph.get(
                    "ch_ready",
                    False
                )

            if not ch_ready:

                self.routing_status.setText(
                    "CH selected — build CH first."
                )  
    # ========================================================
    # BUILD CH
    # ========================================================

    def build_ch(self):

        if not self.current_graph_id:

            self.show_error(
                "Contraction Hierarchy",
                "No graph is loaded."
            )

            return

        try:

            self.ch_button.setEnabled(
                False
            )

            self.routing_status.setText(
                "Building contraction hierarchy..."
            )

            result = self.api.build_ch(
                self.current_graph_id
            )

            ch = result.get(
                "ch",
                {}
            )

            ch_ready = ch.get(
                "ch_ready",
                False
            )

            self.ch_label.setText(
                "Ready"
                if ch_ready
                else "Not ready"
            )

            # Refresh graph information.

            graph_result = self.api.get_graph(
                self.current_graph_id
            )

            self.set_graph(
                graph_result
            )

            self.routing_status.setText(
                "Contraction hierarchy built."
                if ch_ready
                else "Contraction hierarchy was not marked ready."
            )

        except Exception as exc:

            self.show_error(
                "Contraction Hierarchy",
                str(exc)
            )

        finally:

            self.ch_button.setEnabled(
                True
            )

    # ========================================================
    # SAVE GRAPH
    # ========================================================

    def save_graph(self):

        if not self.current_graph_id:

            self.show_error(
                "Save Graph",
                "No graph is loaded."
            )

            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Graph"
        )

        if not filename:
            return

        try:

            self.save_button.setEnabled(
                False
            )

            self.api.save_graph(
                self.current_graph_id,
                filename
            )

            QMessageBox.information(
                self,
                "Save Graph",
                "Graph saved successfully."
            )

        except Exception as exc:

            self.show_error(
                "Save Graph",
                str(exc)
            )

        finally:

            self.save_button.setEnabled(
                True
            )

    # ========================================================
    # SERVER CONNECTION
    # ========================================================

    def connect_to_server(self):

        url = self.server_url_input.text().strip()

        if not url:

            self.show_error(
                "Server",
                "Server URL cannot be empty."
            )

            return

        self.api.base_url = url.rstrip("/")

        self.check_api()

    # ========================================================
    # CHECK API
    # ========================================================

    def check_api(self):

        try:

            self.server_status_label.setText(
                "Connecting..."
            )

            result = self.api.health()

            self.server_status_label.setText(
                "CONNECTED"
            )

            self.server_info_view.setPlainText(
                self.format_server_info(
                    result
                )
            )

            self.api_connection_changed.emit(
                True
            )

        except Exception as exc:

            self.server_status_label.setText(
                "DISCONNECTED"
            )

            self.server_info_view.setPlainText(
                f"Connection failed:\n\n{exc}"
            )

            self.api_connection_changed.emit(
                False
            )

    # ========================================================
    # SERVER INFO
    # ========================================================

    def format_server_info(self, data):

        lines = []

        if isinstance(
            data,
            dict
        ):

            service = data.get(
                "service"
            )

            status = data.get(
                "status"
            )

            graphs_loaded = data.get(
                "graphs_loaded"
            )

            algorithms = data.get(
                "algorithms"
            )

            if service is not None:

                lines.append(
                    f"Service: {service}"
                )

            if status is not None:

                lines.append(
                    f"Status: {status}"
                )

            if graphs_loaded is not None:

                lines.append(
                    f"Graphs loaded: {graphs_loaded}"
                )

            if algorithms is not None:

                lines.append(
                    "Algorithms:"
                )

                for algorithm in algorithms:

                    lines.append(
                        f"  • {algorithm}"
                    )

        if not lines:

            return str(data)

        return "\n".join(lines)
    def update_heuristic_state(self, algorithm):

        heuristic_algorithms = {
            "a_star",
            "bi_a_star",
        }

        self.heuristic_combo.setEnabled(
            algorithm in heuristic_algorithms
        )
    # ========================================================
    # ERROR
    # ========================================================

    def show_error(
        self,
        title,
        message
    ):

        QMessageBox.critical(
            self,
            title,
            message
        )
