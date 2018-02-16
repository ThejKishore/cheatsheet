
## SELECT

```sql
SELECT
    [COLUMN_NAME] as [RENAME_COLUMN_NAME]
        FROM
            [TABLE] [TABLE_ALIAS]

        WHERE
            [CONDITION]
```

### DIFF B/W WHERE AND HAVING
HAVING is used to check conditions after the aggregation takes place.

WHERE is used before the aggregation takes place.


#### WHERE

```sql
select
    City, CNT=Count(1)
        from Address
            where
                State = 'MA'
```

##### OPERATION IN WHERE
|   operator  | description  |
| --- | --- |
| >	|Greater Than |
| >= |	Greater than or Equal to |
| <	| Less Than |
| <= |	Less than or Equal to |
| =	| Equal to |
| <> |	Not Equal to |
| BETWEEN |	In an inclusive Range |
| LIKE	| Search for a pattern |
| IN	| To specify multiple possible values for a column |


##### Query to find 2nd highest salary

```sql
SELECT
    name, MAX(salary) AS salary
        FROM employee
            WHERE salary < (SELECT MAX(salary) FROM employee);
```

##### Aggregate Functions used with `group by`

1) Count()
2) Sum()
3) Avg()
4) Min()
5) Max()

##### Order by

```sql
SELECT * FROM table_name ORDER BY column_name ASC|DESC
```


##### inner join
```sql
SELECT
    table1.column1,table1.column2,table2.column1,....
FROM
    table1
INNER JOIN table2
ON
    table1.matching_column = table2.matching_column;
```

##### left join

```sql
SELECT
    table1.column1,table1.column2,table2.column1,....
FROM
    table1
LEFT JOIN table2
ON
    table1.matching_column = table2.matching_column;

```


##### outer join or right join
```sql
SELECT
    table1.column1,table1.column2,table2.column1,....
FROM
    table1
RIGHT JOIN table2
ON
    table1.matching_column = table2.matching_column;
```


##### fuller join
```sql
SELECT
    table1.column1,table1.column2,table2.column1,....
FROM
    table1
FULL JOIN table2
ON
    table1.matching_column = table2.matching_column;
```


##### UNION | UNION ALL

```sql
SELECT column_name(s) FROM table1 UNION SELECT column_name(s) FROM table2;

Resultant set consists of distinct values.

SELECT column_name(s) FROM table1 UNION ALL SELECT column_name(s) FROM table2;

Resultant set consists of duplicate values too.
```


DROP vs TRUNCATE

* Truncate is normally ultra-fast and its ideal for deleting data from a temporary table.
* Truncate preserves the structure of the table for future use, unlike drop table where the table is deleted with its full structure.
* Table or Database deletion using DROP statement cannot be rolled back, so it must be used wisely.
