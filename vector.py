class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    @classmethod
    def frompair(cls, a):
        return Vector(a[0], a[1])

    def add(self, vector):
        return Vector(self.x + vector.x, self.y + vector.y)

    def in_rect(self, rect):
        return rect.top_left._above_and_left_of(self) \
           and self._above_and_left_of(rect.bottom_right)

    def to_pair(self):
        return [self.x, self.y]

    def _above_and_left_of(self, vector):
        return self.x <= vector.x and self.y <= vector.y

    def __repr__(self):
        return '(%d, %d)' % (self.x, self.y)

class Rect:
    def __init__(self, top_left, bottom_right):
        self.top_left = top_left
        self.bottom_right = bottom_right

    def in_rect(self, rect):
        return self.top_left.in_rect(rect) and self.bottom_right.in_rect(rect)

    def move(self, v):
        return Rect(self.top_left.add(v), self.bottom_right.add(v))

    def intersects(self, r):
        return self.top_left._above_and_left_of(r.bottom_right) and \
               r.top_left._above_and_left_of(self.bottom_right)

    def __repr__(self):
        return 'Rect: %s, %s' % (self.top_left, self.bottom_right)
