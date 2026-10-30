FROM python:3.13-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy the dependencies specification files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv pip install --system -r pyproject.toml

# Copy the application code
COPY . .

# Expose the default Streamlit port
EXPOSE 8501

# Run the Streamlit application
# Streamlit envoie par défaut chaque vue de page à sa télémétrie
# (webhooks.fivetran.com) : URL, navigateur et langue du visiteur. Coupé en
# ligne de commande, car app/.streamlit/config.toml n'est pas lu depuis /app.
CMD ["streamlit", "run", "app/st_main.py", "--server.port=8501", "--server.address=0.0.0.0", "--browser.gatherUsageStats=false"]
