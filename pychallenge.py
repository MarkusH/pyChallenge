#!/usr/bin/env python

import pychallenge
from pychallenge.models import Algorithm

a = Algorithm(name='name',description='desc', algorithm_type_id=23 )
a.save()
a.__meta__['fields']['name'].set_value('test')
a.save()
