from ..overrides import override
from ..importer import modules

GooCanvas = modules['GooCanvas']._introspection_module

__all__ = []

#We cant change the numner of points once constructed, and boxed types do not allow
#arguments to constructors, so override __new__
class CanvasPoints(GooCanvas.CanvasPoints):

    def __new__(cls, points):

        assert len(points)
        assert len(points[0])

        obj = cls.new(len(points))
        i = 0
        for p in points:
            obj.set_point(i, p[0],p[1])
            i += 1
        return obj

CanvasPoints = override(CanvasPoints)
__all__.append('CanvasPoints')

class CanvasPolyline(GooCanvas.CanvasPolyline):

    @classmethod
    def new_line(cls, parent, x1, y1, x2, y2, **props):
        props.update(
                parent=parent,
                points=CanvasPoints(((x1,y1),(x2,y2))),
                close_path=False)
        return cls(**props)

CanvasPolyline = override(CanvasPolyline)
__all__.append('CanvasPolyline')

