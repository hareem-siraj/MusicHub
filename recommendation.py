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
    # Genre Preferences
    # query3 = """
    # MATCH (artist:Artist)-[:CREATED]->(:Track)-[:BELONGS_TO]->(genre:Genre)
    # WITH artist, genre, COUNT(*) AS genreCount
    # ORDER BY artist.Artist_ID, genreCount DESC
    # WITH artist, COLLECT(genre.Name) AS genrePrefs
    # SET artist.genrePreferences = genrePrefs;"""
    # execute_query(query3)

    # Popularity
    query4 = """
    MATCH (a:Artist)-[:CREATED]->(t:Track)
    WITH a, AVG(t.Popularity) AS AveragePopularity
    SET a.AVGpopularity = AveragePopularity;"""
    execute_query(query4)

    # # Album Release Dates
    # query6 = """
    # MATCH (a:Artist)-[:CREATED]->(:Track)<-[:INCLUDES]-(album:Album)
    # WITH a, album, MAX(album.Release_Date) AS latestReleaseDate
    # SET a.LatestRelease = latestReleaseDate;"""
    # execute_query(query6)

    # Average Track Duration
    query7 = """
    MATCH (a:Artist)-[:CREATED]->(t:Track)
    WITH a, AVG(t.Duration) AS averageTrackDuration
    SET a.averageTrackDuration = averageTrackDuration;"""
    execute_query(query7)

    # Create graph projection
    projection_query = """
    CALL gds.graph.project(
    'MyProj3',
    ['Artist', 'Track', 'Genre','Album'],
    ['CREATED', 'BELONGS_TO', 'INCLUDES'])"""
    execute_query(projection_query)


    # Closeness Centrality
    query2 = """
    CALL gds.closeness.write('MyProj3', {
    writeProperty: 'closeness_centrality'
    })
    YIELD centralityDistribution, nodePropertiesWritten
    RETURN nodePropertiesWritten;"""
    execute_query(query2)

    # Similarity
    query5 = """
    CALL gds.nodeSimilarity.write('MyProj3', {
        writeRelationshipType: 'SIMILAR',
        writeProperty: 'score'
    })
    YIELD nodesCompared, relationshipsWritten;
    """
    execute_query(query5)

    # Configure link prediction pipeline
    create_pipeline_query = """
    CALL gds.beta.pipeline.linkPrediction.create('pp3');
    """
    execute_query(create_pipeline_query)

    # Add node properties to the pipeline
    add_node_property_query = """
    CALL gds.beta.pipeline.linkPrediction.addNodeProperty('pp3', 'fastRP', {
      mutateProperty: 'embedding',
      contextNodeLabels: ['Artist'],
      embeddingDimension: 256,
      randomSeed: 42
    })
    """
    execute_query(add_node_property_query)

    # Add link features to the pipeline
    add_link_feature_query = """
    CALL gds.beta.pipeline.linkPrediction.addFeature('pp3', 'cosine', {
      nodeProperties: ['embedding', 'closeness_centrality', 'AVGpopularity', 'averageTrackDuration']
    })
    """
    execute_query(add_link_feature_query)

    # Configure split
    split_query = """
    CALL gds.beta.pipeline.linkPrediction.configureSplit('pp3', {
      testFraction: 0.25,
      trainFraction: 0.6,
      validationFolds: 3
    })
    """
    execute_query(split_query)

    # Adding model candidates
    add_model_candidate_query = """
    CALL gds.beta.pipeline.linkPrediction.addLogisticRegression('pp3')
    """
    execute_query(add_model_candidate_query)

    # Projection for training model
    projection_query2 = """
    CALL gds.graph.project(
    'myGraph4',
    {
      Artist: {
        label: 'Artist',
        properties: 
        ['AVGpopularity',
        'averageTrackDuration',
        'closeness_centrality']
        
      }
    },
    {SIMILAR_UNDIRECTED: {
        type: 'SIMILAR',
        orientation: 'UNDIRECTED',
        properties: 'score'}
    }
    )
    YIELD graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
    RETURN graphName, nodeProjection.artist AS prop, nodes, rels
    """
    execute_query(projection_query2)

    # Train model
    train_query = """
    CALL gds.beta.pipeline.linkPrediction.train('myGraph4',
    { pipeline: 'pp3',
      modelName: 'myModel',
      metrics: ['AUCPR'],
      targetRelationshipType: 'SIMILAR_UNDIRECTED'
    })
    YIELD modelInfo, modelSelectionStats
    RETURN
    modelInfo.bestParameters AS winningModel,
    modelInfo.metrics.AUCPR.train.avg AS avgTrainScore,
    modelInfo.metrics.AUCPR.outerTrain AS outerTrainScore,
    modelInfo.metrics.AUCPR.test AS testScore,
    [cand IN modelSelectionStats.modelCandidates | cand.metrics.AUCPR.validation.avg] AS validationScores
    """
    execute_query(train_query)

    # Applying a trained model for prediction
    predict_query = """
    CALL gds.beta.pipeline.linkPrediction.predict.stream('myGraph2', {
    modelName: 'myModel',
    topN: 1000
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
    user_recommendations = {}
    for row in recommendations:
        user_recommendations[row["ArtistID"]] = [entry["RecommendedArtistID"] for entry in row["recommendations"]]

    return user_recommendations




# call gds.graph.project('myGraph2',['Genre'],{Same_As:{type:'Same_As',orientation:'undirected'}});
# # CALL gds.wcc.write('myGraph2', { writeProperty: 'componentId' })
# # YIELD nodePropertiesWritten, componentCount;


# from neo4j import GraphDatabase

# # Connect to the Neo4j database
# uri = "bolt://localhost:7687"
# driver = GraphDatabase.driver(uri, auth=("neo4j", "12345678"))

# # Function to execute queries
# def execute_query(query, params=None):
#     with driver.session() as session:
#         result = session.run(query, params)
#         return result.data()

# # Define and execute queries to compute and store graph algorithms

# #Useful for identifying artists who act as bridges or intermediaries between different clusters or communities within the network.
# #These artists might have a significant impact on the flow of information or collaborations between different groups.
# query1 = """// Betweenness Centrality 
#   CALL gds.alpha.betweenness.write({
#   nodeProjection: 'Artist',
#   relationshipProjection: {
#     CREATED: {
#       type: 'CREATED',
#       orientation: 'UNDIRECTED'
#     }
#   },
#   writeProperty: 'betweennessCentrality'
# });"""

