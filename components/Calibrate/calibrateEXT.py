op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment
PreShowExtension = mod('preShowEXT').PreShowExtension
ParSendModeExtension = mod('parSendModeEXT').ParSendModeExtension


class CalibrateExtension(PreShowExtension, ParSendModeExtension):

    def __init__(self, my_op):
        PreShowExtension.__init__(self, my_op)
        ParSendModeExtension.__init__(self, my_op)
        self.sliderChange = False
        self.controlIPar = self.Me.op('widget_keyControl/iparLocal')
        self.keyDat = self.Me.op('calibration/keyOffset')
        self.keyChange = False

        return

    def Test(self):
        super().Test()
        self.print('test extension Calibreate Class')
        return
    def Reset(self):
        op('/Calibrate/stoner/settingsUI/reset/button1').click()
        return

    def onStonerKeyChange(self, dat, cells, prev):
        #  TODO fix glitchyness of key translation
        #  this is due to the two bound parameters
        if not self.sliderChange:
            self.keyChange = True
            for i in range(4):
                parNameU = 'Key{}1'.format(i)
                parNameV = 'Key{}2'.format(i)
                cellu = dat[ i + 1, 'u']
                cellv = dat[ i + 1, 'v']
                if cellu.val != '': 
                    self.controlIPar.pars(parNameU)[0].val = cellu
                else:
                    self.controlIPar.pars(parNameU)[0].val = 0.0
                if cellu.val != '':
                    self.controlIPar.pars(parNameV)[0].val = cellv
                else:
                    self.controlIPar.pars(parNameV)[0].val = 0.0
        self.keyChange = False
        return

    def OnsliderChange(self, channel, val ):
        if not self.keyChange:
            self.sliderChange = True
            self.keyDat[ tdu.digits(channel.name), channel.name[-1:] ] = val
        self.sliderChange = False

    def Showui(self):
        self.Me.op('widget_keyControl').openViewer()
        return

    def OnValueChange(self, par):
        super().OnValueChange(par)
        self.sendApplyParVals()
        return

    def OnParsChange(self):
        self.sendApplyPars()
        return