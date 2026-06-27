FROM node:20-alpine

WORKDIR /app

# Copia manifestos primeiro para aproveitar cache de camadas.
COPY package.json package-lock.json* ./
RUN npm install

# O código é montado via volume em dev (ver docker-compose.yml).
COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
