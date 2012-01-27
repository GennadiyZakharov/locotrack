'''
Created on 19.01.2012

@author: gena
'''

class LtObject(object):
    '''
    This class holds all properties of detected video object
    central point, contour, edges, etc 
    '''
    def __init__(self, centralPoint=None):
        '''
        Constructor
        '''
        self.maxBright = None # 
        self.massCenter = centralPoint    # 
        self.contours = None  # 
        
    def centralPoint(self):
        return self.massCenter
        
        