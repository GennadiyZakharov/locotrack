'''
Created on 19.01.2012
@author: gena
'''

class LtObject(object):
    '''
    This class holds all properties of detected video object
    central point, contour, edges, etc 
    '''
    def __init__(self, center, contour=None):
        '''
        Constructor
        ''' 
        self.center = center      # Mass center of objects 
        self.contour = contour  # Objects contour, if present
        
    def intCenter(self):
        return int(self.center[0]),int(self.center[1])
        