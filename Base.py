import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from ChangePixelColor import AlterPixelsColor
from PIL._util import isPath
from PIL import Image
import cStringIO


LastImages = []

def ImageContent(image):
    buffer = QBuffer()
    buffer.open(QIODevice.ReadWrite)
    image.save(buffer, "PNG")
    strio = cStringIO.StringIO()
    strio.write(buffer.data())
    buffer.close()
    strio.seek(0)
    return strio


def rgb(r, g, b, a=255):
    """(Internal) Turns an RGB color into a Qt compatible color integer."""
    # use qRgb to pack the colors, and then turn the resulting long
    # into a negative integer with the same bitpattern.
    return (qRgba(r, g, b, a) & 0xffffffff)

def align8to32(bytes, width, mode):
    """
    converts each scanline of data from 8 bit to 32 bit aligned
    """

    bits_per_pixel = {
        '1': 1,
        'L': 8,
        'P': 8,
    }[mode]

    # calculate bytes per line and the extra padding if needed
    bits_per_line = bits_per_pixel * width
    full_bytes_per_line, remaining_bits_per_line = divmod(bits_per_line, 8)
    bytes_per_line = full_bytes_per_line + (1 if remaining_bits_per_line else 0)

    extra_padding = -bytes_per_line % 4

    # already 32 bit aligned by luck
    if not extra_padding:
        return bytes

    new_data = []
    for i in range(len(bytes) // bytes_per_line):
        new_data.append(bytes[i*bytes_per_line:(i+1)*bytes_per_line] + b'\x00' * extra_padding)

    return b''.join(new_data)


def _toqclass_helper(im):
    data = None
    colortable = None

    # handle filename, if given instead of image name
    if hasattr(im, "toUtf8"):
        # FIXME - is this really the best way to do this?
        if str is bytes:
            im = unicode(im.toUtf8(), "utf-8")
        else:
            im = str(im.toUtf8(), "utf-8")
    if isPath(im):
        im = Image.open(im)

    if im.mode == "1":
        format = QImage.Format_Mono
    elif im.mode == "L":
        format = QImage.Format_Indexed8
        colortable = []
        for i in range(256):
            colortable.append(rgb(i, i, i))
    elif im.mode == "P":
        format = QImage.Format_Indexed8
        colortable = []
        palette = im.getpalette()
        for i in range(0, len(palette), 3):
            colortable.append(rgb(*palette[i:i+3]))
    elif im.mode == "RGB":
        data = im.tobytes("raw", "BGRX")
        format = QImage.Format_RGB32
    elif im.mode == "RGBA":
        try:
            data = im.tobytes("raw", "BGRA")
        except SystemError:
            # workaround for earlier versions
            r, g, b, a = im.split()
            im = Image.merge("RGBA", (b, g, r, a))
        format = QImage.Format_ARGB32
    else:
        raise ValueError("unsupported image mode %r" % im.mode)

    # must keep a reference, or Qt will crash!
    __data = data or align8to32(im.tobytes(), im.size[0], im.mode)
    return {
        'data': __data, 'im': im, 'format': format, 'colortable': colortable
    }

class ImageQt(QImage):

    def __init__(self, im):
        im_data = _toqclass_helper(im)
        QImage.__init__(self,
                        im_data['data'], im_data['im'].size[0],
                        im_data['im'].size[1], im_data['format'])
        if im_data['colortable']:
            self.setColorTable(im_data['colortable'])

class Example(QWidget):

    def __init__(self):
       super(Example, self).__init__()
       self.initUI()
	
    def color_picker(self, widget):
        color = QColorDialog.getColor()
        widget.setStyleSheet("QWidget { background-color: %s}" % color.name())
   
   
    def initUI(self):
      
        hbox = QHBoxLayout(self)
        self.ChangeColor = QLabel("Change Color", self)
       
        self.Searchbox0 = QLabel("", self)
        self.Searchbox0.setStyleSheet("QWidget { background-color:Blue }" )
       
        self.SearchColor0 = QPushButton("Search Color", self)
        self.SearchColor0.clicked.connect(lambda:self.color_picker(self.Searchbox0))
       
        self.Alterbox = QLabel()
        self.Alterbox.setStyleSheet("QWidget { background-color:Green }" )
       
        self.AlterColor = QPushButton("Alter Color", self)
        self.AlterColor.clicked.connect(lambda:self.color_picker(self.Alterbox))
        self.AlterColor.clicked.connect(self.alterColorImage)
        self.slidervalue = QLabel()
        self.slidervalue.setNum(25) 
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(0)
        self.slider.setMaximum(50)
        self.slider.setValue(25)
        self.slider.setTickInterval(1)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self.slidervalue.setNum)
        self.Transparency = QLabel("Transparency", self)
       
        self.Searchbox1 = QLabel("", self)
        self.Searchbox1.setStyleSheet("QWidget { background-color:Blue }" )
       
        self.SearchColor1 = QPushButton("Search Color", self)
        self.SearchColor1.clicked.connect(lambda:self.color_picker(self.Searchbox1))
        self.SearchColor1.clicked.connect(self.apply_transparency)
        bottom = QFrame()
        bottom.setFrameShape(QFrame.StyledPanel)
      
        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(self.ChangeColor)
        splitter1.addWidget(self.SearchColor0)
        splitter1.addWidget(self.Searchbox0)
        splitter1.addWidget(self.AlterColor)
        splitter1.addWidget(self.Alterbox)
        splitter1.addWidget(self.slidervalue)
        splitter1.addWidget(self.slider)
        splitter1.addWidget(self.Transparency)
        splitter1.addWidget(self.SearchColor1)
        splitter1.addWidget(self.Searchbox1)
        splitter1.addWidget(bottom)
        splitter1.setSizes([10,10,10,10,5,5,10,10,10,10,160])
        self.scrollArea = QScrollArea()
        self.scrollArea.setBackgroundRole(QPalette.Dark)
        self.right = QLabel()
        self.right.setSizePolicy(QSizePolicy.Ignored,
                QSizePolicy.Ignored)
        self.right.setScaledContents(True)
        self.scrollArea.setWidget(self.right)
        
        splitter2 = QSplitter(Qt.Horizontal)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(self.scrollArea)	
        splitter2.setSizes([40,350])
        hbox.addWidget(splitter2)
		
        self.setLayout(hbox)
        self.show()
    
    def alterColorImage(self):
        SearchRGBA = self.getColorWidget(self.Searchbox0)
        AlterRGBA = self.getColorWidget(self.Alterbox)
        LastImages.append(self.image.copy())
        stream = AlterPixelsColor(ImageContent(self.image), SearchRGBA,AlterRGBA,int(self.slidervalue.text()))
        self.image = ImageQt(stream)
        self.right.setPixmap(QPixmap.fromImage(self.image))
    
    def apply_transparency(self):
        SearchRGBA = self.getColorWidget(self.Searchbox1)
        LastImages.append(self.image.copy())
        AlterPixelsColor(ImageContent(self.image), SearchRGBA,(0, 0, 0, 0), int(self.slidervalue.text()))
        self.image = QImage(self.fileName)
        self.right.setPixmap(QPixmap.fromImage(self.image))  
    
    def getColorWidget(self,widget):
        palette = widget.palette()
        color = palette.color(widget.backgroundRole())
        rgba = color.red(), color.green(), color.blue(), color.alpha()
        return rgba

