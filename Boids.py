from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QLineF, QSize
from PyQt5.QtGui import QPainter, QColor, QKeyEvent, QMouseEvent, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton

import random

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.paused = 0
        self.main = QHBoxLayout(self)
        self.controls_menu = QVBoxLayout(self)
        self.controls()
        self.BoidWidget = BoidWidget(self)
        self.BoidWidget.boid_moved.connect(self.on_boid_moved)
        self.slider_view.valueChanged.connect(self.on_boid_moved)
        self.slider_coh.valueChanged.connect(self.on_boid_moved)
        self.slider_align.valueChanged.connect(self.on_boid_moved)
        self.slider_sep.valueChanged.connect(self.on_boid_moved)
        self.pause_btn.clicked.connect(self.pause_action)
        self.reset_btn.clicked.connect(self.reset_boids)
        
        self.main.addWidget(self.BoidWidget)
        self.main.addLayout(self.controls_menu)
        self.setLayout(self.main)
        for Boid in self.BoidWidget.Boids:
            Boid.move(self.view,self.sep,self.coh,self.align)

    def controls(self):
        self.animate = False
        self.controls_menu.setAlignment(Qt.AlignTop)
        self.controls_menu.setSpacing(50)

        #buttons
        self.pause_btn = QPushButton(self)
        self.pause_btn.setText("Pause")
        self.pause_btn.show()
        self.controls_menu.addWidget(self.pause_btn)
        self.pause_btn.setStyleSheet("background-color: white;")

        self.reset_btn = QPushButton(self)
        self.reset_btn.setText("Reset")
        self.reset_btn.show()
        self.reset_btn.setStyleSheet("background-color: white;")
        self.controls_menu.addWidget(self.reset_btn)
        
        #distance of alignment and cohesion
        self.view_menu = QVBoxLayout(self)
        self.controls_menu.addLayout(self.view_menu)
        self.view_menu.setAlignment(Qt.AlignTop)
        self.view_menu.setSpacing(10)
        self.view_info = QLabel(self)
        self.view_info.setText("Effect radius")
        self.view_info.setAlignment(Qt.AlignCenter)
        self.view_info.setFixedWidth(100)
        self.view_info.setFixedHeight(20)
        self.view_info.show()
        self.view_menu.addWidget(self.view_info)
        
        self.slider_view = QSlider(Qt.Horizontal, self)
        self.slider_view.setFixedWidth(100)
        self.slider_view.show()
        self.slider_view.setValue(50)
        self.slider_view.setMinimum(5)
        self.slider_view.setMaximum(100)
        self.view_menu.addWidget(self.slider_view)

        #coefficient of separataion
        self.sep_menu = QVBoxLayout(self)
        self.controls_menu.addLayout(self.sep_menu)
        self.sep_menu.setAlignment(Qt.AlignTop)
        self.sep_menu.setSpacing(10)
        self.sep_info = QLabel(self)
        self.sep_info.setText("Separation")
        self.sep_info.setAlignment(Qt.AlignCenter)
        self.sep_info.setFixedWidth(100)
        self.sep_info.setFixedHeight(20)
        self.sep_info.show()
        self.sep_menu.addWidget(self.sep_info)
        
        self.slider_sep = QSlider(Qt.Horizontal, self)
        self.slider_sep.setFixedWidth(100)
        self.slider_sep.show()
        self.slider_sep.setValue(50)
        self.slider_sep.setMinimum(0)
        self.slider_sep.setMaximum(100)
        self.sep_menu.addWidget(self.slider_sep)

        #coefficient of cohession
        self.coh_menu = QVBoxLayout(self)
        self.controls_menu.addLayout(self.coh_menu)
        self.coh_menu.setAlignment(Qt.AlignTop)
        self.coh_menu.setSpacing(10)
        self.coh_info = QLabel(self)
        self.coh_info.setText("Cohession")
        self.coh_info.setAlignment(Qt.AlignCenter)
        self.coh_info.setFixedWidth(100)
        self.coh_info.setFixedHeight(20)
        self.coh_info.show()
        self.coh_menu.addWidget(self.coh_info)
        
        self.slider_coh = QSlider(Qt.Horizontal, self)
        self.slider_coh.setFixedWidth(100)
        self.slider_coh.show()
        self.slider_coh.setValue(50)
        self.slider_coh.setMinimum(0)
        self.slider_coh.setMaximum(100)
        self.coh_menu.addWidget(self.slider_coh)

        #coefficient of alignment
        self.align_menu = QVBoxLayout(self)
        self.controls_menu.addLayout(self.align_menu)
        self.align_menu.setAlignment(Qt.AlignTop)
        self.align_menu.setSpacing(10)
        self.align_info = QLabel(self)
        self.align_info.setText("Alignment")
        self.align_info.setAlignment(Qt.AlignCenter)
        self.align_info.setFixedWidth(100)
        self.align_info.setFixedHeight(20)
        self.align_info.show()
        self.align_menu.addWidget(self.align_info)
        
        self.slider_align = QSlider(Qt.Horizontal, self)
        self.slider_align.setFixedWidth(100)
        self.slider_align.show()
        self.slider_align.setValue(50)
        self.slider_align.setMinimum(0)
        self.slider_align.setMaximum(100)
        self.align_menu.addWidget(self.slider_align)

        self.view = self.slider_view.value()
        self.sep = self.slider_sep.value()
        self.coh = self.slider_coh.value()
        self.align = self.slider_align.value()

    def on_boid_moved(self):
        self.view = self.slider_view.value()
        self.sep = self.slider_sep.value()
        self.coh = self.slider_coh.value()
        self.align = self.slider_align.value()
        self.BoidWidget.update()

    def pause_action(self):
            if self.paused == 0:
                self.paused = 1
                self.pause_btn.setText("Unpause")

            else:
                self.paused = 0
                self.pause_btn.setText("Pause")

    def reset_boids(self):
        while len(self.BoidWidget.Boids) > 0:
            del self.BoidWidget.Boids[0]
        del self.BoidWidget.grid
        self.BoidWidget.init_boids()

    def keyPressEvent(self, event):
        if type(event) == QKeyEvent:
            if event.key() == Qt.Key_Escape:
                sys.exit(0)
            if event.key() == Qt.Key_Space:
                if self.paused == 0:
                    self.paused = 1
                else:
                    self.paused = 0
    
    def mousePressEvent(self, event):
        max_y = self.BoidWidget.screen.height()
        if type(event) == QMouseEvent:
            if event.button() == Qt.LeftButton:
                self.BoidWidget.add_boid(event.x() - 2*self.BoidWidget.radius, max_y - event.y() + 6*self.BoidWidget.radius)
            if event.button() == Qt.RightButton:
                self.BoidWidget.add_avoid(QCursor.pos().x() - 2*self.BoidWidget.radius, max_y - QCursor.pos().y() + 6*self.BoidWidget.radius)

