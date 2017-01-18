from PIL import Image
from cStringIO import StringIO



def AlterPixelsColor(imagefile,SearchColor, AlterColor, margin ):

    img = Image.open(imagefile)
    imga = img.convert("RGBA")
    datas = imga.getdata()

    newData = list()
    for item in datas:
        if abs(item[0] - SearchColor[0])<=margin and abs(item[1] - SearchColor[1])<=margin and abs(item[2] - SearchColor[2])<=margin:
            newData.append(AlterColor)
        else:
            newData.append(item)

    imga.putdata(newData)
    return imga
