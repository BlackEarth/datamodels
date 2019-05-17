# datamodels

The datamodels package builds on dataclasses and adds the following functionality:

* `.dict()` instance method – returns a dict of the data, making it simple to serialize to formats like JSON or YAML.
* `.from_data()` class method – create a new instance by passing in an iterable key-value data source (such as a dict). Unlike the regular constructor, this only uses the values in the input data that match fields in the model — others are ignored. This is useful for pulling model data out of a larger data source.
* `@validator` decorator to specify data validation methods.
* `.validate()` class method – runs the attribute validator methods and returns a `dict` with the fields that have errors as keys and a list of errors as the values.

The datamodels package is inspired by prior art: Django models and forms, the attrs package by which dataclasses was inspired, and the XML world, where schemas and data validation form a key part of production workflows.

Installation:

```bash
pip install datamodels
```



