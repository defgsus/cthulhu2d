

def print_curve(func, range=(0, 1), steps=50, file=None):
    import numpy as np
    x_values = np.linspace(range[0], range[1], steps)

    min_v = min(func(x) for x in x_values)
    max_v = max(func(x) for x in x_values)

    for x in x_values:
        v = func(x)
        width = int((v - min_v) / (max_v - min_v) * 60)
        print(f"{round(x, 3):5} {round(v, 5):8} {' ' * width}#", file=file)
