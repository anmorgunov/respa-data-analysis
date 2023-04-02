from parsers.respa_results import parse_results
import numpy as np
from objects.graph import Graph
import plotly.graph_objects as go
import tools

class Analyzer:

    def __init__(self):
        self.ROUND3 = tools.rounder(3)
        self.bygrade = parse_results(2023)

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
        graph.plot_heatmap(traces, f"results/2023-grade{grade}", f"Корреляция между задачами ({grade} кл.)")
        traces = [go.Heatmap(z=corrs, text=ffit, texttemplate="%{text}", x=labels, y=labels, colorscale='dense')]
        graph.plot_heatmap(traces, f"results/2023-grade{grade}-fit", f"Корреляция между задачами ({grade} кл.)")



    


if __name__ == "__main__":
    a = Analyzer()
    for grade in (9, 10, 11):
        a.heat_map_for_grade(grade)
