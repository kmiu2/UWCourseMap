# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 22:24:45 2021

@author: me
"""

from urllib import request
from bs4 import BeautifulSoup
from lxml.html import parse
import re
import csv
import os

# =================================================

class CurrentTest:
    def __init__(self):
        templateURL = "https://ucalendar.uwaterloo.ca/2122/COURSE/course-{}.html"
        programString = "NE BME ECE SYDE CHE AE CIVE ENVE GENE GEOE ME MTE MSCI CS SE PHYS CHEM MATH STAT"
        self.urls = [templateURL.format(p) for p in programString.split(' ')]
        self.headers = ('code', 'title', 'prereq', 'antireq', 'term', 'ID', 'description')
    
    def instructions(self):
        print((
            "1. Get data: data = courseMap(*urls)\n"
            "2. Save data: writeCSV(file, source, headers\n"
            "3. Load saved data: data = parseCSV(file)\n"
            "4. Create HTML: generateHTML(source, headers)"
        ))

# =================================================

def scrapeCourses(url):
    courses = list()
    r = request.urlopen(url)
    print(r.status, url)
    doc = parse(r)
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
        
        course['code'] = re.sub(
            "^([A-Z]+)([A-Z0-9]+)",
            "\\1 \\2",
            i.find(".//div[@class='divTableCell']/strong/a[@name]").attrib['name']
        )

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

def courseMap(*urls):
    data = []

    for url in urls:
        data += scrapeCourses(url)
    
    return data
            
# -------------------------------------------------

def writeCSV(file, source, header):
    with open(file, 'w', encoding='utf8', newline='') as f:  
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(source)
    print("wrote to file: %s" % os.path.abspath(file))

# -------------------------------------------------

def parseCSV(file):
    with open(file, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

# -------------------------------------------------

def generateHTML(source, header):

    HTML = "<html>"
    HTML += """
        <head><style>
        body {color: white; background-color: black;}
        th {
            position: sticky;
            top: 0;
            background: #30003b;
        }
        .code {white-space: nowrap;}
        a {
            color: HotPink;
            font-weight: 777;
            background-color: transparent;
            text-decoration: none;
        }
        a:hover {color: Gold;}
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
    HTML += "<body>"
    HTML += """
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
    HTML += "<table><tbody>"
    HTML += "<tr>"
    for h in header:
        HTML += "<th class='%s'>%s</th>" % (h, h)
    HTML += "</tr>"
    
    for course in source:
        HTML += "<tr><td><a id='{}'><br /></a></td></tr>".format(course['code'].replace(' ', '').lower())
        HTML += "<tr>"
        for h in header:
            HTML += "<td class='%s'>%s</td>" % (h, course[h])
        HTML += "</tr>"

    HTML += "</tbody></table>"
    HTML +="</body></html>"
    
    for code in [d['code'] for d in source]:
        HTML = re.sub(
            r"(\b{}\b(?:\W*(?:<a href='#\w{{5,8}}'>)?\d{{3}}[A-Z]?(?:<\/a>)?\W*)*(?: |\/))(\b{}\b)".format(*code.split(' ')), 
            r"\1<a href='#{}'>\2</a>".format(code.replace(' ', '').lower()),
            HTML
        )
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(BeautifulSoup(HTML, features='lxml').prettify())
        print("wrote to file: %s" % os.path.abspath('index.html'))

# -------------------------------------------------

def main():
    test = CurrentTest()
    try:
        data = parseCSV("CourseMap.csv")
        print("using file: %s" % os.path.abspath("CourseMap.csv"))
    except FileNotFoundError:
        print("CourseMap.csv not found, scraping web")
        data = courseMap(*test.urls)
        writeCSV('CourseMap.csv', data, test.headers)
    generateHTML(data, test.headers)
    
# -------------------------------------------------

if __name__ == "__main__":
    main()
