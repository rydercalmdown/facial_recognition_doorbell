# Facial Recognition Doorbell
This project expands on the person-detecting doorbell system to allow it to identify faces, and announce names accordingly.


## Installation
To install, clone this repository to your raspberry pi, descend into it, and use the following command:

```bash
make install
```

## Architecture
This project is based off the person-detecting doorbell. At its most basic it will always ring the doorbell if a person is present. When a person is present, it will check their faces against known faces. If the person is known, they will be announced. If not, the doorbell will still ring normally.
