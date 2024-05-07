from flask import Flask, render_template, request, redirect, url_for, session
from neo4j import GraphDatabase

app = Flask(__name__, template_folder='templates')

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Neo4j connection details
uri = "bolt://localhost:7687"
user = "neo4j"
password = "12345678"

# Function to create Neo4j session
def get_neo4j_session():
    return GraphDatabase.driver(uri, auth=(user, password))

################## ------------------------------------querying the pipeline------------------------------------ ##################

# Function to execute queries
def execute_query(query, params=None):
    with get_neo4j_session().session() as session:
        result = session.run(query, params)
        return result.data()

# Define and execute queries to compute and store graph algorithms
def execute_recommendation_pipeline():
    # Applying a trained model for prediction
    predict_query = """
    CALL gds.beta.pipeline.linkPrediction.predict.stream('myGraph4', {
    modelName: 'myModel',
    topN: 10000
    })
    YIELD node1, node2, probability
    WITH gds.util.asNode(node1).Artist_Name AS ArtistID, gds.util.asNode(node2).Artist_Name AS RecommendedArtistID, probability
    WITH ArtistID, collect({RecommendedArtistID: RecommendedArtistID, probability: probability})[..5] AS recommendations
    RETURN ArtistID, recommendations
    """
    answer = execute_query(predict_query)
    return answer

def get_recommendations(username):
    recommendations = execute_recommendation_pipeline()
    print(recommendations)
    user_recommendations = []

    for row in recommendations:
        if row["ArtistID"] == username:
            user_recommendations.extend(entry["RecommendedArtistID"] for entry in row["recommendations"])

    return user_recommendations


################## ------------------------------------additional functions------------------------------------ ##################


def get_top_tracks_and_albums(username):
    query = """
    MATCH (u:Artist {Artist_Name: $username})-[:CREATED]->(t:Track)<-[:INCLUDES]-(a:Album)
    WITH t, a
    ORDER BY t.popularity DESC, t.release_date DESC
    RETURN t.Track_Name AS TrackName
    LIMIT 5
    """
    result = execute_query(query, {"username": username})
    top_tracks = [record["TrackName"] for record in result]
    
    return top_tracks

def get_genre(username):
    query = """
    MATCH (u:Artist {Artist_Name: $username})-[:CREATED]->(t:Track)-[:BELONGS_TO]->(g:Genre)
    RETURN DISTINCT(g.Name) AS GenreName
    """
    result = execute_query(query, {"username": username})
    genre = [record["GenreName"] for record in result]
    
    return genre


################## ------------------------------------Flask Application------------------------------------ ##################

userrn = None

# Route to render the login page
@app.route('/')
def login():
    return render_template('index.html')

# Route to handle form submission
@app.route('/submit', methods=['POST'])
def submit():
    global userrn
    username = request.form['username']

    # Query the Neo4j database to check if the username exists
    with get_neo4j_session().session() as session:
        result = session.run("MATCH (u:Artist {Artist_Name: $username}) RETURN u", username=username)
        user_exists = result.single() is not None

    

        if user_exists:
            # Redirect to the dashboard page if the username exists
            #session['username'] = username
            userrn = username
            return redirect(url_for('dashboard'))
        else:
            # Display error message if the username doesn't exist
            return render_template('index.html', error_message="Invalid Username. Please try again.")

# Route to render the dashboard page
@app.route('/dashboard')
def dashboard():
    global userrn
    # username = session.get('username')
    #username = "Naseebo Lal"
    print("Username:", userrn) 
    recommendations = get_recommendations(userrn)
    print(recommendations)
    # Pass recommendations to the template
    return render_template('dashboard.html', Username=userrn, recommendations=recommendations)

# Route to handle logout
@app.route('/logout')
def logout():
    # Clear the session data
    session.clear()
    # Redirect to the login page
    return redirect(url_for('login'))

# Route to profile page
@app.route('/profile/<recommended_artist>')
def profile(recommended_artist):
    global userrn
    # username = session.get('username')
    #username = "Naseebo Lal"
    tracks = get_top_tracks_and_albums(recommended_artist)
    genre = get_genre(recommended_artist)
    print("genre:", genre)
    return render_template('profile.html', Username=userrn, recommended_artist=recommended_artist, tracks=tracks, genre=genre)

# Route to handle back to dashboard
@app.route('/back-to-dashboard')
def back_to_dashboard():
    # Redirect to the dashboard page
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)