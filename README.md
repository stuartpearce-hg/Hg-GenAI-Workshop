## 🤔 What is this, how does it work?  
This tooling aims to enhance the quality and accuracy of responses Gen AI LLMs provide when asked to support software engineers refactoring enterprise codebases.
Expanding the context made available to the LLM through use of retrieval augmented generation to select code most relevant to an engineer's prompt.  

These tools utilise **LangChain (https://python.langchain.com/docs/get_started/introduction)** source code can be indexed for use with a range of LLMs.
You are encouraged to adapt and enhance tools for specific use cases and where possible contribute back enhancements to the community. Please refer to LICENSE file for details of the MIT license in use

## Usage
**Set configuration values**  
Rename .env.example to .env and populate with configuration values for your LLM provider. Hg currently reccomend use of Azure OpenAI Services    
OPENAI_API_BASE = URL to your LLM account  
OPENAI_API_KEY = Your API Key  
OPENAI_API_TYPE = "azure"  
OPENAI_API_VERSION = Service API version to be used  
OPENAI_API_DEPLOYMENT_NAME = Name of your deployed LLM  
OPENAI_API_EMBEDDINGS_NAME = Name of your deployed embedding engine  
REPOSITORY_DIRECTORY = Path to source code for analysis  

**Dependency setup**  
With pip:
pip install openai tiktoken langchain esprima faiss-cpu unstructured

**Build vecotr database of code**  
Edit line 37 of build.py to refernce file extensions relevant to the codebase e.g. for C# set suffixes=['.cs', '.csproj', '.sln']
Filtering greatly improves performance by eliminating content thats not relevant to queries from the model context
Run build.py

**Query the code**  
Uncomment lines 51-55 of query.py and adjust the prompt to provide base context of the nature of code and application working with. This can help focus the range of suggestions made by LLM.
run query.py pairing with LLM to interogate codebase and options to enhance
prompt "quit" when finished

Large codebases can suffer degraded performance when too much or too little context is made available to the LLM alongside prompt inputs.
Adjusting the code retrieval parameters on line 41  **search_kwargs={"k": 20, "fetch_k": 50}** can improve LLM performance by ensuring sufficient context is provided but not too much to include unrelated code.

**Agent tooling is under development**
This tooling Uses CrewAI to orchestrate agent based resolution of tasks within a defined process
Agents can utilise tools which require external setup for Github and Jira

See https://python.langchain.com/docs/integrations/toolkits/github and https://python.langchain.com/docs/integrations/toolkits/jira for setup instructions
