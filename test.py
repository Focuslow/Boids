from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

import random

class Boid:
    def __init__(self, grid, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.maxspeed = 1
        self.dy = random.choice([-self.maxspeed,self.maxspeed])
        self.dx = random.choice([-self.maxspeed,self.maxspeed])
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.grid = grid
        self.grid_pos = grid.get_cell(self.x,self.y)
        self.grid.add(self,self.grid_pos)

    def move(self):
        neighbors = self.grid.get_local_neighborhood(self,self.grid_pos)
        self.get_nearby(neighbors)
        self.separation()
        self.bound_move()
        self.speedlimit()
        self.y += self.dy
        self.x += self.dx
        new_cell = self.grid.get_cell(self.x, self.y)
        if self.grid_pos != new_cell:
            self.grid.remove(self,self.grid_pos)
            self.grid_pos = new_cell
            self.grid.add(self, self.grid_pos)

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

    def get_nearby(self,neighbors):
        min_distance = self.radius*5
        self.nearby = []
        for boid in neighbors:
            dist = self.distance(boid)
            if dist > 0 and dist < min_distance:
                self.nearby.append(boid)

    def separation(self):
        avoid_factor = 0.05
        distance_x = 0
        distance_y = 0
        for boid in self.nearby:
            dist = self.distance(boid)
            distance_x += (self.x - boid.x)/dist
            distance_y += (self.y - boid.y)/dist
        self.dx += distance_x * avoid_factor
        self.dy += distance_y * avoid_factor

    def distance(self,boid):
        diff_x = self.x-boid.x
        diff_y = self.y-boid.y
        abs_v = ((diff_x)**2+(diff_y)**2)**(1/2)
        return abs_v

    def speedlimit (self):
        if self.dy >= self.maxspeed:
            self.dy = self.maxspeed
        if self.dy <= -self.maxspeed:
            self.dy = -self.maxspeed
        if self.dx >= self.maxspeed:
            self.dx = self.maxspeed
        if self.dx <= -self.maxspeed:
            self.dx = -self.maxspeed


class BoidGrid:
    def __init__(self):
        self.grid_size = 100
        self.dict = {}
    def get_cell(self,x,y):
        return (x//self.grid_size, y//self.grid_size)
    def add(self, boid, cell):
        if cell in self.dict:
            self.dict[cell].append(boid)
        else:
            self.dict[cell] = [boid]
    def remove(self, boid, cell):
        if cell in self.dict and boid in self.dict[cell]:
            self.dict[cell].remove(boid)
    def get_local_neighborhood(self, boid, cell):
        nearby = []
        if cell in self.dict:
            for x in (-1,0,1):
                for y in (-1,0,1):
                    nearby += self.dict.get((cell[0]+x, cell[1]+y),[])
            nearby.remove(boid)
        return nearby

class BoidWidget(QWidget):
    BoidMoved = pyqtSignal(Boid)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.Boids = []
        self.grid = BoidGrid()
        colors = [Qt.red, Qt.blue, Qt.green, Qt.yellow, Qt.magenta, Qt.cyan]
        for i in range(100):
            radius = 10
            x = random.randint(radius, self.screen.width())
            y = random.randint(radius, self.screen.height())
            color = random.choice(colors)
            individual = Boid(self.grid, x, y, radius, color)
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
            qp.drawEllipse(int(Boid.x - Boid.radius), int(self.height() - Boid.y - Boid.radius), 2 * Boid.radius, 2 * Boid.radius)

    def updateBoids(self):
        for Boid in self.Boids:
            Boid.move()
        self.BoidMoved.emit(Boid)

class BoidThread(QThread):
    def __init__(self, Boid, parent=None):
        super().__init__(parent)
        self.Boid = Boid

    def run(self):
        while True:
            self.Boid.move()
            self.usleep(10)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.BoidWidget = BoidWidget(self)
        self.BoidWidget.BoidMoved.connect(self.onBoidMoved)
        layout = QVBoxLayout(self)
        layout.addWidget(self.BoidWidget)

        for Boid in self.BoidWidget.Boids:
            thread = BoidThread(Boid,  self)
            thread.start()

    def onBoidMoved(self):
        self.BoidWidget.update()

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
                sys.exit(0)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    window.show()
    sys.exit(app.exec_())
