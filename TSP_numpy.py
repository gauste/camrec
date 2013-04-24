from __future__ import division
from numpy import *

#example of set of pages belonging to the same topic (the simple topic specific page rank version)
S = set(('wildlife', 'nature'))
Es = matrix([[0], [1],[0], [1]])

def jaccard_sim(tup_1, tup_2, verbose=False):
    """
        calculate the jaccard similiarity of 2 tuples
	due to the reason I added '' as a specific topic, so minus 1 in sum, if we have more than 
	2 specifics, then don't need to minus 1.
    """
    sum = len(tup_1) + len(tup_2)-1
    set_1 = set(tup_1)
    set_2 = set(tup_2)
    inter = 0
    for i in (set_1 & set_2):
        count_1 = tup_1.count(i)
        count_2 = tup_2.count(i)
        inter += count_1 if count_1 < count_2 else count_2
    j_sim = inter/sum
    if verbose : print j_sim
    return j_sim

def page_rank(matrix, teleport=False, b=1, Es=[], S=set(), nbr_iterations=10000000, verbose=False):
    """
        calculate the page rank for each element based on the matrix in input
        we should validate if the matrix is stochastic
        if not we use the teleport method to ovoid dead ends (introducing the random surfers)
            v' = Mv + (1-b)e/n
            v : eigenvector
            The term (1-b)e/n is a vector each of whose components has value (1-b)/n and
            represents the introduction, with probability 1 - b, of a new random surfer at
            a random page.
        The mathematical formulation for the iteration that yields topic-specific
        PageRank is similar to the equation we used for general PageRank. The only
        difference is how we add the new surfers. Suppose S is a set of integers consisting
        of the row/column numbers for the pages we have identified as belonging to a
        certain topic (called the teleport set). Let eS be a vector that has 1 in the
        components in S and 0 in other components. Then the topic-specific Page-
        Rank for S is the limit of the iteration
            v' = bMv + (1 - b)eS/|S|
        Here, as usual, M is the transition matrix, and |S| is the size of set
        S,which means numbers of categories in one topic.
    """
    elements_length = len(matrix)
    eigenvectors = (1/elements_length)*mat(ones((elements_length,1)))
    if S and teleport:
        teleport_v = (1-b)/len(S) * Es
    else:
        teleport_v = (1-b)/elements_length * mat(ones((elements_length,1))) if teleport else mat(ones((elements_length,1))) * 0

    eigenvectors_p = mat(ones((elements_length,1))) * 0
    itr = 0
    while (eigenvectors_p != eigenvectors).any() and itr < nbr_iterations:
        if (eigenvectors_p != (mat(ones((elements_length,1))) * 0)).any() : eigenvectors = eigenvectors_p;
        eigenvectors_p = matrix_vector_multiplication(matrix, eigenvectors, elements_length, b, teleport_v)
        itr += 1
    if verbose: 
	print "Page Rank Values" 
	print eigenvectors
    return eigenvectors

def matrix_vector_multiplication(matrix, vector, length, b, teleport_v):
    """
        calculate the multiplication of matrix by vector
    """
    return b * matrix * vector + teleport_v    

#exemple of sets of keywords, to be used for the topic specific page rank
Sk = tuple((tuple(('wildlife','')),tuple(('nature','')), tuple(('seaworld',''))))

def TS_page_rank(matrix, b=1, P=set(), S=set(), nbr_iterations=100000, verbose=False):
    """
        calculation of the topic specific page rank.
        S is the set of sets of topics
        P is set of topic keywords for each page
        the algorithm we shall implement is the following:

                => calculate the jackard similarity for P and Si
                => classify the page for a topic
                =>construct Es, such that is the set of corresponding teleport surfurs for each set of topics
    """
    elements_length = len(matrix)    
    i = 0
    for s in S:
        Esp = [0] * elements_length
        #calculate the jaccard similarity for each page and set and
        for p in range(elements_length):
            Esp[p] = jaccard_sim(P[p], s)
        Esp = mat(Esp)
	print "Specific Topic:" 
	print s
        print "Esp:" 
	print  Esp
        #calculate the page rank for each topic
        page_rank(matrix, teleport=True, b=b, Es=Esp.getT(), S=S[i], nbr_iterations=10000000, verbose=True)
        i += 1


def test_page_rank():
    m = matrix([[0,0.5,0,0],[1/3,0,0, 0.5],[1/3,0,1,0.5], [1/3, 0.5, 0,0]])     
    page_rank(m, teleport=True, b=0.85, verbose=True)
    page_rank(m, teleport=True, b=0.85, Es=Es, S=S, verbose=True)

def test_TS_page_rank():
    m = matrix([[0,0.5,0,0],[1/3,0,0, 0.5],[1/3,0,1,0.5], [1/3, 0.5, 0,0]])            
    P = tuple((tuple(('seaworld', 'wildlife')), tuple(('wildlife', 'nature')), tuple(('nature')), tuple(('seaworld','nature', 'wildlife'))))
    TS_page_rank(m, b=0.85, P=P, S=Sk, nbr_iterations=100000, verbose=True)


if __name__ == '__main__':
    #print "calculation of page rank"
    #test_page_rank()
    print "calculation of topic specific page rank"
    test_TS_page_rank()
    # note: if we want to input the data, then the transition matrix should be like the value of m shown in the function of test_TS_page_rank(). We also need to change the P shown in the same funciton, each tuple of it contains the categories of each photographer takes. Also, we need to replace the Sk to the true categories we need. 
