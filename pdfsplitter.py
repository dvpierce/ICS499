# Python 2.x Application to preview and split PDF files.

import wx
import wx.lib.sized_controls as sc

import pyPdf
import os

from wx.lib.pdfviewer import pdfViewer, pdfButtonPanel

# Global Variables
path = None
pageCount = None
pdfV = None

class PDFViewer(sc.SizedFrame):
    def __init__(self, parent, **kwds):
        super(PDFViewer, self).__init__(parent, **kwds)

        paneCont = self.GetContentsPane()
        self.buttonpanel = pdfButtonPanel(paneCont, wx.NewId(),
                                wx.DefaultPosition, wx.DefaultSize, 0)
        self.buttonpanel.SetSizerProps(expand=True)
        self.viewer = pdfViewer(paneCont, wx.NewId(), wx.DefaultPosition,
                                wx.DefaultSize,
                                wx.HSCROLL|wx.VSCROLL|wx.SUNKEN_BORDER)
        self.viewer.UsePrintDirect = ``False``
        self.viewer.SetSizerProps(expand=True, proportion=1)

        # introduce buttonpanel and viewer to each other
        self.buttonpanel.viewer = self.viewer
        self.viewer.buttonpanel = self.buttonpanel

def OnClose(event):
    global pageCount
    dlg = wx.MessageDialog(top, 
        "Do you really want to close this application?",
        "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
    result = dlg.ShowModal()
    dlg.Destroy()
    if result == wx.ID_OK:
        top.Destroy()

def SelectFile(event):
    global path
    global pageCount
    OpenFileDlg = wx.FileDialog(top, "Open...", "File Selection", "", "PDF Files (*.pdf)|*.pdf", wx.FD_OPEN|wx.CANCEL|wx.FD_FILE_MUST_EXIST)
    OpenFileDlg.ShowModal()
    path = OpenFileDlg.GetPath()
    OpenFileDlg.Destroy()

    UpdatePDFViewer()
    GetPageCount()
    UpdateSelectionPanel()
    top.SetStatusText(path)
    return

def UpdateSelectionPanel():
    global pageCount
    SelectionPanel.SetItems([ str(x) for x in range(1,pageCount+1) ])

def PDFUpdateButton(event):
    if path:
        if not pdfV:
            CreatePDFViewerObject()
        UpdatePDFViewer()
    else:
        dlg = wx.MessageDialog(top, "No file selected!", "Error...", wx.OK|wx.ICON_QUESTION)
        dlg.ShowModal()
        top.SetStatusText("No file selected. Please use \"Select File...\"")
        
def UpdatePDFViewer():
    global path
    global pdfV
    if not pdfV:
        CreatePDFViewerObject()
    pdfV.viewer.LoadFile(path)
    pdfV.Show()
    
def GetPageCount():
    global path
    global pageCount
    fh = file(path, 'rb')
    input = pyPdf.PdfFileReader(fh)
    pageCount = input.getNumPages()
    fh.close()
    
def ExportSelected(event):
    if path:
        PagesToExport = SelectionPanel.GetSelections()
        if len(PagesToExport) < 1:
            dlg = wx.MessageDialog(top, "No pages selected!", "Error...", wx.OK|wx.ICON_QUESTION)
            dlg.ShowModal()
            dlg.Destroy()
            top.SetStatusText("No pages selected. Please use the selection panel.")
        else:
            fh = file(path, 'rb')
            DestFileName = wx.GetTextFromUser("Please provide output file name:", 
                "Export File Name?", "Pages from "+os.path.basename(path).split('.')[0], top)
            input = pyPdf.PdfFileReader(fh)
            outputPage = pyPdf.PdfFileWriter()
            for PageToExport in PagesToExport:
                outputPage.addPage(input.getPage(PageToExport))
            outputFileName = os.path.dirname(path)+os.sep+DestFileName+".pdf"
            outputStream = file(outputFileName, "wb")
            outputPage.write(outputStream)
            outputStream.close()
            fh.close()
                
    else:
        dlg = wx.MessageDialog(top, "No file selected!", "Error...", wx.OK|wx.ICON_QUESTION)
        dlg.ShowModal()
        top.SetStatusText("No file selected. Please use \"Select File...\"")
    return
    
def AutoSplit(event):
    global pageCount
    global path
    if path:
        dlg = wx.MessageDialog(top, 
            "This will automatically export individual pages.",
            "Confirm AutoSplit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            fh = file(path, 'rb')
            input = pyPdf.PdfFileReader(fh)
            DestFileName = wx.GetTextFromUser("Please provide output file name:", 
            "Export File Name?", "Pages from "+os.path.basename(path).split('.')[0], top)
            for page in range(0,pageCount):
                outputPage = pyPdf.PdfFileWriter()
                outputPage.addPage(input.getPage(page))
                outputFileName = os.path.dirname(path)+os.sep+DestFileName+" - "+str(page+1)+".pdf"
                outputStream = file(outputFileName, "wb")
                outputPage.write(outputStream)
                outputStream.close()
            fh.close()
    else:
        dlg = wx.MessageDialog(top, "No file selected!", "Error...", wx.OK|wx.ICON_QUESTION)
        dlg.ShowModal()
        top.SetStatusText("No file selected. Please use \"Select File...\"")

def CreatePDFViewerObject():
    global pdfV
    pdfV = PDFViewer(panel, pos=(182,5), size=(450,600))
    pdfV.viewer.UsePrintDirect = ``False``
        
# Create App object to provide event loop.
app = wx.App(redirect=True)

# Create main window.
top = wx.Frame(None, title="Donna's PDF Splitter", size=(300,290))
# Add "Are you sure you want to quit" functionality.
top.Bind(wx.EVT_CLOSE, OnClose)

# Add Menu Bar and Exit command
menuBar = wx.MenuBar()
menu = wx.Menu()
m_exit = menu.Append(wx.ID_EXIT, "E&xit\tAlt-X", "Close window and exit program.")
top.Bind(wx.EVT_MENU, OnClose, m_exit)
menuBar.Append(menu, "&File")
top.SetMenuBar(menuBar)

# Add a status bar.
top.CreateStatusBar(style=0)
top.SetStatusText("Hello")

# Add a panel and BoxSizer for the main Window.
panel = wx.Panel(top)
panel.SetBackgroundColour("white")
box = wx.BoxSizer(wx.HORIZONTAL)

# Add a panel to hold the buttons.

#buttonPanel = wx.Panel(panel, -1, pos=(1,1), size=(100,200))

FileSelectButton = wx.Button(panel, wx.ID_ANY, label="Select File...", pos=(5,10), size=(80,30))
FileSelectButton.Bind(wx.EVT_BUTTON, SelectFile)
ExportButton = wx.Button(panel, wx.ID_ANY, label="Export PDF...", pos=(5,50), size=(80,30))
ExportButton.Bind(wx.EVT_BUTTON, ExportSelected)
IndividualButton = wx.Button(panel, wx.ID_ANY, label="Auto Split", pos = (5, 90), size=(80,30))
IndividualButton.Bind(wx.EVT_BUTTON, AutoSplit)
RefreshPDFViewerButton = wx.Button(panel, wx.ID_ANY, label="View PDF", pos=(5,130), size=(80,30))
RefreshPDFViewerButton.Bind(wx.EVT_BUTTON, PDFUpdateButton)
ExitButton = wx.Button(panel, wx.ID_ANY, label="Quit", pos=(5,170), size=(80,30))
ExitButton.Bind(wx.EVT_BUTTON, OnClose)

SelectionPanel = wx.ListBox(panel, id=wx.ID_ANY, pos=(97, 5), size=(60,200), choices=[], style=wx.LB_MULTIPLE)

# Add a PDFViewer Panel, but leave hidden for now.
CreatePDFViewerObject()

panel.SetSizer(box)
panel.Layout()

# Show main window.
top.Show()

app.MainLoop()
