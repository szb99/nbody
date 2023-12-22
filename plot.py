import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class Body:
    def __init__(
            self,
            label: str = "",
            color: str = "blue",
            path_scale: float = 1.0,
            path_length: int = 1000,
            radius: float = 1.0
    ):
        self._label = label
        self._color = color
        self._path_scale = path_scale
        self._path_length = path_length
        self._radius = radius

        self._r = None
        self._path_1 = None
        self._path_2 = None
        self._marker_1 = None
        self._marker_2 = None

    def plot(self, axis_1, axis_2, position):
        # Initializing path values
        self._r = np.repeat(
            position[None, :],
            repeats=self._path_length,
            axis=0
        )

        # Drawing to plot 1
        self._path_1 = axis_1.plot(
            self._r[0, 0],
            self._r[0, 1],
            color=self._color,
            label=self._label
        )[0]
        self._marker_1 = axis_1.add_patch(plt.Circle(
            (
                self._r[0, 0],
                self._r[0, 1]
            ),
            radius=self._radius,
            color=self._color,
            alpha=0.5
        ))

        # Drawing to plot 2
        self._path_2 = axis_2.plot(
            self._r[0, 0],
            self._r[0, 2],
            color=self._color,
            label=self._label
        )[0]
        self._marker_2 = axis_2.add_patch(plt.Circle(
            (
                self._r[0, 0],
                self._r[0, 2]
            ),
            radius=self._radius,
            color=self._color,
            alpha=0.5
        ))

    def step(
            self,
            position: np.array
    ):
        self._r = np.roll(self._r, 1, axis=0)
        self._r[0, :] = position

        self._path_1.set_data(
            self._r[:, 0] * self._path_scale,
            self._r[:, 1] * self._path_scale
        )
        self._marker_1.set_center((
            self._r[0, 0] * self._path_scale,
            self._r[0, 1] * self._path_scale
        ))
        self._path_2.set_data(
            self._r[:, 0] * self._path_scale,
            self._r[:, 2] * self._path_scale
        )
        self._marker_2.set_center((
            self._r[0, 0] * self._path_scale,
            self._r[0, 2] * self._path_scale
        ))

    @property
    def position(self):
        return self._r[0, :]


class NBodyPlot:
    def __init__(
            self,
            step,
            title: str = "Trajectory",
            path_length: int = 1000,
            limits: tuple = None,
            limit_scale: float = 1.5
    ):
        self._step = step
        self._title = title
        self._path_length = path_length
        self._limits = limits
        self._limit_scale = limit_scale

        self._bodies = []

    def add(
            self,
            label: str = "",
            color: str = "blue",
            path_scale: float = 1.0,
            path_length: int = 1000,
            radius: float = 1.0
    ):
        self._bodies.append(Body(
            label=label,
            color=color,
            path_scale=path_scale,
            path_length=path_length,
            radius=radius
        ))

    def _next(self, frame):
        data = self._step()

        for i in range(len(self._bodies)):
            self._bodies[i].step(data[i, :])

    def _setup(
            self,
            frames: int = 500,
            interval: int = 50
    ):
        # Gather initial data
        data = self._step()

        # Prepare display
        self._figure = plt.figure(self._title)
        self._axis_1 = self._figure.add_subplot(1, 2, 1, aspect="equal")
        self._axis_2 = self._figure.add_subplot(1, 2, 2, aspect="equal")

        # Display initial position
        for i in range(len(self._bodies)):
            self._bodies[i].plot(
                self._axis_1,
                self._axis_2,
                position=data[i, :]
            )

        # Calculate axis limits
        if self._limits is None:
            # Calculate axis limits
            radius = max(
                np.linalg.norm(body.position[:2])
                for body in self._bodies
            )
            self._limits = [
                radius * self._limit_scale,
                radius * self._limit_scale,
                radius * self._limit_scale
            ]

        self._axis_1.set_xlim(-self._limits[0], self._limits[0])
        self._axis_1.set_ylim(-self._limits[1], self._limits[1])
        self._axis_2.set_xlim(-self._limits[0], self._limits[0])
        self._axis_2.set_ylim(-self._limits[2], self._limits[2])

        # Display legend
        self._axis_2.legend(bbox_to_anchor=(1, 0.5), loc="center left")

        # Create animation
        self._animation = FuncAnimation(
            fig=self._figure,
            func=self._next,
            frames=frames,
            interval=interval
        )

    def run(self):
        self._setup()
        plt.show()

    def save(
            self,
            path: str,
            dpi: int = 300
    ):
        self._setup()
        self._animation.save(path, dpi=dpi)
