# Clasificador de Tickets con IA

Sistema inteligente de clasificación automática de tickets de soporte utilizando Machine Learning y Streamlit.

---

# Instalación

## 1. Clonar el repositorio

```bash
git clone https://github.com/Rodrigo110620/clasificador_tickets.git
cd clasificador_tickets
```

---

# Linux 

## Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Entrenar el modelo

```bash
python train_model.py
```

## Ejecutar la aplicación

```bash
streamlit run app.py
```

---

# Windows

## Crear entorno virtual

```bash
python -m venv venv
venv\Scripts\activate
```

## Instalar dependencias

```bash
pip install -r requirements.txt
```

## Entrenar el modelo

```bash
python train_model.py
```

## Ejecutar la aplicación

```bash
streamlit run app.py
```

---

# Tecnologías utilizadas

- Python
- Streamlit
- Scikit-learn
- Pandas
- NumPy

---

# Funcionalidades

- Clasificación automática de tickets
- Entrenamiento de modelos IA
- Visualización de métricas
- Interfaz moderna con Streamlit
- Gestión de categorías de soporte

---

# Estructura del proyecto

```text
clasificador_tickets/
│
├── dataset/
├── services/
├── ui/
├── config/
├── models/
├── app.py
├── train_model.py
├── preprocess.py
├── requirements.txt
└── README.md
```
