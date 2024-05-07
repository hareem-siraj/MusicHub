from neo4j import GraphDatabase

# Connect to the Neo4j database
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "12345678"))

# Function to execute queries
def execute_query(query, params=None):
    with driver.session() as session:
        result = session.run(query, params)
        return result.data()

def load_data():
    q = """LOAD CSV WITH HEADERS FROM 'file:///final.csv' AS row


        MERGE (artist:Artist {Artist_ID: row.Artist_ID})

        MERGE (track:Track {Track_ID: row.Track_ID})

        MERGE (genre:Genre {Name: row.Genre})

        MERGE (album:Album {Album_ID: row.Album_ID})

        SET artist.Artist_Name = row.Artist_Name, track.Track_Name = row.Track_Name, track.Popularity = toInteger(row.Popularity), track.Duration = toInteger(row.Duration), track.Preview_URL = row.Preview_URL, album.Album_Name = row.Album_Name, album.Release_Date = row.Release_Date

        MERGE (artist)-[:CREATED]->(track)

        MERGE (track)-[:BELONGS_TO]->(genre)

        MERGE (album)-[:INCLUDES]->(track);"""
    execute_query(q)

    q2_part1 = """
        MATCH (g:Genre)<-[r:BELONGS_TO]-(t:Track) 
        WITH g, collect(t) AS tracks, collect(r) AS rels, count(r) AS countrels
        WHERE countrels > 100
        FOREACH(i IN range(0, countrels/50) |
        MERGE (sub:Genre {Name: g.Name + '_' + (i * 50 + 1) + '-' + (i * 50 + 50)})
        FOREACH(t IN tracks[(i * 50)..((i + 1) * 50)] |
            MERGE (t)-[:BELONGS_TO]->(sub)
            SET sub.tracks_count = coalesce(sub.tracks_count, 0) + 1
        )
        MERGE (sub)-[:Same_As]->(g)
        );
        """
    execute_query(q2_part1)

    q2_part2 = """
    MATCH (g1:Genre)<-[r1:BELONGS_TO]-(t2:Track)
    WHERE g1.tracks_count > 100
    REMOVE g1.tracks_count
    DELETE r1
    """

    execute_query(q2_part2)



def pipeline():

    #Genre Preferences
    query3 = """
        MATCH (genre:Genre)
        WITH genre, id(genre) as genreId
        MATCH (artist:Artist)-[:CREATED]->(:Track)-[:BELONGS_TO]->(genre)
        WITH artist, genreId, COUNT(*) AS genreCount
        ORDER BY artist.Artist_ID, genreCount DESC
        WITH artist, genreId AS genrePrefs
        SET artist.genrePreferences = genrePrefs"""
    execute_query(query3)

    # Popularity
    query4 = """
    MATCH (a:Artist)-[:CREATED]->(t:Track)
    WITH a, AVG(t.Popularity) AS AveragePopularity
    SET a.AVGpopularity = AveragePopularity;"""
    execute_query(query4)

    # Average Track Duration
    query7 = """
    MATCH (a:Artist)-[:CREATED]->(t:Track)
    WITH a, AVG(t.Duration) AS averageTrackDuration
    SET a.averageTrackDuration = averageTrackDuration;"""
    execute_query(query7)

    # # Create graph projection
    # projection_query = """
    # CALL gds.graph.project(
    # 'MyProj3',
    # ['Artist', 'Track', 'Genre','Album'],
    # ['CREATED', 'BELONGS_TO', 'INCLUDES'])"""
    # execute_query(projection_query)

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
    CALL gds.beta.pipeline.linkPrediction.create('ppp');
    """
    execute_query(create_pipeline_query)

    # Add node properties to the pipeline
    add_node_property_query = """
    CALL gds.beta.pipeline.linkPrediction.addNodeProperty('ppp', 'fastRP', {
      mutateProperty: 'embedding',
      contextNodeLabels: ['Artist'],
      embeddingDimension: 256,
      randomSeed: 42
    })
    """
    execute_query(add_node_property_query)

    # Add link features to the pipeline
    add_link_feature_query = """
    CALL gds.beta.pipeline.linkPrediction.addFeature('ppp', 'cosine', {
      nodeProperties: ['embedding', 'closeness_centrality', 'AVGpopularity', 'averageTrackDuration', 'communityId', 'genrePreferences']
    });
    """
    execute_query(add_link_feature_query)

    # Configure split
    split_query = """
    CALL gds.beta.pipeline.linkPrediction.configureSplit('ppp', {
      testFraction: 0.25,
      trainFraction: 0.6,
      validationFolds: 3
    })
    """
    execute_query(split_query)

    # Adding model candidates
    add_model_candidate_query = """CALL gds.beta.pipeline.linkPrediction.addRandomForest('ppp', {numberOfDecisionTrees: 10});"""
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
        'closeness_centrality',
        'communityId', 'genrePreferences']
        
      }
    },
    {SIMILAR_UNDIRECTED: {
        type: 'SIMILAR',
        orientation: 'UNDIRECTED',
        properties: 'score'}
    }
    )
    YIELD graphName, nodeProjection, nodeCount AS nodes, relationshipCount AS rels
    RETURN graphName, nodeProjection.artist AS prop, nodes, rels;
    """
    execute_query(projection_query2)

    # Train model
    train_query = """
    CALL gds.beta.pipeline.linkPrediction.train('myGraph4',
    { pipeline: 'ppp',
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
    [cand IN modelSelectionStats.modelCandidates | cand.metrics.AUCPR.validation.avg] AS validationScores;
    """
    execute_query(train_query)

if __name__ == "__main__":
    load_data()
    pipeline()
    driver.close()
    print("Pipeline executed successfully")