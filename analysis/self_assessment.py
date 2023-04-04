from objects.student import Student
import parsers.parse_oblast
import parsers.parse_respa
import parsers.survey
from parsers.find_overlaps import find_similar_matches
import numpy as np
from objects.graph import Graph
from objects.response import Response
import plotly.graph_objects as go
import tools
import itertools 
import PRIVATE

class Analyzer:

    ASSESS_TO_IND = {"Я не решил(а) эту задачу и я даже не знал(а) с чего начать": 0,
                    "У меня были идеи по решению задачи, но я не смог(ла) их довести до ума": 1,
                    "Я решил(а) задачу, но думаю у меня есть ошибки": 2,
                    "Я решил(а) эту задачу и уверен, что решил(а) правильно на 80% и больше.": 3}
    xVals = ["Я не решил(а) эту задачу<br>и я даже не знал(а) с чего начать",
             "У меня были идеи по решению<br>задачи, но я не смог(ла)<br>их довести до ума",
             "Я решил(а) задачу,<br>но думаю у меня есть ошибки",
             "Я решил(а) эту задачу<br>и уверен, что решил(а)<br>правильно на 80% и больше."]
    def __init__(self, bygrade_scores, bygrade_responses, OLYMP):
        self.ROUND3 = tools.rounder(3)
        self.scores = bygrade_scores
        self.responses = bygrade_responses
        self.OLYMP = OLYMP
        self.gradeToStudent = {}

    def combine_students(self, grade):
        name_to_objs = find_similar_matches([self.scores[grade], self.responses[grade]], "name", testing=False)

        for name, objs in name_to_objs.items():
            student = Student()
            if name in PRIVATE.EXCEPTIONS: # funnily enough, there are two students in different oblasts
                continue # who have identical names and very CLOSE sounding last names, so they get matched accidentally. 
                         # In addition, neither of those students filled the survey.
            student.name = name
            student.numprobs = []
            for obj in objs:
                if isinstance(obj, Response):
                    for i in range(obj.numprobs):
                        setattr(student, f"problem{i+1}_assess", getattr(obj, f"problem{i+1}"))
                        student.numprobs.append(obj.numprobs)
                else:
                    if obj.only_total:
                        break
                    for i in range(obj.numprobs):
                        setattr(student, f"problem{i+1}_score", getattr(obj, f"problem{i+1}"))
                        student.numprobs.append(obj.numprobs)
            else:
                assert len(set(student.numprobs)) == 1, "Number of scores and assessments doesn't match"
                student.numprobs = student.numprobs[0]
                self.gradeToStudent.setdefault(grade, []).append(student)

    def create_bins(self, data, problem):
        bins = [[0], [0], [0], [0]]
        for student in data:
            bins[self.ASSESS_TO_IND[getattr(student, f"{problem}_assess")]].append(getattr(student, f"{problem}_score")["rel"]*100) 
        return bins
    
    def box_plots_total(self):
        graph = Graph()
        bins_bygrade = []
        for grade in (9, 10, 11):
            data = self.gradeToStudent[grade]
            NUMPROBS = data[0].numprobs
            bins_chain = [self.create_bins(data, f"problem{i+1}") for i in range(NUMPROBS)]
            bins = [list(itertools.chain(*sublist)) for sublist in zip(*bins_chain)]
            bins_bygrade.append(bins)
        bins = [list(itertools.chain(*sublist)) for sublist in zip(*bins_bygrade)]

        traces = [go.Box(x=bins[i], name=name) for i, name in enumerate(self.xVals) ] 
        graph.plot_box_plots(reversed(traces), f"selfassessment/{self.OLYMP}allgrade-box", f"Соответствие рефлексии конечному результату (9-11 кл.)")

    def box_plots_by_grade(self, grade):
        graph = Graph()
        data = self.gradeToStudent[grade]
        NUMPROBS = data[0].numprobs
        bins_chain = [self.create_bins(data, f"problem{i+1}") for i in range(NUMPROBS)]
        bins = [list(itertools.chain(*sublist)) for sublist in zip(*bins_chain)]

        
        traces = [go.Box(x=bins[i], name=name) for i, name in enumerate(self.xVals) ] 
        graph.plot_box_plots(reversed(traces), f"selfassessment/{self.OLYMP}grade{grade}-box", f"Соответствие рефлексии конечному результату ({grade} кл.)")

    def box_plots_by_problem(self, grade):
        graph = Graph()
        data = self.gradeToStudent[grade]
        NUMPROBS = data[0].numprobs
        for i in range(NUMPROBS):
            bins = self.create_bins(data, f"problem{i+1}")
            traces = [go.Box(x=bins[i], name=name) for i, name in enumerate(self.xVals) ] 
            graph.plot_box_plots(reversed(traces), f"selfassessment/{self.OLYMP}grade{grade}-problem{i+1}-box", f"Соответствие рефлексии конечному результату<br>(Задача №{i+1}; {grade} кл.)")

    def calculate_correlation(self, grade):
        data = self.gradeToStudent[grade]
        oblast, respa = self.get_oblast_respa_arrays(data)
        return np.corrcoef(oblast, respa)

        


if __name__ == "__main__":
    respa_bygrade = parsers.parse_respa.parse_results(2023)
    oblast_bygrade, oblast_byoblast = parsers.parse_oblast.parse_results()
    survey_respa_full, survey_respa_bygrade = parsers.survey.parse_responses("respa")
    survey_oblast_full, survey_oblast_bygrade = parsers.survey.parse_responses("oblast")

    OLYMP = 'respa/'
    # a = Analyzer(respa_bygrade, survey_respa_bygrade, OLYMP)
    # for grade in (11, 10, 9):
    #     a.combine_students(grade)
    #     a.box_plots_by_grade(grade)
    #     a.box_plots_by_problem(grade)
    
    # a.box_plots_total()

    OLYMP = 'oblast/'
    a = Analyzer(oblast_bygrade, survey_oblast_bygrade, OLYMP)
    for grade in (9, 10, 11):
        a.combine_students(grade)
        a.box_plots_by_grade(grade)
        a.box_plots_by_problem(grade)

    a.box_plots_total()
    
    # A few notes: it matches 12 and 12 students in grade 11 for OBLAST and RESPA respectively
    #                         12 and 8              grade 10
    #                         24 and 7              grade 9
    
    # a.plot_correlations_by_grade()
    # a.plot_correlations_by_oblast()