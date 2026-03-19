FROM python:3.13-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Dependencies ni alohida layer qilamiz (cache uchun)
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Loyiha fayllarini ko'chiramiz (.env ni COPY qilmaymiz)
COPY . .

# DB uchun volume directory
RUN mkdir -p /app/data

# Run the bot
CMD ["uv", "run", "python", "app.py"]
