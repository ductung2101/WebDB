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

12.01.2020:
  Some more thoughts and todos:
  * The graph is being generated and overwritten, but the old one does not disappear and remains underneath, on the web page. This generates weird behavior when hovering the mouse over it. We need to fix this.
  * The form has to look better, and be validated, etc.
  * The correlation numbers have to be meaningful. Ideally we can also select which candidates we include and which not.
  * Go back to the ideas for plots and all those things that we had and start implementing them, one by one.

27.02.2020
  To-do list before the final presentation:
  * Fix all the numbers, display them with only 2 digits. Too many digits now. -DONE
  * Sort out the database according to the plan, and rewrite parts of data.py to use it in an efficient manner. Make sure to keep the same column names, so that no other changes are required downstream for the plots!
  * Make plots nicer, with maybe color schemes, hover text, titles, labels, etc.
  * We have a default value for the "state" field in the form. Set decent default values for "Candidates" and "Outlets". My suggestion: hardcode a list of important candidates, for outlets just use all of them (but populate the form field nevertheless).
  * Right now, in the table, we can see the average percentages across the entire period. Add the growth rate as well, i.e. last_value - first_value of the series. Color it green or red, depending on whether it is positive or negative. It is interesting to see whether candidates are going up or down in polls and media coverage.
  * There is a raw version of the text for now, but we might want it improved.
  * Figure out the per-candidate or per-station page. Up to Michal to decide how.
  * (Optional) Do the about us page.
