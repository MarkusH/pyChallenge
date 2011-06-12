#!/usr/bin/env python

from pychallenge.models import Algorithm

if __name__ == "__main__":
    print Algorithm.create(dry_run=True)
    print Algorithm.query().get()
    print Algorithm.query().all()
    print Algorithm.query().all(name='name')
    print Algorithm.query().filter_or(algorithm_type_id__ge=33, name='name').all()
