from rest_framework import serializers
from api_ejercicio.models import*

class MusculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Musculo
        fields = '__all__'

class TipoEjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoEjercicio
        fields = '__all__'

class NivelDificultadSerializer(serializers.ModelSerializer):
    class Meta:
        model = NivelDificultad
        fields = '__all__'

class EjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ejercicio
        fields = '__all__'

class RutinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rutina
        fields = '__all__'

class RutinaEjercicioSerializer(serializers.ModelSerializer):
    class Meta:
        model = RutinaEjercicio
        fields = '__all__'