# guternberg
This API supports pagination so you can make requests as:

#This will give json with page 1 as default with upto 25 results
http://swarnveer.pythonanywhere.com/api/v1/books?topic=fiction

#In the below request url we are fetching the data from the 45th page
http://swarnveer.pythonanywhere.com/api/v1/books/45?topic=fiction

Below arguments are supported:
book_id 
lang 
mime_type  
topic 
author 
title

Each argument supports multiple value such as request can be like ?book_id=1,2,3

And we can we can use multiple arguments at the same time such as ?book_id=1&lang=en

topic,author and title supports case-insensitive partial match 
