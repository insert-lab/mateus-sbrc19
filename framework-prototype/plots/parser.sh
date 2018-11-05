#!/bin/bash
i=0
declare -a ISR_arr
declare -a VS_arr
declare -a VF_arr
for  f in ../results/exp*; do
  percentage=$(grep -Eo '[0-9]{1,}' <<< "$f")
  grep 'ISR' "$f" | awk -F ':' '{print $2}' > /tmp/foo
  ISR=$(./calcula_ic.r /tmp/foo)
  grep 'VS' "$f" | awk -F ':' '{print $2}' > /tmp/foo
  VS=$(./calcula_ic.r /tmp/foo)
  grep 'VF' "$f" | awk -F ':' '{print $2}' > /tmp/foo
  VF=$(./calcula_ic.r /tmp/foo)
  ISR_arr[$i]=$ISR
  VS_arr[$i]=$VS
  VF_arr[$i]=$VF
  echo "$percentage ${ISR_arr[@]}" >> isr.dat
  echo "$percentage ${VF_arr[@]}" >> vs.dat
  echo "$percentage ${VS_arr[@]}" >> vf.dat
done
