# -*- coding:utf-8 -*- 

from hashlib import sha256
x = 5
y = 0  # y未知
while sha256(f'{x*y}'.encode()).hexdigest()[-1] != "":
    y += 1
print(f'The solution is y = {y}')