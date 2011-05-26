#!/usr/bin/env python

import pychallenge
from pychallenge.models import Algorithm

if __name__ == "__main__":
    a = Algorithm(name='foo',description='foo_desc', algorithm_type_id=11)
    b = Algorithm(name='bar_name',description='bar_desc', algorithm_type_id=21)
    a.save()
    b.save()
    a.name = 'foo_name2'
    a.description = 'foo_desc2'
    a.algorithm_type_id = 12
    b.name= 'bar_name2'
    b.description = 'bar_desc2'
    b.algorithm_type_id = 22
    a.save()
    b.save()

    print(Algorithm.get(name='foo'))
    print(Algorithm.get(name='bar_name', algorithm_type_id='23'))
