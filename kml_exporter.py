"""
Discription: This script provides GUI application that export kml file to be imported with DJI GS Pro.
Author: Kohei Mikami
Version: v0.0.1
Complied on: 2023/7/12
"""


import os
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import PySide6
import qt_material
from PySide6 import QtWidgets


class main(QtWidgets.QWidget):
    """GUI application for kml file exporter."""

    CFG = {
        'window_title': 'Create kml file.',
        'window_position': [0, 0],
        'window_size': [800, 300],
        'theme': 'dark_cyan',
    }

    def __init__(self):
        """Constructor of the class"""
        self.app = QtWidgets.QApplication()
        super().__init__()

        # Set path to QT plugin.
        dir_name = os.path.dirname(PySide6.__file__)
        plugin_path = os.path.join(dir_name, 'plugins', 'platforms')
        os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

        # Set appearance of the window.
        self.setWindowTitle(self.CFG['window_title'])
        self.setGeometry(*self.CFG['window_position'], *self.CFG['window_size'])
        qt_material.apply_stylesheet(self, theme=f'{self.CFG["theme"]}.xml')

        self.init_ui()
        self.export_dir = None

    def init_ui(self):
        """Create initial UI."""
        self.flight_name_label = QtWidgets.QLabel('Flight name')
        self.flight_name_form = QtWidgets.QLineEdit('flight 1')
        self.flight_name_form.setStyleSheet("color: white;")

        self.center_point_lat_label = QtWidgets.QLabel('Latitude (deg)')
        self.center_point_lat_form = QtWidgets.QLineEdit('35.903071')
        self.center_point_lat_form.setStyleSheet("color: white;")
        self.center_point_lon_label = QtWidgets.QLabel('Longitude (deg)')
        self.center_point_lon_form = QtWidgets.QLineEdit('139.881667')
        self.center_point_lon_form.setStyleSheet("color: white;")

        self.flight_area_lat_label = QtWidgets.QLabel('Lat. length (m)')
        self.flight_area_lat_form = QtWidgets.QLineEdit('500')
        self.flight_area_lat_form.setStyleSheet("color: white;")
        self.flight_area_lon_label = QtWidgets.QLabel('Lon. length (m)')
        self.flight_area_lon_form = QtWidgets.QLineEdit('500')
        self.flight_area_lon_form.setStyleSheet("color: white;")

        self.export_dir_dialog_label = QtWidgets.QLabel('Export directory')
        self.export_dir_dialog_button = QtWidgets.QPushButton()
        icon = self.style().standardIcon(QtWidgets.QStyle.SP_DirOpenIcon)
        self.export_dir_dialog_button.setIcon(icon)
        self.export_dir_dialog_button.clicked.connect(lambda: self.get_export_dir())
        self.export_dir_dialog_display = QtWidgets.QLineEdit()
        self.export_dir_dialog_display.setStyleSheet("color: white;")

        self.run_button = QtWidgets.QPushButton('Run')
        self.run_button.clicked.connect(lambda: self.run())

        self.main_layout = QtWidgets.QGridLayout(self)
        self.main_layout.addWidget(self.flight_name_label, 1, 1, 1, 1)
        self.main_layout.addWidget(self.flight_name_form, 1, 2, 1, 3)
        self.main_layout.addWidget(self.center_point_lat_label, 2, 1, 1, 1)
        self.main_layout.addWidget(self.center_point_lat_form, 2, 2, 1, 1)
        self.main_layout.addWidget(self.center_point_lon_label, 2, 3, 1, 1)
        self.main_layout.addWidget(self.center_point_lon_form, 2, 4, 1, 1)
        self.main_layout.addWidget(self.flight_area_lat_label, 3, 1, 1, 1)
        self.main_layout.addWidget(self.flight_area_lat_form, 3, 2, 1, 1)
        self.main_layout.addWidget(self.flight_area_lon_label, 3, 3, 1, 1)
        self.main_layout.addWidget(self.flight_area_lon_form, 3, 4, 1, 1)
        self.main_layout.addWidget(self.export_dir_dialog_label, 4, 1, 1, 1)
        self.main_layout.addWidget(self.export_dir_dialog_button, 4, 2, 1, 1)
        self.main_layout.addWidget(self.export_dir_dialog_display, 4, 3, 1, 2)
        self.main_layout.addWidget(self.run_button, 5, 1, 1, 4)

    def run(self):
        """Run functions."""
        self.get_input_values()
        self.create_kml_file()

    def get_export_dir(self):
        """Call file dialog and get selected files."""
        caption = 'Select the export directory of kml file.'
        # options = QtWidgets.QFileDialog.Options()
        # self.export_dir = QtWidgets.QFileDialog.getExistingDirectory(self, caption, '', options=options)
        self.export_dir = QtWidgets.QFileDialog.getExistingDirectory(self, caption, '')
        self.export_dir_dialog_display.setText(self.export_dir)

    def get_input_values(self):
        """Read inputted values and set to variables."""
        self.flight_name = self.flight_name_form.text().replace(' ', '-')
        self.center_point = (
            float(self.center_point_lat_form.text()),
            float(self.center_point_lon_form.text())
            )  # deg.
        self.flight_area = (
            float(self.flight_area_lat_form.text()),
            float(self.flight_area_lon_form.text())
        )  # m, (NS direction, EW direction)
        if self.export_dir is None:
            raise ValueError('Please select or input export directory.')
        self.export_dir = Path(self.export_dir)
        print(self.export_dir)

    @staticmethod
    def calc_latlon_dist(center_point, flight_area):
        """Convert distance in meter value to latitude/longitude value using Hubeny's equation and WGS84.
        See (https://www.trail-note.net/tech/calc_distance/) in detail.

        Aegs:
            center_point (list): The list of latitude/longitude value of center point.
            flight_area (list): The list of lengths of the rectangular flight area side.

        Returns:
            float: The calculated distance in degree.
        """
        center_point_rad = np.deg2rad(center_point)
        Rx = 6378137.000  # m, WGS84
        Ry = 6356752.314245  # m, WGS84
        e = np.sqrt((Rx**2 - Ry**2) / Rx**2)

        P = center_point_rad[0]  # Approximation

        W = np.sqrt(1 - e**2 * np.sin(P)**2)
        N = Rx / W
        M = Rx * (1 - e**2) / W**3

        lat_diff = np.rad2deg((flight_area[0]/2) / M)  # deg.
        lon_diff = np.rad2deg((flight_area[1]/2) / (N * np.cos(P)))  # deg.
        return lat_diff, lon_diff

    def create_kml_file(self):
        """Create kml file using input values."""
        lat_diff, lon_diff = self.calc_latlon_dist(self.center_point, self.flight_area)
        relative_distance = np.array([
            [lat_diff, lon_diff],  # North east.
            [lat_diff, -lon_diff],  # North west.
            [-lat_diff, -lon_diff],  # South west.
            [-lat_diff, lon_diff],  # South east.
        ])

        relative_points = self.center_point + relative_distance
        coordinates = ' '.join([','.join(relative_points[i].astype('str')[::-1]) for i in (0, 1, 2, 3, 0)])

        kml = [
            '<?xml version="1.0" encoding="UTF-8"?>\n',
            '<kml xmlns="http://www.opengis.net/kml/2.2">\n',
            '<Document>\n',
            '<Style id="PolyStyle1">\n',
            '  <LineStyle>\n',
            '  <color>7f000000</color>\n',
            '  <width>3</width>\n',
            '  </LineStyle>\n',
            '  <PolyStyle>\n',
            '  <color>7f0000ff</color>\n',
            '  </PolyStyle>\n',
            '</Style>\n',
            '<Placemark>\n',
            '<styleUrl>#PolyStyle1</styleUrl>\n',
            '<Polygon>\n',
            '<outerBoundaryIs>\n',
            '<LinearRing>\n',
            f'<coordinates>{coordinates}</coordinates>\n',
            '</LinearRing>\n',
            '</outerBoundaryIs>\n',
            '</Polygon>\n',
            '</Placemark>\n',
            '</Document>\n',
            '</kml>\n',
        ]
        file_name = f'waypoints_{self.flight_name}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.kml'
        with open(self.export_dir / file_name, 'w') as f:
            f.writelines(kml)


if __name__ == '__main__':
    gui = main()
    gui.show()
    sys.exit(gui.app.exec())
