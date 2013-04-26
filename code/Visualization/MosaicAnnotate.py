import cv2, cv, numpy
import os


###############################################################################
def readTiepoints(filePath):
    f = open(filePath,"r")
    tps = [[[int(round(float(y))) for y in x.split(",")] for x in l.strip().split("  ")] for l in f.readlines()]
    f.close()
    return tps

###############################################################################
def tps(p,i1,i2):
    tp1 = os.path.join(p,"%d-%d.tiepoints.txt"%(i1,i2))
    tp2 = os.path.join(p,"%d-%d.tiepoints.txt"%(i2,i1))
    
    if (os.path.exists(tp1)):
        tps = readTiepoints(tp1)
    elif (os.path.exists(tp2)):
        tps = readTiepoints(tp2)
        #swap
        stps = []
        for tp in tps:
            stps.append([tp[1],tp[0]])
        tps=stps
    else:
        raise Exception("tiepoints file does not exist")
    return tps

def readImage(p,iNum):
    return cv2.imread(os.path.join(p,"%d.png"%iNum))

def drawCorrespondence(iMosaic, x,y):
    COLOR = (0,255,255,0)
    cv2.line(iMosaic, x,y, COLOR, lineType=cv.CV_AA) #, thickness=1)
    
def drawFeature(iMosaic, x,y):
    COLOR = (0,255,0,0)
    cv2.circle(iMosaic, x, 1, COLOR, thickness=-1, lineType=cv.CV_AA)
    cv2.circle(iMosaic, y, 1, COLOR, thickness=-1, lineType=cv.CV_AA)
    
def drawLabel(iMosaic, label, org):
    COLOR = (0,255,255,0)
    org = (org[0]-100, org[1]+50)
    cv2.putText(iMosaic, label, org, 
                cv2.FONT_HERSHEY_PLAIN, 20, COLOR, 
                thickness=5, lineType=cv.CV_AA, bottomLeftOrigin=False)
    
###############################################################################
SPACING = 50
LABELS = True
FEATURES = True
CORRESPONDENCES = True

IMAGE_PATH = r"C:\images"

#imageGrid = [[0,1,2],
#             [3,4,5],
#             [6,7,8]]
imageGrid = [[0,1],
             [2,3]]

########################################
images=[]
rowHeights=[]

mosaicWidth=0;mosaicHeight=0;mosaicBands=0

for row in imageGrid:
    imageRow = []
    rowWidth=0;rowHeight=0
    for imageIndex in row:
        im = readImage(IMAGE_PATH,imageIndex)
        rowWidth+=im.shape[1]
        rowHeight=max([rowHeight,im.shape[0]])
        mosaicBands=max([mosaicBands,im.shape[2]])
        imageRow.append(im)
    rowWidth += (len(row)-1)*SPACING
    mosaicWidth = max([rowWidth,mosaicWidth])
    mosaicHeight+=rowHeight
    rowHeights.append(rowHeight)
    images.append(imageRow)
mosaicHeight += (len(imageGrid)-1)*SPACING        

iMosaic = numpy.zeros((mosaicHeight,mosaicWidth,mosaicBands), numpy.uint8)

# create mosaic
dy=0
for r,imageRow in enumerate(images):
    dx=0
    for im in imageRow:
        iMosaic[dy:dy+im.shape[0], dx:dx+im.shape[1], :im.shape[2]] = im
        dx+=im.shape[1]+SPACING
    dy+=rowHeights[r]+SPACING
    
    
    
if (CORRESPONDENCES or LABELS or FEATURES):
    dy=0
    for r in range(len(images)):
        dx=0
        for c in range(len(images[r])):
            refIm = images[r][c]
            
            if (LABELS):
                drawLabel(iMosaic, str(imageGrid[r][c]), (dx+(refIm.shape[1]/2), dy+(refIm.shape[0]/2)))
            
            if (CORRESPONDENCES or FEATURES):
                if (c+1<len(images[r])):
                    testIm = images[r][c+1]
                    testdx = dx+refIm.shape[1]+SPACING
                    
                    tiepoints = tps(IMAGE_PATH,imageGrid[r][c],imageGrid[r][c+1])
                    
                    for i,tp in enumerate(tiepoints):
                        #if ((i%10)==0):
                            x = (tp[1][0]+dx, tp[1][1]+dy)
                            y = (tp[0][0]+testdx, tp[0][1]+dy)
                            if (CORRESPONDENCES):   drawCorrespondence(iMosaic, x,y)
                            if (FEATURES):          drawFeature(iMosaic, x,y)
            
                if (r+1<len(images)):
                    testIm = images[r+1][c]
                    testdy = dy+refIm.shape[0]+SPACING
                    
                    tiepoints = tps(IMAGE_PATH,imageGrid[r][c],imageGrid[r+1][c])
                    
                    for i,tp in enumerate(tiepoints):
                        #if ((i%10)==0):
                            x = (tp[1][0]+dx, tp[1][1]+dy)
                            y = (tp[0][0]+dx, tp[0][1]+testdy)
                            if (CORRESPONDENCES):   drawCorrespondence(iMosaic, x,y)
                            if (FEATURES):          drawFeature(iMosaic, x,y)
                            
            dx+=refIm.shape[1]+SPACING
        dy+=rowHeights[r]+SPACING


cv2.imwrite(os.path.join(IMAGE_PATH, "annotatedMosaic.png"), iMosaic)

