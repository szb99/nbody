import numpy as np
from matplotlib import pyplot as plt

# Simulation settings
#  One time-step elapses dt [s] time
#  The last path_length positions are also preserved and displayed
dt = 5e4
path_length = 500

# Set physical constants
gamma = 6.67e-11

#   Sun - Earth
m_star = 1.9885e30
m_planet = 5.9722e24
r_perihelion = 1.47095e11
v_perihelion = 3.029e4

# Prepare variables
r_star = np.array((0.0, 0.0))
v_star = np.array((0.0, 0.0))
r_planet = np.array((r_perihelion, 0.0))
v_planet = np.array((0.0, v_perihelion))

x_star = np.array((r_star[0],)*path_length)
y_star = np.array((r_star[1],)*path_length)
x_planet = np.array((r_planet[0],)*path_length)
y_planet = np.array((r_planet[1],)*path_length)


# Calculating next time-step
def step(dt):
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
axis.set_xlim(-r_perihelion*1.5, r_perihelion*1.5)
axis.set_ylim(-r_perihelion*1.5, r_perihelion*1.5)

# Display initial positions
p_star = axis.plot(x_star, y_star, color="orange")[0]
p_planet = axis.plot(x_planet, y_planet, color="blue")[0]
star = axis.plot(
    x_star[-1], y_star[-1],
    color="orange",
    marker="o", markersize="15"
)[0]
planet = axis.plot(
    x_planet[-1], y_planet[-1],
    color="blue",
    marker="o", markersize="5")[0]
#plt.show()

# Run animation
while running:
    step(dt=dt)

    # Prepare variables
    x_star = np.roll(x_star, -1)
    y_star = np.roll(y_star, -1)
    x_planet = np.roll(x_planet, -1)
    y_planet = np.roll(y_planet, -1)

    # Obtain new positions
    [x_star[-1], y_star[-1]] = [*r_star]
    [x_planet[-1], y_planet[-1]] = [*r_planet]

    # Display results
    #   Paths
    p_star.set_data(x_star, y_star)
    p_planet.set_data(x_planet, y_planet)
    #   Bodies
    star.set_data((x_star[-1],), (y_star[-1],))
    planet.set_data((x_planet[-1],), (y_planet[-1],))

    plt.pause(0.001)
