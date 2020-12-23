# PGui
simple PyQt5 Web Browser for View You HTML, CSS and JS Code with Flask Framework

# Why PGui
You can use PGui for convert Your Web Site to Desktop app using Flask Framework

# Get Start with any web site

```python
from pgui import PGui, start_ui, default_config, qtw

app = qtw.QApplication([])

url = "https://www.example.com"
cfg = default_config()
window = PGui(cfg)

window.set_url(url)

if __name__ == '__main__':
	start_ui(app, window, None)
```
# Get Start with Flask
```python
from pgui import PGui, start_ui, default_config, base_dir, qtw
from flask import Flask

app = qtw.QApplication([])
flapp = Falsk(__name__)

cfg = default_config()
window = PGui(cfg)

@flapp.route("/")
def home():
    return "Welcom To PGui Framework"
    
if __name__ == '__main__':
	start_ui(app, window, flapp)
```
