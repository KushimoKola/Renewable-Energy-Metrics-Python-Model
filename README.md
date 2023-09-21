# Renewable-Energy-Metrics-Python-Model
Modeling key metrics for a  green energy generating plant - Python code.
 - Only standard Python 2 libraries were used, and code ran successfully in Jython 2.7.

## OBTAINABLES
### MODEL METRICS
Your script should calculate, and your summary table display the following summary metrics:
1. Generation in KWh, defined as the difference in total generation between the meter reading in the period minus the meter reading in the prior period.
2. Average irradiance in Wh per m2, defined as the arithmetic mean of recorded values in the period.
3. Sunshine share in %, defined as the percent of recorded irradiance values in the period >200 Wh per m2.

### ADDITIONAL INSTRUCTIONS
Your script must:
1. Be coded in Jython 2.7.
2. Refrain from using any 3rd party libraries which are not standard Jython or Java packages.
3. Generate hourly summary values for each site and metric.
4. Export output to a .csv file.