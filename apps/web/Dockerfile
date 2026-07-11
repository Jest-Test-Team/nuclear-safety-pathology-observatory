FROM nginx:1.27-alpine
COPY apps/web/nginx.conf /etc/nginx/conf.d/default.conf
COPY apps/web/index.html apps/web/styles.css apps/web/app.js apps/web/labels.json /usr/share/nginx/html/
# Same-origin API via nginx proxy (OCI sidecar / compose). Override with window.NSPO_API if needed.
RUN printf 'window.NSPO_API = window.NSPO_API || "";\n' > /usr/share/nginx/html/config.js
RUN sed -i 's#</head>#  <script src="config.js"></script>\n</head>#' /usr/share/nginx/html/index.html
EXPOSE 80
