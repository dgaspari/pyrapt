# Misc Notes
These are just some random notes while i work on this project (to be removed once project is complete)
### NCCF Notes
Re-use as much of the same code as possible for first-pass and second-pass NCCF runs.
Most of the starting params will be different, though, because:
* different length of audio sample
* different sample rate
* different range of lags

Need to decide which library to use for parabolic interpolation of 1st pass results
so i can map them to lags in the 2nd pass.

Don't forget:
* need theta_max for every frame of nccf - for both first pass and 2nd pass
* 
