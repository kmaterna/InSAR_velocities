#!/usr/bin/python

import sys
import numpy as np

infile = sys.argv[1]
outfile = sys.argv[2]

f = open(infile, 'r')
content = [[t for t in line.split()] for line in f.readlines()[:]]
f2 = open(outfile, 'w')

for i in range(len(content)):
    f2.write('>\n' + content[i][2] + ' 10' + '\n')
    f2.write(content[i][2] + ' -10' + '\n')

f2.close()
