op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment
TDJ = op.TDModules.mod.TDJSON

class PresetEXT():

    def __init__(self, my_op):
        self.Me = my_op
        self.name = my_op.name
        self.parent = self.Me.parent()
        self.SceneName = self.parent.name
        self.Me.par.Scenename = self.SceneName
        self.task = 'Empty'
        self.parDifOp = self.Me.op('parDif')
        self.presetDict = {}

        self.print('init')
        self.Dev()
        self.createMidiConstant()
        return

    def createMidiConstant(self):
        self.print('createMidiConstant')
        children = self.parent.findChildren(name='midi', type=constantCHOP)
        if children == []:
            print('create midi')
            self.Midi = self.parent.create(constantCHOP, 'midi')
            # self.Midi.nodeX = self.Me.nodeX
            # self.Midi.nodeY = self.Me.nodeY - self.Me.nodeHeight - 20
            self.placeNodeUnder(self.Me, self.Midi)
            self.parent.par.iopshortcut2 = 'midi'
            self.parent.par.iop2 = self.Midi.path
        elif len(children) == 1:
            self.Midi = children[0]
        return

    def placeNodeUnder(self, refOp, targetOp):
            targetOp.nodeX = refOp.nodeX
            targetOp.nodeY = refOp.nodeY - refOp.nodeHeight - 20

    def Checkpardifs(self):
        self.task = 'FinishCheckParDifs'
        self.Me.op('datexec_allScene').par.active = True
        self.Me.op('parameter_allScene').bypass = False

        return

    def FinishCheckParDifs(self):
        self.print('FinishCheckParDifs')
        self.task = 'Empty'
        self.Me.op('script_findDif').par.Compare.pulse()
        
        return

    def Setinitialstate(self):
        self.task = 'FinishSetInitialState'
        self.Me.op('datexec_allScene').par.active = True
        self.Me.op('parameter_allScene').bypass = False

        return
    
    def FinishSetInitialState(self):
        self.print('FinishSetInitialState')
        self.task = 'Empty'
        
        self.initialState = self.Me.op('state0')
        self.currentState = self.Me.op('currentParState')

        self.initialState.clear()
        self.initialState.copy(self.currentState)
        return
    
    def OnAllSceneParsChange(self):
        self.Me.op('allScenePars').clear()
        self.Me.op('allScenePars').copy( self.Me.op('parameter_allScene') )
        self.Me.op('parameter_allScene').bypass = True
        self.Me.op('datexec_allScene').par.active = False

        self.callback({'operator': self, 'method': self.task})
        return

    
    def Generatecontrols(self, index=0):
        self.print('Generatecontrols')

        self.presetDict[str(index)] = {}

        nameIndex = self.parDifOp.findCells('name')[0].col
        evalIndex = self.parDifOp.findCells('eval')[0].col
        preEvalIndex = self.parDifOp.findCells('prevEval')[0].col
        defaultIndex = self.parDifOp.findCells('default')[0].col
        
        for i, row in enumerate(self.parDifOp.rows()):

            if i == 0:
                continue

            # test only on row 1
            # if i != 1:
            #     continue

            targetName = row[nameIndex].val
            targetPar = targetName.split(':')[1]
            targetOpPath = targetName.split(':')[0]
            targetOp = op(targetOpPath)
            rangeMax = row[evalIndex].val
            rangeMin = row[preEvalIndex] if row[preEvalIndex].val != '' else row[defaultIndex].val

            
            self.presetDict[str(index)][targetName] = {
                'par': targetPar,
                'op': targetOp,
                'rangeMax': rangeMax,
                'rangeMin': rangeMin,
                'parDictIndex': i
            }
            targetDict = self.presetDict[str(index)][targetName]

            midiSelect = targetOp.parent().loadTox( root.var('TOUCH') + '/components/midiSelect.tox')
            midiSelect.name = 'midiSelect{}_{}'.format(index, i)
            targetDict['midiSelect'] = midiSelect
            self.placeNodeUnder( targetOp, midiSelect )
            midiSelect.par.Index = index
            midiSelect.par.Torange1.val = float(rangeMin)
            midiSelect.par.Torange2.val = float(rangeMax)

            # export null to target parameter
            # set select channel rename to 'op:par'
            midiSelect.op('select2').par.renameto = targetName.split(targetOp.parent().path + '/')[1]
            
            # turn export mode on target par
            targetOp.pars(targetPar)[0].mode = ParMode.EXPORT
            
            tagName =  'preset{}'.format(index)
            midiSelectIndex = -1
            midiSelectParent = None
            if tagName in targetOp.tags:
                #  itterate through our preset index dict
                for k, v in self.presetDict[str(index)].items():
                    # if not our own targetName
                    if k != targetName:
                        #  itterate through each targetName dict to find the highest index
                        for tKey, tValue in  self.presetDict[str(index)][k].items():
                            if tKey == 'parDictIndex':
                                if tValue > midiSelectIndex:
                                    midiSelectIndex = tValue
                        for tKey, tValue in  self.presetDict[str(index)][k].items():
                            if tKey == 'parDictIndex':
                                if tValue == midiSelectIndex:
                                    midiSelectParent = self.presetDict[str(index)][k]['midiSelect']

                if midiSelectParent is not None:
                    self.placeNodeUnder( midiSelectParent, midiSelect )
            else:
                targetOp.tags.add( 'preset{}'.format(index) )
        return

    def Removepreset(self, index=0):

        for k, v in self.presetDict[str(index)].items():
            for tKey, tValue in self.presetDict[str(index)][k].items():
                if tKey == 'midiSelect':
                    tValue.destroy()
                if tKey == 'op':
                    if 'preset{}'.format(index) in tValue.tags:
                        tValue.tags.remove('preset{}'.format(index))
        
        self.presetDict[str(index)] = {}

        return


    def Empty(self):
        self.print('empth task')
        return


    def Dev(self):
        if self.Me.fetch('Dev'):
            self.print('dev mode on')
            self.CreateMidiConstant = self.createMidiConstant
            self.PresetDict = self.presetDict
        else:
            self.print('dev mode off')
        return

    def Test(self):
        self.print('test extension')
        return

    def OnPulse(self, par):
        if hasattr(self.Me, par.name):
            function = getattr(self.Me, par.name)
            if callable(function):
                function()

        return

    def OnValueChange(self, par):
        self.Me.store(par.name, par.eval())
        if hasattr(self.Me, par.name):
            function = getattr(self.Me, par.name)
            if callable(function):
                function()

        return

    def print(self, message):
        print(self.name + ': ', message)
        return

    def callback(self, config):
        if config['operator'] and config['method']:
            if hasattr(config['operator'], config['method']):
                function = getattr(config['operator'], config['method'])
                if callable(function):
                    function()
            else:
                self.print('callback no fire')
                self.print('operator: ' + config['operator'])
                self.print('method: ' + config['method'])
        return
