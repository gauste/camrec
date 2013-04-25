from common import *
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

def topic_specific_pagerank(M, S, beta = 0.8):
    """Run Topic-Specific PageRank, given the adjacency matrix M and the
    teleport set S. Beta is the probability of following links from a
    node, and (1 - Beta) is the probability of teleporting from a
    node.

    """
    
    n = M.rows

if __name__ == "__main__":
    f = open('users_wildlife.dat', 'r')
    u = pickle.load(f)
    f.close()

    oid_nid_map, nid_oid_map, link_map, nid_category_map, category_nid_map = make_users_link_map(u)
    m = make_users_link_matrix(link_map)
