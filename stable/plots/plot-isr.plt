#!/usr/bin/gnuplot

set terminal postscript eps color "Times" 20
set encoding utf8
set termoption enhanced
set output "isr.eps"

set grid ytics lt 0 lw 1 lc rgb "#cccccc"
set grid xtics lt 0 lw 1 lc rgb "#cccccc"

set style line 1 lt 1 pt 1 ps 2 lw 3 lc rgb "green"
set style line 2 lt 2 pt 9 ps 2 lw 3 lc rgb "black"
set style line 3 lt 3 pt 4 ps 2 lw 3 lc rgb "blue"

set xlabel "Porcentagem de nós maliciosos"
set ylabel "ISR (%)"

set xtics 10
set ytics 10
#set yrange [0.0:10]
set xrange [0:31]

plot "isr.dat" using 1:2:3:4 title "ISR" with linespoints ls 1,\
"isr.dat" using 1:2:3:4 notitle with yerrorbars ls 1,\
1 / 0 notitle smooth csplines with lines ls 1