class ImageViewer(QMainWindow):
    def __init__(self):
        super(ImageViewer, self).__init__()

        self.printer = QPrinter()
        self.scaleFactor = 0.0
       
        self.createActions()
        self.createMenus()
        
        self.setWindowTitle("Image Viewer")
        self.ex = Example()
        self.setCentralWidget(self.ex)
        self.resize(500, 400)
        self.show()
    def open(self):
        self.ex.fileName = QFileDialog.getOpenFileName(self, "Open File",
        QDir.currentPath())
        if self.ex.fileName:
            self.ex.image = QImage(self.ex.fileName)
            if self.ex.image.isNull():
               QMessageBox.information(self, "Image Viewer",
               "Cannot load %s." % self.ex.fileName)
               return

            self.ex.right.setPixmap(QPixmap.fromImage(self.ex.image))
            self.scaleFactor = 1.0

            self.printAct.setEnabled(True)
            self.fitToWindowAct.setEnabled(True)
            self.updateActions()

            if not self.fitToWindowAct.isChecked():
                self.ex.right.adjustSize()
    
    def createActions(self):
        self.openAct = QAction("&Open...", self, shortcut="Ctrl+O",
                triggered=self.open)
        
        self.saveAct = QAction("&Save...", self, shortcut="Ctrl+S",
                triggered=self.save)
        
        self.undoAct = QAction("&Undo...", self, shortcut="Ctrl+Z",
                triggered=self.undo)
        
        self.printAct = QAction("&Print...", self, shortcut="Ctrl+P",
                enabled=False, triggered=self.print_)

        self.exitAct = QAction("E&xit", self, shortcut="Ctrl+Q",
                triggered=self.close)

        self.zoomInAct = QAction("Zoom &In (25%)", self,
                shortcut="Ctrl++", enabled=False, triggered=self.zoomIn)

        self.zoomOutAct = QAction("Zoom &Out (25%)", self,
                shortcut="Ctrl--", enabled=False, triggered=self.zoomOut)

        self.normalSizeAct = QAction("&Normal Size", self,
                shortcut="Ctrl+N", enabled=False, triggered=self.normalSize)

        self.fitToWindowAct = QAction("&Fit to Window", self,
                enabled=False, checkable=True, shortcut="Ctrl+F",
                triggered=self.fitToWindow)

        self.aboutAct = QAction("&About", self, triggered=self.about)

        self.aboutQtAct = QAction("About &Qt", self,
                triggered=qApp.aboutQt)
    def createMenus(self):
        self.fileMenu = QMenu("&File", self)
        self.fileMenu.addAction(self.openAct)
        self.fileMenu.addAction(self.printAct)
        self.fileMenu.addAction(self.saveAct)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.exitAct)

        self.editMenu = QMenu("&Edit", self)
        self.editMenu.addAction(self.undoAct)
        
        self.viewMenu = QMenu("&View", self)
        self.viewMenu.addAction(self.zoomInAct)
        self.viewMenu.addAction(self.zoomOutAct)
        self.viewMenu.addAction(self.normalSizeAct)
        self.viewMenu.addSeparator()
        self.viewMenu.addAction(self.fitToWindowAct)

        self.helpMenu = QMenu("&Help", self)
        self.helpMenu.addAction(self.aboutAct)
        self.helpMenu.addAction(self.aboutQtAct)

        
        self.menuBar().addMenu(self.fileMenu)
        self.menuBar().addMenu(self.editMenu)
        self.menuBar().addMenu(self.viewMenu)
        self.menuBar().addMenu(self.helpMenu)

  
    def print_(self):
        dialog = QPrintDialog(self.printer, self)
        if dialog.exec_():
            painter = QPainter(self.printer)
            rect = painter.viewport()
            size = self.imageLabel.pixmap().size()
            size.scale(rect.size(), QtCore.Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(self.imageLabel.pixmap().rect())
            painter.drawPixmap(0, 0, self.imageLabel.pixmap())

    
    def save(self):
        stream = ImageContent(self.ex.image)
        image = Image.open(stream)
        filename = str(self.ex.fileName)
        image.format = filename[filename.index(".")+1:].upper()
        image.save(filename)
        

    def zoomIn(self):
        self.scaleImage(1.25)

    def zoomOut(self):
        self.scaleImage(0.8)
    
    def undo(self):
        self.ex.image = LastImages[-1]
        LastImages.pop()
        self.ex.right.setPixmap(QPixmap.fromImage(self.ex.image))

    def normalSize(self):
        self.ex.right.adjustSize()
        self.scaleFactor = 1.0

    def fitToWindow(self):
        fitToWindow = self.fitToWindowAct.isChecked()
        self.scrollArea.setWidgetResizable(fitToWindow)
        if not fitToWindow:
            self.normalSize()

        self.updateActions()
    
    def about(self):
        QMessageBox.about(self, "About Image Viewer",
                "<p>The <b>Image Viewer</b> example shows how to combine "
                "QLabel and QScrollArea to display an image. QLabel is "
                "typically used for displaying text, but it can also display "
                "an image. QScrollArea provides a scrolling view around "
                "another widget. If the child widget exceeds the size of the "
                "frame, QScrollArea automatically provides scroll bars.</p>"
                "<p>The example demonstrates how QLabel's ability to scale "
                "its contents (QLabel.scaledContents), and QScrollArea's "
                "ability to automatically resize its contents "
                "(QScrollArea.widgetResizable), can be used to implement "
                "zooming and scaling features.</p>"
                "<p>In addition the example shows how to use QPainter to "
                "print an image.</p>")

    def updateActions(self):
        self.zoomInAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.zoomOutAct.setEnabled(not self.fitToWindowAct.isChecked())
        self.normalSizeAct.setEnabled(not self.fitToWindowAct.isChecked())

    def scaleImage(self, factor):
        self.scaleFactor *= factor
        self.imageLabel.resize(self.scaleFactor * self.imageLabel.pixmap().size())

        self.adjustScrollBar(self.scrollArea.horizontalScrollBar(), factor)
        self.adjustScrollBar(self.scrollArea.verticalScrollBar(), factor)

        self.zoomInAct.setEnabled(self.scaleFactor < 3.0)
        self.zoomOutAct.setEnabled(self.scaleFactor > 0.333)

    def adjustScrollBar(self, scrollBar, factor):
        scrollBar.setValue(int(factor * scrollBar.value()
                                + ((factor - 1) * scrollBar.pageStep()/2)))



def main():
   app = QApplication(sys.argv)
   ex = ImageViewer()
   sys.exit(app.exec_())
	
if __name__ == '__main__':
   main()
