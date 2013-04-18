import cv2, numpy
import os


###############################################################################
def readTiepoints(filePath):
    f = open(filePath,"r")
    tps = [[[int(round(float(y))) for y in x.split(",")] for x in l.strip().split("  ")] for l in f.readlines()]
    f.close()
    return tps

###############################################################################
SPACING = 100
TILE_SIZE = 1054
TILES_PER_DIM = 2
TILE_OFFSET = TILE_SIZE+SPACING
MOSAIC_SIZE = (TILE_SIZE*TILES_PER_DIM+SPACING, TILE_SIZE*TILES_PER_DIM+SPACING, 3)
COLOR_LINE = (0,255,255,0)
COLOR_POINT = (0,255,0,0)
ANNOTATE = True

IMAGE_PATH = r"C:\images"
imagePairs = [
[os.path.join(IMAGE_PATH,"UL.jpg"), os.path.join(IMAGE_PATH,"UR.jpg"), os.path.join(IMAGE_PATH,"UL-UR.tiepoints.txt"), (0,0), (TILE_OFFSET,0)],
[os.path.join(IMAGE_PATH,"UL.jpg"), os.path.join(IMAGE_PATH,"LL.jpg"), os.path.join(IMAGE_PATH,"UL-LL.tiepoints.txt"), (0,0), (0,TILE_OFFSET)],
[os.path.join(IMAGE_PATH,"UR.jpg"), os.path.join(IMAGE_PATH,"LR.jpg"), os.path.join(IMAGE_PATH,"UR-LR.tiepoints.txt"), (TILE_OFFSET,0), (TILE_OFFSET,TILE_OFFSET)]
]

iMosaic = numpy.zeros(MOSAIC_SIZE, numpy.uint8)

# create mosaic
for ips in imagePairs:
    iRef = cv2.imread(ips[0])
    iTest = cv2.imread(ips[1])
    offsetRef = ips[3]
    offsetTest = ips[4]
    
    iMosaic[offsetRef[1]:offsetRef[1]+iRef.shape[1], offsetRef[0]:offsetRef[0]+iRef.shape[0],:] = iRef
    iMosaic[offsetTest[1]:offsetTest[1]+iTest.shape[1], offsetTest[0]:offsetTest[0]+iTest.shape[0],:] = iTest
    
if (ANNOTATE):
    # create annotations
    for ips in imagePairs:
        tps = readTiepoints(ips[2])
        offsetRef = ips[3]
        offsetTest = ips[4]
        
        for tp in tps:
            x = (tp[1][0]+offsetRef[0], tp[1][1]+offsetRef[1])
            y = (tp[0][0]+offsetTest[0], tp[0][1]+offsetTest[1])
            cv2.line(iMosaic, x,y, COLOR_LINE)
            cv2.circle(iMosaic, x, 2, COLOR_POINT)
            cv2.circle(iMosaic, y, 2, COLOR_POINT)

cv2.imwrite(os.path.join(IMAGE_PATH, "annotatedMosaic.png"), iMosaic)

