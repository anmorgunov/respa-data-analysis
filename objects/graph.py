import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio   
pio.kaleido.scope.mathjax = None

class Graph:
    SAVE_HTML = False

    def __init__(self):
        self.BLACK = 'rgb(51, 51, 51)'
        self.GREY = 'rgb(236, 236, 236)'
        self.TITLE_SIZE = 16
        self.FONT = 'Helvetica'
        self.BG_COLOR = 'white'
        self.TICK_SIZE = 18
        self.AXIS_TITLE_SIZE = 18
        self.ANNOTATION_SIZE = 14
        self.LEGEND_SIZE = 18

    def _update_fig(self, figure, title=''):
        """A wrapper function with common settings for Figure object from plotly

        Args:
            figure (obj): a plotly Figure graph object
        """
        scale = 1 if "<br>" not in title else 1.3
        figure.update_layout(
            title=dict(
                text=title,
                y=0.9,
                x=0.5,
                xanchor='center',
                yanchor='top',
            ),
            margin=dict(t=100*scale),
            font = dict(
                family=self.FONT,
                size=self.TITLE_SIZE,
                color=self.BLACK,
            ),
            # showlegend=False,
            plot_bgcolor=self.BG_COLOR,
            legend=dict(font=dict(size=self.LEGEND_SIZE))
        )

    def _update_axes(self, figure, xdtick=1, ydtick=1, xtitle='', ytitle=''):

        figure.update_xaxes(title=dict(text=xtitle, font = dict(family=self.FONT, size=self.AXIS_TITLE_SIZE, color=self.BLACK,),),
                showline=True,
                showgrid=True,
                gridcolor=self.GREY,
                mirror=True,
                dtick=xdtick,
                showticklabels=True,
                linecolor=self.BLACK,
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family=self.FONT,
                    size=self.TICK_SIZE,
                    color=self.BLACK,
                ),)
        figure.update_yaxes(title=dict(
                    text=ytitle,
                    standoff=0,
                    font = dict(
                        family=self.FONT,
                        size=self.AXIS_TITLE_SIZE,
                        color=self.BLACK,
                        ),
                ),
                showgrid=True,
                gridcolor=self.GREY,
                zeroline=True,
                mirror=True,
                dtick=ydtick,
                zerolinecolor=self.BLACK,
                showline=True,
                showticklabels=True,
                linecolor=self.BLACK,
                linewidth=2,
                ticks='outside',
                tickfont=dict(
                    family=self.FONT,
                    size=self.TICK_SIZE,
                    color=self.BLACK,
                ),)

    def _save_fig(self, figure, fname, jpg=True, svg=True, pdf=True):
        if self.SAVE_HTML: figure.write_html(f"export/html/{fname}.html", include_plotlyjs='cdn')
        if jpg: figure.write_image(f"export/jpg/{fname}.jpg", scale=4.0)
        if svg: figure.write_image(f"export/svg/{fname}.svg")
        if pdf: figure.write_image(f"export/pdf/{fname}.pdf")

    def plot_data(self, traces, fname, title, xtitle='', ytitle='', eq=None, yaxisparams=None, xaxisparams=None, layoutparams=None):
        if yaxisparams is None: yaxisparams = {}
        if xaxisparams is None: xaxisparams = {}
        if layoutparams is None: layoutparams = {}
        # if eq is None: eq = {}
        fig = go.Figure()
        for trace in traces:
            fig.add_trace(trace)
        self._update_fig(fig, title)
        self._update_axes(fig, xtitle=xtitle, ytitle=ytitle)
        fig.update_yaxes(**yaxisparams)
        fig.update_xaxes(**xaxisparams)
        fig.update_layout(**layoutparams)
        if eq is not None: fig.add_annotation(**eq)
        self._save_fig(fig, fname)

    def plot_linechart(self, traces, fname, title, xtitle, ytitle, eq):
        fig = go.Figure()
        for trace in traces:
            fig.add_trace(trace)
        self._update_fig(fig, title)
        self._update_axes(fig, xdtick=10, ydtick=10, xtitle=xtitle, ytitle=ytitle)
        fig.update_xaxes(range=[0, 100])
        fig.update_yaxes(range=[0, 100], showgrid=True)
        fig.update_layout(width=720, height=720)
        fig.add_annotation(
            xref="paper", yref="paper",
            x=0, y=1,
            text=eq,
            showarrow=False,
        )
        self._save_fig(fig, fname)

    def plot_histogram(self, traces, fname, title):
        fig = go.Figure()
        for trace in traces:
            fig.add_trace(trace)
        self._update_fig(fig, title)
        self._update_axes(fig, xdtick=5)
        fig.update_xaxes(range=[0, 70])
        self._save_fig(fig, fname)
    
    def plot_subplot_histograms(self, rows, cols, traces, fname, titles, title, layoutparams=None):
        if layoutparams is None: layoutparams = {}
        fig = make_subplots(rows=rows, cols=cols, subplot_titles=titles)
        for trace, row, col in traces:
            fig.add_trace(trace, row=row, col=col)
        self._update_fig(fig, title)
        self._update_axes(fig, xdtick=30,)
        fig.update_xaxes(range=[0,100], showgrid=False)
        fig.update_layout(showlegend=False, **layoutparams)
        self._save_fig(fig, fname)

