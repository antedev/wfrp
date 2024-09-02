from flask import Flask, render_template
from utils.data_loader import npcs_data, talents_data, traits_data
from utils.matchers import find_talent_description, find_trait_description

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Adventures page route
@app.route('/adventures')
def adventures():
    return render_template('adventures.html')

@app.route('/npcs')
def npc_list():
    return render_template('npc_list.html', npcs=npcs_data)

@app.route('/npc/<npc_name>')
def npc_viewer(npc_name):
    npc_data = npcs_data.get(npc_name.upper())
    
    if not npc_data:
        return "NPC not found", 404

    # Fetch talent and trait descriptions
    npc_talents = [{'name': t, 'description': find_talent_description(t, talents_data)} for t in npc_data.get('talents', [])]
    npc_traits = [{'name': t, 'description': find_trait_description(t, traits_data)} for t in npc_data.get('traits', [])]

    return render_template('npc_viewer.html', npc=npc_data, npc_talents=npc_talents, npc_traits=npc_traits)

if __name__ == '__main__':
    app.run(debug=True)
