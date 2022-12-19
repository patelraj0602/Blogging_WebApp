# All the functions, instances which are in __init__ can be imported directly via the syntex below
from flaskblog import app                           # (https://www.youtube.com/watch?v=vM3ScLNTGoQ)

if __name__ == '__main__':
    app.run(debug=True)