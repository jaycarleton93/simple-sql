# simple-sql
A simplified extension of the mysql library, making it simpler to query and execute actions, as well as handle the results.

## Setup
This repository requires the mysql-connector package. I reccomend installing this via pip:  
```
pip3 install mysql-connector
```
  
**Python version**: 3

## Usage

### Connection
To connect to a server:
```
from simpleSQL.dbConnection import sqlHelper
  
connection=sqlHelper(
	username='USER',
	password='PASSWORD',
	host='123.45.6.789',
	port=100,
  database='database1'
)
```
**Note:** When you create the connection object, you can leave the database blank, however you would then need to specify the name of the database for each table, in all subsequent SQL statements.

### Querying
Querying is done using the **query()** command, and the results are returned in a list of rows, where each row is a dict(key=column header, value=cell value).   
For example:
```
results=connection.query('''
  SELECT
    name,
    born,
    country_of_origin,
    favourite_movie as `faveFlick`
  FROM
    people
''')
```  
would return the following data:
```
[
  {'name':'Mark Markesson','born':datetime.date(2000,1,1),'country_of_origin':'Canada','faveFlick':'Frankenstein'},
  {'name':'John Johnson','born':datetime.date(`1991,10,3),'country_of_origin':'United States','faveFlick':'Harry Potter'},
]
```
**Optional Parameters:**   
@param exit_on_fail: Whether to exit, when all retries are exhausted. Default is True  
@param retries: Number of times to retry on failure. Defualt is 0  
@param retry_cooldown: Number of seconds to wait between retries, on failue. Default is 7  

### Executing
Execution of UPDATE, INSERT, DELETE, and other commands that modify data is done via the **execute()** function.  
For example:
```
connection.execute('''
  UPDATE
    people
  SET 
    favourite_movie='Titanic'
  WHERE
    born<='2000-01-01'
'''
)
```
**Optional Parameters:**   
@param exit_on_fail: Whether to exit, when all retries are exhausted. Default is True  
@param retries: Number of times to retry on failure. Defualt is 0  
@param retry_cooldown: Number of seconds to wait between retries, on failue. Default is 7  
  
### Other
#### Converting List to SQL Array
To convert a list of values, into SQL-formatted array, use the listToSQLArray function.
For example:
```
names=listToSQLArray(['Ian','Jonas','Katrina'])
results=connection.query(f'''
   SELECT
      *
   FROM
      people
   WHERE
      name in {names}
'''
)
```
