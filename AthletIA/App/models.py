from django.db import models
from django.contrib.auth.models import AbstractUser


# =====================================================
# 1️⃣ PERFIL DE USUARIO
# =====================================================
class TipoSangre(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=50, db_column="NOMBRE")

    class Meta:
        db_table = "TIPO_SANGRE"

    def __str__(self):
        return self.nombre
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

class SaludUsuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    frecuencia_cardiaca_reposo = models.PositiveIntegerField(null=True, db_column="FRECUENCIA_CARDIACA_REPOSO")
    enfermedades_preexistentes = models.TextField(null=True, db_column="ENFERMEDADES_PREEXISTENTES")
    lesiones_actuales = models.TextField(null=True, db_column="LESIONES_ACTUALES")
    alergias = models.TextField(null=True, db_column="ALERGIAS")
    fuma = models.BooleanField(default=False, db_column="FUMA")
    bebe = models.BooleanField(default=False, db_column="BEBE")
    fecha_actualizacion = models.DateField(auto_now=True, db_column="FECHA_ACTUALIZACION")
    tipo_sangre = models.ForeignKey(TipoSangre, null=True, on_delete=models.SET_NULL, db_column="TIPO_SANGRE_ID")

    class Meta:
        db_table = "SALUD_USUARIO"


class Perfil(AbstractUser):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    telefono = models.CharField(max_length=30, null=True, db_column="TELEFONO")
    direccion = models.CharField(max_length=255, null=True, db_column="DIRECCION")
    fecha_nacimiento = models.DateField(null=True, db_column="FECHA_NACIMIENTO")
    genero = models.CharField(max_length=20, null=True, db_column="GENERO")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")
    foto = models.ImageField(upload_to="perfiles/fotos/", null=True, blank=True, db_column="FOTO")
    salud_usuario = models.ForeignKey(SaludUsuario, null=True, blank=True, on_delete=models.SET_NULL, db_column="SALUD_USUARIO_ID")

    class Meta:
        db_table = "PERFIL"

    def __str__(self):
        return self.username


# =====================================================
# 2️⃣ INTERACCIÓN SOCIAL (Publicaciones, Comentarios, Likes)
# =====================================================
class Publicacion(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    contenido = models.TextField(db_column="CONTENIDO")
    media_url = models.FileField(upload_to="publicaciones/media/", null=True, blank=True, db_column="MEDIA_URL")
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column="FECHA_CREACION")
    ultima_actualizacion = models.DateTimeField(auto_now=True, db_column="ULTIMA_ACTUALIZACION")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")

    class Meta:
        db_table = "PUBLICACION"

    def __str__(self):
        return f"{self.perfil.username} - {self.contenido[:40]}"


class Comentario(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column="PUBLICACION_ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    comentario = models.TextField(db_column="COMENTARIO")
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column="FECHA_CREACION")

    class Meta:
        db_table = "COMENTARIO"

class ComentarioReporte(models.Model):
    id = models.AutoField(primary_key=True)
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "COMENTARIO_REPORTE"



class Like(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column="PUBLICACION_ID")
    fecha = models.DateTimeField(auto_now_add=True, db_column="FECHA")

    class Meta:
        db_table = "LIKE"
        unique_together = ('perfil', 'publicacion')


class FavoritoPublicacion(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, db_column="PUBLICACION_ID")
    fecha_agregado = models.DateField(auto_now_add=True, db_column="FECHA_AGREGADO")

    class Meta:
        db_table = "FAVORITO_PUBLICACION"
        unique_together = ('perfil', 'publicacion')


