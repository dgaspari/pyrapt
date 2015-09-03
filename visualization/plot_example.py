from pyrapt import pyrapt, raptparams
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource
import numpy
from matplotlib import mlab
params = raptparams.Raptparams()
example_audio = pyrapt._get_audio_data('example.wav')
samples_per_frame = int(example_audio[0] * params.frame_step_size)
y = pyrapt.rapt('example.wav')
x = range(0, len(y))
y = numpy.array(y)
x = numpy.array(x)
x = x * samples_per_frame
spec = mlab.specgram(example_audio[1])
output_file('visualization/output/example_plot.html', title='example.wav f0')
p = figure(title='freq of example.wav', x_axis_label='x',
           y_axis_label='y')
p.line(range(0, len(example_audio[1])), example_audio[1],
       legend='amp of example.wav', line_width=1, line_color='orange')
p.line(x, y, legend='example.wav f0', line_width=2, line_color='blue')
save(p)
