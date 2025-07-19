import sqlite3

conn = sqlite3.connect("exam.db")
curs = conn.cursor()

sql = """

SELECT  job_id
FROM employees
WHERE job_id LIKE 'S%_C%'

"""

import pandas as pd

df = pd.read_sql(sql,conn)

curs.close()
conn.close()

print(df)