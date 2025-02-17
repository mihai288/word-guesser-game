from flask import Flask, render_template, redirect, url_for, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from rapidfuzz import fuzz  

app = Flask(__name__)
app.config['SECRET_KEY'] = 'cheie-secreta-123'  
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///game.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    score = db.Column(db.Integer, default=600)
    level = db.Column(db.Integer, default=1)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    with app.app_context():
        #db.drop_all()
        db.create_all()

levels = {
  1: { "clue": "Marci de masini", "answers": ["Dacia", "BMW", "Audi", "Mercedes", "Toyota", "Ford"] },
  2: { "clue": "Mancare italiana", "answers": ["Pizza", "Paste", "Lasagna", "Risotto", "Tiramisu"] },
  3: { "clue": "Supereroi", "answers": ["Batman", "Superman", "Flash", "Hulk", "Ironman"] },
  4: { "clue": "Planete din sistemul solar", "answers": ["Mercur", "Venus", "Terra", "Marte", "Jupiter", "Saturn", "Uranus", "Neptun"] },
  5: { "clue": "Sporturi de echipa", "answers": ["Fotbal", "Baschet", "Handbal", "Volei", "Hochei"] },
  6: { "clue": "Mancare romaneasca", "answers": ["Sarmale", "Mici", "Ciorba de burta", "Mamaliga", "Papanasi"] },
  7: { "clue": "Orase din Romania", "answers": ["Bucuresti", "Cluj", "Timisoara", "Iasi", "Constanta"] },
  8: { "clue": "Rauri din Romania", "answers": ["Jiu", "Mures", "Olt", "Siret", "Prut"] },
  9: { "clue": "Muntii din Romania", "answers": ["Carpati", "Bucegi", "Fagaras", "Retezat", "Piatra Craiului"] },
  10: { "clue": "State din SUA", "answers": ["California", "Florida", "Ohio", "Texas", "Nevada"] },
  11: { "clue": "Judete din Romania", "answers": ["Cluj", "Timis", "Brasov", "Constanta", "Dolj"] },
  12: { "clue": "Festivaluri din Romania", "answers": ["Untold", "Neversea", "Electric Castle", "Beach Please", "Hustle"] },
  13: { "clue": "Echipe de fotbal din Romania", "answers": ["Steaua", "Dinamo", "CFR", "Universitatea Craiova", "Rapid"] },
  14: { "clue": "Zilele saptamanii", "answers": ["Luni", "Marti", "Miercuri", "Joi", "Vineri", "Sambata", "Duminica"] },
  15: { "clue": "Lunile anului", "answers": ["Ianuarie", "Februarie", "Martie", "Aprilie", "Mai", "Iunie", "Iulie", "August", "Septembrie", "Octombrie", "Noiembrie", "Decembrie"] },
  16: { "clue": "Culori", "answers": ["Rosu", "Albastru", "Verde", "Galben", "Negru"] },
  17: { "clue": "Forme geometrice", "answers": ["Cerc", "Patrat", "Triunghi", "Dreptunghi", "Paralelipiped"] },
  18: { "clue": "Continente", "answers": ["Africa", "Asia", "Europa", "America", "Antarctica"] },
  19: { "clue": "Animale de ferma", "answers": ["Vaca", "Oaie", "Porc", "Cal", "Gaina"] },
  20: { "clue": "Bauturi", "answers": ["Apa", "Suc", "Ceai", "Cafea", "Lapte"] },
  21: { "clue": "Valute", "answers": ["Euro", "Dolar", "Ron", "Yen", "Lira"] },
  22: { "clue": "Instrumente muzicale", "answers": ["Chitara", "Pian", "Toba", "Vioara", "Flaut"] },
  23: { "clue": "Sporturi individuale", "answers": ["Tenis", "Golf", "Box", "Atletism", "Inot"] },
  24: { "clue": "Animale marine", "answers": ["Balena", "Rechin", "Delfin", "Caracatita", "Meduza"] },
  25: { "clue": "Vehicule", "answers": ["Masina", "Autobuz", "Tren", "Avion", "Bicicleta"] },
  26: { "clue": "Insecte", "answers": ["Albina", "Furnica", "Fluture", "Gandac", "Lacusta"] },
  27: { "clue": "Jocuri video", "answers": ["GTA", "Minecraft", "Fortnite", "Roblox", "GuessIt"] },
  28: { "clue": "Flori", "answers": ["Trandafir", "Lalea", "Orhidee", "Crin", "Garoafa"] },
  29: { "clue": "Oceane", "answers": ["Atlantic", "Pacific", "Indian", "Arctic"] },
  30: { "clue": "Instrumente de scris", "answers": ["Creion", "Pix", "Marker", "Stilou", "Creta"] },
  31: { "clue": "Insule", "answers": ["Bali", "Hawaii", "Sicilia", "Corsica", "Creta"] },
  32: { "clue": "Religii", "answers": ["crestinism", "islam", "budism", "iudaism", "hinduism"] },
  33: { "clue": "Profesii", "answers": ["Medic", "Avocat", "Profesor", "Politist", "Inginer", "Contabil", "Programator"] },
  34: { "clue": "Jocuri de societate", "answers": ["Monopoly", "Activity", "Sequence", "Alias"] },
  35: { "clue": "Criptomonede", "answers": ["Bitcoin", "Ethereum", "Solana", "Dogecoin", "Polkadot"] },
  36: { "clue": "Fluvii din lume", "answers": ["Nil", "Amazon", "Volga", "Dunare"] },
  37: { "clue": "Munti din lume", "answers": ["Everest", "Alpi", "Carpati", "Ural", "Fuji"] },
  38: { "clue": "Lacuri din Romania", "answers": ["Vidraru", "Rosu", "Bicaz", "Balea", "Sfanta Ana"] },
  39: { "clue": "Zodiac", "answers": ["Berbec", "Taur", "Gemeni", "Rac", "Leu", "Fecioara", "Balanta", "Scorpion", "Sagetator", "Capricorn", "Varsator", "Pesti"] },
  40: { "clue": "Retele de socializare", "answers": ["Facebook", "Instagram", "X", "TikTok", "WhatsApp"] },
  41: { "clue": "Arte", "answers": ["Pictura", "Sculptura", "Teatru", "Muzica", "Dans"] },
  42: { "clue": "Fructe", "answers": ["Mar", "Banana", "Portocala", "Kiwi", "Struguri"] },
  43: { "clue": "Legume", "answers": ["Rosie", "Castravete", "Morcov", "Cartof", "Ceapa"] },
  44: { "clue": "Animale de companie", "answers": ["Caine", "Pisica", "Peste", "Papagal", "Hamster"] },
  45: { "clue": "Animale salbatice", "answers": ["Urs", "Lup", "Vulpe", "Cerb", "Caprioara"] },
  46: { "clue": "Elemente din chimie", "answers": ["Hidrogen", "Oxigen", "Carbon", "Azot", "Sulf"] },
  47: { "clue": "Metale", "answers": ["Fier", "Aur", "Argint", "Cupru", "Zinc"] },
  48: { "clue": "Limbaje de programare", "answers": ["Python", "Java", "C++", "JavaScript", "Ruby"] },
  49: { "clue": "Sisteme de operare", "answers": ["Windows", "macOS", "Linux", "Android", "iOS", "Ubuntu"] },
  50: { "clue": "Branduri de bere", "answers": ["Ursus", "Timisoreana", "Ciuc", "Silva", "Bergenbier"] },
  51: { "clue": "Condimente", "answers": ["Sare", "Piper", "Chimen", "Coriandru", "Turmeric"] },
  52: { "clue": "Piese de sah", "answers": ["Rege", "Regina", "Tura", "Nebun", "Cal", "Pion"] },
  53: { "clue": "Capitale europene", "answers": ["Paris", "Bucuresti", "Berlin", "Madrid", "Roma"] },
  54: { "clue": "Capitale asiatice", "answers": ["Tokyo", "Beijing", "Seoul", "Bangkok", "Delhi"] },
  55: { "clue": "Vreme", "answers": ["Ploua", "Ninge", "Insorit", "Innorat"] },
  56: { "clue": "Obiecte de birou", "answers": ["Laptop", "Mouse", "Tastatura", "Monitor", "Imprimanta", "Computer", "Mousepad"] },
  57: { "clue": "Genuri muzicale", "answers": ["Rock", "Pop", "Jazz", "Rap", "Hip Hop", "Manele", "Drill"] },
  58: { "clue": "Jocuri de carti", "answers": ["Poker", "Macao", "Rummy", "Blackjack", "Uno"] },
  59: { "clue": "Cafele", "answers": ["Espresso", "Latte", "Cappuccino", "Mocha", "Americano"] },
  60: { "clue": "Numere", "answers": ["unu", "doi", "trei", "patru", "cinci"] },
  61: { "clue": "Marci de telefoane", "answers": ["Apple", "Samsung", "Huawei", "Xiaomi", "Asus", "Acer", "Allview"] },
  62: { "clue": "Ceaiuri", "answers": ["Verde", "Negru", "Iasomie", "Matcha", "Menta", "Musetel"] },
  63: { "clue": "Sporturi de iarna", "answers": ["Schi", "Snowboard", "Patinaj"] },
  64: { "clue": "Organe", "answers": ["Inima", "Creier", "Plamani", "Ficat", "Rinichi"] },
  65: { "clue": "Animale din jungla", "answers": ["Tigru", "Leu", "Elefant", "Girafa", "Zebra"] },
  66: { "clue": "Jocuri de masa", "answers": ["Dama", "Go", "Backgammon", "Domino", "Carrom"] },
  67: { "clue": "Deserturi", "answers": ["Inghetata", "Tort", "Clatite", "Biscuit", "Prajitura"] },
  68: { "clue": "Peisaje", "answers": ["Padure", "Munte", "Desert", "Lac", "Cascada"] },
  69: { "clue": "Inghetata", "answers": ["Vanilie", "Ciocolata", "Capsuni", "Menta", "Fistic", "Pepene"] },
  70: { "clue": "Emotii", "answers": ["Bucurie", "Furie", "Tristete", "Teama", "Surprindere"] },
  71: { "clue": "Electrocasnice", "answers": ["Frigider", "Cuptor", "Aspirator", "Mixer", "Microunde", "Blender"] },
  72: { "clue": "Tipuri de Carti", "answers": ["Roman", "Poezie", "Eseu", "Biografie", "Drama"] },
  73: { "clue": "Fructe de padure", "answers": ["Zmeura", "Afine", "Mure", "Cirese", "Coacaze"] },
  74: { "clue": "Pasari", "answers": ["Papagal", "Cuc", "Porumbel", "Vultur", "Corb"] },
  75: { "clue": "Ciocolata", "answers": ["Neagra", "Cu lapte", "Alba", "Aerata", "Amara"] },
  76: { "clue": "Desene animate", "answers": ["Mickey Mouse", "Looney Toons", "Tom si Jerry", "Tinerii Titani", "SpongeBob"] },
  77: { "clue": "Ceasuri", "answers": ["Rolex", "Omega", "Casio", "Seiko", "Timex"] },
  78: { "clue": "Tipuri de computere", "answers": ["Laptop", "Desktop", "Tableta", "Server"] },
  79: { "clue": "Arome de parfum", "answers": ["Floral", "Ambrat", "Citrus", "Lemnos", "Oriental"] },
  80: { "clue": "Incaltaminte", "answers": ["Pantofi", "Adidasi", "Cizme", "Sandale", "Papuci"] },
  81: { "clue": "Animale din desert", "answers": ["Camila", "Sarpe", "Scorpion", "Vultur", "Dromader"] },
  82: { "clue": "Sporturi acvatice", "answers": ["Inot", "Surf", "Sarituri", "Scufundare", "Kayak"] },
  83: { "clue": "Biciclete", "answers": ["Mountain Bike", "Cursiera", "Full Suspension", "BMX", "Electrica"] },
  84: { "clue": "Ciuperci", "answers": ["Champignon", "Portobello", "Shiitake", "Oyster", "Enoki"] },
  85: { "clue": "Categorii de trenuri", "answers": ["Intercity", "Regional", "Express", "Suburban"] },
  86: { "clue": "Aeroporturi", "answers": ["Henri Coanda", "Baneasa", "Schiphol", "George Enescu"] },
  87: { "clue": "Fastfood", "answers": ["Burger", "Pizza", "Hotdog", "Taco", "Burrito"] },
  88: { "clue": "Sporturi de contact", "answers": ["Box", "Judo", "Karate", "Kickbox", "Wrestling"] },
  89: { "clue": "Obiecte de baie", "answers": ["Cada", "Sapun", "Perie", "Prosop", "Chiuveta"] },
  90: { "clue": "Plante medicinale", "answers": ["Salie", "Menta", "Busuioc", "Rozmarin", "Cimbru"] },
  91: { "clue": "Locuri in care poti merge in vacanta", "answers": ["Plaja", "Munte", "Oras", "Sat", "Delta"] },
  92: { "clue": "Biscuiti", "answers": ["Petit Beurre", "Oreo", "Ginger", "Amaretti", "Leibniz"] },
  93: { "clue": "Jocuri online", "answers": ["Fortnite", "Minecraft", "Roblox", "Among Us", "Valorant", "Counter Strike", "FiveM"] },
  94: { "clue": "Snackuri", "answers": ["Chips", "Covrigei", "Popcorn", "Alune", "Baton"] },
  95: { "clue": "Unitati de masura", "answers": ["Metru", "Gram", "Litru", "Secunda", "Kelvin", "Celsius"] },
  96: { "clue": "Sarbatori", "answers": ["Craciun", "Paste", "Halloween", "Valentine's Day", "Revelion"] },
  97: { "clue": "Mesele zilei", "answers": ["Mic dejun", "Pranz", "Cina", "Gustare"] },
  98: { "clue": "Marci de haine", "answers": ["Nike", "Adidas", "Puma", "Reebok", "UnderArmour"] },
  99: { "clue": "Marci de pantofi", "answers": ["Clarks", "Timberland", "Converse", "Skechers", "Vans"] },
  100: { "clue": "Sosuri", "answers": ["Ketchup", "Mustar", "Maioneza", "Sriracha", "Tabasco"] }
}

