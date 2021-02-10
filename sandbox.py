from ImageProviders import BasicImageProvider
import matplotlib.pyplot as plt
import numpy as np

buffer = np.zeros((4, 8, 8))

# buffer[-1] = np.ones((8, 8))
# buffer[1] = np.ones((8, 8)) * 2
#
# print(buffer[3])

last_frame = np.ones((8, 8))
buffer = np.roll(buffer, -1, 0)
buffer[-1] = last_frame

last_frame = np.ones((8, 8)) * 2
buffer = np.roll(buffer, -1, 0)
buffer[-1] = last_frame

print(buffer)