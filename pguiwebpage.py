# ### PGUIWEBPAGE #### #

from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5 import QtGui as qtg
from PyQt5 import QtWebKitWidgets as qtwk

from . import messages as msg

class PguiWebPage(QWebEnginePage):
    """Subclassed QWebEnginePage,
    representing the actual web page object in the browser.

    This was subclassed so that some functions can be overridden.
    """

    def __init__(self, config, parent=None, profile=None, debug=None):
        """Constructor for the class"""
        self.debug = debug or (lambda x: None)
        self.config = config
        if not profile:
            super().__init__(parent)
        else:
            super().__init__(profile, parent)
        
        debug(f"Profile is: {self.profile()}")

        self.featurePermissionRequested.connect(self.onFeaturePermissionRequested)

    def onFeaturePermissionRequested(self, url, feature):
        if feature in (QWebEnginePage.MediaAudioCapture, 
            QWebEnginePage.MediaVideoCapture, 
            QWebEnginePage.MediaAudioVideoCapture):
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionGrantedByUser)
        else:
            self.setFeaturePermission(url, feature, QWebEnginePage.PermissionDeniedByUser)

    def javaScriptConsoleMessage(self, level, message, line, sourceid):
        """
        Handle console.log messages from javascript.
        Overridden from QWebEnginePage so that we can
        send javascript errors to debug.
        """

        self.debug(f'Javascript Error in "{sourceid}" line {line}: {message}')

    def javaScriptConfirm(self, frame, msg):
        """
        Handle javascript confirm() dialogs.
        Overridden from QWebEnginePage so that we can (if configured)
        force yes/no on these dialogs.
        """

        if self.config.force_js_confirm == "accept":
            return True

        elif self.config.force_js_confirm == "deny":
            return False
            
        else:
            return super().javaScriptConfirm(self, frame, msg)

    def javaScriptAlert(self, frame, msg):
        if not self.config.suppress_alerts:
            return super().javaScriptAlert(frame, msg)

    def certificateError(self, error):
        """
        Handle SSL errors in the browser.
        Overridden from QWebEnginePage.
        Called whenever the browser encounters an SSL error.
        Checks the ssl_mode and responds accordingly.
        Doesn't seem to get called in Qt 5.4
        """

        self.debug("certificate error")
        
        if self.config.ssl_mode == 'ignore':
            self.debug("Certificate error ignored")
            self.debug(error.errorDescriptforce_js_confirmion())
            return True
            
        else:
            self.setHtml(
                msg.CERTIFICATE_ERROR.format(
                    url=error.url().toString(),
                    start_url=self.config.start_url))

    def renderProcessTerminated(self, *args):
        self.debug("RenderProcessTerminated: {}".format(args))
        super().renderProcessTerminated(args)

# ### END PGUIWEBPAGE DEFINITION ### #
