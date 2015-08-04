import math
from vec2d import vec2d

def cross(a, b, c):
    """Cross product of 2D vectors defined by three points.
    
    The two vectors are a-b and c-b"""
    px = a.x - b.x
    py = a.y - b.y
    qx = c.x - b.x
    qy = c.y - b.y
    
    return px * qy - qx * py
    
def det3(r11,r12,r13,r21,r22,r23,r31,r32,r33):
    """Determinant of a 3x3 matrix"""
    return r11*(r22*r33-r23*r32)-r12*(r21*r33-r23*r31)+r13*(r21*r32-r22*r31)
        
class Circle:
    """http://mathworld.wolfram.com/Circumcircle.html"""
    def __init__(self, a, b, c):
        det_a  =  det3(a.x, a.y, 1, b.x, b.y, 1, c.x, c.y, 1)
        det_bx = -det3(a.get_length_sqrd(), a.y, 1, b.get_length_sqrd(), b.y, 1, c.get_length_sqrd(), c.y, 1)
        det_by =  det3(a.get_length_sqrd(), a.x, 1, b.get_length_sqrd(), b.x, 1, c.get_length_sqrd(), c.x, 1)
        det_c  = -det3(a.get_length_sqrd(), a.x, a.y, b.get_length_sqrd(), b.x, b.y, c.get_length_sqrd(), c.x, c.y)
        self.c = vec2d(-det_bx/(2*det_a), -det_by/(2*det_a))
        self.r = self.c.get_distance(a)
        self.r2 = self.r**2
        
    def inside(self, p):
        return self.r2 > self.c.get_dist_sqrd(p)
        
class Edge:
    def __init__(self, a = None, b = None, l = None, r = None):
        self.a = a
        self.b = b
        self.l = l
        self.r = r

        self.vEdge = []
    
    def setVedge(self, vedge):
        self.vEdge.append(vedge)

    def set(self, a = None, b = None, l = None, r = None):
        self.a = a
        self.b = b
        self.l = l
        self.r = r
        
    def swap(self):
        (self.a, self.b) = (self.b, self.a)
        (self.l, self.r) = (self.r, self.l)
        
    def __str__(self):
        if self.l is None:
            l = -1
        else:
            l = self.l
        if self.r is None:
            r = -1
        else:
            r = self.r
        return "Edge from %d to %d, left: %d, right: %d" % (self.a, self.b, l, r)
        
class Triangulation:
    def __init__(self, points):
        self.points = points
        self.edges = []
        self.edgeset = set()
        
    def cleanup(self):
        self.edges = []
        self.edgeset = set()
        
    def pointCount(self):
        return len(self.points)
        
    def edgeCount(self):
        return len(self.edges)
        
    def addEdge(self, edge):
        if (edge.a, edge.b) not in self.edgeset and (edge.b, edge.a) not in self.edgeset:
            self.edges.append(edge)
            self.edgeset.add((edge.a, edge.b))
            return True
        else:
            return False
            
    def addLefty(self, a, b, l):
        for e in self.edges:
            if (e.a == a and e.b == b):
                e.l = l
                break
            elif (e.a == b and e.b == a):
                e.r = l            
        else:
            edge = Edge(a, b, l)
            self.edges.append(edge)
            self.edgeset.add((edge.a, edge.b))
        
class Delaunay:
    def __init__(self, tri):
        self.tri = tri
        
        self.__do()
        
    def __do(self):
        self.tri.cleanup()
        if self.tri.pointCount() < 2:
            return
            
        (a, b) = self.findNearest2()
        
        self.tri.addEdge(Edge(a, b))
        idx = 0

        while idx < self.tri.edgeCount():
            e = self.tri.edges[idx]
            for i in range(2):
                if e.l is None:
                    self.makeLeftTriangle(e)
                e.swap()
            idx += 1
        print("For: ", self.tri.pointCount(), " point we have: ", self.tri.edgeCount(), " edges")
        
    def findNearest2(self):
        n = self.tri.pointCount()
        (a, b) = (0, 1)
        mind = self.tri.points[a].get_dist_sqrd(self.tri.points[b])
        for i in range(n):
            for j in range(i+1, n):
                d = self.tri.points[i].get_dist_sqrd(self.tri.points[j])
                if d < mind:
                    mind = d
                    (a, b) = (i, j)
        return (a, b)
        
    def makeLeftTriangle(self, edge):
        n = self.tri.pointCount()
        pts = self.tri.points
        idx = 0
        (a, b) = (edge.a, edge.b)
        u = None
        while idx < n:
            if cross(pts[a], pts[b], pts[idx]) > 0:
                u = idx
                break
            idx += 1
            
        if u is None:
            return
            
        idx += 1
        c = Circle(pts[a], pts[b], pts[u])
        while idx < n:
            if cross(pts[a], pts[b], pts[idx]) > 0:
                if c.inside(pts[idx]):
                    u = idx
                    c = Circle(pts[a], pts[b], pts[u])
            idx += 1
            
        edge.l = u
        self.tri.addLefty(u, a, b)
        self.tri.addLefty(b, u, a)
