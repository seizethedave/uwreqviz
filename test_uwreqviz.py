import os

import pytest
from bs4 import BeautifulSoup

from uwreqviz import *

kSingleValidFragment = """<a name="cse120"><p><b>CSE 120 Computer Science Principles (5) NW, QSR</b><br/>Introduces fundamental concepts of computer science and computational thinking. Includes logical reasoning, problem solving, data representation, abstraction, the creation of digital artifacts such as web pages and programs, managing complexity, operation of computers and networks, effective web searching, ethical, legal and social aspects of information technology. May not be taken for credit if credit earned in CSE 100/INFO 100.<br/><a href="https://uwstudent.washington.edu/student/myplan/course/CSE120" target="_blank">View course details in MyPlan: CSE 120</a></p></a>"""

kAnotherValidFragment = """<a name="cse522"><p><b>CSE 522 Design and Analysis of Algorithms II (4)</b><br/>Analysis of algorithms more sophisticated than those treated in CSE 521. Content varies and may include such topics as algebraic algorithms, combinational algorithms, techniques for proving lower bounds on complexity, and algorithms for special computing devices such as networks or formulas. Prerequisite: CSE 521.<br/><a href="https://uwstudent.washington.edu/student/myplan/course/CSE522" target="_blank">View course details in MyPlan: CSE 522</a></p></a>"""

kYetAnotherValidFragment = """<a name="cse401"><p><b>CSE 401 Introduction to Compiler Construction (4)</b><br/>Fundamentals of compilers and interpreters; symbol tables; lexical analysis, syntax analysis, semantic analysis, code generation, and optimizations for general purpose programming languages. No credit to students who have taken CSE 413. Prerequisite: CSE 332; CSE 351.<br/><a href="https://uwstudent.washington.edu/student/myplan/course/CSE401" target="_blank">View course details in MyPlan: CSE 401</a></p></a>"""

def LoadTestingSoup(filename):
    """
    Loads a soup object from one of the testing files in data/.
    """
    return BeautifulSoup(open(os.path.join("data", filename), "r"))

def test_LooksLikeCourseElement():
    matches = BeautifulSoup(kSingleValidFragment).find_all(LooksLikeCourseElement)

    assert 1 == len(matches)

    doc = LoadTestingSoup("cse.html")

    courses = doc.find_all(LooksLikeCourseElement)
    print("found {0} courses.".format(len(courses)))
    assert len(courses) == 113

def test_FromSoupTag():
    soup = BeautifulSoup(kSingleValidFragment)
    tag = soup.a

    course = Course.FromSoupTag(tag)
    assert course is not None
    assert course.number == "CSE 120"
    assert course.name == "Computer Science Principles"
    assert course.credits == "5"

    soup = BeautifulSoup(kAnotherValidFragment)
    tag = soup.a
    course = Course.FromSoupTag(tag)
    assert course is not None
    assert course.number == "CSE 522"
    assert course.name == "Design and Analysis of Algorithms II"
    assert course.credits == "4"
    assert course.prerequisiteNumbers == ["CSE 521"]

    soup = BeautifulSoup(kYetAnotherValidFragment)
    tag = soup.a
    course = Course.FromSoupTag(tag)
    assert course is not None
    assert course.number == "CSE 401"
    assert course.name == "Introduction to Compiler Construction"
    assert course.credits == "4"
    assert course.prerequisiteNumbers == ["CSE 332", "CSE 351"]

def test_LinkPrerequisites():
    course1 = Course("CSE 409", "Blah 1", "5", ("CSE 123", "CSE 139"))
    course2 = Course("CSE 100", "Blah 2", "5", ())
    course3 = Course("CSE 122", "Blah 3", "5", ("CSE 100",))
    course4 = Course("CSE 123", "Blah 4", "5", ("CSE 122",))
    course5 = Course("CSE 139", "Blah 5", "5", ("CSE 100",))
    Course.LinkPrerequisites((course1, course2, course3, course4, course5))

    assert course4 in course1.prerequisites
    assert course5 in course1.prerequisites
    assert course1 not in course1.prerequisites
    assert course2 not in course1.prerequisites

    assert 0 == len(course2.prerequisites)

def test_CourseNumberExpr():
    validCourses = ("CSE 123", "E E 411", "LAW C 333", "CSE 523", "IMMUN 444",
     "B H 301", "B STR 301", "HSMGMT 500", "SOC WF 497")
    for num in validCourses:
        assert kCourseNumberExpression.match(num) is not None
