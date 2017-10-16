from enum import Enum

class LetterGradeCutoffs(Enum):
    A=100
    B=89
    C=79
    D=69
    F=59
    Zero=0

class GradeCodes(Enum):
    Missing="Msg"
    Excused="Exc"
    Incomplete="Inc"

class Cols(Enum):
    # original
    StudentLastname="StuLName"
    StudentFirstname="StuFName"
    StudentId="StuStudentId"
    GradeLevel="StuGradeLevelCode"
    ClassName="ClassName"
    TeacherLastname="TeacherLast"
    TeacherFirstname="TeacherFirst"
    AssignmentName="ASGName"
    Score="Score"
    ScorePossible="ScorePossible"
    CategoryName="CategoryName"
    CategoryWeight="CategoryWeight"
    AssignmentDue="AssignmentDue"
    AssignedDate="AssignedDate"
    GradeEnteredOn="GradeEnteredOn"
    SchoolId="StuSchoolId"
    # added
    TeacherFullname="TeacherFullname"
