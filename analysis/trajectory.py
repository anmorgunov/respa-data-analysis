from objects.student import Student
import parsers.parse_oblast
import parsers.parse_respa
from parsers.find_overlaps import find_similar_matches
import numpy as np
from objects.graph import Graph
import plotly.graph_objects as go
import tools

class Analyzer:

    def __init__(self):
        self.ROUND3 = tools.rounder(3)
        self.respa_bygrade = parsers.parse_respa.parse_results(2023)
        self.oblast_bygrade, self.oblast_byoblast = parsers.parse_oblast.parse_results()
        self.gradeToStudent = {}
        self.oblToGrToStuds = {}

    def combine_students(self, grade, oblast=None):
        grToStudents = {}
        if not oblast:
            name_to_objs = find_similar_matches([self.respa_bygrade[grade], self.oblast_bygrade[grade]], "name", testing=False)
        else:
            name_to_objs = find_similar_matches([self.respa_bygrade[grade], self.oblast_byoblast[oblast][grade]], "name", testing=False)

        for name, objs in name_to_objs.items():
            student = Student()
            student.name = name
            for obj in objs:
                setattr(student, f"{obj.olymp_name}_score", obj.total)
            grToStudents.setdefault(grade, []).append(student)
        self.gradeToStudent = grToStudents
        return grToStudents

    def get_oblast_respa_arrays(self, data, scale=100/70):
        obl, resp = [], []
        for obj in data:
            if hasattr(obj, "oblast_score") and hasattr(obj, "respa_score"):
                obl.append(obj.oblast_score*scale)
                resp.append(obj.respa_score*scale)
        return obl, resp
    
    def calculate_correlation(self, grade):
        data = self.gradeToStudent[grade]
        oblast, respa = self.get_oblast_respa_arrays(data)
        return np.corrcoef(oblast, respa)

    def plot_correlations_by_grade(self):
        graph = Graph()
        grades = sorted(self.gradeToStudent)
        corrs = []
        for grade in grades:
            self.combine_students(grade)
            data = self.gradeToStudent[grade]
            oblast, respa = self.get_oblast_respa_arrays(data)
            corr = np.corrcoef(oblast, respa)[0, 1]
            corrs.append(corr)
            fit = np.polyfit(oblast, respa, 1)
            xgrid = np.mgrid[0:100:2j]
            eq = f"y={self.ROUND3(fit[0])}x+{self.ROUND3(fit[1])}<br>R^2 = {self.ROUND3(corr**2)}"
            yfit = np.vectorize(lambda x: fit[0]*x+fit[1])(xgrid)
            traces = [go.Scatter(x=oblast, y=respa, mode='markers', name="Результаты"),
                        go.Scatter(x=xgrid, y=yfit, mode='lines', name="Best fit")]
            graph.plot_linechart(traces, f"trajectory/gr{grade}-data", f"Корреляция между баллами областного<br>и заключительного этапа РО ({grade} кл.)", xtitle="Баллы (из 100%) на теор. туре областного этапа", ytitle="Баллы (из 100%) на теор. туре заключительного этапа", eq=eq)
        yValLabels = [self.ROUND3(cor) for cor in corrs]
        traces = [go.Bar(y=corrs, x=[f"{grade} класс" for grade in grades], #marker_color=self.BINARY[i],
                                 text=yValLabels, textposition='auto', )] #legendrank=1-i
        graph.vertical_bar_plot(traces, f"trajectory/bygrade", "Корреляция между баллами областного и заключительного этапа")

    def plot_correlations_by_oblast(self):
        graph = Graph()
        grades = [9, 10, 11]
        oblasts = sorted(self.oblast_byoblast)
        xVals = []
        print(oblasts)
        corrs = []
        for oblast in oblasts:
            obl_scores, resp_scores = [], []
            for grade in grades:
                grToStuds = self.combine_students(grade, oblast)
                if grade not in grToStuds:
                    print(f"{oblast} doesn't  have results for {grade}")
                    continue
                data = grToStuds[grade]
                obl, resp = self.get_oblast_respa_arrays(data)
                obl_scores.extend(obl)
                resp_scores.extend(resp)
            if len(obl_scores) <= 2:
                continue
            corr = np.corrcoef(obl_scores, resp_scores)[0, 1]
            corrs.append(corr)
            xVals.append(oblast)

            fit = np.polyfit(obl_scores, resp_scores, 1)
            xgrid = np.mgrid[0:100:2j]
            eq = f"y={self.ROUND3(fit[0])}x+{self.ROUND3(fit[1])}<br>R^2 = {self.ROUND3(corr**2)}"
            yfit = np.vectorize(lambda x: fit[0]*x+fit[1])(xgrid)
            traces = [go.Scatter(x=obl_scores, y=resp_scores, mode='markers', name="Результаты"),
                        go.Scatter(x=xgrid, y=yfit, mode='lines', name="Best fit")]
            graph.plot_linechart(traces, f"trajectory/obl-{oblast}", f"Корреляция между баллами областного<br>и заключительного этапа РО ({oblast})", xtitle="Баллы (из 100%) на теор. туре областного этапа", ytitle="Баллы (из 100%) на теор. туре заключительного этапа", eq=eq)
        
        obl_scores, resp_scores = [], []
        for grade in grades:
            self.combine_students(grade)
            data = self.gradeToStudent[grade]
            obl, resp = self.get_oblast_respa_arrays(data)
            obl_scores.extend(obl)
            resp_scores.extend(resp)
        xVals.append("Суммарно")
        corrs.append(np.corrcoef(obl_scores, resp_scores)[0, 1])
        traces = [go.Bar(y=corrs, x=xVals, text=[self.ROUND3(cor) for cor in corrs], 
                         textposition='auto')]
        graph.vertical_bar_plot(traces, f"trajectory/byoblast", "Корреляция между баллами областного<br>и заключительного этапа по областям")
        


if __name__ == "__main__":
    a = Analyzer()
    # for grade in (11, 10, 9):
    #     a.combine_students(grade)
    #     a.calculate_correlation(grade)
    
    # A few notes: it matches 41/45 students in grade 11
    #                         46/53             grade 10
    #                         44/47             grade 9
    
    # a.plot_correlations_by_grade()
    a.plot_correlations_by_oblast()