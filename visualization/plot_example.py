from pyrapt import pyrapt
from bokeh.plotting import figure, output_file
# from bokeh.plotting import show
y = pyrapt.rapt('example.wav')
x = range(0, len(y))
output_file('visualization/output/example_plot.html', title='example.wav f0')
p = figure(title='freq of example.wav', x_axis_label='frame #',
           y_axis_label='freq (hz)')
p.line(x, y, legend='example.wav f0', line_width=2)
# show(p)
