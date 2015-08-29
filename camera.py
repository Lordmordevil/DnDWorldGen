from vec2d import vec2d

class Camera:
    def __init__(self):
        self.offset = [0,0]
        self.zoom = 1
        self.viewProps = {"ShowPoints" : False , "DrawMode" : 0}
        self.view_w = 800
        self.view_h = 600

    def point_visible(self, point):
        screen_point = self.world_to_screen(point)
        padding = 50
        x_in_frame = (screen_point.x >= (0 - padding)) and (screen_point.x <= (self.view_w + padding))
        y_in_frame = (screen_point.y >= (0 - padding)) and (screen_point.y <= (self.view_h + padding))
        return x_in_frame and y_in_frame


    def world_to_screen(self, coords):
        screen_coords = vec2d(0, 0)
        screen_coords.x = int((coords.x - self.offset[0]) * self.zoom)
        screen_coords.y = int((coords.y - self.offset[1]) * self.zoom)
        return screen_coords

    def screen_to_world(self, coords):
        world_coords = vec2d(0, 0)

        world_coords.x = int((coords.x/self.zoom) + self.offset[0])
        world_coords.y = int((coords.y/self.zoom) + self.offset[1])
        return world_coords