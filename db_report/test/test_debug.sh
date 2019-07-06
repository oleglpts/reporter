#!/bin/bash

cd ..
./__main__.py -p title0=Invoices, customer=, title1=Albums, title2=Money, title3=Sales, title4=Customers, artist= -o ~/.db_report/test -n test_sqlite3_xls -l DEBUG -k 12345
./__main__.py -p title0=Invoices, customer=, title1=Albums, title2=Money, title3=Sales, title4=Customers, artist= -o ~/.db_report/test -n test_sqlite3_csv -l DEBUG -k 12345
