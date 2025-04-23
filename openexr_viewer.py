import sys
import numpy as np
import OpenImageIO as oiio

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtGui import QPainter, QImage, QPen, QColor, QMouseEvent
from PySide6.QtCore import Qt, QPoint


def linear_to_srgb(x):
    """Apply sRGB tone mapping to linear float image"""
    x = np.clip(x, 0.0, 1.0)
    return np.where(x <= 0.0031308, 12.92 * x, 1.055 * np.power(x, 1 / 2.4) - 0.055)


class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 600)
        self.image = QImage(self.size(), QImage.Format_RGB32)
        self.image.fill(QColor("white"))

        self.drawing = False
        self.last_point = QPoint()
        self.pen_color = QColor("black")
        self.pen_width = 2

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing:
            painter = QPainter(self.image)
            pen = QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.position().toPoint())
            self.last_point = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def load_image(self, path):
        if path.lower().endswith(".exr"):
            input_image = oiio.ImageInput.open(path)
            if not input_image:
                raise RuntimeError("Failed to open EXR image")

            spec = input_image.spec()
            pixels = input_image.read_image("float")
            input_image.close()

            if pixels is None or isinstance(pixels, int):
                raise RuntimeError("Failed to read EXR image data: Unsupported layout or compression.")

            try:
                img_np = np.array(pixels).reshape((spec.height, spec.width, spec.nchannels))
            except Exception as e:
                raise RuntimeError(f"Failed to reshape EXR pixel data: {e}")

            # Use first 3 channels (R, G, B)
            if spec.nchannels < 3:
                raise RuntimeError("EXR image does not have at least 3 channels")
            img_np = img_np[:, :, :3]

            # Apply tone mapping to get displayable sRGB
            def reinhard_tonemap(x):
                return x / (1.0 + x)

            img_mapped = reinhard_tonemap(img_np)
            img_srgb = np.power(np.clip(img_mapped, 0, 1), 1/2.2)
            img_uint8 = (img_srgb * 255).astype(np.uint8)

            height, width, _ = img_uint8.shape
            qimage = QImage(img_uint8.data, width, height, 3 * width, QImage.Format_RGB888).copy()

            self.setFixedSize(width, height)
            self.image = qimage
            self.update()

        else:
            loaded = QImage(path)
            if loaded.isNull():
                raise RuntimeError("Failed to load image")
            self.setFixedSize(loaded.width(), loaded.height())
            self.image = loaded.copy()
            self.update()

    def export_image(self, path):
        if path.lower().endswith(".exr"):
            width = self.image.width()
            height = self.image.height()
            
            # Convert to RGB32 format for consistent processing
            rgb_image = self.image.convertToFormat(QImage.Format_RGB32)
            bytes_per_line = rgb_image.bytesPerLine()
            buffer = rgb_image.constBits()
            
            # Create the array using the correct stride
            arr = np.frombuffer(buffer, dtype=np.uint8, count=height * bytes_per_line)
            arr = arr.reshape((height, bytes_per_line // 4, 4))
            
            # Extract RGB channels (QImage.Format_RGB32 is BGRA)
            r_channel = arr[:, :width, 2]
            g_channel = arr[:, :width, 1]
            b_channel = arr[:, :width, 0]
            
            # Stack the channels in RGB order
            rgb_arr = np.stack([r_channel, g_channel, b_channel], axis=2)
            
            # Convert from [0,255] uint8 to [0,1] float
            rgb_srgb = rgb_arr.astype(np.float32) / 255.0
            
            # Convert from sRGB to linear space using the EXACT INVERSE
            # of the transformation used when importing (power function with gamma 2.2)
            rgb_linear = np.power(rgb_srgb, 2.2)
            
            # Inverse of the Reinhard tonemapping
            def inverse_reinhard(x):
                # Clip to avoid division by zero or negative values
                return np.clip(x, 0.0, 0.95) / (1.0 - np.clip(x, 0.0, 0.95))
            
            rgb_hdr = inverse_reinhard(rgb_linear)
            
            # Create EXR with full float precision
            spec = oiio.ImageSpec(width, height, 3, "float")
            out = oiio.ImageOutput.create(path)
            if not out:
                raise RuntimeError("Could not create EXR file")
            out.open(path, spec)
            out.write_image(rgb_hdr)
            out.close()
        else:
            if not self.image.save(path):
                raise RuntimeError("Failed to save image")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenEXR Viewer")
        self.canvas = Canvas()

        load_button = QPushButton("Load PNG/EXR")
        load_button.clicked.connect(self.load_image)

        save_button = QPushButton("Export PNG/EXR")
        save_button.clicked.connect(self.save_image)

        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        layout.addWidget(load_button)
        layout.addWidget(save_button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def load_image(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Images (*.png *.exr)")
        if path:
            try:
                self.canvas.load_image(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def save_image(self):
        # Use separate filters instead of combining them
        path, selected_filter = QFileDialog.getSaveFileName(
            self, 
            "Save Image", 
            "", 
            "EXR Files (*.exr);;PNG Files (*.png)"
        )
        
        if path:
            # Add appropriate extension if user didn't specify one
            if selected_filter == "EXR Files (*.exr)" and not path.lower().endswith(".exr"):
                path += ".exr"
            elif selected_filter == "PNG Files (*.png)" and not path.lower().endswith(".png"):
                path += ".png"
            
            try:
                self.canvas.export_image(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())