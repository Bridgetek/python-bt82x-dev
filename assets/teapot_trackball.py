import math
import sys

CP = (sys.implementation.name == "circuitpython")

if CP:
    import ulab.numpy as np
else:
    import numpy as np

def vcopy(v1):
    return np.copy(v1)

def vadd(v1, v2):
    return np.add(v1, v2)

def vcross(v1, v2):
    return np.array((
        (v1[1] * v2[2]) - (v1[2] * v2[1]),
        (v1[2] * v2[0]) - (v1[0] * v2[2]),
        (v1[0] * v2[1]) - (v1[1] * v2[0])
        ))

def vdot(v1, v2):
    return np.dot(v1, v2)

def vlength(v):
    return np.sqrt(np.sum(v * v))

def length_quat(q):
    return np.sqrt(np.sum(np.square(q)))

def normalize_quat(q):
    mag = np.sqrt(np.sum(q * q))
    return q / mag

def add_quats(q1, q2):
    t1 = q1[:3] * q2[3]
    t2 = q2[:3] * q1[3]

    t3 = vcross(q2, q1)
    tf = t1 + t2 + t3
    tf = np.array((tf[0], tf[1], tf[2], (q1[3] * q2[3]) - vdot(q1[:3], q2[:3])))

    return normalize_quat(tf)

def multiply_quaternions(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2

    w = w1*w2 - x1*x2 - y1*y2 - z1*z2
    x = w1*x2 + x1*w2 + y1*z2 - z1*y2
    y = w1*y2 - x1*z2 + y1*w2 + z1*x2
    z = w1*z2 + x1*y2 - y1*x2 + z1*w2

    return np.array([x, y, z, w])

def build_rotmatrix(q):
    m = np.zeros((3, 3))
    m[0][0] = 1.0 - 2.0 * (q[1] * q[1] + q[2] * q[2])
    m[0][1] = 2.0 * (q[0] * q[1] - q[2] * q[3])
    m[0][2] = 2.0 * (q[2] * q[0] + q[1] * q[3])

    m[1][0] = 2.0 * (q[0] * q[1] + q[2] * q[3])
    m[1][1] = 1.0 - 2.0 * (q[2] * q[2] + q[0] * q[0])
    m[1][2] = 2.0 * (q[1] * q[2] - q[0] * q[3])

    m[2][0] = 2.0 * (q[2] * q[0] - q[1] * q[3])
    m[2][1] = 2.0 * (q[1] * q[2] + q[0] * q[3])
    m[2][2] = 1.0 - 2.0 * (q[1] * q[1] + q[0] * q[0])

    return m

#
# Ok, simulate a track-ball.  Project the points onto the virtual
# trackball, then figure out the axis of rotation, which is the cross
# product of P1 P2 and O P1 (O is the center of the ball, 0,0,0)
# Note:  This is a deformed trackball-- is a trackball in the center,
# but is deformed into a hyperbolic sheet of rotation away from the
# center.  This particular function was chosen after trying out
# several variations.
#
# It is assumed that the arguments to this routine are in the range
# (-1.0 ... 1.0)
#

TRACKBALLSIZE  = .5

def trackball(p1x, p1y, p2x, p2y):
    if (p1x == p2x) and (p1y == p2y):
        return np.array((0, 0, 0, 1))

    #
    # First, figure out z-coordinates for projection of P1 and P2 to
    # deformed sphere
    #

    p1 = np.array((p1x, p1y, tb_project_to_sphere(TRACKBALLSIZE, p1x, p1y)))
    p2 = np.array((p2x, p2y, tb_project_to_sphere(TRACKBALLSIZE, p2x, p2y)))

    #  Now, we want the cross product of P1 and P2
    a = vcross(p1, p2)

    #  Figure out how much to rotate around that axis.
    d = p1 - p2
    t = vlength(d) / (2.0*TRACKBALLSIZE)

    # Avoid problems with out-of-control values...

    t = max(-1, min(t, 1))
    phi = 9.0 * math.asin(t)

    return axis_to_quat(a, phi)

#  Given an axis and angle, compute quaternion.

def axis_to_quat(a, phi):
    q = a * math.sin(phi / 2.0)
    return np.array((q[0], q[1], q[2], math.cos(phi/2.0)))

#
# Project an x,y pair onto a sphere of radius r OR a hyperbolic sheet
# if we are away from the center of the sphere.
#

def tb_project_to_sphere(r, x, y):
    d = math.sqrt(x*x + y*y);
    if d < r * 0.70710678118654752440: # Inside sphere
        z = math.sqrt(r*r - d*d)
    else:           # On hyperbola
        t = r / 1.41421356237309504880
        z = t*t / d
    return z

if __name__ == "__main__":
    print("This program is called by teapot.py.")
