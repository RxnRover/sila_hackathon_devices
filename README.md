# sila_hackathon_devices

Concrete device servers implemented during the Device Integration Hackathon event Oct 20-22, 2026. These features should use abstract base features when possible. Each device server should be created as its own project under a `servers/<device_name>/` subdirectory.

Abstract base features should be implemented in the [sila_abstract_base_features](https://github.com/RxnRover/sila_abstract_base_features) repo.

## Design

**Computer Science Mappings**

| SiLA Concept | Computer Science Concept           |
|--------------|------------------------------------|
| ABF          | Interface/ABC                      |
| Feature      | Implementation of ABF interface(s) |
| Server       | Composition of features (device)   |
| Platform     | Composition of device servers      |

**Concept Hierarchy**

The plan is to map features, servers, and projects in the following manner:

- 1 feature -> 1 behavior/concern
- *n* features compose 1 server
- 1 server -> 1 device/platform
- 1 server -> 1 project/package/repo
- *n* servers -> 1 computer

Visualized, a hierarchy from host computer to two device servers would look like this:

```
computer
├── project1/package1/repo1
│   └── server1 -> device/platform
│       ├── feature1 -> behavior/concern
│       └── feature2 -> behavior/concern
└── project2
    └── server2 -> device/platform2
        └── feature3 -> behavior/concern
```

## Learning

- [UniteLabs CDK Documentation](https://docs.unitelabs.io/connector-development/)
- [UniteLabs Project Structure Description](https://docs.unitelabs.io/connector-development/guides/project-structure/)
- [Naming Conventions](https://docs.unitelabs.io/connector-development/reference/naming-conventions/)
- [Designing Features](https://docs.unitelabs.io/connector-development/concepts/features/)
