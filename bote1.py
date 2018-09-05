from bottle import route, run

@route('/hello')
def hello():
    return "Hello World!\n" 
run(host='10.28.13.25', port=8080, debug=True)
