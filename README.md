# IMDB-gragh

This project was done for the exam  "Advanced algorithms and graph mining"<br />

IMDB (https://www.imdb.com/) Internet Movies DataBase is a website collecting movies and actors, specifying for each actress or actor in which movie he/she starred. <br />

The .tsv file whose rows are formed by two tab separated values. The first value is the name of the actor or of the actress the second value is the name of the movie he/she participated in. For instance, this is a sample:

….. <br />

Pitt, Brad      Voyage of Time (2014)<br />

Pitt, Brad      Weddings of a Lifetime (1995) (TV)<br />

The name of a movie contains also the year in which it has been done (inside the parentheses) and contains “(TV)” if it is a television product.

GRAPH: build the following graph using NetworkX: G is a Bipartite graph, where nodes are actors/actresses and movies. There is an edge between an actor/actress A and a movie M if A participated in M .<b />

1-Considering only the movies up to year x with x in {1930,1940,1950,1960,1970,1980,1990,2000,2010,2020}, write a function which, given x, computes:<br />

Which one is the actor who worked for the longest period (compute the difference between the first and the last year he/she worked), considering only the movies up to year x? For instance A did movies in 1995, 1998, and 1999, meaning that the duration of A is 4 years. <br />

2-Considering only the movies up to year x with x in {1930,1940,1950,1960,1970,1980,1990,2000,2010,2020} and restricting to the largest connected component of the graph.<br /> 


Compute exactly the diameter of G.<br />

3-Who is the actor who participated in movies with largest number of actors, i.e. such that the sum of the sizes of the casts of the movies he participated in is maximum? For example actor A starred in movie M1 and M2. M1 contains 6 actors, M2 contains 2 actors. The score of A is 8.<br />

4-Build also the actor graph, whose nodes are only actors and two actors are connected if they did a movie together. Answer to the following question:<br />

Which is the pair of actors who collaborated the most among themselves?<br />
