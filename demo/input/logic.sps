* Strict GET DATA: Valid for PSPP, Readable by SpecGen.
GET DATA
  /TYPE=TXT
  /FILE='demo_data.csv'
  /DELIMITERS=","
  /ARRANGEMENT=DELIMITED
  /FIRSTCASE=2
  /VARIABLES=
  revenue F8.2
  cost F8.2.

* Logic.
COMPUTE profit = revenue - cost.
SELECT IF (profit > 0).
EXECUTE.

* Strict Save.
SAVE TRANSLATE OUTFILE='demo_results.csv'
  /TYPE=CSV
  /MAP
  /REPLACE.
