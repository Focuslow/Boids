import random
import math

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
        self.collision_factor = 0.1
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
        self.avoid_collision() 
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

    def collision_angle(self,boid):
        heading_now = [self.dx, self.dy]
        scale_now = (heading_now[0]**2 + heading_now[1]**2)**(1/2)

        heading_collision = [boid.x-self.x, boid.y-self.y]
        scale_collision = (heading_collision[0]**2 + heading_collision[1]**2)**(1/2)

        scalar_prod = heading_collision[0]*heading_now[0] + heading_collision[1]*heading_now[1]
        cos_angle = scalar_prod / (scale_collision*scale_now)
        rad_angle = math.acos(cos_angle)
        angle = math.degrees(rad_angle)
        return angle
        
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

    def avoid_collision(self):
        for boid in self.neighbors:
            if isinstance(boid,Avoid):
                dist = self.distance(boid)
                if dist < self.view_radius:
                    angle = self.collision_angle(boid)
                    if abs(angle) < 30:
                        normal_vect = [self.dy, -self.dx]
                        self.dx += normal_vect[0] * self.collision_factor * 1/angle**(1/2) * 1/dist**(1/2)
                        self.dy += normal_vect[1] * self.collision_factor * 1/angle**(1/2) * 1/dist**(1/2)


class Avoid(Boid):
    def __init__(self, grid, x, y, radius, color, size, margin):
        super().__init__(grid, x, y, radius, color, size, margin)
        self.grid = grid
        self.grid_pos = grid.get_cell(x,y)
        self.grid.add(self,self.grid_pos)
        self.neighbors = []
    
    def move(self,view,sep,coh,align):
        pass 