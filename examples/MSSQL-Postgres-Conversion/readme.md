# SQL Server to Postgres Query Translation

 This project uses ChatGPT to convert SQL Server queries into Postgres queries.
 Has an UI App that is used to review the translated code.

## Technologies Used

- ChatGPT
- SQL Server
- Postgres
- Python

## Installation and Running

  This Application runs in two Phases.

1. Batch Conversion 
2. Review and Save Code

To install and run this project, follow these steps:

1. Clone the repository.

2. Install the necessary dependencies.

### Batch Conversion

1. Update the folder path where you have saved your SQL Server Queries in the file `ui_utils.py`
   
   ```
   Example
   #converted from Stored Procedures
   POSTGRES_FUNCTION_A  =  'postgres/functionsA'
   REVIEWED_POSTGRES_FUNCTION_A  =  'postgresR/functionsA'
   SQLSERVER_SP  =  'SQLServer/stored_procedures/'
   ```

#converted from Functions
POSTGRES_FUNCTION_B  =  'postgres/functionsB'
REVIEWED_POSTGRES_FUNCTION_B  =  'postgresR/functionsB'
SQLSERVER_FUNCTIONS  =  'SQLServer/functions/'

#converted from Views
POSTGRES_VIEW  =  'postgres/views'
REVIEWED_POSTGRES_VIEW  =  'postgresR/views'
SQLSERVER_VIEWS  =  'SQLServer/views/'

```
2. Add all the required credentials and resource endpoints for Azure OpenAI API in `sqltops_sp.py`.
```

Example
api_base="" # Base url of endpoint
api_key="" 
deployment_id="" #deployment Name for GPT-4 Model

```
3. Run `app.py`

### Review Converted Queries

1. Make sure the converted Queries are saved at the correct folder location.
2. Update the PostgreSQL credentials in `connect_to_postgres.py`
```

Example 
host="localhost",
database="",
user="",
password=""

```
3. Run `uiapp.py`
4. Open the URL from step 2
5. To save the Query after edit use `Ctrl S`
6. `Run in postgreSQL` will run the query on PostgreSQL.

## Dependencies

This project requires the following dependencies:

- A working installation of Postgres.
- Export of SQL Files from SQL Server
- The necessary libraries for running ChatGPT and API Information.
```