# blog/serializers.py
from rest_framework import serializers
from .models import Post, Image  

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post  
        fields = '__all__'  
