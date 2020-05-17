# Configs

# Configs

System-wide configurations mounted into worker docker containers.

## Types

Types contains the 'type' and 'detail' signatures to mapping a file to a type. 
* The types (values in the k,v pair) are given routing_keys in RabbitMQ
* Worker modules' 'type' attribute defines what routing_keys the module will bind to
* OrientDB Node class' 'element_name' attribute is coupled to a 'type'
    * Worker parent class 'resolve_db_node_cls()' can be used to resolve the specific type Node handle
    given a 'type' string (e.g. resolve_db_node_cls('apk') will return the OrientDB Node class, 'APK')

```json
"application/x-dosexec":"pe",
```

A file matching the above mimetype would be analyzed by all modules handling the "pe" type.

## OrientDB

## Rabbitmq

## Paths