op = op  # pylint:disable=invalid-name,used-before-assignment
root = root  # pylint:disable=invalid-name,used-before-assignment
PreShowExtension = mod('preShowEXT').PreShowExtension

class CalibrateExtension(PreShowExtension):

    def __init__(self, my_op):
        super().__init__(my_op)

        return

    def Test(self):
        super().Test()
        self.print('test extension Calibreate Class')
        return