@app.route('/demo')
def demo():

    level_data = levels[1]
    num_answers = len(level_data["answers"])

    if 'revealed' not in session:
        session['revealed'] = {}
    if str(1) not in session['revealed']:

        session['revealed'][str(1)] = [None] * num_answers
    revealed = session['revealed'][str(1)]

    return render_template('demo.html',
                           clue=level_data["clue"],
                           num_answers=num_answers,
                           revealed=revealed)




@app.route('/')
def index():
    return render_template('menu.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('menu'))
        else:
            return render_template('login.html', error="Username sau parola incorectă.")
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if User.query.filter_by(username=username).first():
            return render_template('register.html', error="Username deja existent.")
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('menu'))
    return render_template('register.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/leaderboard')
@login_required
def leaderboard():
    users = User.query.order_by(User.score.desc()).all()
    return render_template('leaderboard.html', users=users)



@app.route('/game')
@login_required
def game():
    user_level = current_user.level
    if user_level in levels:
        level_data = levels[user_level]
        num_answers = len(level_data["answers"])
        if 'revealed' not in session:
            session['revealed'] = {}
        if str(user_level) not in session['revealed']:
            session['revealed'][str(user_level)] = [None] * num_answers
        revealed = session['revealed'][str(user_level)]
    else:
        level_data = {"clue": "Felicitări! Ai terminat jocul.", "answers": []}
        num_answers = 0
        revealed = []
    return render_template('game.html',
                           clue=level_data["clue"],
                           level=user_level,
                           score=current_user.score,
                           num_answers=num_answers,
                           revealed=revealed)


