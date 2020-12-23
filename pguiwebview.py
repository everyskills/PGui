import subprocess
import re

from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw

from PyQt5 import QtPrintSupport as qtp
from PyQt5 import QtWebEngineWidgets as qtwe
from PyQt5 import QtWebKitWidgets as qtwk
from PyQt5.QtWebKit import QWebSettings

from PyQt5.QtNetwork import QNetworkRequest

from . import messages as msg
from .pguiwebpage import PguiWebPage


class PguiWebView(qtwe.QWebEngineView):
    """This is the webview for the application.

    It represents a browser window, either the main one or a popup.
    It's a simple wrapper around QWebView that configures some basic settings.
    """

    downloads = []
    error = qtc.pyqtSignal(str)

    def __init__(self, config, parent=None, debug=None, **kwargs):
        """Constructor for the PguiWebView

        Parameters:
          - config: The application's runtime configuration
          - parent: The parent widget/window
          - debug:  The function/method for posting debug strings
        """
        super().__init__(parent)
        self.debug = debug or (lambda x: None)
        self.kwargs = kwargs
        self.config = config

        ################################
        # Set up QWebEnginePage object #
        ################################

        self.webprofile = kwargs.get("webprofile")
        # it's important to keep a reference to this
        # Otherwise a generic QWebEnginePage will get used instead
        self._page = PguiWebPage(
            config,
            None,
            self.webprofile,
            debug=self.debug)
        
        self.setPage(self._page)
        
        debug(f"Page profile in use is: {self.page().profile()}")
        debug(f"IS OTR: {self.page().profile().isOffTheRecord()}")

        # configure the QWebSettings
        self._configureSettings(config)

        # zoom factor
        self.setZoomFactor(config.zoom_factor)

        # add printing to context menu if it's allowed
        if config.allow_printing:
            self.print_action = qtw.QAction("Print", self)
            self.print_action.setIcon(qtg.QIcon.fromTheme("document-print"))
            self.print_action.triggered.connect(self.print_webpage)
            self.page().printRequested.connect(self.print_webpage)
            self.print_action.setToolTip("Print this web page")

        # connections for Pguiwebview
        self.page().authenticationRequired.connect(self.auth_dialog)

        # connection to handle downloads
        self.webprofile.downloadRequested.connect(self.onDownloadRequested)

        self.urlChanged.connect(self.onLinkClick)
        self.loadFinished.connect(self.onLoadFinished)


    def show_inspector(self, url: str="", show: bool=False):
        self.webv = qtwk.QWebView(self)
        self.webv.settings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
        self.webv.setUrl(qtc.QUrl(url))

        self.inspector = qtwk.QWebInspector()
        self.inspector.setPage(self.web.page())
        self.inspector.show()

    def _configureSettings(self, config):
        settings = qtwe.QWebEngineSettings.defaultSettings

        try:
            # Popup settings
            settings().setAttribute(
                qtwe.QWebEngineSettings.JavascriptCanOpenWindows,
                config.allow_popups)

            # local storage
            settings().setAttribute(qtwe.QWebEngineSettings.LocalStorageEnabled, True)

            # Plugins
            settings().setAttribute(
                qtwe.QWebEngineSettings.PluginsEnabled,
                config.allow_plugins)
            
            ## everyskills
            settings().setAttribute(qtwe.QWebEngineSettings.JavascriptEnabled, config.allow_js)
            settings().setAttribute(qtwe.QWebEngineSettings.ErrorPageEnabled, config.error_page)
            settings().setAttribute(qtwe.QWebEngineSettings.ShowScrollBars, config.show_scroll_bar)

            settings().setAttribute(qtwe.QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
            settings().setAttribute(qtwe.QWebEngineSettings.AutoLoadImages, True)
            settings().setAttribute(qtwe.QWebEngineSettings.TouchIconsEnabled, True)
            settings().setAttribute(qtwe.QWebEngineSettings.AutoLoadIconsForPage, True)
            settings().setAttribute(qtwe.QWebEngineSettings.AllowRunningInsecureContent, True)

            ## new
            # settings().setAttribute(qtwe.QWebEngineSettings.Accelerated2dCanvasEnabled, True)
            # # settings().setAttribute(qtwe.QWebEngineSettings.AllowAllUnknownUrlSchemes, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.AllowGeolocationOnInsecureOrigins, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.LocalContentCanAccessFileUrls, True)
            settings().setAttribute(qtwe.QWebEngineSettings.JavascriptCanAccessClipboard, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.HyperlinkAuditingEnabled, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.ScrollAnimatorEnabled, True)
            # # settings().setAttribute(qtwe.QWebEngineSettings.AllowUnknownUrlSchemesFromUserInteraction, True)
            settings().setAttribute(qtwe.QWebEngineSettings.AllowWindowActivationFromJavaScript, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.PrintElementBackgrounds, True)

            # settings().setAttribute(qtwe.QWebEngineSettings.ScreenCaptureEnabled, True)
            settings().setAttribute(qtwe.QWebEngineSettings.JavascriptCanPaste, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.FullScreenSupportEnabled, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.LinksIncludedInFocusChain, True)

            # settings().setAttribute(qtwe.QWebEngineSettings.HyperlinkAuditingEnabled, True)

            # settings().setAttribute(qtwe.QWebEngineSettings.DnsPrefetchEnabled, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.ErrorPageEnabled, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.XSSAuditingEnabled, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.PdfViewerEnabled, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.SpatialNavigationEnabled, True)
            # settings().setAttribute(qtwe.QWebEngineSettings.HyperlinkAuditingEnabled, True)


        except AttributeError as ae:
            print(f" ! WebSettings-Error: {ae}")

        finally:
            self.debug("settings configured")

    def createWindow(self, wintype):
        """Handle requests for a new browser window.

        Method called whenever the browser requests a new window
        (e.g., <a target='_blank'> or window.open()).
        Overridden from QWebEngineView to allow for popup windows, if enabled.
        """
        self.debug(f"Popup Requested with argument: {wintype}")
        if self.config.allow_popups:
            self.debug(self.kwargs)
            # we need to create a widget to contain the webview
            # since QWebEngineView objects apparently don't work as top-levels?
            self.popup = qtw.QWidget()
            self.popup.setLayout(qtw.QVBoxLayout())

            webview = PguiWebView(
                self.config,
                parent=None,
                debug=self.debug,
                **self.kwargs)

            self.popup.layout().addWidget(webview)
            # This assumes the window manager has an "X" icon
            # for closing the window somewhere to the right.
            webview.setObjectName("web_content")
            self.popup.setWindowTitle("Click the 'X' to close this window! ---> ")
            
            webview.page().windowCloseRequested.connect(self.popup.close)
            self.popup.show()

            return webview

        else:
            self.debug(f"Popup not loaded on {self.url().toString()}")

    def contextMenuEvent(self, event):
        """
        Handle requests for a context menu in the browser.
        Overridden from QWebView,
        to provide right-click functions according to user settings.
        """

        # menu = qtw.QMenu(self)
        # for action in [
        #         qtwe.QWebEnginePage.Back,
        #         qtwe.QWebEnginePage.Forward,
        #         qtwe.QWebEnginePage.Reload,
        #         qtwe.QWebEnginePage.Stop,
        #         qtwe.QWebEnginePage.InspectElement]:

        #     action = self.pageAction(action)
            
        #     if action.isEnabled():
        #         menu.addAction(action)

        # if self.config.allow_printing:
        #     menu.addAction(self.print_action)

        # menu.exec_(event.globalPos())
        pass
        
    def auth_dialog(self, requestUrl, authenticator):
        """Handle requests for HTTP authentication

        This is called when a page requests authentication.
        It might be nice to actually have a dialog here,
        but for now we just use the default credentials from the config file.
        """
        self.debug(f"Auth required on {requestUrl.toString()}")
        default_user = self.config.default_user
        default_password = self.config.default_password
        if (default_user):
            authenticator.setUser(default_user)
        if (default_password):
            authenticator.setPassword(default_password)

    def onDownloadRequested(self, download_item):
        """Handle requests to open non-web content

        Called whenever a download is requested.
        """
        dl_url = download_item.url().toString()
        dl_mime = download_item.mimeType()
        dl_path = download_item.path()

        if not self.config.allow_external_content:
            self.debug(f"Download request ignored for {dl_url} (not allowed)")
            download_item.cancel()
            self.error.emit('Unable to download file: downloads have been disabled.')

        elif not self.config.content_handlers.get(dl_mime):
            self.debug(f'Download request ignored for mime type {dl_mime} (no handler)')
            download_item.cancel()
            self.error.emit(
                f'Unable to download file: no valid handler for "{dl_mime}"'
                f'{self.config.content_handlers}')

        else:
            self.downloads.append(download_item)
            self.debug(f"Starting download of url {dl_url} of type {dl_mime}")

            if self.url().toString() in ('', 'about:blank'):
                self.setHtml(msg.DOWNLOADING_MESSAGE.format(
                    filename=dl_path,
                    mime_type=dl_mime,
                    url=dl_url
                    ))
            else:
                download_item.accept()

            download_item.finished.connect(self.display_downloaded_content)

    def display_downloaded_content(self):
        """Open downloaded non-html content in a separate application.

        Called when an unsupported content type is finished downloading.
        """

        finished = [x for x in self.downloads if x.isFinished]
        self.debug(f'display downloaded content for downloads: {finished}')

        for dl in finished:
            self.downloads.remove(dl)
            mime = dl.mimeType()
            path = dl.path()
            handler = self.config.content_handlers.get(mime)
            try:
                subprocess.Popen([handler, path])

            except subprocess.CalledProcessError as e:
                self.error.emit(f'Error launching process "{handler}": {e}')

            except FileNotFoundError as e:
                self.error.emit(f'Cannot open: configured handler "{handler}" not found: {e}')

            except Exception as e:
                self.error.emit(f'Unknown error handling file: {e}')

            # Sometimes downloading files opens an empty window.
            # So if the current window has no URL, close it.
            if self.url().toString() in ('', 'about:blank'):
                self.close()

    def onLinkClick(self, url):
        """Handle clicked hyperlinks.

        Overridden from QWebView.
        Called whenever the browser navigates to a URL;
        handles the whitelisting logic and does some debug logging.
        """
        self.debug(f"Request URL: {url.toString()}")
        if not url.isEmpty():
            # If whitelisting is enabled, and this isn't the start_url host,
            # check the url to see if the host's domain matches.
            start_url_host = qtc.QUrl(self.config.start_url).host()
            if all([
                    self.config.whitelist,
                    url.host() != start_url_host,
                    url.toString() != 'about:blank'
                    ]):

                site_ok = False
                pattern = re.compile(str(r"(^|.*\.)(" + "|".join(
                    [re.escape(w)
                     for w
                     in self.config.whitelist]
                ) + ")$"))

                self.debug(f"Whitelist pattern: {pattern.pattern}")

                if re.match(pattern, url.host()):
                    site_ok = True

                if not site_ok:
                    if self.config.page_unavailable_html:
                        self.setHtml(self.config.page_unavailable_html)
                    
                    self.back()
                    self.debug(f"Site violates whitelist: {url.host()}, {url.toString()}")
                    # self.error.emit(self.config.page_unavailable_html) #format(**self.config))

            if not url.isValid():
                self.debug(f"Invalid URL {url.toString()}")

            else:
                self.debug(f"Load URL {url.toString()}")

    def onLoadFinished(self, ok):
        """Handle loadFinished events.

        Overridden from QWebEngineView.
        This function is called when a page load finishes.
        We're checking to see if the load was successful;
        if it's not, we display either the 404 error (if
        it's just some random page), or a "network is down" message
        (if it's the start page that failed).

        Unfortunately this method is broken. 'OK' is not a reliable value,
        it often shows false when there is no apparent problem at all,
        and to make things worse, QtWebEngine has no facility for inspecting
        the errors that lead to a false 'OK'.
        """
        print(f"LoadOK reported: {ok}")
        # return True

        # This is the code that should run.
        if not ok:
            start_url = self.config.start_url
            
            start_host = qtc.QUrl(start_url).host()
            start_path = qtc.QUrl(start_url).path().rstrip('/')
            
            failed_host = self.url().host()
            failed_path = self.url().path().rstrip('/')

            if all([
                    failed_host == start_host,
                    failed_path == start_path
                    ]):
                
                if self.config.network_down_html:
                    self.setHtml(self.config.network_down_html, qtc.QUrl()) # .format(self.config)
                    self.debug("Start Url doesn't seem to be available;\n displaying error")
            else:
                if self.config.page_unavailable_html:
                    self.debug(f"load failed on URL: {self.page().requestedUrl().toString()}")
                    self.setHtml(self.config.page_unavailable_html, qtc.QUrl()) # .format(self.config)
        return True

    def print_webpage(self):
        """Print the webpage to a printer.

        Callback for the print action.
        Should show a print dialog and print the webpage to the printer.
        """
        if self.print_settings.get("mode") == "high":
            printer = qtp.QPrinter(mode=qtp.QPrinter.HighResolution)
        else:
            printer = qtp.QPrinter(mode=qtp.QPrinter.ScreenResolution)

        if self.print_settings:
            if self.print_settings.get("size_unit"):
                try:
                    unit = getattr(
                        QPrinter,
                        self.print_settings.get("size_unit").capitalize()
                    )
                except NameError:
                    self.debug(
                        f"Specified print size unit '{self.print_settings.get('size_unit')}'"
                        " not found, using default."
                    )
                    unit = qtp.QPrinter.Millimeter
            else:
                unit = qtp.QPrinter.Millimeter

            margins = (
                list(self.print_settings.get("margins")) or
                list(printer.getPageMargins(unit))
            )
            margins += [unit]
            printer.setPageMargins(*margins)

            if self.print_settings.get("orientation") == "landscape":
                printer.setOrientation(qtp.QPrinter.Landscape)
            else:
                printer.setOrientation(qtp.QPrinter.Portrait)

            if self.print_settings.get("paper_size"):
                printer.setPaperSize(qtc.QSizeF(
                    *self.print_settings.get("paper_size")
                ), unit)

            if self.print_settings.get("resolution"):
                printer.setResolution(
                    int(self.print_settings.get("resolution"))
                )

        if not self.print_settings.get("silent"):
            print_dialog = qtp.QPrintDialog(printer, self)
            print_dialog.setWindowTitle("Print Page")
            if not print_dialog.exec_() == qtw.QDialog.Accepted:
                return False

        self.print_(printer)
        return True

# ### END PGUIWEBVIEW DEFINITION ### #
