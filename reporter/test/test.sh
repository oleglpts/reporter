#!/bin/bash

cd ..
./report.py -p title0=Invoices, customer=, title1=Albums, title2=Money, title3=Sales, title4=Customers, artist= -o ~/.report/test -n test_$1 -l DEBUG -k 12345
