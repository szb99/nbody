import datetime
import numpy as np

import simulation as sm
import spice as sp
import plot as pl

start = datetime.datetime(2000, 1, 1, 0, 0, 0)
dt = 1e3
n = int(3e3)
path_length = 1000
limit_scale = 1.5
video_path = "trajectories.avi"

targets = [
    {
        "id": 10,
        "name": "Sun",
        "spice color": "orange",
        "sim color": "red",
        "marker scale": 300,
        "path scale": 300,
        "display": True
    },
    {
        "id": 5,
        "name": "Jupiter",
        "spice color": "blue",
        "sim color": "purple",
        "marker scale": 500,
        "path scale": 1,
        "display": True
    },
    {
        "id": 6,
        "name": "Saturn",
        "spice color": "green",
        "sim color": "teal",
        "marker scale": 500,
        "path scale": 1,
        "display": True
    },
    # {
    #     "id": 7,
    #     "name": "Uranus",
    #     "spice color": "brown",
    #     "sim color": "black",
    #     "marker scale": 2000,
    #     "path scale": 1,
    #     "display": True
    # },
    # {
    #     "id": 8,
    #     "name": "Neptune",
    #     "spice color": "red",
    #     "sim color": "pink",
    #     "marker scale": 2000,
    #     "path scale": 1,
    #     "display": True
    # }
]

# Load kernels
sp.furnsh((
    "./kernels/naif0012.tls",
    "./kernels/de432s.bsp",
    "./kernels/pck00010.tpc",
    "./kernels/gm_de440.tpc"
))
sp.set_observer(0)

# Set up simulation and visualization
sim = sm.NBodySim(start)
spice = sp.NBodySpice(start)


# Step function for animation
def step():
    global dt, n

    sim.step(dt, n)
    spice.step(dt*n)

    return np.append(
        sim.position,
        spice.position,
        axis=0
    )


# Set up animation
plot = pl.NBodyPlot(
    step=step,
    path_length=path_length,
    limit_scale=limit_scale
)

# Set up SPICE targets
for target in targets:
    if target["display"]:
        spice.add(
            id=target["id"]
        )

        plot.add(
            label=target["name"]+" (SPICE)",
            color=target["spice color"],
            path_scale=target["path scale"],
            radius=sp.radius(target["id"]) * target["marker scale"]
        )

# Set up simulation targets
for target in targets:
    sim.add_naif(
        id=target["id"],
        display=target["display"]
    )

    if target["display"]:
        plot.add(
            label=target["name"]+" (SIM)",
            color=target["sim color"],
            path_scale=target["path scale"],
            radius=sp.radius(target["id"]) * target["marker scale"]
        )

# Run or save animation
#plot.run()
plot.save(video_path)
