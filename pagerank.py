from common import *
from itertools import izip
from scipy.sparse import coo_matrix, csr_matrix, dok_matrix
import numpy as np
import os
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

def topic_specific_pagerank_multiple_topics(M, S_list, beta = 0.8, state_vector = None):
    """Run TSPR for a list of topics, sequentially. It is faster than
    running the original function separately for each topic because
    the transition matrix scaling (the bottleneck) is done only once.
    """
    n_total = M.shape[0]        # Total number of users

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

    state_vector_list = []

    for S in S_list:
        state_vector = np.array([1./n_total] * n_total, dtype='float64')
        n_S = len(S)                # |S|: Number of users in the given category

        if n_S == 0:
            print "Error: Zero elements in the teleport set."
            return None

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

        state_vector_list.append(state_vector)

    return state_vector_list

def run_pagerank(users_data, category, beta):
    """Wrapper around the TSPR function to run PageRank, given the
    category name."""

    oid_nid_map, nid_oid_map, link_map, nid_category_map, category_nid_map = make_users_link_map(users_data)
    all_maps = {'oid_nid_map': oid_nid_map, 
                'nid_oid_map': nid_oid_map,
                'link_map': link_map,
                'nid_category_map': nid_category_map,
                'category_nid_map': category_nid_map}

    M = make_users_link_matrix(link_map)
    S = category_nid_map[category]
    pagerank = topic_specific_pagerank(M, S, beta)

    return M, all_maps, pagerank

def run_and_save_pagerank(users_data, category, beta):
    """Run PageRank for one topic and save the results."""

    M, all_maps, pagerank = run_pagerank(users_data, category, beta)
    f = open("pagerank_%s.dat" % (category), 'wb')
    pickle.dump(pagerank, f)
    f.close()

def run_and_save_pagerank_multiple_topics(users_data, beta):
    """Runs PageRank for all topics and saves the results."""

    oid_nid_map, nid_oid_map, link_map, nid_category_map, category_nid_map = make_users_link_map(users_data)
    all_maps = {'oid_nid_map': oid_nid_map, 
                'nid_oid_map': nid_oid_map,
                'link_map': link_map,
                'nid_category_map': nid_category_map,
                'category_nid_map': category_nid_map}

    M = make_users_link_matrix(link_map)
    categories = category_nid_map.keys()
    S_list = []
    for category in categories:
        S = category_nid_map[category]
        S_list.append(S)

    print "S list generated."
    pagerank_list = topic_specific_pagerank_multiple_topics(M, S_list, beta)
    for i, category in enumerate(categories):
        f = open('pagerank_%s_1.dat' % (category), 'wb')
        pickle.dump(pagerank_list[i], f)
        f.close()

def load_pagerank(category):
    """Load the PageRank results for one topic from a file."""

    print "Loading PageRank for category: %s" % (category)
    fname = 'pagerank/pagerank_%s_1.dat' % (category)
    f = open(fname, 'r')
    pagerank = pickle.load(f)
    f.close()

    return pagerank

def assign_camera_scores(category, pagerank_vector, users_data, all_maps):
    """Assign camera scores for a topic based on the PageRank results."""

    camera_scores = defaultdict(float)
    nid_oid_map = all_maps['nid_oid_map']
    oid_nid_map = all_maps['oid_nid_map']
    for nid, pagerank_score in enumerate(pagerank_vector):
        oid = nid_oid_map[nid]
        user = users_data[oid]
        if 'cameras_by_category' in user:
            if category in user['cameras_by_category']:
                cameras_in_category = user['cameras_by_category'][category]
                total_photos = sum(cameras_in_category.values()) * 1.0

                for camera, n_photos in cameras_in_category.iteritems():
                    camera_scores[camera] += (n_photos / total_photos) * pagerank_score
        
    return camera_scores

def save_camera_scores(users_data):
    """Assign and save camera scores for all topics."""

    oid_nid_map, nid_oid_map, link_map, nid_category_map, category_nid_map = make_users_link_map(users_data)
    m = make_users_link_matrix(link_map)
    all_maps = {'oid_nid_map': oid_nid_map, 
                'nid_oid_map': nid_oid_map,
                'link_map': link_map,
                'nid_category_map': nid_category_map,
                'category_nid_map': category_nid_map}

    categories = category_nid_map.keys()
    
    for category in categories:
        pagerank = load_pagerank(category)
        camera_scores = assign_camera_scores(category, pagerank, users_data, all_maps)
        f = open('camera_%s.dat' % (category), 'wb')
        pickle.dump(camera_scores, f)
        f.close()

def load_sorted_camera_scores(category):
    """Load camera scores for a topic from a file and sort them."""

    f = open('camera_scores/camera_%s.dat' % (category), 'r')
    camera_scores = pickle.load(f)
    f.close()

    sorted_camera_scores = sorted(camera_scores.items(), key = lambda x: x[1], reverse = True)
    return sorted_camera_scores

def aggregate_camera_scores():
    """Aggregate camera scores from multiple files into a single dictionary."""

    dirname = 'camera_scores'
    current_dir = os.getcwd()
    os.chdir(dirname)
    camera_scores_combined = {}
    for fname in os.listdir('.'):
        category = (fname.split('_')[1]).split('.')[0]
        f = open(fname, 'r')
        camera_scores = pickle.load(f)
        f.close()

        camera_scores_combined[category] = camera_scores

    os.chdir(current_dir)
    return camera_scores_combined

def weighted_camera_scores(combined_camera_scores, **kwargs):
    """Calculates the weighted camera scores. The keyword arguments should
    be of the form category = weight."""

    weighted_camera_scores = defaultdict(float)
    for category in kwargs:
        if category not in combined_camera_scores:
            return None
        
        weight = kwargs[category]
        for camera, camera_score in combined_camera_scores[category].iteritems():
            weighted_camera_scores[camera] += weight * camera_score

    sorted_camera_scores = sorted(weighted_camera_scores.items(), key = lambda x: x[1], reverse = True)
    return sorted_camera_scores

if __name__ == "__main__":
    f = open('users_all_1.dat', 'r')
    users_data = pickle.load(f)
    f.close()

    #run_and_save_pagerank_multiple_topics(users_data, beta = 0.5)
