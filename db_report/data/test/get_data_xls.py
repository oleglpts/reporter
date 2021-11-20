def get_data(self):
    self._conn.execute(
        self._replace_param(
            """SELECT b.LastName, b.FirstName, round(sum(a.Total), 2), round(sum(a.Total)/50, 2) 
            FROM Invoice AS a JOIN Customer AS b ON (b.CustomerId = a.CustomerId)
            WHERE b.LastName LIKE '%{{customer}}%'
            GROUP BY b.LastName, b.FirstName
            ORDER BY b.LastName, b.FirstName;
            """
        )
    )
    return self._conn.fetchall()


self._rows = get_data(self)
