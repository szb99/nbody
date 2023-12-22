import datetime
import spiceypy as sp
import numpy as np
import matplotlib.pyplot as plt

# Simulation settings
#  Simulation starts at start_time [year, month, day, hour, minute, second]
#  One time-step elapses dt [s] time
#  Simulation is displayed after every nth time-step
#  The last path_length positions are also preserved and displayed
start_time = datetime.datetime(2000, 1, 1, 0, 0, 0)
dt = 1e2
n = 500
path_length = 500

# Set physical constants
gamma = 6.67e-11
m_star = 1.9885e30
m_planet = 5.9722e24

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
r_planet = np.array((
    state[0],
    state[1],
    state[2]
))*1000
v_planet = np.array((
    state[3],
    state[4],
    state[5]
))*1000
r_star = np.array((0.0, 0.0, 0.0))
v_star = np.array((0.0, 0.0, 0.0))

x_spice = np.array((r_planet[0],)*path_length)
y_spice = np.array((r_planet[1],)*path_length)
x_sim = np.array((r_planet[0],)*path_length)
y_sim = np.array((r_planet[1],)*path_length)


# Calculating next time-step
def step(dt=5e4):
    global r_star, v_star, r_planet, v_planet

    # Calculating gravitational forces
    r = r_planet-r_star
    f = -gamma*m_star*m_planet/(np.linalg.norm(r))**3*r

    # Calculating new positions
    #   Sun
    a_star = -f/m_star
    r_star += v_star*dt-1/2*a_star*dt**2
    v_star += a_star*dt
    #   Earth
    a_planet = f/m_planet
    r_planet += v_planet*dt-1/2*a_planet*dt**2
    v_planet += a_planet*dt


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
r = np.sqrt(x_spice[0]**2+y_spice[0]**2).item()
axis.set_xlim(-r*1.5, r*1.5)
axis.set_ylim(-r*1.5, r*1.5)

#   Display initial position
path_spice = axis.plot(x_spice, y_spice, color="blue")[0]
path_sim = axis.plot(x_sim, y_sim, color="green")[0]
spice = axis.plot(
    x_spice[0], y_spice[0],
    color="blue",
    marker="o", markersize="5",
    label="SPICE"
)[0]
sim = axis.plot(
    x_sim[0], y_sim[0],
    color="green",
    marker="o", markersize="5",
    label="Simulation"
)[0]
star = axis.plot(0, 0, color="orange", marker="o", markersize="15")[0]
date = axis.text(0, -r*1.3, time, ha="center", va="center")
axis.legend()
#plt.show()

# Run animation
while running:
    # Run simulation n steps
    for i in range(n):
        step(dt=dt)
        time += datetime.timedelta(seconds=dt)

        if not running:
            break

    # Prepare variables
    x_spice = np.roll(x_spice, -1)
    y_spice = np.roll(y_spice, -1)
    x_sim = np.roll(x_sim, -1)
    y_sim = np.roll(y_sim, -1)

    # Calculate time point
    time_utc = time.strftime("%Y-%m-%dT00:00:00")
    time_et = sp.utc2et(time_utc)
    date.set_text(f"UTC {time_utc}")

    # Obtain planet position from SPICE
    state, _ = sp.spkgeo(
        targ=399,
        et=time_et,
        ref="ECLIPJ2000",
        obs=10
    )
    x_spice[-1] = state[0]*1000
    y_spice[-1] = state[1]*1000

    # Obtain planet position from simulation
    r = r_planet-r_star
    x_sim[-1] = r[0]
    y_sim[-1] = r[1]

    # Display results
    #   Paths
    path_spice.set_data(x_spice, y_spice)
    path_sim.set_data(x_sim, y_sim)
    #   Bodies
    spice.set_data((x_spice[-1],), (y_spice[-1],))
    sim.set_data((x_sim[-1],), (y_sim[-1],))

    plt.pause(0.001)