@app.route('/check_answer', methods=['POST'])
@login_required
def check_answer():
    user_level = current_user.level
    if user_level not in levels:
        return jsonify({"status": "error", "message": "Nivel invalid."}), 400

    level_data = levels[user_level]
    user_answer = request.json.get('answer', '').strip()

    SIMILARITY_THRESHOLD = 80

    if 'revealed' not in session:
        session['revealed'] = {}
    if str(user_level) not in session['revealed']:
        session['revealed'][str(user_level)] = [None] * len(level_data["answers"])

    revealed_list = session['revealed'][str(user_level)]

    for i, ans in enumerate(level_data["answers"]):
        if revealed_list[i] is not None:
            if fuzz.ratio(user_answer.lower(), ans.lower()) >= SIMILARITY_THRESHOLD:
                return jsonify({"status": "info", "message": "Ai ghicit deja acest cuvânt."})

    found = False
    index_found = -1
    for i, ans in enumerate(level_data["answers"]):
        if revealed_list[i] is None:
            similarity = fuzz.ratio(user_answer.lower(), ans.lower())
            if similarity >= SIMILARITY_THRESHOLD:
                revealed_list[i] = ans
                session.modified = True
                found = True
                index_found = i
                break

    if found:
        if all(item is not None for item in revealed_list):
            session['revealed'].pop(str(user_level))
            return jsonify({
                "status": "correct",
                "message": "Nivel completat. +100 💎",
                "complete": True,
                "score": current_user.score,
                "level": current_user.level,
                "index": index_found,
                "word": level_data["answers"][index_found]
            })
        else:
            current_user.score += 10
            db.session.commit()
            return jsonify({
                "status": "correct",
                "complete": False,
                "index": index_found,
                "word": level_data["answers"][index_found],
                "score": current_user.score
            })
    else:
        return jsonify({"status": "incorrect", "message": "Răspuns greșit, încearcă din nou."})


