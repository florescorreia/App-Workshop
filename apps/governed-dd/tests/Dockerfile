FROM mcr.microsoft.com/playwright:v1.63.0-noble
WORKDIR /checks
RUN npm install --ignore-scripts playwright@1.63.0
COPY tests/*.cjs ./
ENV NODE_PATH=/checks/node_modules
ENTRYPOINT ["node"]
