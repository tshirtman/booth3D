'''
Panda Wrapper
=============

Minimalist wrapper around showbase, that ensure the good initialisation of Panda
and create custom lighting.
'''

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    AmbientLight,
    AntialiasAttrib,
    DirectionalLight,
    LightAttrib,
    loadPrcFileData,
    Vec3,
    Vec4
)

from pandanode import Node

# they are still issues when clearning the window, so don't report error
# or panda will stop working
#loadPrcFileData('', 'gl-force-no-error 1')

# force the usage of our special GL host display
loadPrcFileData('', 'load-display glhdisplay')

# we have a possibility to do supersampling ourself
# by rendering to a bigger size, and reduce it afterwise.
# but the antialiasing could be also done in shader
#loadPrcFileData('', 'win-size 1600 1200')

# deactivate that if you want to have more output about panda internals
#loadPrcFileData('', 'gl-debug true')
#loadPrcFileData('', 'notify-level spam')
#loadPrcFileData('', 'notify-level-ShowBase debug')
#loadPrcFileData('', 'default-directnotify-level debug')

class ModelShowbase(ShowBase):
    def __init__(self):
        # we must ensure that gl is ok before starting showbase initialization
        import kivy.core.gl
        loadPrcFileData('', 'win-size 800 1080')  # Up to us... at init time only.
        ShowBase.__init__(self)
        self.setup_lights()

    def setup_lights(self):
        render = self.render
        ambientLight = AmbientLight('ambient')
        ambientLight.setColor(Vec4(.5, .5, .5, 1))
        render.setLight(render.attachNewNode(ambientLight))

        directionalLight = DirectionalLight('directional')
        directionalLight.setDirection(Vec3(10, 10, -10))
        directionalLight.setColor(Vec4(.75, .6, .6, 1))
        directionalLight.setSpecularColor(directionalLight.getColor())
        render.setLight(render.attachNewNode(directionalLight))

        skyLight = DirectionalLight('sky')
        skyLight.setDirection(Vec3(-25, 10, -25))
        skyLight.setColor(Vec4(.25, .25, .5, 1))
        skyLight.setSpecularColor(skyLight.getColor())
        render.setLight(render.attachNewNode(skyLight))

    def load_model(self, filename):
        model = self.loader.loadModel(filename)
        model.reparentTo(self.render)
        return Node(node=model)

    def unload_model(self, node):
        return self.loader.unloadModel(node.node)

    def setupMouse(*largs):
        # needed, otherwise panda will break because of glh provider that
        # doesn't include mouse support
        pass