class Boid:
    def __init__(self, grid, x, y, radius, color, size, margin):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.margin = margin
        self.max_speed = 5
        self.size = size
        self.dy = random.uniform(-self.max_speed,self.max_speed)
        self.dx = random.uniform(-self.max_speed,self.max_speed)
        self.grid = grid
        self.grid_pos = grid.get_cell(self.x,self.y)
        self.grid.add(self,self.grid_pos)
        self.neighbors = []
        self.separate_radius = 3 * self.radius
        self.view_radius = 10 * self.radius
        self.cohese_factor = 0.005
        self.separate_factor = 0.05
        self.align_factor = 0.05
        self.history = [[self.x,self.y]]

    def move(self, view, sep, coh, align):
        self.neighbors = self.grid.get_local_neighborhood(self,self.grid_pos)
        self.view_radius = view
        self.separate_factor = sep / 1000
        self.cohese_factor = coh / 10000
        self.align_factor = align / 1000
        self.get_nearby()
        self.cohesion()
        self.separation()
        self.alignment()
        self.noise()   
        self.speed_limit() 
        self.bound_move()
        self.y += self.dy
        self.x += self.dx
        self.update_cell()
        #self.update_color()
        self.history.append ([self.x,self.y])
        if len(self.history) > 25:
            self.history = self.history[1:]

    def noise(self):
        self.dx +=  random.uniform(-self.max_speed,self.max_speed) / 50
        self.dy +=  random.uniform(-self.max_speed,self.max_speed) / 50

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
            if isinstance(boid,Avoid):
                distance_x *= 1.01
                distance_y *= 1.01
        self.dx += distance_x * self.separate_factor
        self.dy += distance_y * self.separate_factor

    def alignment(self):
        avg_dx, avg_dy = [0,0]
        count = 0
        for boid in self.neighbors:
            dist = self.distance(boid)
            if dist > 0 and dist < self.view_radius:
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
            if isinstance(boid,Avoid):
                continue
            else:
                dist = self.distance(boid)
                if dist > 0 and dist > self.view_radius:
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
        if self.x > self.size.width() - self.margin:
            self.dx -= turn_factor
        if self.y > self.size.height() - self.margin:
            self.dy -= turn_factor

    def speed_limit (self):
        if self.dy >= self.max_speed:
            self.dy = self.max_speed
        if self.dy <= -self.max_speed:
            self.dy = -self.max_speed
        if self.dx >= self.max_speed:
            self.dx = self.max_speed
        if self.dx <= -self.max_speed:
            self.dx = -self.max_speed
    
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

class Avoid(Boid):
    def __init__(self, grid, x, y, radius, color, size, margin):
        super().__init__(grid, x, y, radius, color, size, margin)
        self.grid = grid
        self.grid_pos = grid.get_cell(x,y)
        self.grid.add(self,self.grid_pos)
        self.neighbors = []
    
    def move(self,view,sep,coh,align):
        pass        

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
    boid_moved = pyqtSignal(Boid)

    def __init__(self, parent= None):
        super().__init__(parent)
        self.parent = parent
        self.Boids = []
        self.colors = [Qt.blue] #, Qt.red, Qt.yellow, Qt.green, Qt.magenta, Qt.cyan, Qt.black]
        self.margin = 100
        self.num_boids = 100
        self.num_avoids = 10
        self.boid_history = []
        self.radius = 5
        self.screen = QApplication.primaryScreen().availableGeometry()
        #smaller widget to accomodate control panel on the side
        self.setMinimumSize(QSize(self.screen.width() - 120 ,self.screen.height()))
        self.init_boids()
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
                Boid.move(self.parent.view,self.parent.sep,self.parent.coh,self.parent.align)
        self.boid_moved.emit(Boid)

    def init_boids(self):
        self.grid = BoidGrid()
        for i in range(self.num_boids):
            x = random.randint(self.margin, self.width()-self.margin)
            y = random.randint(self.margin, self.height()-self.margin)
            self.add_boid(x,y)
        for i in range(self.num_avoids):
            x = random.randint(self.margin, self.width()-self.margin)
            y = random.randint(self.margin, self.height()-self.margin)
            self.add_avoid(x,y)

    def add_boid(self,x,y):
        color = Qt.blue
        individual = Boid(self.grid, x, y, self.radius, color, self.size(), self.margin)
        self.Boids.append(individual)

    def add_avoid(self,x,y):
        color = Qt.red
        individual = Avoid(self.grid, x, y, self.radius, color, self.size(), self.margin)
        self.Boids.append(individual)

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)
    window = MainWindow()
    window.showFullScreen()
    window.show()
    sys.exit(app.exec_())
