#!/usr/bin/env python3

import sys
import os
from urllib import request
import re

import graphviz
from bs4 import BeautifulSoup

kCourseTitleExpression = re.compile(
 "(?P<number>[A-Z]* [0-9]{3}) (?P<name>[^\(]*)\((?P<credits>[^\)]*)")
kCourseNumberExpression = re.compile("[A-Z]+ [0-9]+")

class Course(object):
    """
    Represents a course.
    """
    def __init__(self, number, name, credits,
     prerequisiteNumbers=(), prerequisiteText=None):
        self.number = number
        self.name = name
        self.credits = credits
        self.prerequisiteNumbers = prerequisiteNumbers
        self.prerequisiteText = prerequisiteText

    @classmethod
    def FromSoupTag(cls, soupTag):
        title = soupTag.p.b.text
        groups = re.match(kCourseTitleExpression, title).groups()
        number, name, credits = (g.strip() for g in groups)

        # Now find the prerequisites string.
        courseText = soupTag.text
        kReqToken = "Prerequisite: "
        i = courseText.find(kReqToken)

        if i != -1:
            i += len(kReqToken)
            reqsText = courseText[i:courseText.find(".", i)]
            # To do this really nicely, we should break the prerequisite
            # language down to their OR/AND components, along with info about
            # "recommended"/"instructor permission" etc.
            prerequisites = re.findall(kCourseNumberExpression, reqsText)
        else:
            # None listed.
            prerequisites = ()
            reqsText = None

        return cls(number, name, credits, prerequisites, reqsText)

    @staticmethod
    def LinkPrerequisites(courses):
        """
        Establishes links based on prerequisites.
        """
        courseLookup = {course.number: course for course in courses}

        for course in courses:
            # TODO: Create dummy Course items for course numbers outside the list.
            prerequisites = (courseLookup.get(p) for p in course.prerequisiteNumbers)
            course.prerequisites = list(filter(None, prerequisites))

def ProduceGraph(url):
    response = request.urlopen(url)
    soup = BeautifulSoup(response.read())
    response.close()
    courses = CoursesFromSoup(soup)
    Course.LinkPrerequisites(courses)

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
