import dht
import machine
import onewire
import time
import uuid

from webthing.action import Action
from webthing.thing import Thing
from webthing.property import Property
from webthing.value import Value


class DS18B20(Thing):
    def __init__(self, name, bus, idx):
        Thing.__init__(self, name, "MultiLevelSensor", "1-wire temperature sensor")
        self._bus = bus
        self._rom = bus.scan()[idx]
        self._level = self._read()
        self.add_property(
            Property(
                self,
                'level',
                Value(self._level, self.read),
                metadata={
                    '@type': 'LevelProperty',
                    'label': 'Temperature',
                    'type': 'number',
                }))

    def _read(self):
        self._bus.convert_temp()
        time.sleep_ms(750)
        return self._bus.read_temp(self._rom)

    def update(self):
        self._level = self._read()


class DHT22(Thing):
    def __init__(self, name, pin):
        Thing.__init__(self, name, "MultiLevelSensor", "dht22 temperature and humidity sensor")
        self._rom = dht.DHT22(machine.Pin(pin))
        self._temp = self._read_temp()
        self._hum = self._read_hum()
        self.add_property(
            Property(
                self,
                'temp',
                Value(self._temp, self.update_temp),
                metadata={
                    '@type': 'LevelProperty',
                    'label': 'Temperature',
                    'type': 'number',
                }
            )
        )
        self.add_property(
            Property(
                self,
                'hum',
                Value(self._hum, self.update_hum),
                metadata={
                    '@type': 'LevelProperty',
                    'label': 'Temperature',
                    'type': 'number',
                }
            )
        )

    def _read_temp(self):
        self._rom.measure()
        return self._rom.temperature()

    def _read_hum(self):
        self._rom.measure()
        return self._rom.humidity()

    def update_temp(self):
        self._temp = self._read_temp()

    def update_hum(self):
        self._hum = self._read_hum()


class ToggleAction(Action):
    def __init__(self, thing):
        Action.__init__(self, uuid.uuid4().hex, thing, 'toggle')

    def perform_action(self):
        if thing.is_on():
            thing.setOnOff(False)
        else:
            thing.setOnOff(True)


class DimmableLight(Thing):
    def __init__(self, name, pwm):
        Ting.__init__(self, name, ['Light', 'OnOffSwitch', 'MultiLevelSwitch'], 'a dimmable light')
        self._light = machine.PWM(machine.Pin(pwm))
        self.on = self.is_on()
        self.brightness = self.get_brightness()
        self.add_property(
            Property(
                self,
                'on',
                Value(self.on, self.setOnOff),
                metadata = {
                    '@type': 'OnOffProperty',
                    'label': 'On/Off State',
                    'type': 'boolean',
                }
            )
        )
        self.add_property(
            Property(
                self,
                'brightness',
                Value(self.brightness, self.setBrightness),
                metadata = {
                    '@type': 'BrightnessProperty',
                    'label': 'brightness level',
                    'type': 'number',
                    'minimum': 0,
                    'maximum': 100,
                    'unit': 'percent'
                }
            )
        )
        self.add_available_action(
            'toggle',
            {
                'label': 'Toggle',
                'description': 'toggle the switch',
            },
            ToggleAction
        )

    def is_on(self):
        return self._light.value()

    def get_brightness(self):
        return round((self._light.duty()/1023)*100)

    def setOnOff(self, onOff):
        self.on = onOff
        self.brightness = 100 if onOff else 0
        self.update()

    def setBrightness(self, level):
        self.on = bool(level)
        self.brightness = level
        self.update()

    def update(self):
        lvl = round((self.brightness/100) * 1023)
        self._light.duty(lvl)
