from django.db import models


# =====================================================
# 1️⃣ BASES DE EJERCICIOS
# =====================================================
class Musculo(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=50, unique=True, db_column="NOMBRE")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "MUSCULO"


class TipoEjercicio(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=50, unique=True, db_column="NOMBRE")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "TIPO_EJERCICIO"


class NivelDificultad(models.Model):
    dificultad_id = models.AutoField(primary_key=True, db_column="DIFICULTAD_ID")
    nombre = models.CharField(max_length=30, db_column="NOMBRE")
    descripcion = models.TextField(db_column="DESCRIPCION")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "NIVEL_DIFICULTAD"


# =====================================================
# 2️⃣ EJERCICIOS
# =====================================================
class Ejercicio(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=100, db_column="NOMBRE")
    descripcion = models.TextField(db_column="DESCRIPCION")
    video_url = models.FileField(upload_to="ejercicios/gifs/", null=True, blank=True, db_column="VIDEO_URL")
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column="FECHA_CREACION")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")
    

    tipo_ejercicio = models.ForeignKey(TipoEjercicio, on_delete=models.CASCADE, db_column="TIPO_EJERCICIO_ID")
    musculo = models.ForeignKey(Musculo, on_delete=models.CASCADE, db_column="MUSCULO_ID")

    nivel_dificultad = models.ForeignKey(
        NivelDificultad,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="NIVEL_DIFICULTAD_ID"
    )

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "EJERCICIO"


# =====================================================
# 3️⃣ RUTINAS Y ASIGNACIÓN DE EJERCICIOS
# =====================================================
class Rutina(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=100, db_column="NOMBRE")
    descripcion = models.TextField(null=True, db_column="DESCRIPCION")
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column="FECHA_CREACION")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")

    perfil = models.ForeignKey('App.Perfil', on_delete=models.CASCADE, db_column="PERFIL_ID")
    nivel_dificultad = models.ForeignKey(NivelDificultad, on_delete=models.PROTECT, db_column="NIVEL_DIFICULTAD_DIFICULTAD_ID")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = "RUTINA"


class RutinaGuardada(models.Model):
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name="guardadas")
    perfil = models.ForeignKey("App.Perfil", on_delete=models.CASCADE, related_name="rutinas_guardadas")
    fecha_guardado = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("rutina", "perfil")

    def __str__(self):
        return f"{self.perfil.username} → {self.rutina.nombre}"



class RutinaEjercicio(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, db_column="RUTINA_ID")
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, db_column="EJERCICIO_ID")
    repeticiones = models.PositiveIntegerField(null=True, db_column="REPETICIONES")
    orden = models.PositiveIntegerField(null=True, db_column="ORDEN")

    class Meta:
        db_table = "RUTINA_EJERCICIO"


# =====================================================
# 4️⃣ PROGRESO DE EJERCICIOS
# =====================================================
class ProgresoEjercicio(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey('App.Perfil', on_delete=models.CASCADE, db_column="PERFIL_ID")
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, db_column="EJERCICIO_ID")
    fecha = models.DateField(auto_now_add=True, db_column="FECHA")
    repeticiones_realizadas = models.PositiveIntegerField(null=True, db_column="REPETICIONES_REALIZADAS")
    peso_usado = models.FloatField(null=True, db_column="PESO_USADO")
    duracion_minutos = models.FloatField(null=True, db_column="DURACION_MINUTOS")

    class Meta:
        db_table = "PROGRESO_EJERCICIO"

# =====================================================
# 5️⃣ CALENDARIO DE RUTINAS
# =====================================================
class CalendarioRutina(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey('App.Perfil', on_delete=models.CASCADE, db_column="PERFIL_ID")
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, db_column="RUTINA_ID")
    fecha = models.DateField(db_column="FECHA")
    hora = models.TimeField(null=True, blank=True, db_column="HORA")
    completada = models.BooleanField(default=False, db_column="COMPLETADA")
    notas = models.TextField(null=True, blank=True, db_column="NOTAS")

    def __str__(self):
        return f"{self.perfil.username} - {self.rutina.nombre} ({self.fecha})"

    class Meta:
        db_table = "CALENDARIO_RUTINA"
        unique_together = ('perfil', 'rutina', 'fecha')