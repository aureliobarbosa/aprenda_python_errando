from __future__ import annotations

import csv
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import pyqtgraph as pg
from PySide6 import QtCore, QtGui, QtWidgets


@dataclass
class ChartConfig:
    chart_type: str = "Linha"
    title: str = "Visualizacao de dados"
    show_legend: bool = True
    show_values: bool = False
    show_grid: bool = True
    line_color: str = "#2f80ed"
    bar_color: str = "#27ae60"
    point_type: str = "Circulo"
    line_width: int = 2
    point_size: int = 9
    bar_width: float = 0.7
    pie_colors: list[str] = field(
        default_factory=lambda: ["#2f80ed", "#27ae60", "#f2994a", "#eb5757", "#9b51e0"]
    )


class PieItem(pg.GraphicsObject):
    def __init__(self, labels: list[str], values: list[float], config: ChartConfig):
        super().__init__()
        self.labels = labels
        self.values = values
        self.config = config
        self._rect = QtCore.QRectF(-1.0, -1.0, 2.0, 2.0)
        self.picture = QtGui.QPicture()
        self._render()

    def _render(self) -> None:
        painter = QtGui.QPainter(self.picture)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        total = sum(value for value in self.values)
        if total <= 0:
            painter.end()
            return
        start_angle = 90.0
        for index, value in enumerate(self.values):
            span = -360.0 * value / total
            color = QtGui.QColor(self.config.pie_colors[index % len(self.config.pie_colors)])
            painter.setBrush(color)
            painter.setPen(QtGui.QPen(QtGui.QColor("white"), 0.01))
            painter.drawPie(self._rect, int(start_angle * 16), int(span * 16))
            if self.config.show_values:
                angle = math.radians(start_angle + span / 2.0)
                label_x = 0.62 * math.cos(angle)
                label_y = -0.62 * math.sin(angle)
                painter.setPen(QtGui.QPen(QtGui.QColor("#222222")))
                painter.drawText(QtCore.QPointF(label_x - 0.08, label_y), f"{value:g}")
            start_angle += span
        painter.end()

    def paint(self, painter: QtGui.QPainter, *args) -> None:
        painter.drawPicture(0, 0, self.picture)

    def boundingRect(self) -> QtCore.QRectF:
        return self._rect


