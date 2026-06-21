import sys, json, numpy as np
from PIL import Image
# ONE fixed grid for every board (same Tellus device/resolution)
COLS=[(44,392),(422,780),(810,1166),(1208,1554),(1594,1942),(1972,2330)]
ROWS=[(144,332),(388,574),(630,816),(872,1058),(1114,1300),(1356,1544)]
PAD=10
def run(img_path, board):
    import os; os.makedirs(f"web/boards/{board}", exist_ok=True)
    im=Image.open(img_path).convert("RGB"); A=np.asarray(im).astype(int); W,H=im.size
    occ=[]
    for ri,(y0,y1) in enumerate(ROWS, start=1):
        for ci,(x0,x1) in enumerate(COLS, start=1):
            reg=A[y0:y1,x0:x1]
            nonwhite=(np.abs(reg-254).max(axis=2)>22).mean()
            if nonwhite>0.02:  # cell has content
                crop=im.crop((max(0,x0-PAD),max(0,y0-PAD),min(W,x1+PAD),min(H,y1+PAD)))
                crop.save(f"web/boards/{board}/r{ri}c{ci}.png")
                occ.append([ri,ci])
    print(board, "cells:", len(occ))
    print(json.dumps(occ))
    # verification montage (native size, not resized — faithful)
    cw=max(c[1]-c[0] for c in COLS)+2*PAD; ch=max(r[1]-r[0] for r in ROWS)+2*PAD; mg=12
    canvas=Image.new("RGB",(6*cw+7*mg,6*ch+7*mg),(40,46,57))
    for ri,ci in occ:
        c=Image.open(f"web/boards/{board}/r{ri}c{ci}.png")
        canvas.paste(c,(mg+(ci-1)*(cw+mg)+(cw-c.width)//2, mg+(ri-1)*(ch+mg)+(ch-c.height)//2))
    canvas.save(f"web/boards/{board}/_verify.png")
if __name__=="__main__":
    run(sys.argv[1], sys.argv[2])
