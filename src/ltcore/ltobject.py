'''
Created on 19.01.2012

@author: gena
'''

class LtObject(object):
    '''
    This class holds all properties of detected video object
    central point, contour, edges, etc 
    '''
    def __init__(self, massCenter=None, maxBright=None, contours=None):
        '''
        Constructor
        '''
        self.maxBright = maxBright # 
        self.massCenter = massCenter    # 
        self.contours = contours  # 
    ''' 
    def massCenter(self):
        return self.massCenter
    ''' 
        