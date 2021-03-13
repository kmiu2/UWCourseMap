# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 22:24:45 2021

@author: me
"""

from urllib import request
from bs4 import BeautifulSoup
from lxml.html import parse
from lxml import etree
import xml.dom.minidom
import re
import json
import csv


def printXML(XMLString):
    dom = xml.dom.minidom.parseString(XMLString)
    print(dom.toprettyxml())

def printJSON(obj):
    print(json.dumps(obj, indent=4, sort_keys=True))
    
# -------------------------------------------------

def scrapeCourses(url):
    courses = list()
    r = request.urlopen(url)
    print(r.status)
    doc = parse(r)
#    printXML(etree.tostring(doc))
    for i in doc.iterfind(".//center/div[@class='divTable']"):
        course = {
            'code': '',
            'ID': '',
            'title': '',
            'prereq': '',
            'antireq': '',
            'term': '',
            'description': ''
        }
        
        course['code'] = i.find(".//div[@class='divTableCell']/strong/a[@name]").attrib['name']

        course['ID'] = i.find(".//div[@class='divTableCell crseid']").text.split(' ')[-1]

        course['title'] = i.find(".//div[@class='divTableCell colspan-2']/strong").text

        for j in i.iterfind(".//div[@class='divTableCell colspan-2']/em"):
            if j.text:
                if "Prereq" in j.text:
                    course['prereq'] = j.text.lstrip().replace("Prereq: ", '')
                elif "Antireq" in j.text:
                        course['antireq'] = j.text.lstrip().replace("Antireq: ", '')
        
        for j in i.iterfind(".//div[@class='divTableCell colspan-2']"):
            if j.text:
                course['term'] = ''.join(re.findall("\[Offered:\s+([^]]+)]", j.text))
                course['description'] = re.sub("\s*\[Offered: [^]]+].*$", '', j.text, flags=re.M)
                
        courses.append(course)
        
    return courses

# -------------------------------------------------

def courseMap():
    templateURL = "https://ucalendar.uwaterloo.ca/2122/COURSE/course-{}.html"
    programString = "NE BME ECE SYDE CHE AE CIVE ENVE GEOE ME MTE MSCI CS SE PHYS CHEM MATH"
    programs = programString.split(' ')
    data = []

    for p in programs:
        print(p)
        data += scrapeCourses(templateURL.format(p))
    
    return data
            
# -------------------------------------------------

def writeCSV(file, source, header):
    with open(file, 'w', encoding='utf8', newline='') as f:  
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(source)

# -------------------------------------------------

def generateHTML(source, header):

    html = "<html>"
    html += """
        <head><style>
        body {color: white; background-color: black;}
        th {
            position: sticky;
            top: 0;
            background: #30003b;
            padding: 7px;
        }
        #topBtn {
            display: none;
            position: fixed;
            bottom: 7px;
            right: 15px;
            z-index: 99;
            font-size: 18px;
            border: none;
            outline: none;
            background-color: blue;
            color: white;
            cursor: pointer;
            padding: 7px;
            border-radius: 49px;
        }
        #topBtn:hover {background-color: #555;}
        </style></head>
    """
    html += "<body>"
    html += """
        <button onclick="toTop()" id="topBtn" title="Go to top">Top</button>
        <script>
        var btn = document.getElementById("topBtn");
        window.onscroll = function() {showOnScroll()};
        function showOnScroll() {
            if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
                btn.style.display = "block";
            } else {
                btn.style.display = "none";
            }
        }
        function toTop() {
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        }
        </script>
    """
    html += "<table><tbody>"
    html += "<tr>"
    for h in header:
        html += "<th>%s</th>" % h
    html += "</tr>"
    
    for course in source:
        html += "<tr><td><a id='{}'><br /></a></td></tr>".format(course['code'].lower())
        html += "<tr>"
        for h in header:
            html += "<td>%s</td>" % course[h]
        html += "</tr>"

    html += "</tbody></table>"
    
    html +="</body></html>"
    
    for code in [d['code'] for d in source]:
        program, number = re.findall("^([A-Z]+)([A-Z0-9]+)", code, flags=re.M)[0]
        html = re.sub(
            "({}[^A-Z]* )({})".format(program, number), 
            "\\1<a href='#{}\'>\\2</a>".format(code.lower()),
            html
        )
            
    return html

# -------------------------------------------------

def main():
    data = courseMap()
#    printJSON(data)
    fieldnames = ('code', 'title', 'prereq', 'antireq', 'term', 'ID', 'description')
#    writeCSV('courseMap.csv', data, fieldnames)
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(generateHTML(data, fieldnames))
    
# -------------------------------------------------

main()
