"""Builds assets/panel_collage.jpg: the owner's four-picture universe collage (nebula, supernova, pulsar, Earth) WITHOUT the title and the four labels.
The title strip and the label strips are cut away (not painted over), so no trace of the text remains; the four pictures are joined again with a thin light divider.
    python tools/make_panel_collage.py <path to the collage picture>"""
import sys
from PIL import Image, ImageEnhance

SRC = sys.argv[1] if len(sys.argv) > 1 else "/mnt/user-data/attachments/8c41cf3f-99e9-5a60-846d-705d1bb08699/52236526-image.png"
im = Image.open(SRC).convert("RGB")                      # 495 x 619: title y<30, labels y 299-316 and 597-614, divider x=248 / y=323
W = im.width
panes = {"tl": (0, 31, 247, 298), "tr": (250, 31, W, 298), "bl": (0, 327, 247, 593), "br": (250, 327, W, 593)}
GAP = 3
cw = max(p[2] - p[0] for p in panes.values())
w_l, w_r = panes["tl"][2] - panes["tl"][0], panes["tr"][2] - panes["tr"][0]
h_t, h_b = panes["tl"][3] - panes["tl"][1], panes["bl"][3] - panes["bl"][1]
out = Image.new("RGB", (w_l + GAP + w_r, h_t + GAP + h_b), (235, 240, 255))
out.paste(im.crop(panes["tl"]), (0, 0))
out.paste(im.crop(panes["tr"]), (w_l + GAP, 0))
out.paste(im.crop(panes["bl"]).resize((w_l, h_b)), (0, h_t + GAP))
out.paste(im.crop(panes["br"]).resize((w_r, h_b)), (w_l + GAP, h_t + GAP))
out = out.resize((out.width * 2, out.height * 2), Image.LANCZOS)
out = ImageEnhance.Brightness(out).enhance(0.85)
out.save("assets/panel_collage.jpg", quality=84, optimize=True, progressive=True)
print(out.size)
