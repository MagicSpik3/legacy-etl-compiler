* Define the input data format.
GET DATA
  /TYPE=TXT
  /FILE='data.csv'
  /ARRANGEMENT=DELIMITED
  /DELIMITERS=","
  /FIRSTCASE=2
  /VARIABLES=
    id F4.0
    gender A1
    height_m F8.2
    weight_kg F8.2.

* Compute BMI.
* Formula: Weight (kg) / Height (m)^2.
COMPUTE bmi = weight_kg / (height_m * height_m).
EXECUTE.

* Categorize BMI into standard WHO categories.
* Underweight: < 18.5
* Normal: 18.5 - 24.9
* Overweight: 25.0 - 29.9
* Obese: >= 30.0.
STRING bmi_category (A15).
RECODE bmi (Lo THRU 18.499 = 'Underweight')
           (18.5 THRU 24.999 = 'Normal')
           (25.0 THRU 29.999 = 'Overweight')
           (30.0 THRU Hi = 'Obese')
           INTO bmi_category.
EXECUTE.

* Add Variable Labels for clarity.
VARIABLE LABELS 
  height_m 'Height in Meters'
  weight_kg 'Weight in Kilograms'
  bmi 'Body Mass Index'
  bmi_category 'WHO BMI Category'.

* Analysis 1: Descriptive Statistics for continuous variables.
DESCRIPTIVES VARIABLES=height_m weight_kg bmi
  /STATISTICS=MEAN STDDEV MIN MAX.

* Analysis 2: Frequency table for categories.
FREQUENCIES VARIABLES=bmi_category
  /ORDER=ANALYSIS.

* Analysis 3: Cross-tabulation by Gender.
CROSSTABS
  /TABLES=gender BY bmi_category
  /CELLS=COUNT ROW.
  
  

* --- NEW: EXPORT GOLD STANDARD OUTPUT ---
* Instead of printing tables, we save the processed data to a CSV.
* This allows the Python Critic to compare dataframes directly.
SAVE TRANSLATE
  /OUTFILE='gold_output.csv'
  /TYPE=CSV
  /MAP
  /REPLACE
  /FIELDNAMES
  /CELLS=VALUES.  
  
  
  