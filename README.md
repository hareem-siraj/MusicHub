# Music Hub: Connecting Pakistani Musicians

## Objective
The objective of this project is to develop an application that facilitates connections among Pakistani musicians based on their interests. The application aims to provide valuable insights into the Pakistani music industry and enable musicians to discover potential collaborators, expand their networks, and increase creativity.

## Methodology
1. Utilize Spotify’s API to gather comprehensive data about Pakistani musicians.
2. Clean data and load into Neo4j.
3. Run graph analytics queries including:
   - Genre Preference
   - Average Popularity
   - Average Track Duration
   - Closeness Centrality
   - Community Detection using Louvain Modularity
4. Build a link prediction model using the GDS library.
5. Train the model using Random Forest and predict recommended artists.
6. Integrate the results into our Music Hub app.

## How to Run:
1. Open neo4j and paste final.csv in the import folder of the database.
2. Install GDS Library.
3. Run pipeline.py first
4. Run app.py
5. Finally, go to link in the terminal and enjoy:)

## Results
Leveraging the GDS library and Random Forest algorithm, we developed a robust link prediction model to recommend potential collaborations between Pakistani musicians. By analyzing the network topology and different analytics, the model accurately predicts synergistic partnerships, fostering creativity and innovation within the music industry.

## Conclusion
We successfully created a platform that connects Pakistani musicians based on their interests and preferences. By applying graph analysis techniques and machine learning algorithms, we aimed to empower musicians to discover new opportunities, enhance their creativity, and contribute to the growth of the Pakistani music industry.

