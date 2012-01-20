'''
Created on 19.01.2012

@author: gena
'''

class LtObject(object):
    '''
    This class holds all properties of detected video object
    central point, contour, edges, etc 
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
        self.maxBright = None # 
        self.massCenter = None    # 
        self.contour = None  # 
        
        