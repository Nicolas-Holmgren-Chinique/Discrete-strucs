from django.db import models

# Create your models here.
"""
These arent really relevant right now as nodes and edges are currently hardcoded in views.py but kept for future use
"""

# this is the model for the nodes in the graph with name and latitude and longitude fields, we aren't using it currently but it's here for future use and was previously used in earlier versions of the project
class Node(models.Model):
    name = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.name
    

# same goes for the edges had earlier but nodes and edges are hardcoded in the views.py for now
class Edge(models.Model):
    source = models.ForeignKey(Node, related_name='edges_from', on_delete=models.CASCADE)
    destination = models.ForeignKey(Node, related_name='edges_to', on_delete=models.CASCADE)
    weight = models.FloatField()
    is_directed = models.BooleanField(default=False)


    class Meta:
        unique_together = ('source', 'destination', 'is_directed')

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.weight})"