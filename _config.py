#!/usr/bin/python3

def get_base_dir(file: str):
	from os import path
	return path.join(path.abspath(path.dirname(__file__)), file)

def fr(file: str):
	return open(file, "r").read()

## Config Window
class Config():
	def __init__(self):
		## Main/User Config
		self.title           = "PGui Framework"
		self.bg_color        = "#fff" # "#358eef"
		self.icon            = get_base_dir("icon.png")
		self.start_url 		 = fr(get_base_dir("index.html")) # url for show
		self.timeout 		 = 1000
		self.zoom_factor 	 = 0
		self.icon_theme 	 = "breeze" # gtk, breeze, oxygen, windows, etc...
		self.style_type      = "breeze" # gtk, breeze, oxygen, windows, etc...
		self.width           = 1000
		self.height          = 600
		self.maximum_size    = () # w, h
		self.minimum_size    = () # w, h
		self.window_fix_size = () # w, h
		self.opacity         = 1
		self.move_window     = (0, 0) # x, y
		self.geometry        = () # x, y, w, h
		self.frame           = True
		self.whitelist       = []
		self.error_page      = True
		self.allow_js        = True
		self.show_scroll_bar = True
		self.stylesheet      = "" # open(get_base_dir("web/css/style.css")).read() # use this for style main window
		
		## More Config
		self.privacy_mode 	  = True
		self.user_agent       = "" # WebKit
		self.allow_popups 	  = True
		self.allow_plugins 	  = True
		self.allow_printing   = True
		self.force_js_confirm = "accept" # (ask, deny)
		self.suppress_alerts  = False
		self.ssl_mode 		  = "strict" # (strict, ignore)
		self.progress_bar     = False

		## web settings
		self.allow_external_content = False # download configur
		self.page_unavailable_html  = "" # self.fr("examples/custom404.html")
		self.network_down_html      = "" # self.fr("examples/custom_network_down.html")
		
		## More Advanced Settings
		self.accelerated_2d_canvas  = False
		self.local_storage          = True
		self.local_content_can_access_remote_urls = True
		self.auto_load_images = True
		self.touch_icons = True
		self.auto_load_icons_for_page = True
		self.allow_running_insecure_content = True
		self.allow_all_unknown_url_schemes = False
		self.allow_geolocation_on_insecure_origins = False
		self.local_content_can_access_file_urls = False
		self.javascript_can_access_clipboard = True
		self.scroll_animator = False
		self.allow_unknown_url_schemes_from_user_interaction = False
		self.allow_window_activation_from_js = True
		self.print_element_backgrounds = False
		self.screen_capture = False
		self.javascript_can_paste = True
		self.full_screen_support = False
		self.links_included_in_focus_chain = False
		self.dns_prefetch = False
		self.XSS_auditing = False
		self.pdf_viewer = False
		self.spatial_navigation = False
		self.hyperlink_auditing = False

		## Printers Settings
		self.print_settings = {
		    "silent": True,
		    "orientation": "landscape",
		    "size_unit": "millimeter",
		    "paper_size": [500, 1000],
		    "margins": [5, 5, 8, 8],
		    "resolution": 300,
		    "mode": "screen"
		    }
		
		self.content_handlers = {
		    "application/pdf": "okular",
		    "application/vnd.oasis.opendocument.text": "libreoffice",
		    "application/zip": "test_test_application",
		    "application/mp4": "vlc"
		    }