import sys

x = sys.argv[1]
with open('temp.txt', 'w') as f:
    f.write(x)
