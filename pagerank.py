from common import *
from itertools import izip
from scipy.sparse import coo_matrix, csr_matrix, dok_matrix
import numpy as np
import cPickle as pickle

def make_users_link_map(users_data):
    """From the user data, make a dictionary which stores the links between users:
    
    {user_x: [list of users which user_x links to], ...}
    
    A link exists between user_a and user_b when:
    - user_a comments on a photo of user_b, or
    - user_a favorites a photo of user_b.
    
    Since the IDs Flickr uses (`oid') are non-numeric, they are
    converted to numeric IDs in this function. The new IDs (`nid')
    start from zero and increase by 1 for each new user (range [0, n],
    where n is the number of users).

    This function returns:
    - The ID mapping, `oid_nid_map' and `nid_oid_map',
    - A dictionary of links between users specified by nid, `link_map',
    - The mapping of nid to photographer category, `nid_category_map', and
    - The mapping of photographer category to nids, `category_nid_map'.
    """

    # Assign users numeric IDs
    oid_nid_map = {}
    nid_oid_map = {}
    nid_category_map = {}
    category_nid_map = defaultdict(set)

    next_nid = 0
    link_map = defaultdict(set)
    for user_oid, user_info in users_data.iteritems():
        if user_oid not in oid_nid_map:
            oid_nid_map[user_oid] = next_nid
            nid_oid_map[next_nid] = user_oid
            next_nid += 1
        
        user_nid = oid_nid_map[user_oid]
        for category in user_info['categories']:
            category_nid_map[category].add(user_nid)
        nid_category_map[user_nid] = user_info['categories']
        link_map[user_nid]      # Make sure we add an entry, even if empty

        if user_info.has_key('commented_on'):
            for commented_oid in user_info['commented_on']:
                # Add the user if not present in the map
                if commented_oid not in oid_nid_map:
                    oid_nid_map[commented_oid] = next_nid
                    nid_oid_map[next_nid] = commented_oid
                    next_nid += 1

                # Make a link between commenter and photographer
                commented_nid = oid_nid_map[commented_oid]
                link_map[user_nid].add(commented_nid)

        if user_info.has_key('fav_on'):
            for favorited_oid in user_info['fav_on']:
                # Add the user if not present in the map
                if favorited_oid not in oid_nid_map:
                    oid_nid_map[favorited_oid] = next_nid
                    nid_oid_map[next_nid] = favorited_oid
                    next_nid += 1

                # Make a link between commenter and photographer
                favorited_nid = oid_nid_map[favorited_oid]
                link_map[user_nid].add(favorited_nid)

    return oid_nid_map, nid_oid_map, link_map, nid_category_map, category_nid_map

def make_users_link_matrix(link_map):
    """Use the user links dictionary to create a sparse matrix of these
    links. This matrix can be used for PageRank calculation.

    link_matrix[nid_1, nid_2] == 1 iff nid_1 links to nid_2.

    """

    nusers = len(link_map)
    link_matrix = dok_matrix((nusers,nusers), dtype=np.int8)

    for uid, link_uids in link_map.iteritems():
        for link_uid in link_uids:
            link_matrix[uid, link_uid] = 1

    return link_matrix

