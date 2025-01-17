from PyQt6.QtCore import Qt, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QFont
from PyQt6.QtWidgets import QWidget
from math import sin, cos, radians


class CompassWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.heading = 0  # Default heading angle in degrees
        self.setMinimumSize(300, 300)

    def set_heading(self, angle):
        """
        Set the heading angle for the compass.
        :param angle: Heading angle in degrees (0 to 360)
        """
        self.heading = angle % 360  # Ensure the angle is within 0-360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Define the center and radius
        center = self.rect().center()
        radius = int(min(self.width(), self.height()) / 2 - 20)

        # Draw compass outer circle
        painter.setPen(QPen(Qt.GlobalColor.black, 3))
        painter.drawEllipse(center, radius, radius)

        # Draw tick marks and degree labels
        for i in range(0, 360, 5):  # Tick marks every 5 degrees
            angle_rad = radians(i - 90)
            outer_x = center.x() + radius * cos(angle_rad)
            outer_y = center.y() + radius * sin(angle_rad)
            if i % 10 == 0:  # Longer tick marks every 10 degrees
                inner_x = center.x() + (radius - 15) * cos(angle_rad)
                inner_y = center.y() + (radius - 15) * sin(angle_rad)
                if i % 30 == 0:  # Draw degree labels every 30 degrees
                    label_radius = radius - 30
                    label_x = center.x() + label_radius * cos(angle_rad)
                    label_y = center.y() + label_radius * sin(angle_rad)
                    painter.setFont(QFont("Arial", 8))
                    painter.drawText(QPointF(label_x - 10, label_y + 5), str(i))
            else:  # Shorter tick marks for other degrees
                inner_x = center.x() + (radius - 10) * cos(angle_rad)
                inner_y = center.y() + (radius - 10) * sin(angle_rad)

            painter.setPen(QPen(Qt.GlobalColor.black, 2))
            painter.drawLine(QPointF(outer_x, outer_y), QPointF(inner_x, inner_y))

        # Draw cardinal and intermediate direction labels
        directions = {
            'N': 0, 'NE': 45, 'E': 90, 'SE': 135,
            'S': 180, 'SW': 225, 'W': 270, 'NW': 315
        }
        for direction, angle in directions.items():
            angle_rad = radians(angle - 90)
            label_radius = radius - 40
            label_x = center.x() + label_radius * cos(angle_rad)
            label_y = center.y() + label_radius * sin(angle_rad)
            painter.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            painter.drawText(QPointF(label_x - 10, label_y + 5), direction)

        # Draw compass needle
        painter.setPen(Qt.GlobalColor.red)
        painter.setBrush(QColor("red"))
        needle_length = radius * 0.7
        needle_base = radius * 0.1
        needle_angle = radians(self.heading - 90)

        # Needle tip and base coordinates
        tip_x = center.x() + needle_length * cos(needle_angle)
        tip_y = center.y() + needle_length * sin(needle_angle)
        left_base_x = center.x() + needle_base * cos(needle_angle + radians(120))
        left_base_y = center.y() + needle_base * sin(needle_angle + radians(120))
        right_base_x = center.x() + needle_base * cos(needle_angle - radians(120))
        right_base_y = center.y() + needle_base * sin(needle_angle - radians(120))

        # Draw needle
        painter.drawPolygon(QPointF(tip_x, tip_y), QPointF(left_base_x, left_base_y), QPointF(right_base_x, right_base_y))

        # Draw a center circle
        painter.setBrush(QColor("black"))
        painter.drawEllipse(center, 5, 5)

        painter.end()