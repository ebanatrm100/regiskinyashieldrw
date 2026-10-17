"""Builds assets/sky_background.jpg from the owner's REGIS' WORLD sky image: removes the big title (with its crown and gold ring), keeps the
sky, clouds, sun, paper plane and the small tagline.
Usage: python tools/make_sky_background.py path/to/original.png
Method: the crown/ring/title are covered by a mask and filled with a harmonic (Laplace) interpolation of the surrounding sky, solved coarse-to-fine, so the fill
matches the real pixels at its edge and shows no seam. The tagline, plane, sun and clouds are left untouched."""
import sys, pathlib
import cv2, numpy as np

src = sys.argv[1]
im = cv2.imread(src)
H, W = im.shape[:2]
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)

# mask: crown + ring (saturated yellow, dilated) + the title block + the lower-left tail of the title's first letter
hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV)
yellow = ((hsv[..., 0] >= 12) & (hsv[..., 0] <= 38) & (hsv[..., 1] > 90) & (hsv[..., 2] > 120)).astype(np.uint8) * 255
yellow = cv2.dilate(yellow, np.ones((25, 25), np.uint8))
yellow[430:, :] = 0
M = yellow > 0
M[118:412, 205:1350] = True          # title block with glow and 3D edge (tagline starts below y=412)
M[395:442, 205:392] = True           # tail of the first letter, left of the tagline rules
M[395:424, 1126:1350] = True         # shadow of the last letter, right of the tagline rules
M[196:312, 1340:1378] = True         # right end of the ring
M[290:410, 150:205] = True           # left end of the ring

y0, y1 = max(0, np.where(M.any(1))[0][0] - 2), min(H, np.where(M.any(1))[0][-1] + 3)
x0, x1 = max(0, np.where(M.any(0))[0][0] - 2), min(W, np.where(M.any(0))[0][-1] + 3)
box = im[y0:y1, x0:x1].astype(np.float32)
mb = M[y0:y1, x0:x1]


def solve(u, free, iters):
    """Jacobi iterations of the Laplace equation on the free pixels; edges of the array are treated as known."""
    for _ in range(iters):
        avg = u.copy()
        avg[1:-1, 1:-1] = 0.25 * (u[:-2, 1:-1] + u[2:, 1:-1] + u[1:-1, :-2] + u[1:-1, 2:])
        u = np.where(free[..., None], avg, u)
    return u


free = mb.copy()
free[0, :] = free[-1, :] = free[:, 0] = free[:, -1] = False
# coarse solve (1/6 scale), then refine at full resolution
sc = 6
small = cv2.resize(box, (box.shape[1] // sc, box.shape[0] // sc), interpolation=cv2.INTER_AREA)
fsmall = cv2.resize(free.astype(np.uint8), (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST).astype(bool)
# unknown pixels start from the mean of the known border so the iteration converges quickly
small[fsmall] = small[~fsmall].mean(0)
small = solve(small, fsmall, 6000)
up = cv2.resize(small, (box.shape[1], box.shape[0]), interpolation=cv2.INTER_CUBIC)
fill = np.where(free[..., None], up, box)
fill = solve(fill, free, 400)
rng = np.random.default_rng(3)
fill = fill + rng.normal(0, 0.8, fill.shape).astype(np.float32)
soft = cv2.GaussianBlur(mb.astype(np.float32), (0, 0), 2.2)[..., None]
soft = np.maximum(soft, mb[..., None].astype(np.float32) * 0 + soft)
res = box * (1 - soft) + fill * soft
out = im.copy()
out[y0:y1, x0:x1] = np.clip(res, 0, 255).astype(np.uint8)
out_path = pathlib.Path(__file__).resolve().parent.parent / "assets" / "sky_background.jpg"
cv2.imwrite(str(out_path), out, [cv2.IMWRITE_JPEG_QUALITY, 82])
cv2.imwrite("/tmp/bg/sky_preview.png", out)
print(out_path, out.shape, out_path.stat().st_size // 1024, "KB")