def topic_specific_pagerank(M, S, beta = 0.8, state_vector = None):
    """Run Topic-Specific PageRank, given the adjacency matrix M and the
    teleport set S. Beta is the probability of following links from a
    node, and (1 - Beta) is the probability of teleporting from a
    node.

    """
    n_total = M.shape[0]        # Total number of users
    n_S = len(S)                # |S|: Number of users in the given category
    
    if n_S == 0:
        print "Error: Zero elements in the teleport set."
        return None

    # Set uniform initial state = 1/n for each node
    print "Generating state vector..."
    if state_vector is None:
        state_vector = np.array([1./n_total] * n_total, dtype='float64')
    print "Done."

    # Normalize the transition matrix
    print "Scaling transition matrix..."
    ones_in_row = {}
    M = csr_matrix(M).astype('float64')
    for r in range(n_total):
        ones_in_row[r] = M[r].nnz

    M = dok_matrix(M)
    print "Converted to DOK matrix."
    nonzero = M.nonzero()
    nonzero_r, nonzero_c = nonzero[0], nonzero[1]
    current_r = -1

    # Keep track of the indices of dangling nodes
    dangling_nodes = set(range(n_total))

    print "Total number of nodes = %d" % (n_total)
    print "Number of nonzero elements = %d" % (M.nnz)

    for r,c in izip(nonzero_r, nonzero_c):
        # For every new row, get the number of nonzero elements
        if r != current_r:
            #print "New r = ", r
            # This is not a dangling node
            dangling_nodes.discard(r)

            #ones_in_row = M[r,:].nnz
            current_r = r

        #print "Previous M[%d,%d] = %.4f" % (r,c, M[r,c])
        #print "Multiplying by:", beta/ones_in_row
        M[r,c] *= beta/ones_in_row[r]
        #print "New M[%d,%d] = %.4f" % (r,c, M[r,c])

    print "Number of dangling nodes = %d" % (len(dangling_nodes))

    # Calculation of Topic-Specific PageRank
    # ======================================
    # 
    # Matrix has been scaled by beta, but dangling nodes remain.
    # For a dangling node i, the row M[i,:] will have only zeroes.
    # Leave it as it is. Handle it in the teleportation matrix.
    
    # For a node j in S:
    # Teleport[i][j] = (1-Beta)/|S|
    #
    # For a node j not in S:
    # Teleport[i][j] = 0
    #
    # For a node j in S, and j is a dangling node:
    # Teleport[j][k] = 1/|S|, for all k in S
    #

    # For any node j, the contribution of the links to the state is:
    #
    # New state[j] = state * M[:,j] 
    #
    # In general, for a node j in S, the teleportation contribution is:
    # 
    # New state[j] += ((1 - Beta)/|S|) * sum(state) + (Beta/|S|) * sum(dangling_state)
    #
    # For a node j not in S, the teleportation contribution is:
    # 
    # New state[j] += 0

    topic_teleport = ((1 - beta)/n_S)
    dangling_teleport = beta/n_S

    state_diff = 1e6
    state_maxdiff = 0.00000001
    not_S = set(range(n_total)).difference_update(S)
    M = csr_matrix(M)

    print "Calculating PageRank..."
    iter = 0
    while state_diff > state_maxdiff:
        dangling_states = np.array([state_vector[i] for i in dangling_nodes])
        sum_dangling_states = dangling_states.sum()

        iter += 1
        sum_states = state_vector.sum()

        # Contribution of links
        new_state_vector = state_vector * M

        # Contribution of teleport
        for j in S:
            new_state_vector[j] += topic_teleport * sum_states
            new_state_vector[j] += dangling_teleport * sum_dangling_states

        # Normalize the state vector
        new_state_vector *= 1./new_state_vector.sum()
    
        state_diff = sum(abs(new_state_vector - state_vector))
        print "Iteration %d: Total change this iteration = %.7f" % (iter, state_diff)
        state_vector = new_state_vector

    print "Topic-Specific PageRank calculation complete."

    return state_vector

def run_pagerank(users_data, category, beta):
    oid_nid_map, nid_oid_map, link_map, nid_category_map, category_nid_map = make_users_link_map(users_data)
    M = make_users_link_matrix(link_map)
    S = category_nid_map[category]
    pagerank = topic_specific_pagerank(M, S, beta)

    return M, S, pagerank

if __name__ == "__main__":
    f = open('users_wildlife.dat', 'r')
    users_data = pickle.load(f)
    f.close()

    oid_nid_map, nid_oid_map, link_map, nid_category_map, category_nid_map = make_users_link_map(users_data)
    m = make_users_link_matrix(link_map)