class SettingsDialog(QtWidgets.QDialog):
    settings_applied = QtCore.Signal()

    def __init__(self, config: ChartConfig, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Configuracoes do grafico")
        self.setMinimumWidth(430)
        self._build_ui()
        self._sync_type_fields()

    def _build_ui(self) -> None:
        layout = QtWidgets.QVBoxLayout(self)
        form = QtWidgets.QFormLayout()

        self.title_edit = QtWidgets.QLineEdit(self.config.title)
        self.type_combo = QtWidgets.QComboBox()
        self.type_combo.addItems(["Linha", "Barras", "Pizza"])
        self.type_combo.setCurrentText(self.config.chart_type)
        self.type_combo.currentTextChanged.connect(self._sync_type_fields)
        self.legend_check = QtWidgets.QCheckBox("Exibir legenda")
        self.legend_check.setChecked(self.config.show_legend)
        self.values_check = QtWidgets.QCheckBox("Exibir rotulos dos valores")
        self.values_check.setChecked(self.config.show_values)
        self.grid_check = QtWidgets.QCheckBox("Exibir grade")
        self.grid_check.setChecked(self.config.show_grid)

        form.addRow("Tipo:", self.type_combo)
        form.addRow("Titulo:", self.title_edit)
        form.addRow("Opcoes gerais:", self.legend_check)
        form.addRow("", self.values_check)
        form.addRow("", self.grid_check)
        layout.addLayout(form)

        self.line_group = QtWidgets.QGroupBox("Opcoes especificas de linha")
        line_form = QtWidgets.QFormLayout(self.line_group)
        self.point_combo = QtWidgets.QComboBox()
        self.point_combo.addItems(["Circulo", "Quadrado", "Triangulo", "X", "Nenhum"])
        self.point_combo.setCurrentText(self.config.point_type)
        self.line_color_button = self._color_button(self.config.line_color, self._choose_line_color)
        self.line_width_spin = QtWidgets.QSpinBox()
        self.line_width_spin.setRange(1, 10)
        self.line_width_spin.setValue(self.config.line_width)
        self.point_size_spin = QtWidgets.QSpinBox()
        self.point_size_spin.setRange(2, 30)
        self.point_size_spin.setValue(self.config.point_size)
        line_form.addRow("Tipo de ponto:", self.point_combo)
        line_form.addRow("Cor da linha:", self.line_color_button)
        line_form.addRow("Espessura:", self.line_width_spin)
        line_form.addRow("Tamanho do ponto:", self.point_size_spin)
        layout.addWidget(self.line_group)

        self.bar_group = QtWidgets.QGroupBox("Opcoes especificas de barras")
        bar_form = QtWidgets.QFormLayout(self.bar_group)
        self.bar_color_button = self._color_button(self.config.bar_color, self._choose_bar_color)
        self.bar_width_spin = QtWidgets.QDoubleSpinBox()
        self.bar_width_spin.setRange(0.1, 1.0)
        self.bar_width_spin.setSingleStep(0.1)
        self.bar_width_spin.setValue(self.config.bar_width)
        bar_form.addRow("Cor das barras:", self.bar_color_button)
        bar_form.addRow("Largura:", self.bar_width_spin)
        layout.addWidget(self.bar_group)

        self.pie_group = QtWidgets.QGroupBox("Opcoes especificas de pizza")
        pie_form = QtWidgets.QFormLayout(self.pie_group)
        pie_form.addRow("Cores:", QtWidgets.QLabel("Paleta automatica"))
        layout.addWidget(self.pie_group)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._apply)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _color_button(self, color: str, callback) -> QtWidgets.QPushButton:
        button = QtWidgets.QPushButton(color)
        button.setStyleSheet(f"background-color: {color}; color: white; font-weight: bold;")
        button.clicked.connect(callback)
        return button

    def _choose_line_color(self) -> None:
        self.config.line_color = self._choose_color(self.config.line_color, self.line_color_button)

    def _choose_bar_color(self) -> None:
        self.config.bar_color = self._choose_color(self.config.bar_color, self.bar_color_button)

    def _choose_color(self, current: str, button: QtWidgets.QPushButton) -> str:
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(current), self)
        if color.isValid():
            value = color.name()
            button.setText(value)
            button.setStyleSheet(f"background-color: {value}; color: white; font-weight: bold;")
            return value
        return current

    def _sync_type_fields(self) -> None:
        chart_type = self.type_combo.currentText()
        self.line_group.setVisible(chart_type == "Linha")
        self.bar_group.setVisible(chart_type == "Barras")
        self.pie_group.setVisible(chart_type == "Pizza")

    def _apply(self) -> None:
        self.config.chart_type = self.type_combo.currentText()
        self.config.title = self.title_edit.text().strip() or "Visualizacao de dados"
        self.config.show_legend = self.legend_check.isChecked()
        self.config.show_values = self.values_check.isChecked()
        self.config.show_grid = self.grid_check.isChecked()
        self.config.point_type = self.point_combo.currentText()
        self.config.line_width = self.line_width_spin.value()
        self.config.point_size = self.point_size_spin.value()
        self.config.bar_width = self.bar_width_spin.value()
        self.settings_applied.emit()
        self.accept()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gerador de graficos")
        self.resize(980, 680)
        self.config = ChartConfig()
        self.labels: list[str] = []
        self.values: list[float] = []
        self.file_path: Path | None = None
        self._build_ui()
        self._build_menu()
        self._show_empty_state()

    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central)
        toolbar = QtWidgets.QHBoxLayout()
        self.open_button = QtWidgets.QPushButton("Ler arquivo")
        self.settings_button = QtWidgets.QPushButton("Configuracoes")
        self.open_button.clicked.connect(self.open_file)
        self.settings_button.clicked.connect(self.open_settings)
        toolbar.addWidget(self.open_button)
        toolbar.addWidget(self.settings_button)
        toolbar.addStretch()
        self.status_label = QtWidgets.QLabel("Nenhum arquivo carregado")
        toolbar.addWidget(self.status_label)
        layout.addLayout(toolbar)

        self.plot = pg.PlotWidget()
        self.plot.setBackground("#fafafa")
        self.plot.showGrid(x=True, y=True, alpha=0.18)
        layout.addWidget(self.plot, 1)
        self.setCentralWidget(central)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("Arquivo")
        open_action = file_menu.addAction("Abrir")
        open_action.triggered.connect(self.open_file)
        close_action = file_menu.addAction("Fechar")
        close_action.triggered.connect(self.close)
        chart_menu = self.menuBar().addMenu("Graficos")
        for chart_type in ["Linha", "Barras", "Pizza"]:
            action = chart_menu.addAction(chart_type)
            action.triggered.connect(lambda checked=False, value=chart_type: self._select_chart(value))

    def _show_empty_state(self) -> None:
        self.plot.clear()
        self.plot.setTitle("Leia um arquivo para visualizar os dados")
        self.plot.hideAxis("bottom")
        self.plot.hideAxis("left")

    def _select_chart(self, chart_type: str) -> None:
        self.config.chart_type = chart_type
        self.render_chart()

    def open_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Abrir arquivo", "", "Arquivos de texto (*.txt *.csv *.tsv);;Todos os arquivos (*)"
        )
        if path:
            self._load_path(Path(path))

    def _load_path(self, path: Path) -> None:
        try:
            labels, values = load_two_columns(path)
        except ValueError as error:
            QtWidgets.QMessageBox.warning(self, "Arquivo invalido", str(error))
            return
        self.file_path = path
        self.labels = labels
        self.values = values
        self.status_label.setText(f"{path.name} - {len(values)} registros")
        self.render_chart()

    def open_settings(self) -> None:
        dialog = SettingsDialog(self.config, self)
        dialog.settings_applied.connect(self.render_chart)
        dialog.exec()

    def render_chart(self) -> None:
        if not self.values:
            return
        self.plot.clear()
        self.plot.showAxis("bottom")
        self.plot.showAxis("left")
        self.plot.setTitle(self.config.title)
        self.plot.showGrid(x=self.config.show_grid, y=self.config.show_grid, alpha=0.18)
        if self.config.chart_type == "Linha":
            self._render_line()
        elif self.config.chart_type == "Barras":
            self._render_bars()
        else:
            self._render_pie()

    def _render_line(self) -> None:
        symbols = {"Circulo": "o", "Quadrado": "s", "Triangulo": "t", "X": "x", "Nenhum": ""}
        item = pg.PlotDataItem(
            list(range(len(self.values))),
            self.values,
            pen=pg.mkPen(self.config.line_color, width=self.config.line_width),
            symbol=symbols[self.config.point_type],
            symbolSize=self.config.point_size,
            symbolBrush=self.config.line_color,
            name="Valores" if self.config.show_legend else None,
        )
        self.plot.addItem(item)
        if self.config.show_legend:
            self.plot.addLegend(offset=(20, 20)).addItem(item, "Valores")
        self._set_x_labels()
        if self.config.show_values:
            self._add_value_labels()

    def _render_bars(self) -> None:
        bars = pg.BarGraphItem(
            x=list(range(len(self.values))),
            height=self.values,
            width=self.config.bar_width,
            brush=self.config.bar_color,
            name="Valores" if self.config.show_legend else None,
        )
        self.plot.addItem(bars)
        if self.config.show_legend:
            self.plot.addLegend(offset=(20, 20)).addItem(bars, "Valores")
        self._set_x_labels()
        if self.config.show_values:
            self._add_value_labels()

    def _render_pie(self) -> None:
        self.plot.setAspectLocked(True)
        self.plot.setXRange(-1.2, 1.2)
        self.plot.setYRange(-1.2, 1.2)
        self.plot.hideAxis("bottom")
        self.plot.hideAxis("left")
        self.plot.addItem(PieItem(self.labels, self.values, self.config))
        if self.config.show_legend:
            legend = self.plot.addLegend(offset=(20, 20))
            for index, label in enumerate(self.labels):
                sample = pg.PlotDataItem([], [], pen=pg.mkPen(self.config.pie_colors[index % len(self.config.pie_colors)], width=8))
                legend.addItem(sample, label)

    def _set_x_labels(self) -> None:
        axis = self.plot.getAxis("bottom")
        axis.setTicks([list(enumerate(self.labels))])

    def _add_value_labels(self) -> None:
        for index, value in enumerate(self.values):
            text = pg.TextItem(f"{value:g}", color="#333333", anchor=(0.5, 1.0))
            text.setPos(index, value)
            self.plot.addItem(text)


def load_two_columns(path: Path) -> tuple[list[str], list[float]]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except OSError as error:
        raise ValueError(f"Nao foi possivel ler o arquivo: {error}") from error
    rows = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]
    if not rows:
        raise ValueError("O arquivo esta vazio.")
    delimiter = "," if "," in rows[0] else "\t" if "\t" in rows[0] else None
    parsed = list(csv.reader(rows, delimiter=delimiter or " ", skipinitialspace=True)) if delimiter else [re.split(r"\s+", row.strip()) for row in rows]
    labels: list[str] = []
    values: list[float] = []
    for row_number, row in enumerate(parsed, start=1):
        if len(row) != 2:
            raise ValueError(f"A linha {row_number} deve conter exatamente duas colunas.")
        try:
            value = float(row[1].strip().replace(",", "."))
        except ValueError as error:
            if row_number == 1:
                continue
            raise ValueError(f"O valor da linha {row_number} nao e numerico: {row[1]}") from error
        labels.append(row[0].strip())
        values.append(value)
    if not values:
        raise ValueError("Nenhum dado numerico foi encontrado na segunda coluna.")
    return labels, values


def main() -> None:
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()