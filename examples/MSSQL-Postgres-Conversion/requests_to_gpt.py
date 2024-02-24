### Defines all the diffent purpose request sent to GPT model.
from sqltops_sp import send_request_to_azure
from ui_utils import extract_content_from_response
import json


with open('table_schema.json', 'r') as ts:
    table_schema = json.load(ts)


def send_requet_with_custom_conv(sp, system_message):
    conversation = [system_message]

    current_message = {"role":"user", "content":str(sp)}
    conversation = conversation +[current_message]
    return send_request_to_azure(conversation)


## Extract important table names 
# System Setup
system_message_find_tables = {
    "role": "system",
    "content": """
        Given the following SQL Server Stored Procedures find out the tables, What are the names of the table. Respond is a json formatted value.
        example : {tables: ["table1","table2"]}
        """
}


def find_tables_from_sp(sp):
    return send_requet_with_custom_conv(sp, system_message_find_tables)


# System Setup
system_message_translate_to_postgres= {
    "role": "system",
    "content": "You help convert SQL Server Stored Procedures to PostgreSQL Stored Procedures. \
        You are a confindant Assistant. Make sure that the bits in SQL server are translated to boolean of Postgres \
        Make the CameCase column names in doublequotes.\
        Only repond with conveted SQL.\
        Make sure the datatypes match the schema of tables provided.\
        Copy the parameter name exactly wihtout '@'"
}


def translate_to_postgres(sp):
    resp = find_tables_from_sp(sp)
    # print(resp.json())
    if resp.ok:
        tables = extract_content_from_response(find_tables_from_sp(sp))
        print(tables)
        tables = json.loads(tables)
        sp += "\n Here are the Shemas of realted tables\n"
        for item in tables['tables']:
            schema = table_schema.get(item)
            if schema:
                sp += schema +'\n'

    
    return send_requet_with_custom_conv(sp, system_message_translate_to_postgres)

sample_sp = """
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE PROCEDURE [dbo].[GetDynamicRoleEffectivePermissionsByDynamicRoleID]
(
	@dynamicRoleID int
)
AS
BEGIN
	SELECT CAST(ROW_NUMBER() OVER (ORDER BY (SELECT 1)) AS INT) ID, d.[ID] AS PermissionID, d.[SecurableCommand], d.[StateDef], d.[Source]
		FROM (
			-- Select all permissions which are directly applied to this dynamic role
			SELECT p.[ID], p.[ObjectFunctionID] AS SecurableCommand, p.[StateDef], 'Applied Directly' AS Source
				FROM [Permission] p
				WHERE (p.[AppliesToDynamicRoleID] = @dynamicRoleID)) d;
END
GO

"""

if __name__ == "__main__":
    res = translate_to_postgres(sample_sp)
    print(extract_content_from_response(res))