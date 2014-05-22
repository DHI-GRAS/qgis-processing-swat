from processing.core.ProcessingConfig import ProcessingConfig

class WG9HMUtils:
    MAPWINDOW_FOLDER = 'MAPWINDOW_FOLDER'
    
    @staticmethod
    def mapwindowPath():
        folder = ProcessingConfig.getSetting(WG9HMUtils.MAPWINDOW_FOLDER)
        if folder is None:
            folder = "C:\Program Files (x86)\MapWindow\MapWindow.exe"
            
        return folder


