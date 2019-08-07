op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment
PreShowExtension = mod('preShowEXT').PreShowExtension

class CalibrateExtension(PreShowExtension):

    def __init__(self, my_op):
        super().__init__(my_op)
        self.Keys = {
            '0' : {'u': 0, 'v' : 0},
            '1' : {'u': 0, 'v' : 0},
            '2' : {'u': 0, 'v' : 0},
            '3' : {'u': 0, 'v' : 0}
        }
        self.xy1keyOffset = self.Me.op('widget_keyControl/slider2D_keyOffset1')
        self.keyDat = self.Me.op('calibration/keyOffset')

        # self.xy1keyControl = self.Me.op('widget_keyControl/slider2D_keyControl1')

        return

    def Test(self):
        super().Test()
        self.print('test extension Calibreate Class')
        return

    def onStonerKeyChange(self, dat, cells, prev):
        # print( dat['0','u'], dat['0', 'v'])
        self.xy1keyOffset.par.Value0 = dat['0','u']
        self.xy1keyOffset.par.Value1 = dat['0','v']
        return

    def OnsliderChange(self, channel, val ):
        self.keyDat[ tdu.digits(channel.name), channel.name[-1:] ] = val