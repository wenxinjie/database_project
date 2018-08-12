#!/usr/bin/env python2.7

"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver

To run locally:

    python server.py

Go to http://localhost:8111 in your browser.

A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from flask_bootstrap import Bootstrap
import numpy as np
import json

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
bootstrap = Bootstrap(app)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@104.196.18.7/w4111
#
# For example, if you had username biliris and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://biliris:foobar@104.196.18.7/w4111"
#
DATABASEURI = "postgresql://xw2504:0242@35.231.44.137/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);""")
engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

@app.route('/',methods=["GET","POST"])
def index():

  """
  #request is a special object that Flask provides to access web request information:

  #request.method:   "GET" or "POST"
  #request.form:     if the browser submitted a form, this contains the data in the form
  #request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  #See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data

  """

  # DEBUG: this is debugging code to see what request looks like
  print (request.args)

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#

  #
  # example of a database query
  #

  #cursor=g.conn.execute("SELECT first_name FROM coach")
  #names = [ ]
  #for result in cursor:
   # names.append(result[ 'first_name' ])  # can also be accessed using result[0]
  #cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  #context = dict(data=names)


  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("login.html")

  #
  # This is an example of a different path.  You can see it at:
  #
  #     localhost:8111/another
  #
  # Notice that the function name is another() rather than index()
  # The functions for each app.route need to have different names


@app.route('/home',methods=['GET'])
def home():
  return render_template('index.html')


@app.route('/query_all')
def query_all():
  table_names=['coach','game','player','playoff','pre_team','record',
              'team','team_competition']

  return render_template('query_all.html',table_names=table_names)


@app.route('/home_1')
def search_column():
  table_names = ['coach', 'game', 'player', 'playoff', 'pre_team', 'record',
                 'team', 'team_competition']

  table = request.args.get("table_name")

  global home_table
  home_table=str(table)
  cursor = g.conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s",home_table)
  columns = []
  for result in cursor:
    columns.append(result['column_name'])  # can also be accessed using result[0]
  cursor.close()

  global key_column
  key_column = columns

  return render_template('query_all.html', data_1=columns,table_names=table_names,table_holder = home_table)


@app.route('/home_2')
def search_row():
  table_names = ['coach', 'game', 'player', 'playoff', 'pre_team', 'record',
                 'team', 'team_competition']

  cursor = g.conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", home_table)

  columns = []
  for result in cursor:
    columns.append(result['column_name'])  # can also be accessed using result[0]
  cursor.close()

  column = request.args.get("column")

  global column_global
  column_global=column

  sent="SELECT DISTINCT "+ column +" FROM "+home_table
  cursor = g.conn.execute(sent)

  values = []
  for result in cursor:
    values.append(result[column])  # can also be accessed using result[0]
  cursor.close()

  return render_template('query_all.html', data_2=values, data_1=columns,table_names=table_names,table_holder = home_table,column_holder=column)


@app.route('/home_result')
def search_home_result():

  table_names = ['coach', 'game', 'player', 'playoff', 'pre_team', 'record',
                 'team', 'team_competition']


  cursor = g.conn.execute("SELECT column_name FROM information_schema.columns WHERE table_name = %s", home_table)
  columns = []
  for result in cursor:
    columns.append(result['column_name'])  # can also be accessed using result[0]
  cursor.close()


  sent = "SELECT DISTINCT " + column_global + " FROM " + home_table
  cursor = g.conn.execute(sent)
  values = []

  for result in cursor:
    values.append(result[column_global])  # can also be accessed using result[0]
  cursor.close()


  row = request.args.get("row")

  column_word  = 'SELECT '

  for i in range(len(key_column)):
    if i < len(key_column)-1:
     temp = str(key_column[i]) + ','
    else:
      temp = str(key_column[i])
    column_word += temp

  sent= column_word + " FROM "+ home_table + " WHERE "  +column_global + " = %s"

  cursor = g.conn.execute(str(sent),row)
  results = []
  for result in cursor:
    n = len(result)
    tem=[]
    for i in range(n):
      if type(getattr(result, str(key_column[i]))) is unicode:
        tem.append(unicode.encode(getattr(result, str(key_column[i]))))
      else:
        tem.append(getattr(result, str(key_column[i])))
    results.append(tem)  # can also be accessed using result[0]
  cursor.close()


  return render_template('query_all.html', result=results,data_2=values, data_1=columns,table_names=table_names,
                         table_holder = home_table,column_holder=column_global,column_value_holder=row,column_name = key_column,length = range(len(key_column)))


