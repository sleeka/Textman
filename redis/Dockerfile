FROM redis:3.0.7-alpine

MAINTAINER Sean A. Leeka <sleeka@swbell.net>

EXPOSE 6379

#COPY redis.conf /usr/local/etc/redis/redis.conf

CMD ["redis-server", "--save ''"] #, "/usr/local/etc/redis/redis.conf"]

#ENTRYPOINT ["redis-cli set global_message_id 0"]
#COPY ./docker-entrypoint.sh /
#ENTRYPOINT ["/docker-entrypoint.sh"]

