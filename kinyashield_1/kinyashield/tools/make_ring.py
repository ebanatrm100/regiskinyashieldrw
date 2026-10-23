"""Extracts the golden ring from the owner's REGIS' WORLD picture and writes assets/ring.png (transparent background).
The picture only shows two end-arcs of the ring (the middle is hidden behind the letters), so: the two arcs are cut out by colour,
an ellipse is fitted through them, and the hidden part is completed along that ellipse using the arcs' own gold colours and thickness.
    python tools/make_ring.py <path to the REGIS' WORLD picture>"""
import sys, math
import numpy as np, cv2
from PIL import Image

SRC = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/attachments/8c41cf3f-99e9-5a60-846d-705d1bb08699/540627e6-image.png"
im = np.array(Image.open(SRC).convert("RGB")).astype(float)
R, G, B = im[..., 0], im[..., 1], im[..., 2]
alpha = np.clip((R - B - 70) / 60.0, 0, 1)
box = np.zeros(alpha.shape, bool)
box[195:315, 215:325] = True          # left arc
box[130:240, 1355:1450] = True        # right arc (crown and everything else excluded)
alpha *= box
mask = (alpha > .5).astype(np.uint8)
pts = np.argwhere(mask)[:, ::-1].astype(np.float32)
(cx, cy), (w, h), ang = cv2.fitEllipse(pts)           # centre, full axes, rotation (deg)
# colours and thickness measured from the arcs
gold = im[mask > 0]
c_lo, c_hi = np.percentile(gold, 15, axis=0), np.percentile(gold, 85, axis=0)
thick_max = 0.0
for comp in (mask[195:315, 215:325], mask[130:240, 1355:1450]):
    thick_max = max(thick_max, cv2.distanceTransform(comp, cv2.DIST_L2, 3).max() * 2)
print("ellipse", round(cx), round(cy), round(w), round(h), round(ang), "thickness", round(thick_max, 1))

S = 1000                                                # output size (square, transparent)
a, b = (max(w, h) / 2), (min(w, h) / 2)
scale = S * 0.46 / a
A, Bm = a * scale, b * scale
big = np.zeros((S * 2, S * 2, 4), np.uint8)             # draw at 2x then shrink for smooth edges
rot = math.radians(ang if w >= h else ang + 90)
# draw the ring as many small discs along the ellipse, thick near the two far ends and thin where the ring passes behind the letters
for t in np.linspace(0, 2 * math.pi, 1600):
    x, y = A * math.cos(t), Bm * math.sin(t)
    X = S + (x * math.cos(rot) - y * math.sin(rot)) * 2 * 1.0
    Y = S + (x * math.sin(rot) + y * math.cos(rot)) * 2 * 1.0
    k = abs(math.cos(t))                                # 1 at the ends of the long axis
    r = (0.18 + 0.82 * k ** 1.5) * thick_max * scale * 2 / 2
    f = 0.5 + 0.5 * math.sin(t + rot)                   # light from one side
    col = (c_lo * (1 - f) + c_hi * f).astype(int)
    cv2.circle(big, (int(X), int(Y)), max(1, int(r)), (int(col[0]), int(col[1]), int(col[2]), 255), -1, cv2.LINE_AA)
img = Image.fromarray(big).resize((S, S), Image.LANCZOS)
bb = img.getbbox(); img = img.crop(bb)
img.save("assets/ring.png", optimize=True)
print("saved", img.size)
