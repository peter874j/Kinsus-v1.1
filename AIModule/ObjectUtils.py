from dataclasses import dataclass
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

@dataclass
class Point2D:
    x: int
    y: int


class YoloBBox:
    def __init__(self, zoneName, startPoint, endPoint, centerPoint):
        self.zoneName = zoneName
        self.startPoint = startPoint
        self.endPoint = endPoint
        self.centerPoint = centerPoint

    @classmethod
    def get_from_list(cls, zoneName, startPointX, startPointY, endPointX, endPointY):
        centerPointX = int((startPointX + endPointX)/2)
        centerPointY = int((startPointY + endPointY)/2)
        return cls(zoneName, Point2D(startPointX, startPointY), Point2D(endPointX, endPointY), Point2D(centerPointX, centerPointY))

class BBox:

    def __init__(self, zoneName, pointOfTopLeft, pointOfTopRight, pointOfBottomLeft, pointOfBottomRight):
        self.zoneName = zoneName
        self.pointOfTopLeft = pointOfTopLeft
        self.pointOfTopRight = pointOfTopRight
        self.pointOfBottomLeft = pointOfBottomLeft
        self.pointOfBottomRight = pointOfBottomRight
        
    @classmethod
    def get_from_list(cls, zoneName, pointOfTopLeft_X, pointOfTopLeft_Y, pointOfTopRight_X, pointOfTopRight_Y, pointOfBottomLeft_X,
                            pointOfBottomLeft_Y, pointOfBottomRight_X, pointOfBottomRight_Y):

        return cls(zoneName, Point2D(pointOfTopLeft_X, pointOfTopLeft_Y), Point2D(pointOfTopRight_X, pointOfTopRight_Y), 
                                Point2D(pointOfBottomLeft_X, pointOfBottomLeft_Y), Point2D(pointOfBottomRight_X, pointOfBottomRight_Y))

    def contains_point(self, point):
        yoloCenterPoint = Point(point.x, point.y)
        polygon = Polygon([(self.pointOfTopLeft.x, self.pointOfTopLeft.y), (self.pointOfTopRight.x, self.pointOfTopRight.y),
                             (self.pointOfBottomLeft.x, self.pointOfBottomLeft.y), (self.pointOfBottomRight.x, self.pointOfBottomRight.y)])
        return polygon.contains(yoloCenterPoint)

class Zone:
    A = "Placement"
    B = "Jig"
    C = "Work_Rack"
    D = "Finish"

class Label:
    type1 = "no_PCB"
    type2 = "PCB_frame"
    type3 = "frame"
    order = [type1, type2, type3, type2, type1]

    def __init__(self, previous, current):
        self.previous = previous
        self.current = current

    @classmethod
    def initialize(cls):
        return cls(cls.type1, cls.type1)

    def is_not_same_label(self, step):
        if self.previous == step.previousLabel and self.current == step.currentLabel:
            return "NO"
        else:
            return "YES"  

    def get_Jig_label(self, yoloResult, allRectangleInfo):
        if len(yoloResult["coordinate"]) == 1:
            if allRectangleInfo[1].contains_point(yoloResult["coordinate"][0].centerPoint): ##########要改 1
                return yoloResult["label"][0]
        return None
    
    def update_info(self, yoloResult, allRectangleInfo):
        self.previous = self.current
        jigCurrentLabel = self.get_Jig_label(yoloResult, allRectangleInfo)
        self.current = jigCurrentLabel if jigCurrentLabel is not None else self.current

class Step:
    def __init__(self, number, label):
        self.number = number
        self.previousLabel = label.previous
        self.currentLabel = label.current

    @classmethod
    def initialize(cls):
        return cls(0, Label.initialize())

    def update_info(self):
        self.number += 1 
        self.previousLabel = Label.order[self.number-1]
        self.currentLabel = Label.order[self.number]

    @staticmethod
    def goto_next(jigLabel):
        if not jigLabel.previous == jigLabel.current:
            return True

