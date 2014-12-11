# -*- coding: utf-8 -*- 

import os
import cgi
import cgitb; cgitb.enable()
import logging
#from renderer import Renderer

def main():
    print "Content-type:text/html\n"
    print "args:<ul>",
    arguments = cgi.FieldStorage()
    for k in sorted(arguments.keys()):
        print "<li>%s %s</li>" % (k, arguments[k].value),
    print "</ul>",

if __name__ == "__main__":
    main()

#print "<br>"
#print image_names
