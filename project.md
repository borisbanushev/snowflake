So I want to make end-to-end demo on the Snowflake Data Platform for a financial services use case. Can you recommend some use case? Most likely credit decisioning or credit scoring. 

The idea behind the demo is the following - make sure you create the project in the same way. 

1. First, create a very professional project that will be on GitHub. 

2. The project needs to be cloned once developed, needs to be cloned on the Snowflake data platform and automatically somehow developed or deployed for testing. 

3. Third, there should be a few external data sources that you need to connect through their Horizon catalogue. 
3.1. The first one should be Databricks that will store some of the data 
3.2. Second one should be MySQL database which will be on laptop stored 
3.3. Third one would be Oracle database that will store let's say T24 Terminus 24 financial services data. 

The project should also have proper governance lineage that will be It would have the following components:
- first, unification of all the data of these sources to be merged in this unified one single place in Snowflake governed by their governance catalog; 
- second, it should do some sort of data cleaning, processing, etc. and then
- finally it should create a machine learning model for, let's say, creating the the credit score of a person based on features. 

Make all these tables with a lot of columns, make them very professional, create a schema for each table and populate with sample data. We need to create realistic estate of the data estate for a large bank. Then there should be the GenAI capabilities of Snowflake where we will have to query data with Cortex and all of that should be inside of an application in Streamlit. Give me a plan on how would you implement it, what sources, how would you put the data in these external data sources, how would you connect to it, then it should have the data, the Snowflake native connectors, what will be the Snowflake components, how can I develop and through GitHub published into Snowflake and everything in the professional plan. 