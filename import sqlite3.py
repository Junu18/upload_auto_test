import sqlite3
conn = sqlite3.connect("exam.db")



curs = conn.cursor()

sql = """

SELECT  last_name, salary * 12  AS "연봉"
FROM employees    
WHERE salary * 12 >= 12000
"""
import pandas as pd

df = pd.read_sql(sql,conn)

curs.close()
conn.close()

print(df)
