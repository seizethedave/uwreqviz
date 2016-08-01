#!/usr/bin/env python3

import sys
import os
import re
from urllib import request
import itertools
from operator import attrgetter
import argparse

from graphviz import Digraph
from bs4 import BeautifulSoup

kCourseTitleExpression = re.compile(
 r"(?P<number>[A-Z][A-Z ]+ [\d]+) (?P<name>[^(]*)\((?P<credits>[^)]*)")
kCourseNumberExpression = re.compile(r"[A-Z][A-Z ]+[\d]{3}")
kPrereqExpression = re.compile(r"(?:Prerequisite: )(.*?)\.(?=[\D])")

def debug(s):
    print(s, file=sys.stderr)

class Course:
    """
    Represents a course.
    """
    def __init__(self, number, name, credits, rank,
     prerequisiteNumbers=(), prerequisiteText=None):
        self.number = number
        self.name = name
        self.credits = credits
        self.rank = rank
        self.prerequisiteNumbers = prerequisiteNumbers
        self.prerequisiteText = prerequisiteText

    def __repr__(self):
        return u"Course({0})".format(self.number)

    @property
    def caption(self):
        result = u"{0} {1}".format(self.number, self.name)
        if self.prerequisiteText:
            result += "\n(Req: %s)" % (self.prerequisiteText)
        return result

    @classmethod
    def FromSoupTag(cls, soupTag):
        title = soupTag.p.b.text
        groups = re.match(kCourseTitleExpression, title).groups()
        number, name, credits = (g.strip() for g in groups)

        # Rank is the first digit of the numeric course number. (CSE 423 is
        # rank 4.)
        rank = next(int(c) for c in number if c.isdigit())

        # Now find the prerequisites string.
        courseText = soupTag.text

        prereqStrings = re.findall(kPrereqExpression, courseText)

        if len(prereqStrings) > 0:
            reqsText = prereqStrings[0]
            prerequisites = re.findall(kCourseNumberExpression, reqsText)
        else:
            # None listed.
            reqsText = None
            prerequisites = []

        return cls(number, name, credits, rank, prerequisites, reqsText)

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
    soup = BeautifulSoup(response.read(), "html.parser")
    response.close()
    courses = [Course.FromSoupTag(courseTag)
     for courseTag in soup.find_all(LooksLikeCourseElement)]
    Course.LinkPrerequisites(courses)
    return courses

def ProduceGraph(args):
    dot = Digraph()
    rankGetter = attrgetter("rank")

    courses = CoursesFromUrl(args.url)
    filteredCourses = list(filter(lambda c: c.rank <= args.maxrank, courses))
    sortedCourses = sorted(filteredCourses, key=rankGetter)

    for rank, coursesByRank in itertools.groupby(sortedCourses, rankGetter):
        subgraph = Digraph(name="cluster_%d" % rank)

        for course in coursesByRank:
            subgraph.node(course.number, course.caption)

        dot.subgraph(subgraph)

    for course in filteredCourses:
        for prerequisite in course.prerequisites:
            dot.edge(course.number, prerequisite.number)

    return str(dot)

if __name__ == "__main__":
    argParser = argparse.ArgumentParser(
        description="Requirements visualizer for University of Washington class listings.")
    argParser.add_argument("url", nargs='?', help="URL to read")
    argParser.add_argument("-r", "--maxrank",
        help=("restricts course rank to a maximum number. (That is, --maxrank=4 "
            "restricts to 400-level classes and lower.)"),
        type=int, default=8, required=False, choices=range(1, 9))

    args = argParser.parse_args()

    if args.url:
        print(ProduceGraph(args))
