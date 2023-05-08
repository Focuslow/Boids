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
        self.r = QColor(color).red()
        self.g = QColor(color).green()
        self.b = QColor(color).blue()
        self.maxspeed = 2
        self.dy = random.choice([-self.maxspeed,self.maxspeed])
        self.dx = random.choice([-self.maxspeed,self.maxspeed])
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.grid = grid
        self.grid_pos = grid.get_cell(self.x,self.y)
        self.grid.add(self,self.grid_pos)
        self.neighbors = []
        self.separate_radius = 10 * self.radius
        self.align_radius = 2 * self.separate_radius
        self.cohese_radius = self.align_radius


    def move(self):
        self.neighbors = self.grid.get_local_neighborhood(self,self.grid_pos)
        self.get_nearby()
        self.alignment()
        self.separation()
        self.noise()
        self.cohesion()      
        self.bound_move()
        self.speedlimit()
        self.y += self.dy
        self.x += self.dx
        self.update_cell()
        #self.update_color()

    def noise(self):
        self.dx +=  random.randint(-self.maxspeed//10,self.maxspeed//10)
        self.dy +=  random.randint(-self.maxspeed//10,self.maxspeed//10)

    def distance(self,boid):
        diff_x = self.x-boid.x
        diff_y = self.y-boid.y
        abs_v = ((diff_x)**2+(diff_y)**2)**(1/2)
        return abs_v

    def get_nearby(self):
        min_distance = self.radius*50
        self.nearby = []
        for boid in self.neighbors:
            dist = self.distance(boid)
            if dist > 0 and dist < min_distance:
                self.nearby.append(boid)

    def separation(self):
        distance_x = 0
        distance_y = 0
        for boid in self.neighbors:
            dist = self.distance(boid)
            if dist > 0:
                distance_x += (self.x - boid.x) / dist
                distance_y += (self.y - boid.y) / dist
        self.dx += distance_x
        self.dy += distance_y

    def alignment(self):
        avg_dx, avg_dy = [0,0]
        count = 0
        for boid in self.neighbors:
            dist = self.distance(boid)
            if dist > 0:
                avg_dx += boid.dx / dist
                avg_dy += boid.dy / dist
                count += 1
            
        if count > 0:
            avg_dx /= count
            avg_dy /= count
            self.dx += (avg_dx - self.dx)
            self.dy += (avg_dy - self.dy)

    def cohesion(self):
        cohese_factor = 0.05
        centroid = [0,0]
        count = 0
        x_dir, y_dir = [0,0]
        for boid in self.neighbors:
            dist = self.distance(boid)
            if dist > 0:
                centroid[0] += boid.x
                centroid[1] += boid.y
                count += 1
        if count > 0:
            centroid[0] = centroid[0] / count
            centroid[1] = centroid[1] / count

            x_dir = centroid[0] - self.x
            y_dir = centroid[1] - self.y

        self.dx += x_dir * cohese_factor
        self.dy += y_dir    * cohese_factor

    def bound_move(self):
        if self.y - self.radius < 0:
            self.y = self.screen.height()
        if self.x - self.radius < 0:
            self.x = self.screen.width()
        #idk why 5*radius seems to be reading full screen width value somewhat wrong
        if self.x > self.screen.width():
            self.x = 5
        if self.y - self.radius > self.screen.height():
            self.y = 5

    def speedlimit (self):
        if self.dy >= self.maxspeed:
            self.dy = self.maxspeed
        if self.dy <= -self.maxspeed:
            self.dy = -self.maxspeed
        if self.dx >= self.maxspeed:
            self.dx = self.maxspeed
        if self.dx <= -self.maxspeed:
            self.dx = -self.maxspeed
    
    def update_cell(self):
        new_cell = self.grid.get_cell(self.x, self.y)
        if self.grid_pos != new_cell:
            self.grid.remove(self,self.grid_pos)
            self.grid_pos = new_cell
            self.grid.add(self, self.grid_pos)

    def update_color(self):
        count = 0
        sum_r = 0
        sum_g = 0
        sum_b = 0
        for boid in self.nearby:
            sum_r += boid.r
            sum_g += boid.g
            sum_b += boid.b
            count += 1
        if count > 0:
            self.r = sum_r//count
            self.g = sum_g//count
            self.b = sum_b//count

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
            qp.setBrush(QColor(Boid.r , Boid.g, Boid.b))
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
            Boid.move()
            #thread = BoidThread(Boid, self)
            #thread.start()

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
