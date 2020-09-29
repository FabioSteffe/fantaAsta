
from flask import ( Flask, render_template, request, 
redirect, url_for, jsonify, abort )
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func
from flask_migrate import Migrate
import pandas as pd
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://fsteffenino:@localhost:5432/fanta'
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Player(db.Model):
    __tablename__ = 'player'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    fullname = db.Column(db.String(), nullable=False)
    position = db.Column(db.String(), nullable=False)
    value = db.Column(db.Integer, nullable=True)
    team = db.Column(db.String(), nullable=False)
    nation = db.Column(db.String(), nullable=False)
    pic = db.Column(db.String(), nullable=False)
    deleted = db.Column(db.Boolean(), nullable=False, default=False)
    archived = db.Column(db.Boolean(), nullable=False, default=False)
    assigned = db.Column(db.Boolean(), nullable=False, default=False)
    fantateam = db.Column(db.Integer, db.ForeignKey('team.id'),nullable=True)

class FantaTeam(db.Model):
    __tablename__ = 'team'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    players = db.relationship('Player', backref='list', lazy=True)

db.create_all()

@app.route('/reload', methods=['POST'])
def create():
    desc = request.get_json()['description']
    if desc == "admin":

        error = False
        try:
            db.session.query(Player).delete()
            df = pd.read_csv('players.csv', header=None)
            for row in df.itertuples():
                player = Player(
                    name = row._2,
                    fullname = row._3,
                    position = row._4,
                    value = row._6,
                    team = row._10,
                    nation = row._14,
                    pic = row._16
                )
                db.session.add(player)

            db.session.query(FantaTeam).delete()
            dft = pd.read_csv('fantateams.csv', header=None)
            for row in dft.itertuples():
                team = FantaTeam(name=row._1)
                db.session.add(team)

            db.session.commit()
        except:
            db.session.rollback()
            error = True
            print(sys.exc_info())
        finally:
            db.session.close()
        if error:
            abort(400)
        else:
            return jsonify({
                'description' : 'ok'
            })
    
    else:
        return jsonify({
                'description' : 'nada de nada'
            })

@app.route('/call', methods=['POST'])
def call():
    desc = request.get_json()['description']
    print(desc)
    result = db.session.query(Player).filter( Player.name.ilike('%'+desc+'%') ).first()
    print(result)
    if result:
        return jsonify({
            'id' : result.id,
            'name' : result.name,
            'fullname' : result.fullname,
            'position' : result.position,
            'value' : result.value,
            'team' : result.team,
            'nation' : result.nation,
            'pic' : result.pic,
            'deleted' : result.deleted,
            'archived' : result.archived,
            'assigned' : result.assigned,
            'fantateam' : result.fantateam
        })
    else:
        return jsonify({
            'description' : 'nada de nada'
        })

@app.route('/random', methods=['POST'])
def random():
    desc = request.get_json()['description']
    print(desc)
    result = db.session.query(Player).filter( Player.assigned == False,
                                            Player.archived == False,
                                            Player.deleted == False).order_by(func.random()).first()
    print(result)
    if result:
        return jsonify({
            'id' : result.id,
            'name' : result.name,
            'fullname' : result.fullname,
            'position' : result.position,
            'value' : result.value,
            'team' : result.team,
            'nation' : result.nation,
            'pic' : result.pic,
            'deleted' : result.deleted,
            'archived' : result.archived,
            'assigned' : result.assigned,
            'fantateam' : result.fantateam
        })
    else:
        return jsonify({
            'description' : 'nada de nada'
        })

@app.route('/action', methods=['POST'])
def action():
    fullname = request.get_json()['fullname']
    team = request.get_json()['team']
    action = request.get_json()['type']
    print(fullname)
    print(team)
    print(action)
    error = False
    player = db.session.query(Player).filter( Player.fullname == fullname,
                                              Player.team == team).first()
    print(player)
    try:
        if action == 'archive':
            player.archived = True
            db.session.commit()
        elif action == 'sell':
            player.assigned = True
            db.session.commit()
        elif action == 'delete':
            player.deleted = True
            db.session.commit()
        else:
            return jsonify({
                'description' : 'nada de nada'
            })
    except:
        db.session.rollback()
        error = True
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        abort(400)
    else:
        return jsonify({
            'description' : 'ok'
        })

@app.route('/')
def index():
    return render_template('index.html')