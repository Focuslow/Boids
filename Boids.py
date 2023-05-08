from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal, QLineF
from PyQt5.QtGui import QPainter, QColor, QKeyEvent
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout

import random

class Boid:
    def __init__(self, grid, x, y, radius, color, margin):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.margin = margin
        self.maxspeed = 5
        self.dy = random.uniform(-self.maxspeed,self.maxspeed)
        self.dx = random.uniform(-self.maxspeed,self.maxspeed)
        self.screen = QApplication.primaryScreen().availableGeometry()
        self.grid = grid
        self.grid_pos = grid.get_cell(self.x,self.y)
        self.grid.add(self,self.grid_pos)
        self.neighbors = []
        self.separate_radius = 3 * self.radius
        self.align_radius = 10 * self.radius
        self.cohese_radius = self.align_radius
        self.cohese_factor = 0.005
        self.separate_factor = 0.05
        self.align_factor = 0.05
        self.history = [[self.x,self.y]]



    def move(self):
        self.neighbors = self.grid.get_local_neighborhood(self,self.grid_pos)
        self.get_nearby()
        self.cohesion()
        self.separation()
        self.alignment()
        self.noise()   
        self.speedlimit() 
        self.bound_move()
        self.y += self.dy
        self.x += self.dx
        self.update_cell()
        #self.update_color()
        self.history.append ([self.x,self.y])
        if len(self.history) > 25:
            self.history = self.history[1:]

    def noise(self):
        self.dx +=  random.uniform(-self.maxspeed,self.maxspeed) / 50
        self.dy +=  random.uniform(-self.maxspeed,self.maxspeed) / 50

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
            if dist < self.separate_radius:
                distance_x += (self.x - boid.x)
                distance_y += (self.y - boid.y)
        self.dx += distance_x * self.separate_factor
        self.dy += distance_y * self.separate_factor

    def alignment(self):
        avg_dx, avg_dy = [0,0]
        count = 0
        for boid in self.neighbors:
            dist = self.distance(boid)
            if dist > 0 and dist < self.align_radius:
                avg_dx += boid.dx
                avg_dy += boid.dy
                count += 1
            
        if count > 0:
            avg_dx /= count
            avg_dy /= count
            self.dx += (avg_dx - self.dx) * self.align_factor
            self.dy += (avg_dy - self.dy) * self.align_factor

    def cohesion(self):
        centroid = [0,0]
        count = 0
        x_dir, y_dir = [0,0]
        for boid in self.neighbors:
            dist = self.distance(boid)
            if dist > 0 and dist > self.cohese_radius:
                centroid[0] += boid.x
                centroid[1] += boid.y
                count += 1
        if count > 0:
            centroid[0] = centroid[0] / count
            centroid[1] = centroid[1] / count

            x_dir = centroid[0] - self.x
            y_dir = centroid[1] - self.y

            self.dx += x_dir * self.cohese_factor
            self.dy += y_dir * self.cohese_factor

    def bound_move(self):
        turn_factor = 1
        if self.y - self.margin < 0:
            self.dy += turn_factor
        if self.x - self.margin < 0:
            self.dx += turn_factor
        if self.x > self.screen.width() - self.margin:
            self.dx -= turn_factor
        if self.y > self.screen.height() - self.margin:
            self.dy -= turn_factor

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
        sum_color = {}
        for boid in self.nearby:
            dist = self.distance(boid)
            if dist > 0 and dist > self.cohese_radius/2:
                if boid.color in sum_color:
                    sum_color[boid.color] += 1
                else:
                    sum_color[boid.color] = 1
                count += 1
            if count > 0:
                self.color = max(sum_color)

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
        colors = [Qt.blue] #, Qt.red, Qt.yellow, Qt.green, Qt.magenta, Qt.cyan, Qt.black]
        margin = 100
        self.boid_history = []
        for i in range(100):
            radius = 5
            x = random.randint(margin, self.screen.width()-margin)
            y = random.randint(margin, self.screen.height()-margin)
            color = random.choice(colors)
            individual = Boid(self.grid, x, y, radius, color, margin)
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
            qp.drawEllipse(int(Boid.x-Boid.radius), int(self.height() - Boid.y - Boid.radius), 2 * Boid.radius, 2 * Boid.radius)
            for i in range(len(Boid.history)-1):
                qp.setPen(QColor(0,0,255,100))
                line = QLineF(int(Boid.history[i][0]),int(self.height()-Boid.history[i][1]),
                             int(Boid.history[i+1][0]), int(self.height()-Boid.history[i+1][1]))
                qp.drawLine(line)
            
            

    def updateBoids(self):
        paused = window.paused
        for Boid in self.Boids:
            if not paused:
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
        self.paused = 0

        for Boid in self.BoidWidget.Boids:
            Boid.move()
            #thread = BoidThread(Boid, self)
            #thread.start()

    def onBoidMoved(self):
        self.BoidWidget.update()

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Escape:
                sys.exit(0)
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Space:
                if self.paused == 0:
                    self.paused = 1
                else:
                    self.paused = 0
                
if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    window.show()
    sys.exit(app.exec_())
