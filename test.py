from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QKeyEvent, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

import random

class Boid:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.pos = [self.x, self,y]
        self.radius = radius
        self.color = color
        self.dy = random.choice([-0.5,0.5])
        self.dx = random.choice([-0.5,0.5])
        self.vel = [self.dx, self.dy]
        self.screen = QApplication.primaryScreen().availableGeometry()

    def move(self,flock):
        self.separation(flock)
        self.bound_move()

        self.y += self.dy
        self.x += self.dx

    def bound_move(self):
        if self.y - self.radius < 0:
            self.dy *= -1
        if self.x - self.radius < 0:
            self.dx *= -1
        #idk why 5*radius seems to be reading full screen width value somewhat wrong
        if self.x + 5*self.radius > self.screen.width():
            self.dx *= -1
        if self.y - self.radius > self.screen.height():
            self.dy *= -1

    def separation(self,flock):
        min_distance = self.radius*5
        avoid_factor = 0.05
        distance_x = 0
        distance_y = 0
        for boid in flock:
            dist = self.distance(boid)
            if dist > 0 and dist < min_distance:
                distance_x += (self.x - boid.x)/dist
                distance_y += (self.y - boid.y)/dist
        self.dx += distance_x * avoid_factor
        self.dy += distance_y * avoid_factor

    def distance(self,boid):
        diff_x = self.x-boid.x
        diff_y = self.y-boid.y
        abs_v = ((diff_x)**2+(diff_y)**2)**(1/2)
        return abs_v

    def speedlimit ():
        pass
class BoidWidget(QWidget):
    BoidMoved = pyqtSignal(Boid)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.Boids = []
        colors = [Qt.red, Qt.blue, Qt.green, Qt.yellow, Qt.magenta, Qt.cyan]
        for i in range(20):
            radius = 10
            x = random.randint(radius, self.screen.width())
            y = random.randint(radius, self.screen.height())
            color = random.choice(colors)
            individual = Boid(x, y, radius, color)
            self.Boids.append(individual)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateBoids)
        self.timer.start(10)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        #pixmap = QPixmap("D:\\OneDrive - Thermo Fisher Scientific\\Documents\\Phd_teach\\Boids\\fish.gif")
        
        for Boid in self.Boids:
            #qp.drawPixmap(QRect(Boid.x,Boid.y,100,50), pixmap)
            qp.setBrush(QColor(Boid.color))
            qp.drawEllipse(Boid.x - Boid.radius, self.height() - Boid.y - Boid.radius, 2 * Boid.radius, 2 * Boid.radius)

    def updateBoids(self):
        for Boid in self.Boids:
            Boid.move(self.Boids)
            self.BoidMoved.emit(Boid)

class BoidThread(QThread):
    def __init__(self, Boid, Flock, parent=None):
        super().__init__(parent)
        self.Boid = Boid
        self.Flock = Flock

    def run(self):
        while True:
            self.Boid.move(self.Flock)
            self.usleep(10)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.BoidWidget = BoidWidget(self)
        self.BoidWidget.BoidMoved.connect(self.onBoidMoved)
        layout = QVBoxLayout(self)
        layout.addWidget(self.BoidWidget)

        for Boid in self.BoidWidget.Boids:
            thread = BoidThread(Boid, self.BoidWidget.Boids,  self)
            thread.start()

    def onBoidMoved(self, Boid):
        self.BoidWidget.update()

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Escape:
                sys.exit(0)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    window.show()
    sys.exit(app.exec_())
