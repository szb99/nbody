import datetime
import spice as sp
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Animation settings
#  Simulation starts at start_time [year, month, day, hour, minute, second]
#  One time-step elapses dt [s] time
#  The last path_length positions are also preserved and displayed
start_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
dt = 1e6
path_length = 1000
targets = [
    {
        "id": 10,
        "name": "Sun",
        "color": "orange",
        "marker scale": 200,
        "path scale": 200
    },
    {
        "id": 5,
        "name": "Jupiter",
        "color": "blue",
        "marker scale": 500,
        "path scale": 1
    },
    # {
    #     "id": 6,
    #     "name": "Saturn",
    #     "color": "green",
    #     "marker scale": 1500,
    #     "path scale": 1
    # },
    # {
    #     "id": 7,
    #     "name": "Uranus",
    #     "color": "brown",
    #     "marker scale": 1500,
    #     "path scale": 1
    # },
    # {
    #     "id": 8,
    #     "name": "Neptune",
    #     "color": "brown",
    #     "marker scale": 1500,
    #     "path scale": 1
    # }
]

# Load kernels
sp.furnsh("./kernels/naif0012.tls")
sp.furnsh("./kernels/de432s.bsp")
sp.furnsh("./kernels/pck00010.tpc")

# Prepare SPICE
sp.set_observer(0)

# Prepare variables
time = start_time

# Obtain starting positions and parameters
r = np.empty((0, path_length, 3))
radii = []
for target in targets:
    position = sp.position(target["id"], time)
    r = np.append(
        r,
        np.repeat(
            position[None, None, :],
            path_length, axis=1
        ),
        axis=0
    )

    radius = sp.radius(target["id"])
    radii.append(radius)

# Prepare display
figure = plt.figure("Sun movement")
axis = figure.add_subplot(1, 1, 1, aspect="equal")

#   Set axis limits
distance = max(
    np.linalg.norm(r[i, 0, :]) * targets[i]["path scale"]
    for i in range(len(targets))
)
axis.set_xlim(-distance * 1.5, distance * 1.5)
axis.set_ylim(-distance * 1.5, distance * 1.5)

#   Display initial position
paths = []
objects = []
for i in range(len(targets)):
    paths.append(axis.plot(
        r[i, :, 0] * targets[i]["path scale"],
        r[i, :, 1] * targets[i]["path scale"],
        color=targets[i]["color"],
        label=targets[i]["name"]
    )[0])
    objects.append(axis.add_patch(plt.Circle(
        (
            r[i, 0, 0] * targets[i]["path scale"],
            r[i, 0, 1] * targets[i]["path scale"]
        ),
        radii[i] * targets[i]["marker scale"],
        color=targets[i]["color"],
        alpha=0.5
    )))
center = axis.plot(0, 0, marker="+", color="black")
date = axis.text(
    0, -distance * 1.3,
    sp.dt2utc(time),
    ha="center", va="center"
)
axis.legend(bbox_to_anchor=(1, 0.5), loc="center left")
#plt.show()


def step(frame):
    global time, r

    r = np.roll(r, 1, axis=1)

    for i in range(len(targets)):
        position = sp.position(targets[i]["id"], time)
        r[i, 0, :] = position

    for i in range(len(targets)):
        paths[i].set_data(
            r[i, :, 0] * targets[i]["path scale"],
            r[i, :, 1] * targets[i]["path scale"]
        )
        objects[i].set_center((
            r[i, 0, 0] * targets[i]["path scale"],
            r[i, 0, 1] * targets[i]["path scale"]
        ))
    date.set_text(sp.dt2utc(time))

    time += datetime.timedelta(seconds=dt)


animation = FuncAnimation(figure, step, frames=100, interval=50)
plt.show()
