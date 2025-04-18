from __future__ import print_function

import time

from six.moves import range

def twiddle(evaluator, tol=0.001, params=3, error_cmp=None, initial_guess=None):
    """
    A coordinate descent parameter tuning algorithm.
    
    https://en.wikipedia.org/wiki/Coordinate_descent
    
    Params:
    
        evaluator := callable that will be passed a series of number parameters, which will return
            an error measure
            
        tol := tolerance threshold, the smaller the value, the greater the tuning
        
        params := the number of parameters to tune
        
        error_cmp := a callable that takes two error measures (the current and last best)
            and returns true if the first is less than the second
            
        initial_guess := parameters to begin tuning with
    """

    def _error_cmp(a, b):
        # Returns true if a is closer to zero than b.
        return abs(a) < abs(b)
        
    if error_cmp is None:
        error_cmp = _error_cmp

    if initial_guess is None:
        p = [0]*params
    else:
        p = list(initial_guess)
    dp = [1]*params
    best_err = evaluator(*p)
    steps = 0
    while sum(dp) > tol:
        steps += 1
        print('steps:', steps, 'tol:', tol, 'best error:', best_err)
        for i in range(len(p)):
            
            # first try to increase param
            p[i] += dp[i]
            err = evaluator(*p)
            
            if error_cmp(err, best_err):
                # Increasing param reduced error, so record and continue to increase dp range.
                best_err = err
                dp[i] *= 1.1
            else:
                # Otherwise, increased error, so undo and try decreasing dp
                p[i] -= 2.*dp[i]
                err = evaluator(*p)
                
                if error_cmp(err, best_err):
                    # Decreasing param reduced error, so record and continue to increase dp range.
                    best_err = err
                    dp[i] *= 1.1
                    
                else:
                    # Otherwise, reset param and reduce dp range.
                    p[i] += dp[i]
                    dp[i] *= 0.9
                
    return p

class PID(object):
    """
    Simple PID control.
    """
    
    def __init__(self, p=0, i=0, d=0, **kwargs):
        
        self._get_time = kwargs.pop('get_time', None) or time.time
        
        # initialze gains
        self.Kp = p
        self.Ki = i
        self.Kd = d
        
        # The value the controller is trying to get the system to achieve.
        self._target = 0
        
        # initialize delta t variables
        self._prev_tm = self._get_time()
        
        self._prev_feedback = 0
        
        self._error = None

    @property
    def error(self):
        return self._error

    @property
    def target(self):
        return self._target
        
    @target.setter
    def target(self, v):
        self._target = float(v)

    def __call__(self, feedback, curr_tm=None):
        """ Performs a PID computation and returns a control value.
        
            This is based on the elapsed time (dt) and the current value of the process variable 
            (i.e. the thing we're measuring and trying to change).
            
        """
        
        # Calculate error.
        error = self._error = self._target - feedback
        
        # Calculate time differential.
        if curr_tm is None:
            curr_tm = self._get_time()
        dt = curr_tm - self._prev_tm
        
        # Initialize output variable.
        alpha = 0
        
        # Add proportional component.
        alpha -= self.Kp * error
        
        # Add integral component.
        alpha -= self.Ki * (error * dt)
        
        # Add differential component (avoiding divide-by-zero).
        if dt > 0:
            alpha -= self.Kd * ((feedback - self._prev_feedback) / float(dt))
        
        # Maintain memory for next loop.
        self._prev_tm = curr_tm
        self._prev_feedback = feedback

        return alpha
