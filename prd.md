# Historial de Versiones y Cambios del Dashboard de Arbitraje

Este documento detalla la evolución del dashboard, desde su concepción inicial hasta las versiones más recientes, incluyendo mejoras de UI/UX, funcionalidades avanzadas y correcciones de errores.

---

### **Versión 1.3 (Actual) - Estabilización y Toques Finales**

Esta versión se centró en resolver errores críticos de ejecución, mejorar la robustez y aplicar los últimos detalles de personalización.

**Corrección de Errores Críticos:**
- **`AttributeError: module 'streamlit' has no attribute 'experimental_rerun'`**: Se actualizó la llamada `st.experimental_rerun()` (obsoleta) a la nueva sintaxis `st.rerun()`, restaurando la funcionalidad de auto-refresco.
- **`Error connecting to [exchange]: There is no current event loop...`**: Se implementó una gestión robusta del bucle de eventos de `asyncio` para garantizar que siempre esté disponible en el hilo de ejecución de Streamlit, eliminando los fallos de conexión asíncrona.
- **`UserWarning: pandas only supports SQLAlchemy connectable...`**: Se reemplazó la conexión directa `psycopg2` por `SQLAlchemy` en el módulo `database.py` para seguir las mejores prácticas de `pandas` y eliminar las advertencias.
- **Logo no se mostraba**: Se solucionó el problema de visualización del logo. Ahora la imagen se descarga desde la URL, se codifica en Base64 y se incrusta directamente en el HTML, asegurando su correcta visualización en todo momento.

**Mejoras y Personalización:**
- **Lista de Exchanges Ampliada**: Se actualizó el selector para incluir más de 100 exchanges, según lo solicitado.
- **Métrica de Ganancia en Verde**: El color del porcentaje de la métrica de ganancia se cambió a verde para una señal visual más clara.
- **Firma y Disclaimer**: Se añadió el logo de "Made by CryptoPlaza" en el pie de página y se actualizó el texto del disclaimer con una versión más completa y profesional.

---

### **Versión 1.2 - Integración con Base de Datos PostgreSQL**

Esta versión transformó el dashboard de una herramienta de monitoreo en tiempo real a una plataforma con capacidad de análisis histórico.

**Arquitectura de Datos:**
- **Persistencia en PostgreSQL**: Se eliminó el almacenamiento de historial en `st.session_state` y se reemplazó por una base de datos PostgreSQL para persistencia de datos a largo plazo.
- **Módulo `database.py`**: Se creó un nuevo módulo para encapsular toda la lógica de la base de datos (conexión, inicialización y operaciones CRUD).
- **Esquema de Base de Datos Robusto**: Se diseñó un esquema con dos tablas:
    1.  `arbitrage_runs`: Almacena cada ejecución de arbitraje (exchange, profit, timestamp).
    2.  `trade_steps`: Almacena cada paso individual de una oportunidad, vinculado a una ejecución por `run_id`.
- **Gestión Segura de Credenciales**: Se creó un archivo `.env` para almacenar la URL de la base de datos de forma segura, y se añadió al `.gitignore` para evitar la exposición de credenciales.
- **Dependencias Actualizadas**: Se añadieron `psycopg2-binary`, `python-dotenv` y `SQLAlchemy` al archivo `requirements.txt`.

---

### **Versión 1.1 - Mejoras Avanzadas de UI/UX**

Basado en una evaluación de ingeniería senior, esta versión introdujo mejoras funcionales para elevar la calidad del dashboard.

**Mejoras Funcionales:**
- **Gráfico de Tendencia de Ganancias**: Se reemplazó el historial de texto por un gráfico de líneas (`sparkline chart`) que muestra la evolución del profit en las últimas 100 detecciones.
- **Indicador de Latencia**: El timestamp de "Última actualización" se hizo dinámico, cambiando de color (verde → naranja → rojo) según la antigüedad de los datos para indicar el riesgo.
- **Tarjetas de Operación Enriquecidas**: Se añadió el par de mercado específico (ej. `BTC/USDT`) a cada tarjeta para mayor claridad.

---

### **Versión 1.0 - Rediseño Inicial y Modernización de UI/UX**

Esta fue la primera gran refactorización, transformando la aplicación de una simple tabla de datos a un dashboard interactivo y moderno.

**Cambios Clave:**
- **Layout Moderno**: Se adoptó un tema oscuro y se movieron todos los controles (selector de exchange, botón de refresco) a una barra lateral (`sidebar`).
- **Diseño Basado en Tarjetas**: Se reemplazó la tabla de datos por tarjetas individuales para cada paso de la operación, usando colores (verde para compra, rojo para venta) para una fácil interpretación.
- **Foco en la Métrica Principal**: Se introdujo `st.metric` para destacar la oportunidad de ganancia estimada como el dato más importante del dashboard.
- **Funcionalidad de Auto-Refresco**: Se implementó la primera versión de la funcionalidad de auto-actualización.
