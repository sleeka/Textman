FROM nginx:1.13.1-alpine

MAINTAINER Sean A. Leeka <sleeka@swbell.net>

#ADD sites-enabled.conf /etc/nginx/conf.d/sites-enabled.conf
#COPY api_* /etc/nginx/sites-available/
#RUN mkdir -v /usr/share/nginx/{api_1,api_2}
#RUN ln -s /etc/nginx/sites-available/api_1 /etc/nginx/sites-enabled/api_1
#RUN ln -s /etc/nginx/sites-available/api_2 /etc/nginx/sites-enabled/api_2

COPY nginx.conf /etc/nginx/nginx.conf