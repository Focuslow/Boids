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