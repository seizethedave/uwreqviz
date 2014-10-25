#!/usr/bin/env python3

import sys
import os
from urllib import request
import re

import graphviz
from bs4 import BeautifulSoup

kCourseTitleExpression = re.compile(
 "(?P<number>[A-Z]* [0-9]{3}) (?P<name>[^\(]*)\((?P<credits>[^\)]*)")

class Course(object):
    """
    Represents a course.
    Contains prerequisites.
    """
    def __init__(self, number, name, credits):
        self.number = number
        self.name = name
        self.credits = credits

    @classmethod
    def FromSoupTag(cls, soupTag):
        title = soupTag.p.b.text
        groups = re.match(kCourseTitleExpression, title).groups()
        number, name, credits = (g.strip() for g in groups)
        return cls(number, name, credits)

def ProduceGraph(url):
    response = request.urlopen(url)
    soup = BeautifulSoup(response.read())
    response.close()

def LooksLikeCourseElement(tag):
    return (tag.name == "a" and 'name' in tag.attrs
     and tag.contents[0].name == "p"
     and tag.p.contents[0].name == "b")

def CoursesFromSoup(soup):
    """
    Yields Course objects for the given soup document.
    """
    for courseTag in soup.find_all(LooksLikeCourseElement):
        yield Course.FromSoupTag(courseTag)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            (
            "Usage:\n"
            "   {0} [course listing URL]\n\n"
            "An example course listing URL can be seen here:\n"
            "   http://www.washington.edu/students/crscat/cse.html"
            ).format(os.path.basename(sys.argv[0]))
        )
        sys.exit(1)

    listingUrl = sys.argv[1]
    ProduceGraph(listingUrl)
