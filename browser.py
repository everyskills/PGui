#!/usr/bin/python

from datetime import datetime
from os import path as os_path
from threading import Thread

from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtWidgets as qtw
from PyQt5 import QtWebEngineWidgets as qtwe

from .pguiwebview import PguiWebView
from .inactivity_filter import InactivityFilter

from PyQt5.QtNetwork import QSslConfiguration, QSsl

def set_ssl_protocol():
    default_config_ssl = QSslConfiguration.defaultConfiguration()
    default_config_ssl.setProtocol(QSsl.TlsV1_2)
    QSslConfiguration.setDefaultConfiguration(default_config_ssl)

class PGui(qtw.QMainWindow):
    """
    This is the main application window class
    it defines the GUI window for the browser
    """

    def __init__(self, config: object=None, parent=None, debug=None):
        """Construct a MainWindow Object."""
        super().__init__(parent)

        self.debug = debug or (lambda x: None)
        self.config = config

        # self.popup will hold a reference to the popup window
        # if it gets opened
        self.popup = None

        self.setMouseTracking(True)

        self.setWindowTitle('Loading...')

        self.pro_bar = qtw.QProgressBar()

        try:
            if self.config.whitelist:
                whitelist = self.config.whitelist
                if not isinstance(whitelist, list):
                    whitelist = []

                start_host = qtc.QUrl(self.config.start_url).host()
                whitelist.append(start_host)
                self.config.whitelist = set(whitelist) 

            if self.config.progress_bar:
                self.pro_bar.show()
                self.on_load_progress(self.prog)

        except AttributeError:
            pass

        self.__initUI__()

    def adjustTitle(self):
        self.setWindowTitle(self.title())

    def prog(self, value):
        Thread(target=self.set_pro, kwargs={"value": value}, daemon=True).start()

    def set_pro(self, value=0):
        self.pro_bar.setValue(value)
        if value >= 100:
            self.pro_bar.close()

    def __initUI__(self):
        self.create_webprofile()
        self.build_ui()
        self.set_config_data()

    def set_config_data(self):
        g = self.config.geometry

        try:
            self.setWindowTitle(self.config.title)
            self.setWindowOpacity(self.config.opacity)
            self.setWindowIcon(qtg.QIcon(self.config.icon))

            if self.config.maximum_size:
                x, y = self.config.maximum_size
                self.setMaximumSize(qtc.QSize(x, y))
            
            if self.config.minimum_size:
                x, y = self.config.minimum_size
                self.setMinimumSize(qtc.QSize(x, y))

            if self.config.stylesheet:
                self.setStyleSheet(self.config.stylesheet)

            if g: self.setGeometry(g[0], g[1], g[2], g[3])
            else: self.setGeometry(0, 0, self.config.width, self.config.height)

            if not self.config.frame:
                self.setWindowFlags(self.windowFlags() | qtc.Qt.FramelessWindowHint | qtc.Qt.WindowStaysOnTopHint)
                self.setAttribute(qtc.Qt.WA_TranslucentBackground, True)
                # self.setWindowFlag(qtc.Qt.FramelessWindowHint)

            x, y = self.config.move_window
            self.move(qtc.QPoint(x, y))

            if self.config.style_type:
                qtw.QApplication.setStyle(qtw.QStyleFactory.create(self.config.style_type))

            if self.config.bg_color:
                self.browser_window._page.setBackgroundColor(qtg.QColor(self.config.bg_color))

        except AttributeError as at:
            print(f" ! Somthing error in Config function: ({at})")

    
    #####################################
    # PGui Function for using interface #
    #####################################

    ## web load
    def on_load_finished(self, call: object):
        self.browser_window.loadFinished.connect(call)

    def on_load_started(self, call: object):
        self.browser_window.loadStarted.connect(call)

    def on_load_progress(self, call: object):
        self.browser_window.loadProgress.connect(call)

    def set_win_radius(self, radius: float=9.0, w: int=1000, h: int=600):
        self.setWindowFlags(self.windowFlags() | qtc.Qt.FramelessWindowHint | qtc.Qt.WindowStaysOnTopHint)
        self.setFixedSize(w, h)
        path = qtg.QPainterPath()
        path.addRoundedRect(qtc.QRectF(self.rect()), radius, radius)
        mask = qtg.QRegion(path.toFillPolygon().toPolygon())
        self.setMask(mask)

    def web_back(self, count: int=1):
        for _ in range(1, count):
            self.browser_window.back()

    def web_forward(self, count: int=1):
        for _ in range(1, count):
            self.browser_window.forward()

    def web_reload(self, count: int=1):
        for _ in range(1, count):
            self.browser_window.reload()

    def web_stop(self):
        self.browser_window.stop()

    def set_config(self, config: object):
        self.config = config

    ## Window Title
    def set_title(self, text: str):
        self.setWindowTitle(text)
        
    @property
    def width(self):
        return self.width()

    @property
    def height(self):
        return self.height()

    @property
    def title(self):
        return self.windowTitle()
    
    ## Window Icon
    def set_icon(self, icon: str):
        self.setWindowIcon(qtg.QIcon(icon))
        
    @property
    def icon(self):
        return self.windowIcon()

    ## Window Opacity
    def set_opacity(self, value: float):
        return self.setWindowOpacity(value)
    
    @property
    def opacity(self):
        return self.windowOpacity()

    ## Window Role    
    def set_role(self, value: str):
        self.setWindowRole(value)
    
    @property
    def role(self):
        return self.windowRole()
    
    ## Window Frame Less
    def set_frame(self, value: bool=True):
        if not value: self.setWindowFlag(qtc.Qt.FramelessWindowHint)
        else: return None

    @property
    def frame(self):
        return self.windowFlag()
        
    ## Style Sheet (CSS)
    def set_stylesheet(self, txt_or_file: str):
        pass
        if os_path.exists(txt_or_file):
            try:
                with open(txt_or_file, "r") as handle:
                    self.setStyleSheet(handle.read())
            except IOError as e:
                self.debug(f'Problem loading stylesheet file "{self.config.stylesheet}": {e} ''\nusing default style.')
            except AttributeError:
                pass
        else:
            self.setStyleSheet(txt_or_file)

    @property
    def stylesheet(self):
        return self.styleSheet()

    def set_full_screen(self):
        self.showFullScreen()
    
    def set_minimized(self):
        self.showMinimized()

    def set_maximized(self):
        self.showMaximized()

    def set_normal(self):
        self.showNormal()

    def set_bg_color(self, color: str):
        self.browser_window._page.setBackgroundColor(qtg.QColor(color))

    def set_url(self, url: str, type: str=""):
        _type = type.strip().lower()

        if _type == "file":
            _type = "file://"
        elif _type == "url":
            _type = "http://"
        elif _type == "surl":
            _type = "https://"
        else: _type = ""

        if _type == "text":
            self.browser_window.setHtml(url)
        else:
            self.browser_window.setUrl(qtc.QUrl(_type+url))
            
        self.config.start_url = _type+url
    
    def set_html(self, html: str, url: str):
    	self.browser_window.setHtml(html, qtc.QUrl(url))
    	
    def set_icon_theme(self, theme: str):
        qtg.QIcon.setThemeName(theme)

    def set_app_theme(self, theme: str):
        qtw.QApplication.setStyle(qtw.QStyleFactory.create(theme))

    def set_width(self, value: int):
        self.setGeometry(0, 0, value, self.config.height)

    def set_height(self, value: int):
        self.setGeometry(0, 0, self.config.width, value)

    def set_max_size(self, w: int, h: int):
        self.setMaximumSize(qtc.QSize(w, h))

    def set_min_size(self, w: int, h: int):
        self.setMinimumSize(qtc.QSize(w, h))

    def set_fix_size(self, size: object):
        """
        size: str(full), str(max), str(min), (int(w), int(h))
        """
        self._set_fixed_size(size)

    def set_move(self, x: int, y: int):
        self.move(qtc.QPoint(x, y))

    def set_geometry(self, x: int, y: int, w: int, h: int):
        self.setGeometry(x, y, w, h)

    def run_js(self, script: str):
        self.browser_window._page.runJavaScript(script)

    def find_text(self, text: str):
        print(self.browser_window._page.findText(text))

    def show_incpectro(self, url: str="", show: bool=False):
        self.browser_window.show_inspector(url, show)
        
    def set_port(self, port: int):
        self.config.port = port

    ########################################## Web Profile ##########################################
    def create_webprofile(self):
        """Create a webengineprofile to use in all views."""
        # create private/nonprivate webprofile per settings
        try:
            webprofile = (
                qtwe.QWebEngineProfile()
                if self.config.privacy_mode
                else qtwe.QWebEngineProfile.defaultProfile())

            self.debug(f"Browser session is private: {webprofile.isOffTheRecord()}")

            # set the user agent string
            if self.config.user_agent:
                webprofile.setHttpUserAgent(self.config.user_agent)

            # use webprofile
            self.webprofile = webprofile
        except AttributeError:
            pass

    def set_shortcut(self, key: str, call: object):
        shortcut = qtw.QShortcut(qtg.QKeySequence(key), self)
        shortcut.activated.connect(call)

    ########################################## End Web Profile ##########################################
    ## Show Error Box Messages
    def show_error(self, error):
        qtw.QMessageBox.critical(self, "Error", error)
        self.debug(f"Error shown: {error}")

    ########################################## Debug ##########################################
    def debug(self, message):
        """Log or print a message if the global DEBUG is true."""
        if not (self.config.debug or self.config.debug_log):
            pass
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            debug_message = f"{timestamp}:: {message}"
            if self.config.debug:
                print(debug_message)

            if self.config.debug_log:
                try:
                    with open(self.config.debug_log, 'a') as handle:
                        handle.write(debug_message + "\n")
                except IOError as e:
                    print(f"unable to write log '{self.config.debug_log}':  {e}")

    ########################################## End Debug ##########################################
    def __create_action(self, menu, value):
  
        for l in value:
            action = qtw.QAction(l.get("label"), self)

            if l.get("label"):
                action.setText(l.get("label"))

            if l.get("icon") is not None:
                action.setIcon(qtg.QIcon(l.get("icon")))

            if l.get("shortcut"):
                action.setShortcut(qtg.QKeySequence(l.get("shortcut")))

            if l.get("tip") is not None:
                action.setToolTip(l.get("tip"))
                action.setStatusTip(l.get("tip"))

            if l.get("execute") is not None:
                action.__getattr__(l.get("signal", "triggered")).connect(l.get("execute"))

            if not l.get("checkable") is None:
                action.setCheckable(l.get("checkable", False))
            
            if not l.get("show") is None:
                action.setVisible(l.get("show", True))

            action.setEnabled(l.get("enabled", True))

            menu.addAction(action)

    def create_action(self, data, show_menu_bar: bool=True, style: str=""):
        bar = self.menuBar()
        if style: bar.setStyleSheet(style)

        for rk, rv in data.items():
            if show_menu_bar:
                if not rv.get("show"):
                    continue
                menu = bar.addMenu(rk)
            else: 
                menu = self

            self.__create_action(menu, rv.get("data"))

    def build_ui(self):
        """
        Set up the user interface for the main window.
        Unlike the constructor, this method is re-run
        whenever the browser is "reset" by the user.
        """
        self.debug("build_ui")

        inactivity_timeout = self.config.timeout
        curl = self.config.start_url.strip()

        self.screensaver_active = False

        ### Start GUI configuration ###
        self.browser_window = PguiWebView(
            self.config,
            webprofile = self.webprofile,
            debug = self.debug)

        self.browser_window.setObjectName("web_content")
        self.setCentralWidget(self.browser_window)
        self.browser_window.error.connect(self.show_error)

        # Icon theme setting
        qtg.QIcon.setThemeName(self.config.icon_theme)

        self.setCentralWidget(self.browser_window)
        self.debug(f"loading {curl}")

        if curl.startswith(("http", "https", "www", "ftp")):
        	self.browser_window.setUrl(qtc.QUrl(curl))
        else: 
        	self.browser_window.setHtml(curl)

        self._set_fixed_size()
        # Call a reset function after timeout
        if inactivity_timeout != 0:
            self.event_filter = InactivityFilter(inactivity_timeout)
            qtc.QCoreApplication.instance().installEventFilter(self.event_filter)
            self.browser_window.page().installEventFilter(self.event_filter)
        else:
            self.event_filter = None

        self.browser_window.page().setInspectedPage(self.browser_window._page)

    def _set_fixed_size(self, size: object=None):
        """
        size: str(full), str(max), str(min), (int(w), int(h))
        """

        win_size = self.config.window_fix_size if size == None else size

        if not isinstance(win_size, tuple) and win_size.lower() == 'full':
            self.showFullScreen()

        elif not isinstance(win_size, tuple) and win_size.lower() == 'max':
            self.showMaximized()
        
        elif not isinstance(win_size, tuple) and win_size.lower() == "min":
            self.showMinimized()

        elif not isinstance(win_size, tuple) and win_size.lower() == "normal":
            self.showNormal()

        elif win_size:
            self.setFixedSize(int(win_size[0]), int(win_size[1]))
        
        else:
            self.debug(f'Ignoring invalid window size "{win_size}"')

    def zoom_in(self, value: float=0.1):
        """
        Zoom in action callback.
        Note that we cap zooming in at a factor of 3x.
        """
        if self.browser_window.zoomFactor() < 3.0:
            self.browser_window.setZoomFactor(self.browser_window.zoomFactor() + value)

    def zoom_out(self, value: float=0.1):
        """
        Zoom out action callback.
        Note that we cap zooming out at 0.1x.
        """
        if self.browser_window.zoomFactor() > 0.1:
            self.browser_window.setZoomFactor(self.browser_window.zoomFactor() - value)

    def create_tray_icon(self, data: dict):
        if not qtw.QSystemTrayIcon.isSystemTrayAvailable():
            qtw.QMessageBox.critical(None, "Systray", "I couldn't detect any system tray on this system.")
        else:
            self.trayIcon = qtw.QSystemTrayIcon(self)
            self.trayIconMenu = qtw.QMenu(self)
            
            if data.get("icon"):
                self.trayIcon.setIcon(qtg.QIcon(data.get("icon")))
            
            for k, v in data.items():
                self.trayIconMenu.addAction(qtw.QAction(qtg.QIcon(v.get("icon")), k, self, triggered=v.get("execute")))
            
            self.trayIcon.setContextMenu(self.trayIconMenu)
            self.trayIcon.show()

    def sys_alert(self, title: str="", body: str="", icon: int=1, duration: int=1):
        self.trayIcon.showMessage(title, body, icon, duration * 1000)


def base_dir(base: str, file: str):
    return os_path.join(os_path.abspath(os_path.dirname(base)), file)

def default_config():
	from ._config import Config
	config = Config()
	return config

## Start UI
def start_ui(app: object, window: object, fserver: object, 
            duration=0, on_load_finished: bool=False, **fkwargs):
    
    from threading import Thread
    from time import sleep
    from sys import exit

    set_ssl_protocol()
    
    # fkwargs["host"] = "127.0.0.1"
    # fkwargs["port"] = 5000
    # fkwargs["debug"] = True
    fkwargs["threaded"] = True
    fkwargs["use_reloader"] = False

    if fserver is not None:
        Thread(target=fserver.run, daemon=True, kwargs=fkwargs).start()
        print("\n ##--------------- Start Flask Server ---------------##\n")

    if on_load_finished:
        sleep(duration)
        window.browser_window.loadFinished.connect(window.show)
    else: 
        sleep(duration)
        window.show()

    exit(app.exec_())
