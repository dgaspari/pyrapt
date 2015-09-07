from pyrapt import pyrapt, raptparams
from bokeh.plotting import figure, output_file, save
# from bokeh.models import ColumnDataSource
import numpy
from matplotlib import mlab
params = raptparams.Raptparams()
example_audio = pyrapt._get_audio_data('example.wav')
samples_per_frame = int(example_audio[0] * params.frame_step_size)
results = pyrapt.rapt_with_nccf('example.wav')
nccf_results = results[0]
nccf_cands = []
z = []
iter = 1
for a in nccf_results:
    for b in a:
        if b[0] > 0.0:
            nccf_cands.append(float(example_audio[0]) / float(b[0]))
            z.append(iter * samples_per_frame)
    iter += 1
y = results[1]
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
p.circle(z, nccf_cands, legend='nccf candidates', color='red', size=1)
save(p)
