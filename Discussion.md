# WebDB

Make Django app run on localhost: Tutorial
  https://docs.djangoproject.com/en/2.2/intro/tutorial01/
  
Work to be done:
  
  Figure out:
    
    1. Data 
        How to get data put into DB --> all data in Django is created and managed in Model
        How to create function to update DB (automatically): DB is on GitHub, use python to download CSV file and update.
        
    2. HTML
        Frontend: Create a view (use Tutorial + Templates from Django?)
                  Develop a good view.
        Backend:
                  Use data in DB to display in view
                  How to do visualization

02.12.2019:
  Questions and to-do items going forward:
  * Added the sample graph with the polling aggregations, however we need to figure out how to make it interactive. What kind of selectors do we have? How do we pass that information to the backend request? How do we recompute the information required?
  * What are question_id, poll_id, pollster_id? Where can we get descriptions for them? Would they be useful for us?
  * We need to import the data for media in the sqlite database. How do we do the linking with the current polling data, by candidate_id maybe? Do we have a schema?
  * The updating code is written, but it needs to be automated:
    * pull data from github
    * compare and add to local database.