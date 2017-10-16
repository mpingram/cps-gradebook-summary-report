* Purpose:
  **Present assignment data from CPS gradebook grouped by teacher, in order to 
  identify issues in teachers' gradebook records. Issues include: 
    *** large numbers of missing or excused grades
    *** unimportant assignments with inordinately large downward impact
        on grades
    *** large numbers of students failing
    *** grade categories that have been created and not used
    *** grade category weights not adding up to 100%


* Source files:
  ** Gradebook -> Custom Reports -> CPS All Assignments and Grades Extract
      --> "./source/CPSAllAssignmentsandGradesExtract(SlowLoad).csv"
  ** Gradebook -> Custom Reports -> CPS Teacher Categories and Total Points Logic
      --> "./source/CPSTeacherCategoriesandTotalPointsLogic.csv"
  ** Gradebook -> Custom Reports -> CPS Unused Categories in Teacher Gradebooks
      --> "./source/CPSUnusedCategoriesinTeacherGradebooks.csv"
  ** Gradebook -> reports -> ES Cumulative Grades Extract
      --> "./source/ESCumulativeGradesExtract.csv"

* Output:
  ** One PDF report for each teacher in subfolder "./reports". Report contains:
    *** pie chart breakdown of A,B,C,D, and F's for each subject.
    *** list of # of failing students, grouped by subject and HR.
    *** list of unused categories, grouped by subject.
    *** list of top 5 assignments with highest negative impact score,
      per subject. Negative impact formula: 
      **** impact = ((100-pct)*weight)/float(total_assigns)
    *** for each subject, a list of categories, which shows category weights, 
    total # of assignments in category, and average grade in category. Flagged
    if category weights do not add up to 100%, which is possible 
    *** for each suject, # of excused grades by category
    *** for each subject, # of missing, 0, or incomplete grades by category
    *** [Considering / WIP] list of assignments for which student scores are higher than max scores.

* Language:
  ** python=3.6

* Dependencies:
  ** jupyter
  ** pandas
  ** numpy
  ** jinja2
  ** weasyprint
