import os

os.system('pip freeze > requirements.txt')
f = open('requirements.txt', 'r')
lines = f.readlines()
f.close()
f = open('requirements.txt', 'w')
for line in lines:
    if '@' not in line:
        f.write(line)
f.close()
