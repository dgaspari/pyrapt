from pyrapt import pyrapt, raptparams
from bokeh.plotting import figure, output_file, save
import numpy
# from matplotlib import mlab
params = raptparams.Raptparams()
example_audio = pyrapt._get_audio_data('example.wav')
samples_per_frame = int(example_audio[0] * params.frame_step_size)
y1 = pyrapt.rapt('example.wav')
y2 = pyrapt.rapt('example.wav', doubling_cost=15.0)
x = range(0, len(y1))
y1 = numpy.array(y1)
y2 = numpy.array(y2)
x = numpy.array(x)
x = x * samples_per_frame
# spec = mlab.specgram(example_audio[1])
output_file('visualization/output/example_plot.html', title='example.wav f0s')
p = figure(title='vocal frequency', x_axis_label='x',
           y_axis_label='y')
p.line(range(0, len(example_audio[1])), example_audio[1],
       legend='amp of example.wav', line_width=1, line_color='orange')
p.line(x, y1, legend='example.wav f0 (basic)', line_width=2, line_color='blue')
p.line(x, y2, legend='example.wav f0 (high doubling cost)', line_width=2,
       line_color='red')
save(p)
