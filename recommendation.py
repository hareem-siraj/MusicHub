from neo4j import GraphDatabase

# Connect to the Neo4j database
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "12345678"))

# Function to execute queries
def execute_query(query, params=None):
    with driver.session() as session:
        result = session.run(query, params)
        return result.data()

# Define and execute queries to compute and store graph algorithms

#Useful for identifying artists who act as bridges or intermediaries between different clusters or communities within the network.
#These artists might have a significant impact on the flow of information or collaborations between different groups.
query1 = """// Betweenness Centrality 
  CALL gds.alpha.betweenness.write({
  nodeProjection: 'Artist',
  relationshipProjection: {
    CREATED: {
      type: 'CREATED',
      orientation: 'UNDIRECTED'
    }
  },
  writeProperty: 'betweennessCentrality'
});"""

execute_query(query1)

#Useful for identifying artists who are close to other artists in terms of collaboration opportunities. 
#Artists with high closeness centrality might be more reachable or accessible for potential collaborations.
query2 = """// Closeness Centrality
    CALL gds.alpha.closeness.write({
    nodeProjection: 'Artist',
    relationshipProjection: {
        CREATED: {
        type: 'CREATED',
        orientation: 'UNDIRECTED'
        }
    },
    writeProperty: 'closenessCentrality'
    });"""

execute_query(query2)

#Useful for understanding the musical preferences of each artist. This information can be used to recommend similar artists to users based 
#on their favorite genres.
query3 = """// Genre Preferences 
MATCH (a:Artist)-[:CREATED]->(:Track)-[:BELONGS_TO]->(g:Genre)
WITH a, g, COUNT(*) AS genreCount
ORDER BY a.Artist_ID, genreCount DESC
WITH a, COLLECT({ genre: g.Name, count: genreCount }) AS genreCounts
SET a.genrePreferences = genreCounts;"""

execute_query(query3)

#Useful for recommending popular artists to users who might be interested in mainstream or trending music.
query4 = """// Popularity
// For example, if there's a property 'Popularity' on tracks representing the number of streams:
MATCH (a:Artist)-[:CREATED]->(t:Track)
WITH a, SUM(t.Popularity) AS totalPopularity
SET a.popularity = totalPopularity;"""

execute_query(query4)


#Useful for finding artists with similar genre preferences. This metric can be used to recommend artists who have comparable musical tastes.
query5 = """// Similarity
// For example, Jaccard similarity based on genre preferences
MATCH (a1:Artist), (a2:Artist)
WHERE id(a1) < id(a2)
WITH a1, a2, gds.alpha.similarity.jaccard(a1.genrePreferences, a2.genrePreferences) AS similarity
MERGE (a1)-[s:SIMILAR_TO]->(a2)
SET s.jaccardSimilarity = similarity;"""

execute_query(query5)


#Useful for recommending artists based on recent activity or releases. 
#Users interested in discovering new music might appreciate recommendations from artists with recent album releases.
query6 = """// Album Release Dates
MATCH (a:Artist)-[:CREATED]->(:Track)-[:INCLUDED_IN]->(album:Album)
WITH a, album, COLLECT(album.Release_Date) AS releaseDates
SET a.albumReleaseDates = releaseDates;"""  

execute_query(query6)


#Useful for understanding the typical length of tracks created by each artist. 
#This information can be used to recommend artists who produce music with similar durations to what the user prefers.
query7 = """// Average Track Duration
MATCH (a:Artist)-[:CREATED]->(t:Track)
WITH a, AVG(t.Duration) AS averageTrackDuration
SET a.averageTrackDuration = averageTrackDuration;"""

execute_query(query7)

#configure link prediction pipeline
configure_query = """
CALL gds.beta.pipeline.linkPrediction.create('artist_collaboration_prediction_model');

CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'gds.alpha.betweenness', {})
YIELD nodePropertySteps;

CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'gds.alpha.closeness', {})
YIELD nodePropertySteps;

CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query3', {})
YIELD nodePropertySteps;

CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query4', {})
YIELD nodePropertySteps;

CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query5', {})
YIELD nodePropertySteps;

CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query6', {})
YIELD nodePropertySteps;

CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query7', {})
YIELD nodePropertySteps;

"""


# Train a link prediction model using provided metrics
train_query = """
CALL gds.alpha.ml.linkPrediction.train(
  graphName: 'your_graph_name',
  modelName: 'artist_collaboration_prediction_model',
  relationshipTypes: ['SIMILAR_TO', 'COLLABORATED_WITH'],
  holdoutFraction: 0.2 // Fraction of relationships to use for testing
)
YIELD modelInfo;
"""

execute_query(train_query)

# Make recommendations of artists for collaboration
recommendation_query = """
MATCH (a1:Artist)
WHERE NOT EXISTS((a1)-[:COLLABORATED_WITH]-(:Artist)) // Exclude artists who already have collaborations
MATCH (a2:Artist)
WHERE a1 <> a2
WITH a1, a2
CALL gds.alpha.ml.linkPrediction.predict(
  'artist_collaboration_prediction_model',
  {node1: id(a1), node2: id(a2)}
)
YIELD score
WITH a1, a2, score
ORDER BY score DESC
LIMIT 10 // Limit the number of recommendations
RETURN a1.Artist_ID AS ArtistID, a2.Artist_ID AS RecommendedArtistID, score;
"""

recommendations = execute_query(recommendation_query)

# Print recommendations
print("Top 10 Artist Collaboration Recommendations:")
print("===========================================")
for recommendation in recommendations:
    print(f"ArtistID: {recommendation['ArtistID']}, Recommended ArtistID: {recommendation['RecommendedArtistID']}, Score: {recommendation['score']}")


