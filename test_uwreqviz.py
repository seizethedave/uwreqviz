import os

import pytest
from bs4 import BeautifulSoup

import uwreqviz

kSingleValidFragment = """<a name="cse120"><p><b>CSE 120 Computer Science Principles (5) NW, QSR</b><br/>Introduces fundamental concepts of computer science and computational thinking. Includes logical reasoning, problem solving, data representation, abstraction, the creation of digital artifacts such as web pages and programs, managing complexity, operation of computers and networks, effective web searching, ethical, legal and social aspects of information technology. May not be taken for credit if credit earned in CSE 100/INFO 100.<br/><a href="https://uwstudent.washington.edu/student/myplan/course/CSE120" target="_blank">View course details in MyPlan: CSE 120</a></p></a>"""

def LoadTestingSoup(filename):
    """
    Loads a soup object from one of the testing files in data/.
    """
    return BeautifulSoup(open(os.path.join("data", filename), "r"))

def test_LooksLikeCourseElement():
    matches = BeautifulSoup(kSingleValidFragment).find_all(uwreqviz.LooksLikeCourseElement)

    assert 1 == len(matches)

    doc = LoadTestingSoup("cse.html")

    courses = doc.find_all(uwreqviz.LooksLikeCourseElement)
    print("found {0} courses.".format(len(courses)))
    assert len(courses) == 113

def test_FromSoupTag():
    soup = BeautifulSoup(kSingleValidFragment)
    tag = soup.a

    course = uwreqviz.Course.FromSoupTag(tag)
    assert course is not None
    assert course.number == "CSE 120"
    assert course.name == "Computer Science Principles"
    assert course.credits == "5"



