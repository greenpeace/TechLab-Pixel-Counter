# API for a pixel-based petition counter

Server API for the [multi-organization petition counter](https://github.com/greenpeace/gpes-multi-organizations-counter-front). Although you should **run your own tests in your own server with your capacity**, this API should work fine for 10 signups and around 100 page views per second. Upgrading your hardware or reconfiguring your server will affect it's capacity.

## Upload this API script

Upload the content of this repo to a folder in your server. The idea is to be able to access it in `https://sub.domain.org/counter-name/`

* It needs a PHP/MySQL server but it also supports other databases.
* It's required to use https and recommended to set up a subdomain for all your counters.
* Don't upload the `.git` folder or the `README.md` file.

## Configure the database

### Create a database

Preferably MySQL but any [Medoo supported database](https://medoo.in/api/new) will do.

### Initialization script

If it's MySQL run the following initialization SQL script to create the table and add an example counter

```sql
START TRANSACTION;
SET time_zone = "+00:00";
CREATE TABLE `counters` (
  `counter_name` varchar(255) CHARACTER SET latin1 COLLATE latin1_general_ci NOT NULL,
  `counter_value` int NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1 COLLATE=latin1_general_ci;
INSERT INTO `counters` (`counter_name`, `counter_value`) VALUES
('example', 0);
COMMIT;
```

## API config

First, Rename `config.php.dist` to `config.php`.

Edit `config.php` and configure the database settings.

## Add another counter

You can run multiple counters in the same database by uploading multiple scripts to different folders after editing this line: `define('COUNTER_NAME', 'example');` in `config.php` and inserting another row in the `counters` table with the new counter name.

You can use the following SQL to create the `example2` counter:

```sql
INSERT INTO `counters` (`counter_name`, `counter_value`) VALUES
('example2', 0);
```

## Insert the counters in your websites

For more information visit the [frontend repository](https://github.com/greenpeace/gpes-multi-organizations-counter-front) where you can find an **example** on how to add counters to your site.
