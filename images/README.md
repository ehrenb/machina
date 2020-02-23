# Module Development

## Notable worker modules

### Identifier

Entrypoint to the system - determines a type for the input data and tags it, triggering other modules to fire that support that tagged type

## How to develop new worker modules

### Dockerfile

* Base image should be "machina/base-alpine3" OR "machina/base-ubuntu18"
    - An alpine base is preferred, because it is lighter
    - The ubuntu base makes dependency installation easier, but can increase image size
* Install any system requirements needed for the worker module you are creating

### Requirements.txt

* Put any Python 3 requirements required by your worker module into requirements.txt and ensure that you copy requirements.txt into the image and 'pip install -r requirements.txt' to install the dependencies

### module.py

* Subclass the machina.core.worker.Worker class, this will ensure your worker module has connectivity to the Database, RabbitMQ, and configurations
* Specify the Machina types (see configs/types.json) your worker module supports, or specify '*' for all
* Ensure that you import your worker module class into machina.core.worker module so that its schema gets automatically created in the database at startup

#### types

Your worker's 'types' must consist of at least one of the available_types in the types.json config. or '*'

E.g.

```python
class ZipAnalyzer(Worker):
    types = ["zip"] #This worker can handle data typed as 'zip'

    def __init__(self, *args, **kwargs):
        super(ZipAnalyzer, self).__init__(*args, **kwargs)
```

### Schema

Schemas are used to validate incoming data to the worker. Schema names must match the class name that they belong to, e.g. for the worker module 'AndroguardAnalysis', there must exist a schema in the schemas directory names 'AndroguardAnalysis.json'

Typically, since workers are handling data published by the Identifier, they inherit from the 'binary.json' schema.   

### Database

## Insertions

Worker modules are not supposed to create new objects (e.g. files, binary data) in the database directly, only update elements or create edges (relationships).  They should publish any extracted data of interest to the Identifier queue so that it re-enters the pipeline, e.g.:

```python
channel.basic_publish(exchange='machina',
                           routing_key='Identifier',
                           body=json.dumps(body))
``` 

## Updates

When updating elements in the database, it is highly recommended to use the the Worker base class' update_node or create_edge functions.  These functions attempt to avoid updating a stale/out-of-date handle to a database element. 


### Configuration

Your worker module must have a configuration file in in the project's root directory (/machina/configs/workers/XAnalysis.json).  If your module has no configurations, make the configuration like below.  

XAnalysis.json
```json
{}
```

Otherwise, specify a configuration you need to access from the worker module, e.g.

XAnalysis.json
```json
{
    "hash_algorithms": ["md5", "sha256"]
}
```

You can then access the worker-specific configuration in your worker class module class using the 'worker' dictionary in self.config:

```python
class XAnalysis(Worker):
    types = ['*']
    ...
    def callback(self, data, properties):
        self.logger.info(self.config['worker']['hash_algorithms'])
```

## Notes

### Retyping

Sometimes, obscure or less standard filetypes cannot be identified with cursory static analysis.  Sometimes it requires a bit of context, e.g. an Android APK is technically a zip file, and can only really be identified by peering into the zip and searching for common APK files.  Only then can we retype the binary as an APK. This burden should be on the zip module to discover, not the identifier.

The snippet below is an example of when the Zip analysis module detects that it is actually working on an APK.  The Zip module resubmits most of the same data that consumed from the queue, except it manually specifies the 'type' to 'apk', which the Identifier will take at face value.

```python
body = {
        "data": data_encoded,
        "origin": {
            "ts": data['ts'],
            "md5": data['hashes']['md5'],
            "id": data['id'], #I think this is the only field needed, we can grab the unique node based on id alone
            "type": data['type']},
        'type': 'apk'}

channel = self.get_channel(self.config['rabbitmq'])
channel.basic_publish(exchange='machina',
                       routing_key='Identifier',
                       body=json.dumps(body))
```  


## Future modules

* ssdeep (in identifier)
* PCAP - Extract files, and ip+ports and create "entities"
 that can be used to link communications to other nodes (e.g. a dynamic analysis of binary b1 produces a pcap, which contains a hostname that is also found in another binary, b3. We can make a link that connects b1 and b2 via the hostname entity)
* Images (PNG,JPEG) - steganography
* APKid
* PEid
* lief
* Relays to other services (Cuckoo, VT, Hybrid Analysis)