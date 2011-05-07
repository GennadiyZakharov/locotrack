'''
Created on 27.04.2011

@author: Gena
'''

class LtTrajectory(object):
    '''
    classdocs
    '''


    def __init__(self,startframe=0):
        '''
        Constructor
        '''
        self.trajectory=[]
        self.startframe=startframe
        
    def getLast(self, count=20):
        return self.trajectory[-count:]
    
    def setItem(self, pos, item):
        while len(self.trajectory) =< pos :
            self.trajectory.append(None)
        self.trajectory[pos]=item
   
   
   def __delitem__(self, ii):
        """Delete an item"""
        del self.list[ii]    # Thank you @Thomas for the pointer about .remove()
        return
    
         
'''
class HostList(collections.MutableSequence):
    """A container for manipulating lists of hosts"""
    def __init__(self):
        """Initialize the class"""
        self.list = list()
    >>> import HostList as H
>>> foo = H.HostList()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: Can't instantiate abstract class HostList with abstract methods __delitem__
>>> 

'''