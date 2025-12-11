# AthletIA – Plataforma Inteligente de Gestión de Rutinas

![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)
![Django](https://img.shields.io/badge/Django-Framework-092E20?style=for-the-badge&logo=django)
![TensorFlow](https://img.shields.io/badge/TensorFlow-ML-FF6F00?style=for-the-badge&logo=tensorflow)
![Azure](https://img.shields.io/badge/Azure-Cloud-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-Database-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**AthletIA** es una plataforma web inteligente diseñada para revolucionar la experiencia deportiva. Integra un gestor avanzado de rutinas, calendarios interactivos, seguimiento de progreso y módulos sociales, todo envuelto en una identidad visual futurista basada en **Glassmorphism**.

El núcleo del proyecto combina la robustez de **Django** con la potencia del **Machine Learning** para ofrecer personalización real a sus usuarios.

---

## 📋 Descripción General

AthletIA está construida como un ecosistema deportivo completo para usuarios que buscan eficiencia, organización y un seguimiento detallado de su rendimiento físico.

**La plataforma permite a los usuarios:**
- Crear, gestionar y visualizar rutinas de entrenamiento.
- Organizar sus sesiones en un calendario interactivo.
- Llevar un seguimiento detallado de su progreso físico.
- **Recibir recomendaciones automáticas** de rutinas gracias a una IA integrada.
- Interactuar socialmente (likes, comentarios, grupos).
- Comunicarse vía mensajería privada.

---

## 🚀 Características Principales

### 1. Gestor de Rutinas
- Creación y edición de rutinas 100% personalizadas.
- Asignación detallada de ejercicios, repeticiones, series y tiempos de descanso.
- Organización visual intuitiva en vistas semanales o mensuales.

### 2. Calendario Interactivo
- Integración completa con **FullCalendar**.
- Gestión de eventos dinámicos: registro de días entrenados y días pendientes.
- Edición rápida de sesiones mediante modales interactivos.

### 3. Seguimiento de Progreso
- Registro histórico de métricas por ejercicio.
- Visualización de datos mediante gráficos dinámicos con **Chart.js**.
- Dashboard principal con estadísticas personales y KPIs de rendimiento.

### 4. Inteligencia Artificial – AthletIA
El corazón inteligente del sistema.
- **Modelo:** Red Neuronal.
- **Entrenamiento:** Entrenado con un dataset de **200.000 registros sintéticos**.
- **Funcionalidad:** Analiza el perfil del usuario y recomienda el **Top 3 de rutinas** más probables y efectivas para sus objetivos.

### 5. Módulo Social
- Feed de publicaciones con soporte para imágenes y texto.
- Interacciones sociales: Likes, comentarios y sistema de favoritos.
- Creación de grupos de entrenamiento y muros colaborativos.

### 6. Mensajería Privada
- Sistema de chat interno tipo "bandeja de entrada".
- Conversaciones privadas ordenadas por usuario para facilitar la comunicación.

---

## 🎨 Identidad Visual (UI/UX)

AthletIA destaca por su interfaz moderna y minimalista, utilizando un estilo **Glassmorphism Oscuro** que transmite tecnología y dinamismo.

| Color | Hex | Uso |
| :--- | :--- | :--- |
| **Cyan Neon** | `#25e2d7` | Color Primario / Acentos |
| **Soft Cyan** | `#5ff5e5` | Variación Suave / Hover |
| **Ice White** | `#e8fdf8` | Texto Claro / Contenido |

---

## 🛠️ Tecnologías Utilizadas

### Backend
- **Lenguaje:** Python 3
- **Framework Web:** Django
- **Base de Datos:** MySQL
- **Machine Learning:**
  - TensorFlow / Keras
  - scikit-learn

### Frontend
- **Estructura y Estilo:** HTML5, CSS3 (Glassmorphism design)
- **Lógica:** JavaScript (ES6+)
- **Librerías:**
  - [FullCalendar](https://fullcalendar.io/) (Gestión de fechas)
  - [Chart.js](https://www.chartjs.org/) (Visualización de datos)
  - [SweetAlert2](https://sweetalert2.github.io/) (Alertas modales)

---

## 🔧 Instalación y Configuración

Sigue estos pasos para levantar el proyecto en local:

1. **Clonar el repositorio**
   ```bash
   git clone [https://github.com/tu-usuario/athletia.git](https://github.com/tu-usuario/athletia.git)
   cd athletia
   pip install -r requirements.txt
   py manage.py runserver
