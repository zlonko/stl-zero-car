# stl-crime

## Description
This code transforms NIBRS data reported by the St. Louis Metropolitan Police Department. These data are included as a static extract for the years 2021-2023 in the `process_data` directory. 

The script will aggregate incident-level data by neighborhood, date (month-year), and firearm use. The output is a count of incidents at each level. 

Not all incidents are associated with UCR codes or related to offenses. For that reason, incidents that are unresolved or unspecified are excluded from these aggregations.

## Instructions
Run the following command in the terminal:
```
python3 transform_stl_city_data.py
```