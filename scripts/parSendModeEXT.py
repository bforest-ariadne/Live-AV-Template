op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment

TDF = op.TDModules.mod.TDFunctions  # utility functions
TDJ = op.TDModules.mod.TDJSON
parComMod = mod('/scripts/parComMOD')


class ParSendModeExtension():
    def __init__(self, my_op):
        self.com = op('/IO/base_com')
        print('parSendModeExtension')

        return

    def sendApplyParVals(self, pageName='Settings'):
        parDict = parComMod.pageToDict(self.Me, pageName, [])

        msg = {
            'messagekind'	: "ApplyParVals",
            'target'		: op.Com.Hostname,
            'sender'		: op.Com.Hostname,
            'output'		: None,
            'parameter'		: None,
            'value'			: {
                            "parDict"	: parDict,
                            "target": self.name+'1'
            }
        }
        # if self.Me.fetch('Uipars'):
            # self.print('send applyParVals')
        self.com.Send_msg(msg)
        return

    def sendApplyPars(self, pageIndex=0):
        pageDict = TDJ.pageToJSONDict(self.Me.customPages[pageIndex], ['val', 'order'])
        pars = self.Me.customPages[pageIndex].pars
        parOrder = []
        for par in pars:
            parOrder.append(par.tupletName)

        msg = {
            'messagekind'	: "ApplyPars",
            'target'		: op.Com.Hostname,
            'sender'		: op.Com.Hostname,
            'output'		: None,
            'parameter'		: None,
            'value'			: {
                            'pageDict': pageDict,
                            "target": self.name+'1',
                            'parOrder': parOrder,
            }
        }
        # if self.Me.fetch('Ui'):
            # self.print('SentApplyPars')
        self.com.Send_msg(msg)
        return