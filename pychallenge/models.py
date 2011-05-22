from pychallenge.utils import models

class Algorithm(models.Model):
    algorithm_id = models.PK()
    name = models.Text()
    description = models.Text()
    algorithm_type_id = models.FK('Algorithm_Type')