# =====================================================
# 3️⃣ RED SOCIAL (Seguimiento, Notificaciones, Mensajes)
# =====================================================
class SeguimientoUsuario(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    seguidor = models.ForeignKey(Perfil, related_name='seguidos', on_delete=models.CASCADE, db_column="SEGUIDOR_ID")
    seguido = models.ForeignKey(Perfil, related_name='seguidores', on_delete=models.CASCADE, db_column="SEGUIDO_ID")
    fecha_seguimiento = models.DateField(auto_now_add=True, db_column="FECHA_SEGUIMIENTO")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")

    class Meta:
        db_table = "SEGUIMIENTO_USUARIO"
        unique_together = ('seguidor', 'seguido')


class Notificacion(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil_destino = models.ForeignKey(Perfil, related_name='notificaciones_recibidas', on_delete=models.CASCADE, db_column="PERFIL_DESTINO_ID")
    perfil_origen = models.ForeignKey(Perfil, related_name='notificaciones_enviadas', null=True, blank=True, on_delete=models.SET_NULL, db_column="PERFIL_ORIGEN_ID")
    tipo = models.CharField(max_length=50, db_column="TIPO")
    mensaje = models.CharField(max_length=255, db_column="MENSAJE")
    leida = models.BooleanField(default=False, db_column="LEIDA")
    fecha = models.DateTimeField(auto_now_add=True, db_column="FECHA")

    class Meta:
        db_table = "NOTIFICACION"

class MensajePrivado(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    emisor = models.ForeignKey(Perfil, related_name='mensajes_enviados', on_delete=models.CASCADE, db_column="EMISOR_ID")
    receptor = models.ForeignKey(Perfil, related_name='mensajes_recibidos', on_delete=models.CASCADE, db_column="RECEPTOR_ID")
    contenido = models.TextField(db_column="CONTENIDO")
    fecha_envio = models.DateTimeField(auto_now_add=True, db_column="FECHA_ENVIO")
    leido = models.BooleanField(default=False, db_column="LEIDO")

    class Meta:
        db_table = "MENSAJE_PRIVADO"


# =====================================================
# 4️⃣ GRUPOS Y COMUNIDADES
# =====================================================
class GrupoEntrenamiento(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=100, db_column="NOMBRE")
    descripcion = models.TextField(db_column="DESCRIPCION")
    perfil_creador = models.ForeignKey(Perfil, related_name='grupos_creados', on_delete=models.CASCADE, db_column="PERFIL_CREADOR_ID")
    fecha_creacion = models.DateField(auto_now_add=True, db_column="FECHA_CREACION")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")

    class Meta:
        db_table = "GRUPO_ENTRENAMIENTO"


class GrupoMiembro(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    grupo_entrenamiento = models.ForeignKey(GrupoEntrenamiento, on_delete=models.CASCADE, db_column="GRUPO_ENTRENAMIENTO_ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    rol = models.CharField(max_length=30, db_column="ROL")
    fecha_ingreso = models.DateField(auto_now_add=True, db_column="FECHA_INGRESO")
    activo = models.BooleanField(default=True, db_column="ACTIVO")

    class Meta:
        db_table = "GRUPO_MIEMBRO"


# =====================================================
# 5️⃣ PROGRESO, SALUD Y NUTRICIÓN
# =====================================================
class ProgresoUsuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    peso_kg = models.FloatField(null=True, db_column="PESO_KG")
    altura_cm = models.FloatField(null=True, db_column="ALTURA_CM")
    comentario = models.TextField(null=True, db_column="COMENTARIO")
    imc_calculado = models.FloatField(null=True, db_column="IMC_CALCULADO")
    fecha = models.DateField(auto_now_add=True, db_column="FECHA")

    class Meta:
        db_table = "PROGRESO_USUARIO"


class HistorialMedidas(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    progreso_usuario = models.ForeignKey(ProgresoUsuario, on_delete=models.CASCADE, db_column="PROGRESO_USUARIO_ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True, db_column="PERFIL_ID")
    grasa_corporal = models.FloatField(null=True, db_column="GRASA_CORPORAL")
    masa_muscular = models.FloatField(null=True, db_column="MASA_MUSCULAR")
    cintura_cm = models.FloatField(null=True, db_column="CINTURA_CM")
    cadera_cm = models.FloatField(null=True, db_column="CADERA_CM")

    class Meta:
        db_table = "HISTORIAL_MEDIDAS"


class NutricionRegistro(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    fecha = models.DateField(db_column="FECHA")
    comida = models.CharField(max_length=100, db_column="COMIDA")
    calorias = models.FloatField(null=True, db_column="CALORIAS")
    proteinas = models.FloatField(null=True, db_column="PROTEINAS")
    carbohidratos = models.FloatField(null=True, db_column="CARBOHIDRATOS")
    grasas = models.FloatField(null=True, db_column="GRASAS")
    descripcion = models.TextField(null=True, db_column="DESCRIPCION")

    class Meta:
        db_table = "NUTRICION_REGISTRO"


class SuenoUsuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    fecha = models.DateField(db_column="FECHA")
    horas_dormidas = models.FloatField(null=True, db_column="HORAS_DORMIDAS")
    calidad_sueno = models.CharField(max_length=20, null=True, db_column="CALIDAD_SUEÑO")
    despertares_nocturnos = models.PositiveIntegerField(null=True, db_column="DESPERTARES_NOCTURNOS")

    class Meta:
        db_table = "SUEÑO_USUARIO"


# =====================================================
# 6️⃣ OBJETIVOS Y PLANES
# =====================================================
class TipoObjetivo(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=50, db_column="NOMBRE")

    class Meta:
        db_table = "TIPO_OBJETIVO"

    def __str__(self):
        return self.nombre


class ObjetivoUsuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    tipo_objetivo = models.ForeignKey(TipoObjetivo, on_delete=models.CASCADE, db_column="TIPO_OBJETIVO_ID")
    meta_peso_kg = models.FloatField(null=True, db_column="META_PESO_KG")
    meta_grasa_corporal = models.FloatField(null=True, db_column="META_GRASA_CORPORAL")
    fecha_inicio = models.DateField(db_column="FECHA_INICIO")
    fecha_meta = models.DateField(null=True, db_column="FECHA_META")
    estado = models.CharField(max_length=50, db_column="ESTADO")
    activo = models.BooleanField(default=True, db_column="ACTIVO")

    class Meta:
        db_table = "OBJETIVO_USUARIO"




# =====================================================
# 7️⃣ OPINIONES Y CONTACTO
# =====================================================
class Opinion(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, db_column="PERFIL_ID")
    contenido = models.TextField(db_column="CONTENIDO")
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column="FECHA_CREACION")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")

    class Meta:
        db_table = "OPINION"


class Contacto(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    nombre = models.CharField(max_length=100, db_column="NOMBRE")
    correo = models.EmailField(db_column="CORREO")
    asunto = models.CharField(max_length=150, db_column="ASUNTO")
    mensaje = models.TextField(db_column="MENSAJE")
    fecha_envio = models.DateTimeField(auto_now_add=True, db_column="FECHA_ENVIO")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")

    class Meta:
        db_table = "CONTACTO"

class Tip(models.Model):
    id = models.BigAutoField(primary_key=True, db_column="ID")
    titulo = models.CharField(max_length=100, db_column="TITULO")
    contenido = models.TextField(db_column="CONTENIDO")
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column="FECHA_CREACION")
    vigente = models.BooleanField(default=True, db_column="VIGENTE")

    class Meta:
        db_table = "TIP"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return self.titulo
    

# =====================================================
# ESTILO DE VIDA DEL USUARIO
# =====================================================
class EstiloVidaUsuario(models.Model):
    id = models.AutoField(primary_key=True, db_column="ID")
    perfil = models.ForeignKey('App.Perfil', on_delete=models.CASCADE, db_column="PERFIL_ID")
    nivel_estres = models.CharField(max_length=30, null=True, db_column="NIVEL_ESTRES")
    horas_sueno = models.FloatField(null=True, db_column="HORAS_SUENO")
    calidad_sueno = models.CharField(max_length=20, null=True, db_column="CALIDAD_SUENO")
    alimentacion = models.CharField(max_length=50, null=True, db_column="ALIMENTACION")
    actividad_laboral = models.CharField(max_length=50, null=True, db_column="ACTIVIDAD_LABORAL")
    entorno_entrenamiento = models.CharField(max_length=50, null=True, db_column="ENTORNO_ENTRENAMIENTO")
    frecuencia_entrenamiento = models.CharField(max_length=30, null=True, db_column="FRECUENCIA_ENTRENAMIENTO")

    fecha_actualizacion = models.DateTimeField(auto_now=True, db_column="FECHA_ACTUALIZACION")

    class Meta:
        db_table = "ESTILO_VIDA_USUARIO"

    def __str__(self):
        return f"Estilo de vida de {self.perfil.username}"
