FROM node:18-alpine

WORKDIR /app

COPY package*.json ./

RUN npm ci
RUN npm rebuild esbuild

COPY . .

RUN npm run build

RUN npm install -g serve

EXPOSE 5173

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5173 || exit 1

CMD ["serve", "-s", "dist", "-l", "5173", "--cors", "--no-clipboard", "--single"]