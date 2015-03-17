from rest_framework import generics

# Create your views here.
from rest_framework import serializers
from urqa.models import Projects


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects

class ProjectList(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer


class ProjectDetail(generics.RetrieveUpdateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer


