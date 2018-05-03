set terminal png truecolor medium size 800,800 crop
set noxzeroaxis
set noyzeroaxis
### Using xScale = nd
### Using yScale = nd
set style fill  transparent solid 0.10 noborder
### keyLoc=top keySpacing=0.7 keyFontFace=medium keyFontSize=
set key top samplen 1 spacing 0.7  font "medium,"
set size ratio 0.821894871074622
set title ''
set grid
set pointsize 3
set ylabel 'PMiss (in %)'
set xlabel 'PFA (in %)'
set label 1 "0.300" at graph 0.005, graph 0.575729465340501 left nopoint textcolor rgb "#b0b0b0b"
set noxtics
set xtics ('.0001' -4.7534, '.001' -4.2649, '.004' -3.9444, '.01' -3.7190, '.02' -3.5401, '.05' -3.2905, '.1' -3.0902, '.2' -2.8782, '.5' -2.5758, '1' -2.3263, '2' -2.0537, '5' -1.6449, '10' -1.2816, '20' -0.8416, '40' -0.2533)
set noytics
set ytics ('5' -1.6449, '10' -1.2816, '20' -0.8416, '40' -0.2533, '60' 0.2533, '80' 0.8416, '90' 1.2816, '95' 1.6449, '98' 2.0537)
plot [-4.75343910607888:-0.253347103317183] [-1.64485362793551:2.05374890849825] \
  -x title 'Random Performance' with lines lt 1,\
  'overall/nist/nist.dets/sum.isometriclines' title 'Iso-TWV lines' with lines lt rgb "#b0b0b0b" lw 1,\
  'overall/nist/nist.dets/sum.Occurrence.dat.1' using 3:2 notitle with  lines  lc 2 lw 1,\
    'overall/nist/nist.dets/sum.Occurrence.dat.2' using 11:10 title 'Occurrence: Act  TWV=0.6668  PMiss= 0.215  PFA=0.00012  Thr=1.0000' with linespoints pt 7 ps 2 lc 2,\
  'overall/nist/nist.dets/sum.Occurrence.dat.2' using 6:5 title 'Max  TWV=0.6668  PMiss= 0.215  PFA=0.00012  Thr=1.0000' with points lc 2 pt 6 lw 1 ps 2