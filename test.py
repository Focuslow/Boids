from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal, QRect
from PyQt5.QtGui import QPainter, QColor, QKeyEvent, QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel

import random

class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.dy = 0
        self.gravity = 0.01

    def move(self):
        
        if self.y - self.radius < 0:
            self.y = 0 + self.radius
            self.dy *= -1

        else:
            self.dy -= self.gravity
            self.y += self.dy


class BallWidget(QWidget):
    ballMoved = pyqtSignal(Ball)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.balls = []
        colors = [Qt.red, Qt.blue, Qt.green, Qt.yellow, Qt.magenta, Qt.cyan]
        screen = QApplication.primaryScreen().availableGeometry()
        for i in range(20):
            x = random.randint(0, screen.width())
            y = random.randint(0, screen.height())
            radius = 5
            color = random.choice(colors)
            ball = Ball(x, y, radius, color)
            self.balls.append(ball)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateBalls)
        self.timer.start(10)

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setRenderHint(QPainter.Antialiasing)
        pixmap = QPixmap("D:\\OneDrive - Thermo Fisher Scientific\\Documents\\Phd_teach\\Boids\\fish.gif")
        
        for ball in self.balls:
            qp.drawPixmap(QRect(ball.x,ball.y,100,50), pixmap)
            #qp.setBrush(QColor(ball.color))
            #qp.drawEllipse(ball.x - ball.radius, self.height() - ball.y - ball.radius, 2 * ball.radius, 2 * ball.radius)

    def updateBalls(self):
        for ball in self.balls:
            ball.move()
            self.ballMoved.emit(ball)

class BallThread(QThread):
    def __init__(self, ball, parent=None):
        super().__init__(parent)
        self.ball = ball

    def run(self):
        while True:
            self.ball.move()
            self.usleep(10)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.ballWidget = BallWidget(self)
        self.ballWidget.ballMoved.connect(self.onBallMoved)

        layout = QVBoxLayout(self)
        layout.addWidget(self.ballWidget)

        for ball in self.ballWidget.balls:
            thread = BallThread(ball, self)
            thread.start()

    def onBallMoved(self, ball):
        self.ballWidget.update()

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
