"""A simple implementation of the quick hull algorithm."""

from MathUtils import *
from itertools import izip
import operator

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007, Python File Format Interface
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

# adapted from
# http://en.literateprograms.org/Quickhull_(Python,_arrays)
def qdome2d(vertices, base, normal, precision = 0.0001):
    vert0, vert1 = base
    outer = [ (dist, vert)
          for dist, vert
          in izip( ( vecDotProduct(vecCrossProduct(normal,
                                                   vecSub(vert1, vert0)),
                                   vecSub(vert, vert0))
                     for vert in vertices ),
                   vertices )
          if dist > precision ]

    if outer:
        pivot = max(outer)[1]
        outer_verts = map(operator.itemgetter(1), outer)
        return qdome2d(outer_verts, [vert0, pivot], normal) \
               + qdome2d(outer_verts, [pivot, vert1], normal)[1:]
    else:
        return base

def qhull2d(vertices, normal, precision = 0.0001):
    """Simple implementation of the 2d quickhull algorithm in 3 dimensions for
    vertices viewed from the direction of C{normal}.
    Returns a fan of vertices that makes up the surface.

    >>> import random
    >>> plane = [(0,0,0),(1,0,0),(0,1,0),(1,1,0)]
    >>> for i in xrange(200):
    ...     plane.append((random.random(), random.random(), 0))
    >>> verts = qhull2d(plane, (0,0,1))
    >>> len(verts)
    4"""
    base = basesimplex3d(vertices, precision)
    if len(base) >= 2:
        vert0, vert1 = base[:2]
        return qdome2d(vertices, [vert0, vert1], normal) \
               + qdome2d(vertices, [vert1, vert0], normal)[1:-1]
    else:
        return base

def basesimplex3d(vertices, precision = 0.0001):
    """Find four extreme points, to be used as a starting base for the
    quick hull algorithm.

    The algorithm tries to find four points that are
    as far apart as possible, because that speeds up the quick hull
    algorithm. The vertices are ordered so their signed volume is positive.

    If the volume zero up to C{precision} then only three vertices are
    returned. If the vertices are colinear up to C{precision} then only two
    vertices are returned. Finally, if the vertices are equal up to C{precision}
    then just one vertex is returned.

    >>> base = basesimplex3d([(0,0,0),(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(1,1,1)])
    >>> len(base)
    4
    >>> (0,0,0) in base
    True
    >>> (1,1,1) in base
    True
    """
    # sort axes by their extent in vertices
    extents = sorted(range(3),
                     key=lambda i:
                     max(vert[i] for vert in vertices)
                     - min(vert[i] for vert in vertices))
    # extents[0] has the index with largest extent etc.
    # so let us minimize and maximize vertices with key
    # (vert[extents[0]], vert[extents[1]], vert[extents[2]])
    # which we can write as operator.itemgetter(*extents)(vert)
    vert0 = min(vertices, key=operator.itemgetter(*extents))
    vert1 = max(vertices, key=operator.itemgetter(*extents))
    # check if all vertices coincide
    if vecDistance(vert0, vert1) < precision:
        return [ vert0 ]
    # as a third extreme point select that one which maximizes the distance
    # from the vert0 - vert1 axis
    vert2 = max(vertices,
                key=lambda vert: vecDistanceAxis((vert0, vert1), vert))
    #check if all vertices are colinear
    if vecDistanceAxis((vert0, vert1), vert2) < precision:
        return [ vert0, vert1 ]
    # as a fourth extreme point select one which maximizes the distance from
    # the v0, v1, v2 triangle
    vert3 = max(vertices,
                key=lambda vert: abs(vecDistanceTriangle((vert0, vert1, vert2),
                                                         vert)))
    # ensure positive orientation and check if all vertices are coplanar
    orientation = vecDistanceTriangle((vert0, vert1, vert2), vert3)
    if orientation > precision:
        return [ vert0, vert1, vert2, vert3 ]
    elif orientation < -precision:
        return [ vert1, vert0, vert2, vert3 ]
    else:
        # coplanar
        return [ vert0, vert1, vert2 ]

