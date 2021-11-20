global data, description

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
data, description = cursor.fetchall(), cursor.description
