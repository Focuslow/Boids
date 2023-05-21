from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QLineF, QSize
from PyQt5.QtGui import QPainter, QColor, QKeyEvent, QMouseEvent, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider, QPushButton, QCheckBox
from Boid import Boid, Avoid
from BoidGrid import BoidGrid
import random


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.paused = 0
        self.tracers_only_enabled = 0
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
        self.tracers_btn.clicked.connect(self.tracers_only)
        
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

        self.tracers_btn = QPushButton(self)
        self.tracers_btn.setText("Hide Boids")
        self.tracers_btn.show()
        self.tracers_btn.setStyleSheet("background-color: white;")
        self.controls_menu.addWidget(self.tracers_btn)
        
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
        self.slider_sep.setValue(80)
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
        self.slider_coh.setValue(20)
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

    def tracers_only(self):
        if self.tracers_only_enabled:
            self.tracers_only_enabled = 0
            self.tracers_btn.setText("Show Boids")
        else:
            self.tracers_only_enabled = 1
            self.tracers_btn.setText("Hide Boids")

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
            if not window.tracers_only_enabled:
                qp.drawEllipse(int(Boid.x-Boid.radius), int(self.height() - Boid.y - Boid.radius), 2 * Boid.radius, 2 * Boid.radius)
            else:
                if isinstance(Boid,Avoid):
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
