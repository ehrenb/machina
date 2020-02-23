# Models

Models are used to specify what data are extracted by a worker to be inserted into the database. A Model can be represent any time of data extracted from a file or binary blob that you want to track.  Examples include:

* Indicators (URL, IP Address)
* The file itself (e.g. an exe file)
* Memory dumps produced by dynamic analysis
* Etc 

# Relationships

Relationships are used to define connections between Node models.  For example, analyzing an APK will result in many other files being extracted from its structure, and thus those files get created as nodes, and get an edge to the APK labeled as "Extracted"