import sqlite3

conn = sqlite3.connect("exam.db")
curs = conn.cursor()


sql = """
SELECT AVG(salary),MAX(salary),MIN(salary),SUM(salary)
FROM employees
"""

import pandas as pd

df = pd.read_sql(sql,conn)

curs.close()
conn.close()
print(df)