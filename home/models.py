from django.db import models

# Create your models here.



class Node(models.Model):
    name = models.CharField(max_length=100)
    lat = models.FloatField()
    lng = models.FloatField()

    def __str__(self):
        return self.name
    


class Edge(models.Model):
    source = models.ForeignKey(Node, related_name='edges_from', on_delete=models.CASCADE)
    destination = models.ForeignKey(Node, related_name='edges_to', on_delete=models.CASCADE)
    weight = models.FloatField()
    is_directed = models.BooleanField(default=False)


    class Meta:
        unique_together = ('source', 'destination', 'is_directed')

    def __str__(self):
        return f"{self.source} -> {self.destination} ({self.weight})"