def qhull3d(vertices, precision = 0.0001):
    """Return the triangles making up the convex hull of C{vertices}.
    Regards distances less than C{precision} to be zero (useful to simplify
    the hull of a complex mesh, at the expense of exactness of the hull).
    
    @param vertices: The vertices to find the hull of.

    Test a tetrahedron
    ------------------

    >>> import random
    >>> tetrahedron = [(0,0,0),(1,0,0),(0,1,0),(0,0,1)]
    >>> for i in xrange(200):
    ...     alpha = random.random()
    ...     beta = random.random()
    ...     gamma = 1 - alpha - beta
    ...     if gamma >= 0:
    ...         tetrahedron.append((alpha, beta, gamma))
    >>> verts, triangles = qhull3d(tetrahedron)
    >>> (0,0,0) in verts
    True
    >>> (1,0,0) in verts
    True
    >>> (0,1,0) in verts
    True
    >>> (0,0,1) in verts
    True
    >>> len(verts)
    4
    >>> len(triangles)
    4

    Test a pyramid
    --------------

    >>> verts, triangles = qhull3d([(0,0,0),(1,0,0),(0,1,0),(1,1,0),(0.5,0.5,1)])
    >>> (0,0,0) in verts
    True
    >>> (1,0,0) in verts
    True
    >>> (0,1,0) in verts
    True
    >>> (1,1,0) in verts
    True
    >>> len(verts)
    5
    >>> len(triangles)
    6

    Test the unit cube
    ------------------

    >>> import random
    >>> cube = [(0,0,0),(0,0,1),(0,1,0),(1,0,0),(0,1,1),(1,0,1),(1,1,0),(1,1,1)]
    >>> for i in xrange(200):
    ...     cube.append((random.random(), random.random(), random.random()))
    >>> verts, triangles = qhull3d(cube)
    >>> len(triangles) # 6 faces, written as 12 triangles
    12
    >>> len(verts)
    8

    Test a degenerate shape: unit square
    ------------------------------------
    
    >>> import random
    >>> plane = [(0,0,0),(1,0,0),(0,1,0),(1,1,0)]
    >>> for i in xrange(200):
    ...     plane.append((random.random(), random.random(), 0))
    >>> verts, triangles = qhull3d(plane)
    >>> len(verts)
    4
    >>> len(triangles)
    2

    Test a random shape
    -------------------

    >>> import random
    >>> shape = []
    >>> for i in xrange(2000):
    ...     vert = (random.random(), random.random(), random.random())
    ...     shape.append(vert)
    >>> verts, triangles = qhull3d(shape)
    """
    # find a simplex to start from
    hull_vertices = basesimplex3d(vertices, precision)

    # handle degenerate cases
    if len(hull_vertices) == 3:
        # coplanar
        hull_vertices = qhull2d(vertices, vecNormal(*hull_vertices))
        return hull_vertices, [ (0, i+1, i+2)
                                for i in xrange(len(hull_vertices) - 2) ]
    elif len(hull_vertices) <= 2:
        # colinear or singular
        # no triangles for these cases
        return hull_vertices, []
    
    # construct list of triangles of this simplex
    hull_triangles = set([ operator.itemgetter(i,j,k)(hull_vertices)
                         for i, j, k in ((1,0,2), (0,1,3), (0,3,2), (3,1,2)) ])

    # construct list of outer vertices for each triangle
    outer_vertices = {}
    for triangle in hull_triangles:
        outer = \
            [ (dist, vert)
              for dist, vert
              in izip( ( vecDistanceTriangle(triangle, vert)
                         for vert in vertices ),
                       vertices )
              if dist > precision ]
        if outer:
            outer_vertices[triangle] = outer

    # as long as there are triangles with outer vertices
    while outer_vertices:
        # grab a triangle and its outer vertices
        triangle, outer = outer_vertices.iteritems().next()
        # calculate pivot point
        pivot = max(outer)[1]
        # add it to the list of extreme vertices
        hull_vertices.append(pivot)
        # and update the list of triangles:
        # 1. calculate visibility of triangles to pivot point
        visibility = [ vecDistanceTriangle(othertriangle, pivot) > precision
                       for othertriangle in outer_vertices.iterkeys() ]
        # 2. get list of visible triangles
        visible_triangles = [ othertriangle
                              for othertriangle, visible
                              in izip(outer_vertices.iterkeys(), visibility)
                              if visible ]
        # and list of all vertices associated with visible triangles
        visible_outer = reduce(operator.add,
                               [ [ vert
                                   for dist, vert
                                   in outer_vertices[othertriangle] ]
                                 for othertriangle in visible_triangles ] )
        # 3. find all edges of visible triangles
        visible_edges = reduce(operator.add,
                               [ [ operator.itemgetter(i,j)(visible_triangle)
                                   for i, j in ((0,1),(1,2),(2,0)) ]
                                 for visible_triangle in visible_triangles ],
                               [] )
        # 4. construct horizon: edges that are not shared with another triangle
        horizon_edges = [ edge for edge in visible_edges
                          if not tuple(reversed(edge)) in visible_edges ]
        # 5. remove visible triangles from list
        # this puts a hole inside the triangle list
        for triangle in visible_triangles:
            hull_triangles.remove(triangle)
            del outer_vertices[triangle]
        # 6. close triangle list by adding cone from horizon to pivot
        # also update the outer triangle list as we go
        for edge in horizon_edges:
            newtriangle = edge + ( pivot, )
            newouter = \
                [ (dist, vert)
                  for dist, vert in izip( ( vecDistanceTriangle(newtriangle,
                                                                vert)
                                            for vert in visible_outer ),
                                          visible_outer )
                  if dist > precision ]
            hull_triangles.add(newtriangle)
            if newouter:
                outer_vertices[newtriangle] = newouter

    # no triangle has outer vertices anymore
    # so the convex hull is complete!
    # remap the triangles to indices that point into hull_vertices
    return hull_vertices, [ tuple(map(lambda vert: hull_vertices.index(vert),
                                      triangle))
                            for triangle in hull_triangles ]

if __name__ == "__main__":
    import doctest
    doctest.testmod()
