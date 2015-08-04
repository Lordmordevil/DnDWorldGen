from delaunay import *
from vec2d import vec2d

class Voronoi:
    def __init__(self, tri, boundary = None):
        self.tri = tri
       
        self.__do(boundary)
        
    def __do(self, boundary):
        self.points = []
        self.pdict = {}
        
        for e in self.tri.edges:
            a = self.tri.points[e.a]
            b = self.tri.points[e.b]
            
            if e.l is not None and e.r is not None:
                ca = Circle(a, b, self.tri.points[e.l])
                cb = Circle(a, b, self.tri.points[e.r])
                atu = (ca.c.x, ca.c.y)
                btu = (cb.c.x, cb.c.y)
                
                if atu in self.pdict:
                    aidx = self.pdict[atu]
                else:
                    aidx = len(self.points)
                    self.points.append(vec2d(atu[0], atu[1]))
                    self.pdict[atu] = aidx
                    
                if btu in self.pdict:
                    bidx = self.pdict[btu]
                else:
                    bidx = len(self.points)
                    self.points.append(vec2d(btu[0], btu[1]))
                    self.pdict[btu] = bidx
                    
                e.setVedge(Edge(aidx, bidx))
            elif boundary is not None and (e.l is not None or e.r is not None):
                mid = (a+b)/2
                if e.l is not None:
                    c = Circle(a, b, self.tri.points[e.l])
                    p = c.c
                else:
                    c = Circle(a, b, self.tri.points[e.r])
                    p = c.c
                v = mid - p
                tx = -1
                ty = -1
                
                if v.x>0:
                    tx = (boundary[2]-p.x)/v.x
                elif v.x<0:
                    tx = (boundary[0]-p.x)/v.x
                if v.y>0:
                    ty = (boundary[3]-p.y)/v.y
                elif v.y<0:
                    ty = (boundary[1]-p.y)/v.y
                
                if tx > 0 or ty > 0:
                    if tx>ty and ty>0:
                        t = ty
                    else:
                        t = tx
                    p = p+v*t
                    ptu = (p.x, p.y)
                    ctu = (c.c.x, c.c.y)
                    if ptu in self.pdict:
                        pidx = self.pdict[ptu]
                    else:
                        pidx = len(self.points)
                        self.points.append(p)
                        self.pdict[ptu] = pidx
                    if ctu in self.pdict:
                        cidx = self.pdict[ctu]
                    else:
                        cidx = len(self.points)
                        self.points.append(c.c)
                        self.pdict[ctu] = cidx
                    e.setVedge(Edge(pidx, cidx))