# execute_query(query1)

# #Useful for identifying artists who are close to other artists in terms of collaboration opportunities. 
# #Artists with high closeness centrality might be more reachable or accessible for potential collaborations.
# query2 = """// Closeness Centrality
#     CALL gds.alpha.closeness.write({
#     nodeProjection: 'Artist',
#     relationshipProjection: {
#         CREATED: {
#         type: 'CREATED',
#         orientation: 'UNDIRECTED'
#         }
#     },
#     writeProperty: 'closenessCentrality'
#     });"""

# execute_query(query2)

# #Useful for understanding the musical preferences of each artist. This information can be used to recommend similar artists to users based 
# #on their favorite genres.
# query3 = """// Genre Preferences 
# MATCH (a:Artist)-[:CREATED]->(:Track)-[:BELONGS_TO]->(g:Genre)
# WITH a, g, COUNT(*) AS genreCount
# ORDER BY a.Artist_ID, genreCount DESC
# WITH a, COLLECT({ genre: g.Name, count: genreCount }) AS genreCounts
# SET a.genrePreferences = genreCounts;"""

# execute_query(query3)

# #Useful for recommending popular artists to users who might be interested in mainstream or trending music.
# query4 = """// Popularity
# // For example, if there's a property 'Popularity' on tracks representing the number of streams:
# MATCH (a:Artist)-[:CREATED]->(t:Track)
# WITH a, SUM(t.Popularity) AS totalPopularity
# SET a.popularity = totalPopularity;"""

