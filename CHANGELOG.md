# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.2.0] - 2018-12-09
### Added
- Blink LED slowly if in config mode
- Setup menu is now split in multiple forms to avoid memory allocation issues

### Fixed
- Fixed typo in bw-shp2 pin assignment
- Fixed an issue with mqtt publishing

### Changed
- Converted to obi_socket package, hence new file structure
- Converted config file from dict to list to save memory - Please delete old config file before updating

### Removed
- Removed debug prints to save memory

## [0.1.0] - 2018-11-29
### Added
- Initial release. Will do proper changelogs from now on ;-)
