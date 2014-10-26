#!/usr/bin/env python3

import sys
import os
import re
from urllib import request

from graphviz import Digraph
from bs4 import BeautifulSoup

kCourseTitleExpression = re.compile(
 r"(?P<number>[A-Z]+ [\d]+) (?P<name>[^(]*)\((?P<credits>[^)]*)")
kCourseNumberExpression = re.compile(r"[A-Z][A-Z ]+[\d]+")

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

    def __repr__(self):
        return u"Course({0})".format(self.number)

    @property
    def displayName(self):
        return u"{0} {1}".format(self.number, self.name)

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
            prerequisites = []
            reqsText = None

        return cls(number, name, credits, prerequisites, reqsText)

    @staticmethod
    def LinkPrerequisites(courses):
        """
        Given a sequence of courses, establishes 'prerequisites' properties
        based on the 'prerequisiteNumbers' property.
        """
        courseLookup = {course.number: course for course in courses}

        for course in courses:
            # TODO: Create dummy Course items for course numbers outside the
            # list.
            prerequisites = (courseLookup.get(p)
             for p in course.prerequisiteNumbers)
            course.prerequisites = list(filter(None, prerequisites))

def ProduceGraph(url):
    courses = CoursesFromUrl(url)

    dot = Digraph()

    for course in courses:
        dot.node(course.number, course.displayName)

        for prerequisite in course.prerequisites:
            dot.edge(course.number, prerequisite.number)

    return str(dot)

def LooksLikeCourseElement(tag):
    """
    A predicate function for discovering course tags.
    Unfortunately, there aren't any useful classes, so we're banking on the
    following telltale element configuration:
        <a name="something"><p><b>...</b></p></a>
    """
    return (tag.name == "a" and 'name' in tag.attrs
     and tag.contents[0].name == "p"
     and tag.p.contents[0].name == "b")

def CoursesFromUrl(url):
    """
    Returnes a list of Course objects for the given URL with the prerequisites
    linked.
    """
    response = request.urlopen(url)
    soup = BeautifulSoup(response.read())
    response.close()
    courses = [Course.FromSoupTag(courseTag)
     for courseTag in soup.find_all(LooksLikeCourseElement)]
    Course.LinkPrerequisites(courses)
    return courses

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
    print(ProduceGraph(listingUrl))
