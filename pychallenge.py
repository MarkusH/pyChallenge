#!/usr/bin/env python

from pychallenge.models import Algorithm

if __name__ == "__main__":
    a = Algorithm(name='test', description='test', algorithm_type_id=11)
    b = Algorithm(name='bar_name', description='bar_desc',
            algorithm_type_id=21)
    a.save()
    b.save()
    b.name = 'bar_name2'
    b.description = 'bar_desc2'
    b.algorithm_type_id = 22
    b.save()

    print(Algorithm.query(name='foo'))
    print(Algorithm.get(name='test', description='test'))
    a.delete()
    print(Algorithm.get(name='test', description='test'))
    print(Algorithm.query(name='bar_name2'))
    for instance in Algorithm.query(name='bar_name2'):
        instance.delete()
    print(Algorithm.query(name='bar_name2'))
