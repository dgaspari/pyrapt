# pyrapt
A pitch tracker inspired by David Talkin's RAPT (Robust Algorithm for Pitch Tracking) written in Python. This work is an educational exercise as part of my master's thesis at Harvard Extension School.

### Introduction

This project started as an attempt to implement an algorithm proposed by David Talkin in this paper:
> Talkin, David. "A robust algorithm for pitch tracking (RAPT)." Speech coding and synthesis 495 (1995): 518.

This paper was recommended to me by my advisor as a good vocal pitch tracker I could write on my own. During the course of my thesis project I have adjusted my implementation. It is *not* a pure implementation of RAPT by any means. If you're interested in more recent work by David Talkin, I recommend checking out his latest algorithm, REAPER, on Github: https://github.com/google/REAPER

### Installation Notes

This module is currently being developed for use with Python 2.7. Because the scipy/numpy libraries are dependencies, make sure you can obtain and build those packages first (need fortran compiler, python dev packages, and ability to comipile c extensions)

### Misc Notes:

While working on the NCCF portion of RAPT, to save time, I've included a pickle of the nccf output: example\_nccf\_data.p
To load it up, just import pickle and then call load method like so: ncc\_data = pickle.load(open("example\_nccf\_data.p", "rb"))

