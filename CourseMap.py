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
        programString = "NE BME ECE SYDE CHE AE CIVE ENVE GENE GEOE ME MTE MSCI CS SE PHYS CHEM MATH AMATH STAT"
        self.urls = [templateURL.format(p) for p in programString.split(' ')]
        
        self.sheet = "CourseMap.csv"
        self.indexTemplate = "template.html"
        self.index = "index.html"
    
    def guide(self):
        print((
            "1. Get data: data = courseMap(*urls)\n"
            "2. Save data: writeCSV(file, source)\n"
            "3. Load saved data: data = parseCSV(file)\n"
            "4. Create HTML: generateHTML(source, template, dest)"
        ))

# =================================================

def scrapeCourses(url):
    courses = list()
    r = request.urlopen(url)
    print("\t", r.status, url)
    doc = parse(r)
    for i in doc.iterfind(".//center/div[@class='divTable']"):
        course = {
            'code': '',
            'title': '',
            'prereq': '',
            'antireq': '',
            'term': '',
            'ID': '',
            'description': ''
        }
        
        course['code'] = re.sub(
            "^([A-Z]+)([A-Z0-9]+)",
            "\\1 \\2",
            i.find(".//div[@class='divTableCell']/strong/a[@name]").attrib['name']
        )

        course['title'] = i.find(".//div[@class='divTableCell colspan-2']/strong").text

        for j in i.iterfind(".//div[@class='divTableCell colspan-2']/em"):
            if j.text:
                if "Prereq" in j.text:
                    course['prereq'] = j.text.lstrip().replace("Prereq: ", '')
                elif "Antireq" in j.text:
                        course['antireq'] = j.text.lstrip().replace("Antireq: ", '')
        
        course['ID'] = i.find(".//div[@class='divTableCell crseid']").text.split(' ')[-1]

        for j in i.iterfind(".//div[@class='divTableCell colspan-2']"):
            if j.text:
                course['term'] = ''.join(re.findall("\[Offered:\s+([^]]+)]", j.text))
                course['description'] = re.sub("\s*\[Offered: [^]]+].*$", '', j.text, flags=re.M)
                
        courses.append(course)
        
    return courses

# -------------------------------------------------

def courseMap(*urls):
    print("scraping web...")
    data = []
    for url in urls:
        data += scrapeCourses(url)
    return data
            
# -------------------------------------------------

def writeCSV(file, source):
    with open(file, 'w', encoding='utf8', newline='') as f:  
        writer = csv.DictWriter(f, fieldnames=source[0].keys())
        writer.writeheader()
        writer.writerows(source)
    print("wrote to file: %s" % os.path.abspath(file))

# -------------------------------------------------

def parseCSV(file):
    with open(file, 'r') as f:
        print("loading data from file: %s" % os.path.abspath("CourseMap.csv"))
        reader = csv.DictReader(f)
        return list(reader)

# -------------------------------------------------

def generateHTML(source, template="template.html", dest="index.html"):
    
    with open(template, 'r') as f:
        soup = BeautifulSoup(f.read(), features='lxml')
        print("using template: %s" % os.path.abspath(template))
        
    html = str()
    for course in source:
        html += "<tr><td><a id='%s'><br /><br /></a></td></tr>" % course['code'].replace(' ', '').lower()
        html += "<tr>"
        for k, v in course.items():
            html += "<td class='%s'>%s</td>" % (k, v)
        html += "</tr>"
    
    for code in [d['code'] for d in source]:
        html = re.sub(
            r"(\b%s\b(?:\W*(?:<a href='#\w{5,8}'>)?\d{3}[A-Z]?(?:<\/a>)?\W*)*(?: |\/))(\b%s\b)" % tuple(code.split(' ')), 
            r"\1<a href='#{}'>\2</a>".format(code.replace(' ', '').lower()),
            html
        )
    
    tbody = BeautifulSoup(html, features='lxml')
    soup.body.table.tbody.append(tbody)
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
        print("wrote to file: %s" % os.path.abspath(dest))

# -------------------------------------------------

def main():
    test = CurrentTest()
    try:
        data = parseCSV(test.sheet)
    except FileNotFoundError:
        data = courseMap(*test.urls)
        writeCSV(test.sheet, data)
    generateHTML(data, test.indexTemplate, test.index)
    
# -------------------------------------------------

if __name__ == "__main__":
    main()
