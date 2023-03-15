FROM php:7.2-cli
# Evgenii Sopov <mrseakg@gmail.com>

ADD www /root/www
RUN chmod 777 /root/www/lnks

EXPOSE 3154

CMD cd /root/ && php -S 0.0.0.0:3154 -t www