@app.route('/next_level', methods=['POST'])
@login_required
def next_level():
    try:
        current_user.level += 1  
        current_user.score += 250
        db.session.commit()
        return jsonify({"status": "success", "level": current_user.level})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_answer', methods=['POST'])
@login_required
def get_answer():
    user_level = current_user.level
    if user_level not in levels:
        return jsonify({"status": "error", "message": "Nivel invalid."}), 400

    if current_user.score < 150:
        return jsonify({"status": "error", "message": "Sold insuficient pentru a obține un răspuns."})

    level_data = levels[user_level]

    if 'revealed' not in session:
        session['revealed'] = {}
    if str(user_level) not in session['revealed']:
        session['revealed'][str(user_level)] = [None] * len(level_data["answers"])

    revealed_list = session['revealed'][str(user_level)]

    index_found = -1
    for i, ans in enumerate(level_data["answers"]):
        if revealed_list[i] is None:
            index_found = i
            revealed_list[i] = ans  
            session.modified = True
            break

    if index_found == -1:
        return jsonify({"status": "error", "message": "Toate răspunsurile sunt deja dezvăluite."})

    current_user.score -= 150
    db.session.commit()

    all_revealed = all(item is not None for item in revealed_list)

    return jsonify({
        "status": "success",
        "index": index_found,
        "word": level_data["answers"][index_found],
        "score": current_user.score,
        "complete": all_revealed
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
