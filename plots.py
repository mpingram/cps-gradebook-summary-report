import matplotlib.pyplot as plt
from gradeconvert import to_letter_grade

def create_lettergrade_breakdown_diagram(**kwargs):
    """Returns URL of a diagram of letter grade distribution for given grade data.
    
    Keyword args:
    grades: float[] -- list of percentage grades as floats.
    output_url: str -- valid url to save diagram to. 
    label: str? -- (optional) label for diagram

    Returns:
    (success: bool, err: Error | None)
    """
    grades = kwargs.get("grades", None)
    output_url = kwargs.get("output_url", None)
    diagram_label = kwargs.get("label", None)

    if grades is None:
        raise ValueError("Missing required keyword argument grades")
    if output_url is None:
        raise ValueError("Missing required keyword argument output_url")
    
    def create_pie_chart_image(letter_grades, output_url):
        """Creates image at URL. Returns success(bool), err(Error | None)
        
        Positional args:
        letter_grades: str[] of type ("A" | "B" | "C" | "D" | "F").
        output_url: str of valid URL to save image to.

        Returns:
        (success: bool, err: Error | None)
        """
        # count number of students with each grade
        letters = ["A", "B", "C", "D", "F"]
        colormap = {"A":"green", 
                "B": "yellowgreen", 
                "C": "yellow", 
                "D": "orange", 
                "F": "red"}
        # create pie chart sizes and label them with corresponding letter grade
        letter_grade_counts = {letter: letter_grades.count(letter) for letter in letters 
                if letter_grades.count(letter) != 0}
        sizes = []
        labels = []
        colors = []
        # put labels and colors in correct order, skipping letter grades for which
        # there are no letter grades
        for letter, count in letter_grade_counts.items():
            labels.append(letter)
            sizes.append(count)
            colors.append(colormap[letter])
        # create pie chart
        def make_autopct(values):
            def my_autopct(pct):
                total = sum(values)
                val = int(round(pct*total/100.0))
                return '{v:d}'.format(v=val)
            return my_autopct

        fig1, ax1 = plt.subplots()
        pie_chart = ax1.pie(sizes, colors=colors, labels=labels, autopct=make_autopct(sizes))
        if diagram_label is not None:
            plt.title(diagram_label)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        try:
            plt.savefig(output_url)
            return (True, None)
        except IOError as ioErr:
            return (False, ioErr)
        except BaseException as e:
            return (False, e)
        finally:
            # grungy necessity due to matplotlib: clear the global
            # figure that's been created due to earlier call to plt.
            plt.clf()
            plt.close("all")

    letter_grades = [to_letter_grade(grade, 100) for grade in grades]
    letter_grades = [grade for grade in letter_grades if grade is not None]

    return create_pie_chart_image(letter_grades, output_url)
