# Configs

# Configs

System-wide configurations mounted into worker docker containers.

## Types

Types contains the 'type' and 'detail' signatures to mapping a file to a type. The types (values in the k,v pair) are mapped to routing_keys in RabbitMQ.

```json
"application/x-dosexec":"pe",
```

A file matching the above mimetype would be analyzed by all modules handling the "pe" type.

## OrientDB

## Rabbitmq

## Paths