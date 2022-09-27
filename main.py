from distutils.log import info
from itertools import combinations
import numpy as np
import pandas as pd
from queue import Queue
import networkx as nx
import re
import os
import logging 
from collections import defaultdict


#un commento
class IMDBGraph:
    '''
    This class use IM Data base for buld graph,
    It was written for the exame  "Advanced algorithm and graph mining.
    This class use mainly Networkx libreray and pandas for reading the data file.
    '''
    def __init__(self,path="data.tsv") -> None:
        '''
        Description:
        ----------
        path: str deafualt value="data.tsv"
            direction of data file, contain rows (actor, movie).
        g: nx.Graph
            empty graph
        A: nx.Graph 
            Actors graph, Nodes are actors, edge between two actors if they've interpreted a movie toghether.
        listYears: list 
            list of years, used to performed som query on graph in this years.
        logger: logger
            helping object for creating a log file.
        reversedAcrtorsDict,reversedMovieDict: dict
            help dicts where keys are id of actor/movie, 
            and value is dict of info(label,year(just for movie)).

        Raises
        ------
        FileNotFoundError
            If no file fuond at the specified path .
        
        '''
        self.g=nx.Graph()
        self.A=nx.Graph()
        self.path=path
        #verify that file exsist otherwise rais an error.
        if not os.path.isfile(self.path):
            raise FileNotFoundError(f" No file {self.path} found, pleas choose a for read the graph")
        self.reversedAcrtorsDict={}
        self.reversedMovieDict={}
        self.listYears=[1930,1940,1950,1960,1970,1980,1990,2000,2010,2020]
        #now we will Create and configure logger
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.basicConfig(level=logging.INFO,filename="log.txt", 
					format='%(asctime)s %(message)s', 
					filemode='w') 
        
        self.logger=logging.getLogger()
        self.logger.info('Object is constructed')
    def read_main_graph_from_gpickle(self,filename="main_graph.gpickle"):
        self.logger.info(f'g was read from file {filename}')
        self.g=nx.read_gpickle(filename)
    def read_actors_graph_from_gpickle(self,filename="actors_graph.gpickle"):
        self.logger.info(f'A was read from file {filename}')
        self.A=nx.read_gpickle(filename)
        
    def construct_graph(self)-> nx.Graph:
        '''
        Read the data in self.path and build the g graph
        Return
        -------
           g: nx.Graph 
              a graph that containes edges between actor and all movie he has interpreted.

        '''
        self.g=nx.Graph()
        df=pd.read_csv(self.path,delimiter="\t", names=['actor','film'])
        self.logger.info(df.head(10))
        #assign id to each actor and to each movie
        actorsDict=dict(map(reversed,enumerate(df.actor.unique())))
        movieDict=dict(map(reversed,enumerate(df.film.unique(),start=len(actorsDict))))
        #extract year from list of unique movie titles, creat dict {movie title: year}
        yearDict= dict(map(self.get_year,df.film.unique()))
        self.logger.info(f'len movie is {len(movieDict)} and len actors is {len(actorsDict)}')
        #add id_actor,id_film,year columns in df
        df['id_actor']=df['actor'].map(actorsDict)
        df['id_film']=df['film'].map(movieDict)
        df['year']=df['film'].map(yearDict)
        self.logger.info(df.head(10))
        #build the graph from df using id_actor, id_film columns
        self.g=nx.from_pandas_edgelist(df,"id_actor","id_film")
        self.logger.info('Graph g is constructed')
        #create reversed dict {id_actor:{label:name_of_actor,type:0}}
        self.reversedAcrtorsDict=dict(map(lambda x: (x[1],{'label':x[0],'type':0}),actorsDict.items()))
        self.logger.info('reversedAcrtorsDict is constructed')
        df2=df.drop_duplicates('id_film')
        df2=df2.rename(columns={'film':'label'}).set_index('id_film')
        #create reversed dict of movie{ id_movie: {label:title of movie, type:1, year:year}}
        self.reversedMovieDict=df2[['label','year']].to_dict(orient='index')
        list(map(lambda x: x[1].update({'type':1}) ,self.reversedMovieDict.items()))
        #set nodes attributes in graph
        nx.set_node_attributes(self.g,self.reversedAcrtorsDict)
        self.logger.info('acrtors attri is setted')
        nx.set_node_attributes(self.g,self.reversedMovieDict)
        self.logger.info('movies attri is setted')
        nx.write_gpickle(self.g, "main_graph.gpickle")
        return self.g
    
    ##########################################
    ## Question 1.E
    ##########################################
    def find_actor_with_longestPeriod(self,x: int)-> tuple:
        '''
        Which one is the actor who worked for the longest period 
        (compute the difference between the first and the last year he/she worked),
        considering only the movies up to year x? 
        For instance A did movies in 1995, 1998, and 1999,
        meaning that the duration of A is 4 years.

        Parameters:
        -----------
            x:int
                must be a year
        Return
        ------
            longestActorId:int
                    the id of the actor who worked for the longest period 
            longestPeriod: int
                    the longest period found until year x.
        '''
        longestPeriod=0
        longestActorId=0
        for j,d in self.g.nodes(data=True):
            #iterate over actors nodes defined by type 0
            if d['type']==0:
                #get the movie list of the actor j
                movies=list(self.g.neighbors(j)) 
                years=set()  
                if(len(movies)!=0):
                    for m in movies:
                        #check if the year of the movie smaller or equal to year x add it to set years
                        if(self.g.nodes[m]['year']<=x):
                            years.add(self.g.nodes[m]['year'])
                #take the lenghth of set years "len(years)":
                # if len(years)==0 then the he dose not work and must have period =0
                # if the len(years)==1 then he worked for one year
                #else take the diffrence between the min and max year in the set
                period=(lambda x,y: 0 if x==0 else( 1 if x==1 else max(y)-min(y)))(len(years),years) 
                if(period>longestPeriod):
                    longestPeriod=period
                    longestActorId=j
        return (longestActorId,longestPeriod)            
    def find_actor_longestperiod_allYear(self):
        for x in range(0,len(self.listYears)):
            longestActorId,longestPeriod=self.find_actor_with_longestPeriod(self.listYears[x])
            self.logger.info(f"\n -----\n The actor who worked for the longest period until year {self.listYears[x]} is :\n {self.g.nodes[longestActorId]['label']},\n His id is {longestActorId},n\Years of work:{longestPeriod} ")
    #######################################
    ## Question2.1
    #######################################
    '''
    Considering only the movies up to year x with x in 
    {1930,1940,1950,1960,1970,1980,1990,2000,2010,2020} and
    restricting to the largest connected component of the graph. 
    Compute exactly the diameter of G
    '''
    def get_largest_cc(self,year: int) ->nx.Graph:
        '''
        Return:
        -------
        largest_cc_graph: nx.graph
                the largest connected component int the graph self.g

        '''
        self.logger.info(f"Year is {year}")
        dictfiltermovie=dict(filter(lambda d: d[1]['year']<year,self.reversedMovieDict.items()))
        nodefilterlist=list(dictfiltermovie.keys())+list(self.reversedAcrtorsDict.keys())
        h=self.g.subgraph(nodefilterlist).copy()
        self.logger.info(f"number of nodes: {h.number_of_nodes()}")
        cc =list(nx.connected_components(h))
        self.logger.info(f"number of connected components: {len(cc)}")
        largest_cc=max(cc,key=len)
        self.logger.info(f"Number of nodes in the largest cc{len(largest_cc)}")
        largest_cc_graph=self.g.subgraph(largest_cc).copy()
        
        return largest_cc_graph
    def get_hiestDegree_node(self,graph:nx.Graph) -> tuple:
        '''
        Used to finde the start node for the calculation of the diameter
        Parameters:
        -----------
            graph:nx.Graph
                the largest connected graph 
        Return:
        -------
            hiestdegreenode:tuple
                (the id of the node with the hieghest degree, the hieghest degree)

        '''
        hiestdegreenode=max(graph.degree,key=lambda x: x[1])
        self.logger.info(f"Hiegest node degree :{hiestdegreenode}")
        return hiestdegreenode

    def breadth_first_search(self,cc:nx.Graph,start_node:int)->dict:
        '''
        Used to find the ecc of the graph cc and to find the distances of all nodes from start_node
        Parameters:
        ------------
            cc: the largest connected graph
            start_node: the node from which begin the BFS, in this example it's the one with hieghest degree
        Return:
        --------
           B_u:dict
              { level:[ list of nodes id that are at these levele]}
              ex: {24 :[123,56,88896]} nodes in the list are at distance 24 from the start_node

        '''
        visited = {}
        queue = Queue()
        queue.put(start_node)
        #nod start_node is at level(distance) equale to 0
        visited[start_node]=0
        while not queue.empty():
            current_node = queue.get()
            for next_node in cc.neighbors(current_node):
                if next_node not in visited:
                    queue.put(next_node)
                    visited[next_node]=visited[current_node]+1
        #Gruob by distance to create dict of distance
        B_u = defaultdict(list)
        for key, value in visited.items():
            B_u[value].append(key)
        return B_u
    def calc_diameter(self,cc:nx.Graph,B_u:dict)->int:
        '''
        Return:
        -------
            lb:int
               the diameter of the graph cc
        '''
        ecc=max(B_u)
        self.logger.info(f"ecc of nodo u is {ecc}") 
        i=ecc
        lb=ecc
        up=2*ecc
        while up >lb:
            eccs=nx.eccentricity(cc, v=B_u[i])
            B_i=max(eccs.values())
            max_val=max(B_i,lb)
            self.logger.info (f"i is {i} , B_i is {B_i}, lb is {lb}, 2*(i-1) is {2*(i-1)},uper is {up}")
            if max_val > 2*(i-1):
                return max_val
            else:
                lb=max_val
                up=2*(i-1)
            i-=1
        return lb
    def find_all_diameter(self):
        for year in self.listYears:
            largest_cc_graph=self.get_largest_cc(year)
            hiestdegreenode=self.get_hiestDegree_node(largest_cc_graph)
            B_u=self.breadth_first_search(largest_cc_graph,hiestdegreenode[0])
            diametro=self.calc_diameter(largest_cc_graph,B_u)
            self.logger.info (f"Diametro per l'anno {year } is {diametro}")

    #######################################
    ## Question3.IV
    #######################################
   
    def find_actor_with_largest_staff(self)-> tuple:
        '''
        Who is the actor who participated in movies with largest number of actors,
        i.e. such that the sum of the sizes of the casts of the movies he participated in is maximum?
        For example actor A starred in movie M1 and M2. M1 contains 6 actors, M2 contains 2 actors.
        The score of A is 8.

        '''
        largestscore=0
        largestActorId=0
        for j,d in self.g.nodes(data=True):
            if d['type']==0:
                movies=list(self.g.neighbors(j))  
                score=sum(map(lambda x: len(list(self.g.neighbors(x))) ,movies))
                if(score>largestscore):
                    largestscore=score
                    largestActorId=j
        self.logger.info(f"the actor who participated in movies with largest number of actors : \n {self.g.nodes[largestActorId]['label']} \n score:{largestscore}")
        return (largestActorId,largestscore) 

    #######################################
    ## Question4
    #######################################
    def create_actor_graph_from_dict(self,saveName="actors_graph.gpickle"):
        '''
        Build the actor graph, 
        whose nodes are only actors and two actors are connected if they did a movie together. 
        '''
        self.logger.info("Start creating acrtors graph")
	#print("Start creating acrtors graph")
        movie_list=self.reversedMovieDict.keys()
        print(len(movie_list))
        self.A=nx.Graph()
        for j in movie_list:
            #consider the actors who partecipated at movie j 
            actors=list(self.g.neighbors(j))
            #consider all possibile combination of actors
            for i in combinations(actors,2):
                #i is a tuple of two actors id in the movie j
                #two cases:
                #1- (i1,i2) are visited in a previous movie and inserted to the graph, so just add one to the edge wieght
                #2- j is the first movie they are visited in, so add a new edge with wieght equal to 1 
                if self.A.has_edge(*i):
                    self.A[i[0]][i[1]]['weight']+=1
                else:
                    self.A.add_edge(i[0],i[1],weight=1)
        self.logger.info("Grafo di attori è stato costruito")        
        return self.A
    def find_most_actors(self):
        '''
        Which is the pair of actors who collaborated the most among themselves?
        '''
        max_a=max(self.A.edges(data=True),key=lambda x:x[2]['weight'])
        self.logger.info(f"The acrtors that collaborate in the biggest number of movie is {max_a},{self.g.nodes[max_a[1]]} ,,,,{self.g.nodes[max_a[0]]} ")
        
          
    @staticmethod
    def get_year(str): 
        year=2000
        strr=re.findall(r'\(.*?\)',str)
        for i in range (len(strr)):
            s=re.findall(r'\d+',strr[i])
            if(len(s)>0):
                year= int(s[0])
        return str,year
    def get_actors(self)-> dict:
        '''
        Return 
        -------
            dict: keys are id's of actors and values are dict {"label":name of the actor, "type":0}

        '''
        return self.reversedAcrtorsDict
    def get_movies(self)-> dict:
        '''
        Return 
        -------
            dict: keys are id's of movies and values are dict {"label":name of the actor,"year":int ,"type":1}

        '''
        return self.reversedMovieDict
    def get_list_years(self)-> list:
        return self.listYears 
    def get_main_graph(self)-> nx.Graph:
        return self.g   
    def get_actor_graph(self):
        return self.A
        

if __name__=="__main__":
    
    obj=IMDBGraph() # you can pass the path of data file to the class constructor
    obj.construct_graph()
    ## Question1:E
    obj.find_actor_longestperiod_allYear()
    ## Question2.1
    obj.find_all_diameter()
    ## Question3.IV
    obj.find_actor_with_largest_staff()
    ## Question4
    obj.create_actor_graph_from_dict()
    obj.find_most_actors()










