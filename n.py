def func(x, y, a):
    return (5 * y - x > a) or not (2 * x + 3 * y < 90) or not (y - 2 * x < -50)


c = 0
for a in range(1, 1000):

    flag = 0
    for x in range(1, 1000):
        for y in range(1, 1000):
            if not func(x, y, a):
                flag = 1
    if flag == 0:
        c += 1
        print(a, end=' ')
print()

print(c)