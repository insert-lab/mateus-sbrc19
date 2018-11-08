#!/bin/bash
i=0
declare -a ISR_arr
declare -a VS_arr
declare -a VF_arr
declare -a RC_arr
for f in ../results/exp*; do
  percentage=$(grep -Eo '[0-9]{1,}' <<< "$f")
  grep 'ISR' "$f" | awk -F ':' '{print $2*100}' > /tmp/foo
  ISR=$(./calcula_ic.r /tmp/foo)
  grep 'VS' "$f" | awk -F ':' '{print $2}' > /tmp/foo
  VS=$(./calcula_ic.r /tmp/foo)
  grep 'VF' "$f" | awk -F ':' '{print $2}' > /tmp/foo
  VF=$(./calcula_ic.r /tmp/foo)
  grep 'RC' "$f" | awk -F ':' '{print $2}' > /tmp/foo
  RC=$(./calcula_ic.r /tmp/foo)

  ISR_arr[$i]=$ISR
  VS_arr[$i]=$VS
  VF_arr[$i]=$VF
  RC_arr[$i]=$RC

  echo "$percentage ${ISR_arr[@]}" >> isr.dat
  echo "$percentage ${VF_arr[@]}" >> vf.dat
  echo "$percentage ${VS_arr[@]}" >> vs.dat
  echo "$percentage ${RC_arr[@]}" >> rc.dat
done
