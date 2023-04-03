from parsers.parse_respa import parse_results
import numpy as np
from objects.graph import Graph
import plotly.graph_objects as go
import tools

class Analyzer:

    def __init__(self, year):
        self.ROUND3 = tools.rounder(3)
        self.year = year
        self.bygrade = parse_results(year)

    def results_for_problem(self, data, probnum, scale=100):
        return [getattr(obj, f"problem{probnum}")["rel"]*scale for obj in data]
    
    def heat_map_for_grade(self, grade):
        graph = Graph()
        data = self.bygrade[grade]
        NUMPROB = data[0].numprobs
        arrays = [self.results_for_problem(data, i+1) for i in range(NUMPROB)]
        corrs = np.corrcoef(arrays)
        cortext = [self.ROUND3(cor) for cor in corrs]
        bestfit = [[np.polyfit(self.results_for_problem(data, i+1), self.results_for_problem(data, j+1), 1)
                     for j in range(NUMPROB)] for i in range(NUMPROB)]
        ffit = [[f"{self.ROUND3(arr[0])}x+{self.ROUND3(arr[1])}" for arr in row] for row in bestfit]
        labels = [f"№{i}" for i in range(1, NUMPROB+1)]
        traces = [go.Heatmap(z=corrs, text=cortext, texttemplate="%{text}", x=labels, y=labels, colorscale='dense')]
        graph.plot_heatmap(traces, f"results/{self.year}/grade{grade}", f"Корреляция между задачами ({grade} кл.)")
        traces = [go.Heatmap(z=corrs, text=ffit, texttemplate="%{text}", x=labels, y=labels, colorscale='dense')]
        graph.plot_heatmap(traces, f"results/{self.year}/grade{grade}-fit", f"Корреляция между задачами ({grade} кл.)")

    def line_two_problems(self, grade, i, j):
        graph = Graph()
        data = self.bygrade[grade]
        x = self.results_for_problem(data, i)
        y = self.results_for_problem(data, j)
        fit = np.polyfit(x, y, 1)
        corr = np.corrcoef(x, y)
        xgrid = np.mgrid[0:100:2j]
        eq = f"y={self.ROUND3(fit[0])}x+{self.ROUND3(fit[1])}<br>R^2 = {self.ROUND3(corr[0, 1]**2)}"
        yfit = np.vectorize(lambda x: fit[0]*x+fit[1])(xgrid)
        traces = [go.Scatter(x=x, y=y, mode='markers', name="Результаты"),
                  go.Scatter(x=xgrid, y=yfit, mode='lines', name="Best fit")]
        graph.plot_linechart(traces, f"results/{self.year}/grade{grade}-{i}-{j}", f"Корреляция между задачами {i} и {j}", f"Задача №{i}", f"Задача №{j}", eq)


if __name__ == "__main__":
    a = Analyzer(2023)
    for grade in (9, 10, 11):
        a.heat_map_for_grade(grade)
    # a.line_two_problems(11, 2, 8)
    # a.line_two_problems(11, 2, 7)
    # a.line_two_problems(11, 3, 8)
    # a.line_two_problems(11, 4, 5)
    # a.line_two_problems(11, 5, 6)
    # a.line_two_problems(10, 2, 5)
    # a.line_two_problems(10, 4, 5)
    # a.line_two_problems(10, 4, 6)
    # a.line_two_problems(10, 4, 7)
    # a.line_two_problems(10, 5, 6)

    a = Analyzer(2022)
    for grade in (9, 10, 11):
        a.heat_map_for_grade(grade)

    a = Analyzer(2021)
    for grade in (9, 10, 11):
        a.heat_map_for_grade(grade)