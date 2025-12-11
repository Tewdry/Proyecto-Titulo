from django.db import models

class RecomendacionIA(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(
        'App.Perfil',
        on_delete=models.CASCADE,
        db_column="PERFIL_ID",
        related_name="recomendaciones_ia"
    )

    # Rutina principal recomendada por el modelo IA
    rutina_recomendada = models.CharField(max_length=120, db_column="RUTINA_RECOMENDADA")

    # Lista top3 devuelta por la IA (JSON con nombre + probabilidad)
    top3_recomendaciones = models.JSONField(null=True, db_column="TOP3_RECOMENDACIONES")

    # Lista de ejercicios seleccionados para esa rutina (máx 8)
    ejercicios = models.JSONField(null=True, db_column="EJERCICIOS")

    # Parámetros de entrada que usó la IA (edad, BMI, objetivo, etc.)
    parametros_entrada = models.JSONField(null=True, db_column="PARAMETROS_ENTRADA")

    # Métricas del modelo (accuracy, versión IA)
    modelo_version = models.CharField(max_length=50, default="AthletIA v8", db_column="MODELO_VERSION")
    precision_modelo = models.FloatField(null=True, db_column="PRECISION_MODELO")

    # Fecha automática de la recomendación
    fecha_recomendacion = models.DateTimeField(auto_now_add=True, db_column="FECHA_RECOMENDACION")

    # Estado (por si el usuario la guarda, rechaza, etc.)
    estado = models.CharField(
        max_length=30,
        choices=[("pendiente", "Pendiente"), ("aceptada", "Aceptada"), ("rechazada", "Rechazada")],
        default="pendiente",
        db_column="ESTADO"
    )

    class Meta:
        db_table = "RECOMENDACION_IA"
        verbose_name = "Recomendación IA"
        verbose_name_plural = "Recomendaciones IA"
        ordering = ["-fecha_recomendacion"]

    def __str__(self):
        return f"{self.perfil.username} - {self.rutina_recomendada} ({self.fecha_recomendacion.date()})"
