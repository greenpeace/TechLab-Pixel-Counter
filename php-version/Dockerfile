FROM composer:2 as composer
# PHP + Apache
FROM php:8.0-apache

# Update OS and install common dev tools
# hadolint ignore=DL3008
RUN apt-get update \
	&& apt-get install --no-install-recommends -y wget vim git zip unzip zlib1g-dev libzip-dev libpng-dev cron \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# hadolint ignore=SC2046
RUN docker-php-ext-install -j$(nproc) mysqli pdo_mysql gd zip pcntl exif

# Enable common Apache modules
RUN a2enmod headers expires rewrite

# Install Composer
COPY --from=composer /usr/bin/composer /usr/local/bin/composer

# Set working directory to web files
WORKDIR /var/www/html

# Copy vhosts
COPY --chown=www-data ./docker/apache/vhosts.conf /etc/apache2/sites-available/000-default.conf
COPY --chown=www-data ./docker/apache/apache2.conf /etc/apache2/apache2.conf
# Copy local.ini
COPY --chown=www-data ./docker/php/local.ini /usr/local/etc/php/conf.d/local.ini
COPY --chown=www-data ./database.php /var/www/html/app/config/database.php
# Copy crontab
COPY --chmod=0644 ./docker/cron/emily-crontab /etc/cron.d/emily-crontab
RUN crontab /etc/cron.d/emily-crontab
# Copy emily application
COPY --chown=www-data . .
RUN mv app/core/My_Log.php.disabled app/core/My_Log.php
RUN usermod -u 1000 www-data \
	&& groupmod -g 1000 www-data

COPY --chmod=770 ./docker/entrypoint.sh entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
CMD ["apache2-foreground"]
