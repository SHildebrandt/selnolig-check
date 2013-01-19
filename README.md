# selnolig-check

This repository contains the source code and [documentation](https://github.com/SHildebrandt/selnolig-check/blob/master/selnolig-check-documentation.pdf) of selnolig-check.
selnolig-check tests the German ligature suppression patterns of the LuaLaTeX package [selnolig](https://github.com/micoloretan/selnolig) for morphological correctness and relative completeness, based on an extensive corpus.

We conducted the majority of this project as our final project for the class *Introducton to Computational Linguistics* at the University of Massachusetts at Amherst in the fall of 2012.

## Running the Programs

In order to run the programs, two external resources are required, which are *not* included in this repository:

- **the SDeWaC corpus**, licenses to be obtained from the [Web-as-Corpus kool ynitiative](http://wacky.sslmit.unibo.it/)  
  the untagged version (`sdewac-v3.corpus`) renamed `corpus.raw` and placed in the directory `src/testing_dictionary/`.  
  M. Baroni, S. Bernardini, A. Ferraresi and E. Zanchetta. 2009. [The WaCky Wide Web: A Collection of Very Large Linguistically Processed Web-Crawled Corpora](http://wacky.sslmit.unibo.it/lib/exe/fetch.php?media=papers:wacky_2008.pdf). *Language Resources and Evaluation* 43 (3): p. 209–226.
- **the morphological analyzer SMOR**, licenses to be obtained from the [Institut für Maschinelle Sprachverarbeitung](http://www.ims.uni-stuttgart.de/) at Universität Stuttgart, 
  placed in a directory named `98-SMOR_binaries/` within the directory `src/selnolig-check/`.  
  Helmut Schmid, Arne Fitschen and Ulrich Heid: [SMOR: A German Computational Morphology Covering Derivation, Composition, and Inflection](http://www.ims.uni-stuttgart.de/www/projekte/gramotron/PAPERS/LREC04/smor.pdf), *Proceedings of the IVth International Conference on Language Resources and Evaluation (LREC 2004)*, p. 1263–1266, Lisbon, Portugal.

The programs are supposed fo be run in the following order:

1. in `src/testing_dictionary/`:
    1. `corpus_to_words`
    2. `words_to_ligs`
    3. `ligs_to_ligdict`
2. in `src/selnolig_check/`:
    1. `ligdict_to_smor`  (this is just a script to call SMOR with the correct input and output files)
    2. `smor_to_morphemes`
    3. `morphemes_to_analyses`
    4. `analyses_to_errors`

## Licenses

The code is licensed under a Simplified BSD License, to be viewed in the file [LICENSE.md](https://github.com/SHildebrandt/selnolig-check/blob/master/LICENSE.md).

The documentation is licensed under a [Creative Commons Attribution-NonCommercial-ShareAlike 3.0 Unported License](http://creativecommons.org/licenses/by-nc-sa/3.0/).
