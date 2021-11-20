global columns, data

sql = """
    SELECT
        b.LastName AS "First name", b.FirstName AS "Last name", round(sum(a.Total), 2) AS Total,
        round(sum(a.Total)/50, 2) AS Discount
    FROM Invoice AS a JOIN
        Customer AS b ON (b.CustomerId = a.CustomerId)
    WHERE b.LastName LIKE '%{{customer}}%'
    GROUP BY b.LastName, b.FirstName
    ORDER BY b.LastName, b.FirstName;
"""
for parameter in parameters_list:
    sql = sql.replace('{{%s}}' % parameter, parameters_list[parameter])
cursor.execute(sql)
columns = [col[0] for col in cursor.description]
data = [dict(zip(columns, (str(y) for y in rw))) for rw in cursor.fetchall()]
