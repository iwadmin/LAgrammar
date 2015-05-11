from language_check import LanguageTool as lc
import urllib.request as ul

lc._start_server()
ul.urlopen('http://127.0.0.1:8081',bytes("text=asd%0A&language=en-GB","UTF-8"),300)
