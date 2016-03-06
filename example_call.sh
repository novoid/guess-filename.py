#!/bin/sh

myexit() {
    echo "./guessfilename_test.sh returned ERROR(S). Please do test and try again."
    exit 1
}

## run unit tests beforehand but dump output:
./guessfilename_test.sh >/dev/null 2>&1 || myexit()

echo

./guessfilename.py --verbose --dryrun testdata/2016-02-24\ A1\ Rechnung\ 02-2016\ -\ 12,12\ EUR\ --\ scan\ finance.pdf

##end
