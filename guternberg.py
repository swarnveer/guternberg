from flask import Flask
import mysql.connector
from flask import request, jsonify

app = Flask(__name__)
app.config["DEBUG"] = True

#to add %s in where clause, see function usage to get more info
def api_split(le):
    a="%s,"*le
    return a[:-1]

#similar to above funtion with varied requirement
def app_complex_split(st,obj):
    s=" where"
    if st=="topic":
        for _ in range(len(obj)):
            s+=' bsub.name like %s COLLATE utf8_general_ci or bs.name like %s COLLATE utf8_general_ci or'
        return s[:-3]
    elif st=="author":
        for _ in range(len(obj)):
            s+=' a.name like %s COLLATE utf8_general_ci or'
        return s[:-3]
    elif st=="title":
        for _ in range(len(obj)):
            s+=' b.title like %s COLLATE utf8_general_ci or'
        return s[:-3]

#using pagination here as per the requirement
@app.route('/api/v1/books', defaults={'page':1}, methods=['GET'])
@app.route('/api/v1/books/<int:page>', methods=['GET'])
def api_specific(page):
    conn = mysql.connector.connect(CONNECTION_DETAILS)
    #extracting the arguments from the url
    query_parameters = request.args
    book_id = query_parameters.get('book_id')
    lang = query_parameters.get('lang')
    mime_type = query_parameters.get('mime_type')
    topic = query_parameters.get('topic')
    author = query_parameters.get('author')
    title = query_parameters.get('title')

    #As the data is splitted into 10 tables so a join was needed
    query = '''SELECT SQL_CALC_FOUND_ROWS b.title "title",a.name "author",b.media_type "genre",GROUP_CONCAT(DISTINCT l.code) "language",GROUP_CONCAT(DISTINCT bsub.name) "subject(s)",GROUP_CONCAT(DISTINCT bs.name) "bookshelf(s)",GROUP_CONCAT(DISTINCT f.url) "links"
    FROM books_book b
inner join books_book_authors ba on b.id=ba.book_id
inner join books_author a on a.id=ba.author_id
inner join books_book_bookshelves bss on ba.book_id=bss.book_id
inner join books_bookshelf bs on bss.bookshelf_id=bs.id
inner join books_book_subjects bsubs on bsubs.book_id=ba.book_id
inner join books_subject bsub on bsubs.subject_id=bsub.id
inner join books_format f on f.book_id=ba.book_id
inner join books_book_languages ls on ls.book_id=ba.book_id
inner join books_language l on ls.language_id=l.id'''
    to_filter = tuple()
    #Based on which arguments are present we can add the where condition in where clause
    if book_id:
        book_var=tuple(book_id.split(","))
        query += ' where b.gutenberg_id in ('+api_split(len(book_var))+') AND'
        to_filter+=book_var
    if lang:
        lang_var=tuple(lang.split(","))
        query += ' where l.code in ('+api_split(len(lang_var))+') AND'
        to_filter+=lang_var
    if mime_type:
        if ',' in mime_type:
            mime_type_var=tuple(mime_type.split(","))
        else:
            mime_type_var=tuple(mime_type)
        query += ' where f.mime_type in ('+api_split(len(mime_type_var))+') AND'
        to_filter+=mime_type_var
    if topic:
        topic_var=tuple(topic.split(","))
        query += app_complex_split("topic",topic_var)+' AND'
        topic_var=list(topic_var)
        for item in range(len(topic_var)):
            topic_var[item]="%"+topic_var[item]+"%"
        topic_var2=tuple(topic_var)*2
        to_filter+=topic_var2
    if author:
        author_var=tuple(author.split(","))
        query += app_complex_split("author",author_var)+' AND'
        author_var=list(author_var)
        for item in range(len(author_var)):
            author_var[item]="%"+author_var[item]+"%"
        author_var2=tuple(author_var)
        to_filter+=author_var2
    if title:
        title_var=tuple(title.split(","))
        query += app_complex_split("title",title_var)+' AND'
        title_var=list(title_var)
        for item in range(len(title_var)):
            title_var[item]="%"+title_var[item]+"%"
        title_var2=tuple(title_var)
        to_filter+=title_var2
    if(query[-4:]==" AND"):
        query = query[:-4]

    query+=''' GROUP by b.title,a.name,b.media_type order by b.download_count desc LIMIT 25 OFFSET %s;'''
    if(page==1):
        to_filter+=(0,)
    else:
        to_filter+=(((page-1)*25),)
    if conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        if(len(to_filter)>0):
            cursor.execute(query,to_filter)
        else:
            cursor.execute(query)
        record = cursor.fetchall()
        #to get total row count, irrespective of offset and limit
        cursor.execute('SELECT FOUND_ROWS() "count";')
        count=cursor.fetchall()
        t={}
        t.update(count[0])
        t["result"]=record
    conn.close()
    return jsonify(t)

@app.route('/')
def hello_world():
    return 'Hello from Flask!'


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404
