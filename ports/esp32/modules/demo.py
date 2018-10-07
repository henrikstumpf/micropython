import network

from webthing.thing import Thing
from webthing.property import Property
from webthing.value import Value
#from webthing.server import SingleThing, WebThingServer

def connect(ssid="WLAN-Henrik", key="k1rneH:)"):
    sta = network.WLAN(network.STA_IF)
    sta.active(True)
    sta.connect(ssid, key)

def httpHandler(httpClient, httpResponse, routeArgs=None):
    print("http Handler")

handlers = [("/test", "GET", httpHandler),]

class DemoLight(Thing):
    def __init__(self, name):
        Thing.__init__(self, name, "OnOffSwitch", "a simple light")
        self.on = False
        self.add_property(Property(self, 'on', Value(self.on, self.setOnOff)))
    def setOnOff(self, onOff):
        self.on = onOff
    def __repr__(self):
        return "an" if self.on else "aus"

light = DemoLight('light')
#srv = WebThingServer(SingleThing(light))
