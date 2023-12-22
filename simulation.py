import numpy as np
import datetime as dt
import spice as sp

GAMMA = 6.67e-11


class NBodySim:
    def __init__(
            self,
            start: dt.datetime
    ):
        self._time = start
        self._masses = np.empty((0,))
        self._display = []
        self._a = np.empty((0, 3))
        self._r = np.empty((0, 3))
        self._v = np.empty((0, 3))

    def __len__(self):
        return len(self._masses)

    def step(self, time: int, n: int = 1):
        for k in range(n):
            f = np.zeros((len(self), len(self), 3))
            for i in range(1, len(self)):
                for j in range(i):
                    dr = self._r[j, :] - self._r[i, :]
                    d = np.linalg.norm(dr)
                    g = GAMMA * self._masses[i] * self._masses[j]

                    f[i, j, :] = g * dr / d ** 3

            self._a = (np.sum(f, axis=1) - np.sum(f, axis=0)) \
                      / self._masses[:, None]
            self._r += self._v * time + self._a / 2 * time ** 2
            self._v += self._a * time

        self._time += dt.timedelta(seconds=time * n)

    def add_object(
            self,
            mass: int,
            position: np.array,
            velocity: np.array,
            display: bool = True
    ):
        self._masses = np.append(self._masses, mass)
        self._display.append(display)
        self._r = np.append(self._r, position[None, :], axis=0)
        self._v = np.append(self._v, velocity[None, :], axis=0)

    def add_naif(
            self,
            id: int,
            display: bool = True,
            reference: str = None,
            observer: int = None
    ):
        mass = sp.mass(id)
        position = sp.position(
            id, self._time,
            reference=reference,
            observer=observer
        )
        velocity = sp.velocity(
            id, self._time,
            reference=reference,
            observer=observer
        )

        self.add_object(
            mass=mass,
            position=position,
            velocity=velocity,
            display=display
        )

    @property
    def mass(self):
        return self._masses

    @property
    def time(self):
        return self._time

    @property
    def position(self):
        return self._r[self._display, :]

    @property
    def velocity(self):
        return self._v[self._display, :]
