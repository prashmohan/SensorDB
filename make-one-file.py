#!/usr/bin/env python
"""
Summary:

Author:  prashmohan@gmail.com
         http://www.cs.berkeley.edu/~prmohan
        
License: Licensed under the CRAPL non-license -
         http://matt.might.net/articles/crapl/CRAPL-LICENSE.txt
         
         This code is provided "as-is" and is available for
         modification. If you have any questions do mail
         me.  I will _try_ to get back to you as soon as possible.
"""

import sys
import os
import string

def make_one_file(file_names):
    for file_name in open(file_names, 'r'):
        for line in open(file_name.strip(), 'r'):
            print os.path.basename(file_name.strip()) + ',', ', '.join(map(string.strip, line.split(',')))

if __name__ == '__main__':
    make_one_file(sys.argv[1])
