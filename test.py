WIDTH = 1920
p = 8
step = WIDTH // p


ranges = [(i * step, (i + 1) * step) for i in range(p)]

print(ranges)
