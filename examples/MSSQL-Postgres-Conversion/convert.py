from sqltops_sp import convert_to_postgreSQL
from tqdm import tqdm 

from ui_utils import read_sql_server_sp, save_updated_sp, extract_content_from_response
from requests_to_gpt import translate_to_postgres
import os


# def save_postgres_sp(converted_sp):
#     for item in converted_sp.items():
#         sp_name = item[0] + ".sql"
#         sp_base = "postgres SP"
#         file = Path(sp_base, sp_name)

#         with open(file, 'w') as csp:
#             csp.writelines(item[1])

# def extract_content_from_response(resp):
#     return resp.json()['choices'][0]["message"]['content']



def translate_sp():
    with open ("Web Client SP list.txt", 'r') as wsp:
        web_sp_list = wsp.readlines() 

    web_sp_list = [x.split("\n")[0] for x in web_sp_list]

    errors = {}
    sql_server_sp = {}
    model_response = {}

    for item in tqdm(web_sp_list, "Reading SQL Server Files..."):
        try:
            sql_server_sp[item] = read_sql_server_sp(item)
        except Exception as e :
            errors[item] = e

    for sp_name, sp in tqdm(sql_server_sp.items(), "Translating SQL Server Files to Postgres..."):
        try:
            model_response[sp_name] = extract_content_from_response(translate_to_postgres(sp))
        except Exception as e:
            errors[sp_name] = e
    
    for item in tqdm(model_response.items(), "Saving to file..."):
        save_updated_sp(item[0], item[1])

    print(errors)




def translate_functions():
    func_list = os.listdir()

def translate_views():
    pass




if __name__ == "__main__":
    

    translate_sp()


    
        
