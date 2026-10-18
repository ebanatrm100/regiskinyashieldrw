"""Removes the small tagline "LET THE SKY NOT BE THE LIMIT" (and the two rules beside it) from assets/sky_background.jpg, because the app now shows the tagline as
vertical text in front of the lock signs and servers (see security_art.py). Same method as make_sky_background.py: harmonic (Laplace) fill of the sky around the mask.
Usage: python tools/remove_tagline.py   (run once; it keeps assets/sky_background_with_tagline.jpg as the untouched copy)"""
import pathlib, shutil
import cv2, numpy as np

assets = pathlib.Path(__file__).resolve().parent.parent / "assets"
path, keep = assets / "sky_background.jpg", assets / "sky_background_with_tagline.jpg"
if not keep.exists():
    shutil.copy(path, keep)
im = cv2.imread(str(keep))
M = np.zeros(im.shape[:2], bool)
M[398:448, 385:1135] = True
y0, y1, x0, x1 = 386, 460, 372, 1148
box = im[y0:y1, x0:x1].astype(np.float32)
mb = M[y0:y1, x0:x1]
free = mb.copy(); free[0, :] = free[-1, :] = free[:, 0] = free[:, -1] = False


def solve(u, free, iters):
    for _ in range(iters):
        avg = u.copy()
        avg[1:-1, 1:-1] = 0.25 * (u[:-2, 1:-1] + u[2:, 1:-1] + u[1:-1, :-2] + u[1:-1, 2:])
        u = np.where(free[..., None], avg, u)
    return u


sc = 4
small = cv2.resize(box, (box.shape[1] // sc, box.shape[0] // sc), interpolation=cv2.INTER_AREA)
fs = cv2.resize(free.astype(np.uint8), (small.shape[1], small.shape[0]), interpolation=cv2.INTER_NEAREST).astype(bool)
small[fs] = small[~fs].mean(0)
small = solve(small, fs, 8000)
up = cv2.resize(small, (box.shape[1], box.shape[0]), interpolation=cv2.INTER_CUBIC)
fill = solve(np.where(free[..., None], up, box), free, 400)
fill = fill + np.random.default_rng(5).normal(0, 0.8, fill.shape).astype(np.float32)
soft = cv2.GaussianBlur(mb.astype(np.float32), (0, 0), 2.0)[..., None]
res = box * (1 - soft) + fill * soft
out = im.copy()
out[y0:y1, x0:x1] = np.clip(res, 0, 255).astype(np.uint8)
cv2.imwrite(str(path), out, [cv2.IMWRITE_JPEG_QUALITY, 82])
print(path, path.stat().st_size // 1024, "KB")
