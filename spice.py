import spiceypy as sp
import numpy as np
import datetime

GAMMA = 6.67e-11
OBSERVER = 10
REFERENCE = "ECLIPJ2000"


def furnsh(kernel: str | tuple | list):
    if not isinstance(kernel, list):
        kernel = (kernel,)

        for k in kernel:
            sp.furnsh(k)


def set_observer(observer: int):
    global OBSERVER

    OBSERVER = observer


def set_reference(reference: str):
    global REFERENCE

    REFERENCE = reference


def dt2utc(time: datetime.datetime):
    return time.strftime("%Y-%m-%dT00:00:00")


def dt2et(time: datetime.datetime):
    return sp.utc2et(dt2utc(time))


def position(
        id: int,
        time: datetime.datetime,
        reference: str = None,
        observer: int = None
):
    if reference is None:
        reference = REFERENCE
    if observer is None:
        observer = OBSERVER

    et = dt2et(time)
    state, _ = sp.spkgeo(
        targ=id,
        et=et,
        ref=reference,
        obs=observer
    )

    return np.array((*state[:3],))*1000


def velocity(
        id: int,
        time: datetime.datetime,
        reference: str = None,
        observer: int = None
):
    if reference is None:
        reference = REFERENCE
    if observer is None:
        observer = OBSERVER

    et = dt2et(time)
    state, _ = sp.spkgeo(
        targ=id,
        et=et,
        ref=reference,
        obs=observer
    )

    return np.array((*state[3:6],))*1000


def mass(id: int):
    if id < 10:
        id = id*100+99

    _, gm = sp.bodvcd(
        bodyid=id,
        item="GM",
        maxn=1
    )

    return gm[0]*1000**3/GAMMA


def radius(id: int):
    if id < 10:
        id = id*100+99

    _, rad = sp.bodvcd(
        bodyid=id,
        item="RADII",
        maxn=3
    )

    return rad[0]*1000


class NBodySpice:
    def __init__(
            self,
            start: datetime.datetime,
            reference: str = None,
            observer: int = None
    ):
        self._time = start
        self._reference = reference
        self._observer = observer
        self._ids = []

    def step(self, time: int):
        self._time += datetime.timedelta(seconds=time)

    def add(
            self,
            id: int,
    ):
        self._ids.append(id)

    @property
    def time(self):
        return self._time

    @property
    def position(self):
        positions = np.empty((0, 3))
        for id in self._ids:
            positions = np.append(
                positions,
                position(
                    id,
                    self._time,
                    reference=self._reference,
                    observer=self._observer
                )[None, :],
                axis=0
            )

        return positions
