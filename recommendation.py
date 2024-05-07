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

#     call gds.graph.project('myGraph2',['Genre'],{Same_As:{type:'Same_As',orientation:'undirected'}});
# CALL gds.wcc.write('myGraph2', { writeProperty: 'componentId' })
# YIELD nodePropertiesWritten, componentCount;

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

    # community detection
    query8 = """
    CALL gds.louvain.write('MyProj3', {
    writeProperty: 'communityId'
    })
    YIELD communityCount, modularity, modularities;
    """
    execute_query(query8)

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
      nodeProperties: ['embedding', 'closeness_centrality', 'AVGpopularity', 'averageTrackDuration', 'communityId']
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

    #CALL gds.beta.pipeline.linkPrediction.addRandomForest('pp3', {numberOfDecisionTrees: 10})

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
        'closeness_centrality',
        'communityId',]
        
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
