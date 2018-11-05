#!/usr/bin/Rscript
args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0)
{
  stop("Error",call.=FALSE)
}
w1 <- read.table(args[1])[,1]

# Errors
errorFDP <- qt(0.975,df=length(w1)-1)*sd(w1)/sqrt(length(w1))
# errorFIP <- qt(0.975,df=length(w1$FIP)-1)*sd(w1$FIP)/sqrt(length(w1$FIP))
# errorISD <- qt(0.975,df=length(w1$ISD)-1)*sd(w1$ISD)/sqrt(length(w1$ISD))
# errorISR <- qt(0.975,df=length(w1$ISR)-1)*sd(w1$ISR)/sqrt(length(w1$ISR))

rightFDP <- mean(w1)-errorFDP
leftFDP <- mean(w1)+errorFDP
# rightFIP <- mean(w1$FIP)-errorFIP
# leftFIP <- mean(w1$FIP)+errorFIP
# rightISD <- mean(w1$ISD)-errorISD
# leftISD <- mean(w1$ISD)+errorISD
# rightISR <- mean(w1$ISR)-errorISR
# leftISR <- mean(w1$ISR)+errorISR

FDP <- c(mean(w1),rightFDP,leftFDP)
# FIP <- c(mean(w1$FIP),rightFIP,leftFIP)
# ISD <- c(mean(w1$ISD),rightISD,leftISD)
# ISR <- c(mean(w1$ISR),rightISR,leftISR)

cat(FDP,"\n")
