## GNUPLOT command file
set terminal postscript color
set style data lines
set title 'Threshold Plot for Occurrence'
set xlabel 'Detection Score'
set grid
set size ratio 0.85
plot [0.999999:1.000001]  \
  'overall_EMORY/nist/nist.dets/sum.Occurrence.dat.1' using 1:4 title 'PMiss' with lines lt 2, \
  'overall_EMORY/nist/nist.dets/sum.Occurrence.dat.1' using 1:5 title 'PFA' with lines lt 3, \
  'overall_EMORY/nist/nist.dets/sum.Occurrence.dat.1' using 1:6 title 'TWV' with lines lt 4, \
  0.601158606432775 title 'Actual TWV 0.601' with lines lt 5, \
  'overall_EMORY/nist/nist.dets/sum.Occurrence.dat.2' using 1:2 title 'Max TWV 0.601, scr 1.000' with points lt 6
