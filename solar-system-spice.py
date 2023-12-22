import spiceypy as sp
import datetime
import numpy as np
import matplotlib.pyplot as plt

# Animation settings
#  Animation starts at start_time [year, month, day, hour, minute, second]
#  One time-step elapses dt [s] time
#  The last path_length positions are also preserved and displayed
start_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
dt = 5e4
path_length = 500

# Load kernels
sp.furnsh("./kernels/naif0012.tls")
sp.furnsh("./kernels/de432s.bsp")

# Prepare variables
#   Obtain start time
time = start_time
time_utc = time.strftime("%Y-%m-%dT00:00:00")
time_et = sp.utc2et(time_utc)

#   Obtain starting position of Earth
state, _ = sp.spkgeo(
    targ=399,
    et=time_et,
    ref="ECLIPJ2000",
    obs=10
)
x_planet = np.array((state[0],)*path_length)
y_planet = np.array((state[1],)*path_length)

#   Set position of Sun
x_star = 0
y_star = 0


# Handle program closing
running = True


def on_close(event):
    global running

    event.canvas.figure.axes[0].has_been_closed = True
    running = False


# Prepare display
figure = plt.figure("Planetary motion")
figure.canvas.mpl_connect("close_event", on_close)
axis = figure.add_subplot(1, 1, 1, aspect="equal")

#   Set axis limits
r = np.sqrt(x_planet[0]**2+y_planet[0]**2)
axis.set_xlim(-r*1.5, r*1.5)
axis.set_ylim(-r*1.5, r*1.5)

# Display initial position
p_planet = axis.plot(
    x_planet, y_planet,
    color="blue"
)[0]
star = axis.plot(
    x_star, y_star,
    color="orange",
    marker="o", markersize="15"
)[0]
planet = axis.plot(
    x_planet[-1], y_planet[-1],
    color="blue",
    marker="o", markersize="5"
)[0]
date = axis.text(0, -r*1.3, time, ha="center", va="center")
#plt.show()

# Run animation
while running:
    # Calculate time point
    time += datetime.timedelta(seconds=dt)
    time_utc = time.strftime("%Y-%m-%dT00:00:00")
    time_et = sp.utc2et(time_utc)
    date.set_text(f"UTC {time_utc}")

    # Prepare variables
    x_planet = np.roll(x_planet, -1)
    y_planet = np.roll(y_planet, -1)

    # Obtain planet position
    state, _ = sp.spkgeo(
        targ=399,
        et=time_et,
        ref="ECLIPJ2000",
        obs=10
    )

    x_planet[-1] = state[0]
    y_planet[-1] = state[1]
    p_planet.set_data(x_planet, y_planet)
    planet.set_data((x_planet[-1],), (y_planet[-1],))

    plt.pause(0.001)
