import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtCore import QTimer
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtOpenGL import QGLWidget

class HeartVisualization(QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(800, 600)
        self.rotation_x = 0
        self.rotation_y = 0
        self.scale = 1.0
        self.translate_z = -5.0
        self.last_x = 0
        self.last_y = 0
        self.mouse_pressed = False
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_rotation)
        self.timer.start(30)

    def initializeGL(self):
        glClearColor(1.0, 1.0, 1.0, 1.0)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
        glEnable(GL_NORMALIZE)
        glShadeModel(GL_SMOOTH)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)

    def heart_function(self, u, v):
        x = 16 * (np.sin(u) ** 3)
        y = 13 * np.cos(u) - 5 * np.cos(2 * u) - 2 * np.cos(3 * u) - np.cos(4 * u)
        z = (np.cos(v) * (1 + 0.5 * np.sin(u))) * 5
        return x, y, z

    def generate_heart_mesh(self):
        u = np.linspace(0, 2 * np.pi, 30)  # 0 ~ 2π
        v = np.linspace(0, np.pi, 30)  # 0 ~ π
        u, v = np.meshgrid(u, v)

        x, y, z = self.heart_function(u, v)

        vertices = np.array([x.flatten(), y.flatten(), z.flatten()]).T
        faces = []

        rows, cols = u.shape
        for i in range(rows - 1):
            for j in range(cols - 1):
                idx1 = i * cols + j
                idx2 = i * cols + (j + 1)
                idx3 = (i + 1) * cols + j
                idx4 = (i + 1) * cols + (j + 1)

                faces.append([idx1, idx2, idx3])
                faces.append([idx3, idx2, idx4])

        return vertices, np.array(faces)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 카메라
        glTranslatef(0, 0, self.translate_z)

        glRotatef(self.rotation_x, 1, 0, 0)
        glRotatef(self.rotation_y, 0, 1, 0)
        glScalef(self.scale, self.scale, self.scale)

        vertices, faces = self.generate_heart_mesh()

        glBegin(GL_TRIANGLES)
        for face in faces:
            glColor4f(0.9, 0.1, 0.1, 0.8)  # 약간의 투명도
            for vertex_idx in face:
                glVertex3fv(vertices[vertex_idx])
        glEnd()

        glColor4f(0.0, 0.0, 0.0, 1.0)  # 검은선
        glBegin(GL_LINES)
        for face in faces:
            for i in range(3):
                glVertex3fv(vertices[face[i]])
                glVertex3fv(vertices[face[(i + 1) % 3]])
        glEnd()

    def update_rotation(self):
        self.rotation_x += 1
        self.rotation_y += 0.5
        self.update()

    def mousePressEvent(self, event):
        self.mouse_pressed = True
        self.last_x = event.x()
        self.last_y = event.y()

    def mouseMoveEvent(self, event):
        if self.mouse_pressed:
            dx = event.x() - self.last_x
            dy = event.y() - self.last_y
            self.rotation_x += dy
            self.rotation_y += dx
            self.last_x = event.x()
            self.last_y = event.y()
            self.update()

    def mouseReleaseEvent(self, event):
        self.mouse_pressed = False

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
        self.update()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('❣️')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        layout = QVBoxLayout()

        heart_widget = HeartVisualization()
        layout.addWidget(heart_widget)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
