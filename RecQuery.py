#!/usr/bin/env python
"""
implementation of the sqlalchemy query method
"""

from sqlalchemy.orm.query import Query
try:
    from numpy import recarray
except ImportError:
    raise("You must have numpy installed for this recipe to work")


class RecQuery(Query):
    """
    A re-implementation of sqlalchemy's Query object to add the get_array method to obtain
    a numpy.recarray object as a result of a query.

    Examples:
    >>> results = Table.query.all()
    standard sqlalchemy results
    >>> results = Table.query.as_recarray()
    returns a recarray object
    >>> results['column1']
    contents of column 1
    >>> results[0]
    first row in results
    """





if __name__ == '__main__':
    pass