@app.route('/validcheck',methods=['POST','GET'])
def validcheck():
  ninput=request.form['username']
  pinput=request.form['password']
  if ninput=='xw2504' and pinput=='0242':
    return render_template('dashboard.html')
  else:
    msg = 'username or passwords wrong, please input again'
    return render_template('login.html',msg = msg)



@app.route('/dashboard')
def dash():
  return render_template('dashboard.html')


@app.route('/update')
def update():
  cursor = g.conn.execute("SELECT team_id FROM team")
  teams_id = []
  for result in cursor:
    teams_id.append(result['team_id'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT DISTINCT(position) FROM player")
  poses = []
  for result in cursor:
    poses.append(result['position'])  # can also be accessed using result[0]
  cursor.close()
  return render_template('update.html',teams_id = teams_id,poses=poses,heights=np.arange(170,231),years=np.arange(1995,2019),ages=np.arange(18,40) )

@app.route('/add_player')
def add_player():
  pid = request.args.get('pid')
  fname = request.args.get('fname')
  lname = request.args.get('lname')
  college = request.args.get('college')
  height = request.args.get('height')
  position = request.args.get('pos')
  tid = request.args.get('team_id')
  since = request.args.get('since')
  age = request.args.get('age')

  cursor = g.conn.execute("SELECT team_id FROM team")
  teams_id = []
  for result in cursor:
    teams_id.append(result['team_id'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT DISTINCT(position) FROM player")
  poses = []
  for result in cursor:
    poses.append(result['position'])  # can also be accessed using result[0]
  cursor.close()

  cursor = g.conn.execute("SELECT player_id FROM player")
  players_id = []
  for result in cursor:
    players_id.append(result['player_id'])  # can also be accessed using result[0]
  cursor.close()

  if len(pid) !=5 :
    msg = 'Invalid Id'
    return render_template('update.html',msg = msg,teams_id = teams_id,poses=poses,heights=np.arange(170,231),years=np.arange(1995,2019),ages=np.arange(18,40))
  elif pid in players_id:
    msg = 'Id Already Exists!'
    return render_template('update.html',msg = msg,teams_id = teams_id,poses=poses,heights=np.arange(170,231),years=np.arange(1995,2019),ages=np.arange(18,40))
  else :
    g.conn.execute('INSERT INTO player(player_id,first_name,last_name,height,college,position,team_id,since,age) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s);',
      (pid, fname, lname, height, college, position, tid, since, age))
    msg = 'Add a new player successfully!'
    return render_template('update.html', msg1=msg,teams_id = teams_id,poses=poses,heights=np.arange(170,231),years=np.arange(1995,2019),ages=np.arange(18,40))



@app.route('/search_coach')
def search_coach():
  cursor = g.conn.execute("SELECT team_name FROM team")
  team_names = []
  for result in cursor:
    team_names.append(result['team_name'])  # can also be accessed using result[0]
  cursor.close()# import to make sure no SQL injection
  return render_template("search_coach.html", team_names=team_names)

@app.route('/search_coach_result',methods=['GET'])
def search_coach_result():
  cursor = g.conn.execute("SELECT team_name FROM team")
  team_names = []
  for result in cursor:
    team_names.append(result['team_name'])  # can also be accessed using result[0]
  cursor.close()  # import to make sure no SQL injection

  query=request.args.get('query')
  cursor=g.conn.execute("SELECT coach_id,first_name,last_name,age,start_year from coach JOIN team on team.team_id = coach.team_id where team_name = %s", query)
  coach_info = []

  for info in cursor:
    name = info['first_name'] + ' ' + info['last_name']
    coach_info.append([info['coach_id'], name , info['age'], query,info['start_year']])
  cursor.close()
  return render_template('search_coach.html', data=coach_info,team_names=team_names,Team_name=query)


@app.route('/sort_position')
def position():
  cursor = g.conn.execute("SELECT DISTINCT(position) FROM player")
  position_names = []
  for result in cursor:
    position_names.append(result['position'])
  cursor.close()
  return render_template('position.html',position_names= position_names)


@app.route('/search_player_position')
def search_position():
  cursor = g.conn.execute("SELECT DISTINCT(position) FROM player")
  position_names = []
  for result in cursor:
    position_names.append(result['position'])
  cursor.close()

  query = request.args.get('query')
  cursor = g.conn.execute("SELECT player_id,first_name,last_name,height,team_id,since FROM player where position = %s",query)
  players_info = []
  for result in cursor:
    players_info.append([result['player_id'],result['first_name']+' '+result['last_name'],result['height'],result['team_id'],result['since']])
  cursor.close()

  return render_template('position.html',position_names=position_names, data = players_info,position = query)


@app.route('/player_game_performance')
def player_search():

  cursor=g.conn.execute("SELECT first_name,last_name FROM player where player_id IN (SELECT player_id from record)")
  player_names=[]
  for result in cursor:
    player_names.append(result['first_name']+' '+result['last_name'])
  cursor.close()
  return render_template('player_game_performance.html',player_names=player_names)



@app.route('/game_search')
def game_search():
  cursor=g.conn.execute("SELECT first_name,last_name FROM player where player_id IN (SELECT player_id from record)")
  player_names = []
  for result in cursor:
    player_names.append(result['first_name'] + ' ' + result['last_name'])
  cursor.close()

  query = request.args.get('player_name')
  query = str(query).split(" ")
  name = str(query[0]) + str(' ') + str(query[1])
  global m
  m = name

  cursor=g.conn.execute("SELECT * FROM record JOIN player ON record.player_id = player.player_id  WHERE player.first_name=%s and player.last_name=%s",(query[0],query[1]))

  game_ids=[]
  for result in cursor:
    game_ids.append(result["game_id"])
  cursor.close()
  global games_id
  games_id= game_ids

  return render_template('player_game_performance.html',game_ids=game_ids, player_names=player_names,player_name = name)



@app.route('/performance',methods=['GET','POST'])
def record_search():
  cursor=g.conn.execute("SELECT first_name,last_name FROM player where player_id IN (SELECT player_id from record)")
  player_names = []
  for result in cursor:
    player_names.append(result['first_name'] + ' ' + result['last_name'])
  cursor.close()

  game_id = request.args.get('game_id')
  query = str(m).split(" ")

  cursor=g.conn.execute("SELECT game_id,goal,three_pa,ast,blk FROM record JOIN player ON record.player_id = player.player_id WHERE player.first_name=%s and player.last_name=%s and record.game_id=%s",(query[0],query[1],game_id))
  info=[]
  name = query[0] + ' ' + query[1]

  for result in cursor:

    info.append([name,result['game_id'],result["goal"],result["three_pa"],result["ast"],result["blk"]])
  cursor.close()
  return render_template('player_game_performance.html',data=info,game_id=game_id,player_name = name,player_names=player_names,game_ids=games_id)



@app.route('/playoff')
def is_playoff():
  cursor = g.conn.execute("SELECT distinct(in_playoff) from team")
  bl = []
  for is_or in cursor:
    bl.append(is_or[0])
  cursor.close()
  return render_template('playoff.html',is_or_not = bl )

@app.route('/playoff_result_is')
def in_or_not():
  cursor = g.conn.execute("SELECT distinct(in_playoff) from team")
  bl = []
  for is_or in cursor:
    bl.append(is_or[0])
  cursor.close()

  query = request.args.get('in')
  global judge
  judge = query
  cursor = g.conn.execute("SELECT team_id from team where in_playoff = %s", query)
  teams_id = []
  for team in cursor:
    teams_id.append(str(team)[3:6])
  cursor.close()
  return render_template('playoff.html', teams_id= teams_id,is_or_not = bl,judge = judge)



@app.route('/playoff_result_team')
def playoff_result():
  cursor = g.conn.execute("SELECT distinct(in_playoff) from team")
  bl = []
  for is_or in cursor:
    bl.append(is_or[0])
  cursor.close()

  query = request.args.get('team_id')
  cursor = g.conn.execute("SELECT team_id from team where in_playoff = (SELECT in_playoff from team where team_id = %s)", query)
  teams_id = []
  for team in cursor:
    teams_id.append(str(team)[3:6])
  cursor.close()

  cursor=g.conn.execute("SELECT team_id,team_name,homecourt FROM team WHERE team_id=%s",query)
  team_info = []
  for info in cursor:
    team_info.append([info['team_id'],info['team_name'],info['homecourt']])
  cursor.close()

  cursor = g.conn.execute("SELECT t1.team1_id as team1_id, t1.team2_id as team2_id,t1.team1_score as team1_score, t1.team2_score as team2_score,t1.game_id as game_id ,game.location as location,game.date as date FROM (SELECT * from team_competition where team1_id=%s UNION SELECT * from team_competition where team2_id=%s) AS t1, game where t1.game_id = game.game_id",(query,query))
  game_info = []
  for info in cursor:
    game_info.append([info['team1_id'],info['team2_id'],info['team1_score'],info['team2_score'],info['game_id'],info['location'],info['date']])
  cursor.close()

  return render_template('playoff.html',data = team_info,teams_id = teams_id, is_or_not = bl,record=game_info,judge = judge,team_id = query)



@app.route('/preteam')
def preteam():
  cursor = g.conn.execute("SELECT player_id,team_id from player")
  player_info=[]
  for info in cursor:
    player_info.append([info['player_id'],info['team_id']])
  cursor.close()
  return render_template('preteam.html',player_info = player_info)

@app.route('/preteam_result')
def preteam_result():
  cursor = g.conn.execute("SELECT player_id,team_id from player")
  player_info = []
  for info in cursor:
    player_info.append([info['player_id'], info['team_id']])
  cursor.close()

  query = request.args.get('player_info')
  player_id = query[3:8]
  team_id = query[13:16]
  cursor = g.conn.execute("SELECT team_id FROM pre_team WHERE player_id=%s", player_id)
  teams_id=[]
  for info in cursor:
    teams_id.append(info['team_id'])

  if len(teams_id)== 0:
    preteam_id = None
  else:
    preteam_id = teams_id[0]

  cursor = g.conn.execute("SELECT first_name,last_name,height,position,age,college FROM player WHERE player_id=%s", player_id)
  information = []
  for info in cursor:
    tem = info['first_name'] + ' ' + info['last_name']
    information.append([tem, info['height'],info['position'],info['age'],info['college']])
  cursor.close()


  return render_template('preteam.html',player_id= player_id,team_id=team_id,preteam_id=preteam_id,player_info=player_info,information=information)



@app.route('/team_performance')
def search_teamone():

  cursor = g.conn.execute("SELECT team_name FROM team WHERE team.team_id IN (SELECT team1_id FROM team_competition) ")
  team_names = []
  for result in cursor:
    team_names.append(result['team_name'])
  cursor.close()
  return render_template("team_performance.html", team1_names=team_names)



@app.route('/team_performance_another')
def search_teamtwo():
  cursor = g.conn.execute("SELECT team_name FROM team WHERE team.team_id IN (SELECT team1_id FROM team_competition) ")
  team1_names = []
  for result in cursor:
    team1_names.append(result['team_name'])
  cursor.close()

  query = request.args.get("team_1")
  global team_1
  team_1=query
  cursor = g.conn.execute("SELECT team.team_name FROM team WHERE team.team_id IN (SELECT team_competition.team2_id FROM team_competition JOIN team team1 ON team_competition.team1_id=team1.team_id WHERE team1.team_name=%s)" ,query)
  team_names=[]
  for result in cursor:
    team_names.append(result['team_name'])
  cursor.close()

  return render_template("team_performance.html", team2_names=team_names,team1_names=team1_names, t1= team_1)



@app.route('/team_performance_game')
def search_team_game():
  cursor = g.conn.execute("SELECT team_name FROM team WHERE team.team_id IN (SELECT team1_id FROM team_competition) ")
  team1_names = []
  for result in cursor:
    team1_names.append(result['team_name'])
  cursor.close()

  cursor = g.conn.execute(
    "SELECT team.team_name FROM team WHERE team.team_id IN (SELECT team_competition.team2_id FROM team_competition JOIN team team1 ON team_competition.team1_id=team1.team_id WHERE team1.team_name=%s)",
    team_1)
  team_names = []
  for result in cursor:
    team_names.append(result['team_name'])
  cursor.close()

  global team_2
  query = request.args.get("team_2")
  team_2= query
  cursor = g.conn.execute("SELECT game_id FROM team_competition WHERE (team_competition.team1_id= (SELECT team1.team_id FROM team team1 WHERE team1.team_name=%s) AND team_competition.team2_id"
                          "= (SELECT team2.team_id FROM team team2 WHERE team2.team_name=%s)) ",team_1,query)

  game_ids = [ ]
  for result in cursor:
    game_ids.append(result['game_id'])
  cursor.close()

  return render_template('team_performance.html', result=game_ids, team2_names=team_names,team1_names=team1_names,t1= team_1,t2=team_2)

@app.route('/result_team_performance')
def search_performance_result():
  cursor = g.conn.execute("SELECT team_name FROM team WHERE team.team_id IN (SELECT team1_id FROM team_competition) ")
  team1_names = []
  for result in cursor:
    team1_names.append(result['team_name'])
  cursor.close()

  cursor = g.conn.execute(
    "SELECT team.team_name FROM team WHERE team.team_id IN (SELECT team_competition.team2_id FROM team_competition JOIN team team1 ON team_competition.team1_id=team1.team_id WHERE team1.team_name=%s)",
    team_1)
  team_names = []
  for result in cursor:
    team_names.append(result['team_name'])
  cursor.close()

  cursor = g.conn.execute(
    "SELECT game_id FROM team_competition WHERE (team_competition.team1_id= (SELECT team1.team_id FROM team team1 WHERE team1.team_name=%s) AND team_competition.team2_id"
    "= (SELECT team2.team_id FROM team team2 WHERE team2.team_name=%s)) ", team_1, team_2)

  game_ids = []
  for result in cursor:
    game_ids.append(result['game_id'])
  cursor.close()



  query=request.args.get("query")
  cursor=g.conn.execute("SELECT team1_id,team2_id,team1_score,team2_score,game_id FROM team_competition WHERE team_competition.game_id = %s",query)

  team_performance = []
  for result in cursor:
    team_performance.append([result['team1_id'],result['team2_id'],result['team1_score'],result['team2_score'],result['game_id']])
  cursor.close()

  return render_template('team_performance.html', data=team_performance,result=game_ids, team2_names=team_names,team1_names=team1_names,t1= team_1,t2=team_2,game_id=query)


# @app.route('/login')
# def login():
#     os.abort(401)


if __name__ == "__main__":


  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)



  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """

    HOST, PORT = host, port
    print ("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()