# execute_query(query4)


# #Useful for finding artists with similar genre preferences. This metric can be used to recommend artists who have comparable musical tastes.
# query5 = """// Similarity
# // For example, Jaccard similarity based on genre preferences
# MATCH (a1:Artist), (a2:Artist)
# WHERE id(a1) < id(a2)
# WITH a1, a2, gds.alpha.similarity.jaccard(a1.genrePreferences, a2.genrePreferences) AS similarity
# MERGE (a1)-[s:SIMILAR_TO]->(a2)
# SET s.jaccardSimilarity = similarity;"""

# execute_query(query5)


# #Useful for recommending artists based on recent activity or releases. 
# #Users interested in discovering new music might appreciate recommendations from artists with recent album releases.
# query6 = """// Album Release Dates
# MATCH (a:Artist)-[:CREATED]->(:Track)-[:INCLUDED_IN]->(album:Album)
# WITH a, album, COLLECT(album.Release_Date) AS releaseDates
# SET a.albumReleaseDates = releaseDates;"""  

# execute_query(query6)


# #Useful for understanding the typical length of tracks created by each artist. 
# #This information can be used to recommend artists who produce music with similar durations to what the user prefers.
# query7 = """// Average Track Duration
# MATCH (a:Artist)-[:CREATED]->(t:Track)
# WITH a, AVG(t.Duration) AS averageTrackDuration
# SET a.averageTrackDuration = averageTrackDuration;"""

# execute_query(query7)

# #configure link prediction pipeline
# configure_query = """
# CALL gds.beta.pipeline.linkPrediction.create('artist_collaboration_prediction_model');

# CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'gds.alpha.betweenness', {})
# YIELD nodePropertySteps;

# CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'gds.alpha.closeness', {})
# YIELD nodePropertySteps;

# CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query3', {})
# YIELD nodePropertySteps;

# CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query4', {})
# YIELD nodePropertySteps;

# CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query5', {})
# YIELD nodePropertySteps;

# CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query6', {})
# YIELD nodePropertySteps;

# CALL gds.beta.pipeline.linkPrediction.addNodeProperty('artist_recommendation', 'query7', {})
# YIELD nodePropertySteps;

# """


# # Train a link prediction model using provided metrics
# train_query = """
# CALL gds.alpha.ml.linkPrediction.train(
#   graphName: 'your_graph_name',
#   modelName: 'artist_collaboration_prediction_model',
#   relationshipTypes: ['SIMILAR_TO', 'COLLABORATED_WITH'],
#   holdoutFraction: 0.2 // Fraction of relationships to use for testing
# )
# YIELD modelInfo;
# """

# execute_query(train_query)

# # Make recommendations of artists for collaboration
# recommendation_query = """
# MATCH (a1:Artist)
# WHERE NOT EXISTS((a1)-[:COLLABORATED_WITH]-(:Artist)) // Exclude artists who already have collaborations
# MATCH (a2:Artist)
# WHERE a1 <> a2
# WITH a1, a2
# CALL gds.alpha.ml.linkPrediction.predict(
#   'artist_collaboration_prediction_model',
#   {node1: id(a1), node2: id(a2)}
# )
# YIELD score
# WITH a1, a2, score
# ORDER BY score DESC
# LIMIT 10 // Limit the number of recommendations
# RETURN a1.Artist_ID AS ArtistID, a2.Artist_ID AS RecommendedArtistID, score;
# """

# recommendations = execute_query(recommendation_query)

# # Print recommendations
# print("Top 10 Artist Collaboration Recommendations:")
# print("===========================================")
# for recommendation in recommendations:
#     print(f"ArtistID: {recommendation['ArtistID']}, Recommended ArtistID: {recommendation['RecommendedArtistID']}, Score: {recommendation['score']}")

