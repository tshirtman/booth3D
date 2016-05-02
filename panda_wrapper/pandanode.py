from panda3d.core import NodePath, Vec3

from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
    ReferenceListProperty
)


class Node(EventDispatcher):
    node = ObjectProperty(None)

    # Pos
    x = NumericProperty(0)
    y = NumericProperty(0)
    z = NumericProperty(0)
    pos = ReferenceListProperty(x, y, z)

    # Rot
    h = NumericProperty(0)
    p = NumericProperty(0)
    r = NumericProperty(0)
    hpr = ReferenceListProperty(h, p, r)

    def __init__(self, **kwargs):
        super(Node, self).__init__(**kwargs)
        trigger = Clock.create_trigger(self.update_node)
        self.bind(
            pos=trigger,
            hpr=trigger,
            node=trigger,
        )

    def update_node(self, *args):
        node = self.node
        if node:
            node.setPos(Vec3(*self.pos))
            node.setHpr(Vec3(*self.hpr))

    def remove_all_children(self):
        for child in self.node.getChildren():
            child.removeNode()

    def reparent_to(self, node):
        self.node.reparentTo(node.node)
