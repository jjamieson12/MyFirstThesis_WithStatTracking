# <div align="center">Thesis template for an experimental particle physics PhD with in-built progress tracking</div> #

This workflow is based heavily on the excellent hepthesis template, written and maintained by Andy Buckley, thanks go to him for providing it freely. 

hepthesis is avaliable in all good LaTeX distributions, and on [CTAN](https://ctan.org/pkg/hepthesis?lang=en), packaged with a similar working example.

This repository aims to provide a one-stop-shop solution to setting up a hep-themed PhD thesis using hepthesis with the following useful additions:
- A more fully featured makefile with options for reduced and quiet running
- Several potentially useful LaTeX macros
- Tweaked directory layout for an improved writing workflow 
- A series of bash and python scripts to enable seamless tracking of writing progress displayed in html format.

<span style="font-size:1.75em">Author: </span> <span style="font-size:1.25em"> Jonathan Jamieson </span>\
jonathan.jamieson@cern.ch

## <div align="center"> A brief guide to this repo: </div> ##

Run 'make (quiet)' to compile thesis (quietly)
Run 'make (q)content' to compile a minimal version without front or back matter (quietly) 

Add additions to your thesis as you see fit, I'm not going to write it for you...

NB: New thesis chapters must be placed inside directories named 'Section_\<chapter name\>' in order for tracking of chapter numbers to work properly. 

NB2: If you would like to track the amount of non-final red-text over time you need to use the \col{words go here} macro. This will colour 'words go here' in red and tell texcount to record this seperately from regular text

When you have staged changes to commit **do not use git commit!** Instead run 
```bash
bash commit.sh "commit message" x
```
from inside the base directory. Replace x with an integer between 0(bad) and 10(good) which asseses the quality of what was written in this commit. 

This script will then, in this order:
- Check all changes have been staged and request permission to carry on if non-staged changes persist
- Re-compile the full latex document twice, once using 'make content' and another using full 'make'
    - This is to get a reading of the number of pages with/without front/backmatter
- Run a comprehensive word-count and append the values to a running log inside stats/
- Run a python plotting script to produce 13 plots based on the recorded statistics of this and all previous commits as well as a word-cloud of most commonly used words
    - The word-cloud shape can be changed by modifying the relevent configuration parameters in statPlots&#46;py to point to your own image masks. See the [wordcloud documenation](https://amueller.github.io/word_cloud/) for more details
- Save a full word-count breakdown in html format inside stats/snapshots (only if a snapshot doesn't already exist for the current month)
- Run git commit using your input commit message
- Remind you to run git push and exit gracefully

Final plots can be viewed by pointing a web browser to index&#46;html inside stats/figures/ 

You can check [here](https://jjamieson12.github.io/MyFirstThesis_WithStatTracking/) for an in-progress look at these plots for my own thesis, here's hoping they make me look good. 
