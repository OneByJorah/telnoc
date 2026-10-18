# Changelog
## [0.1.1](https://github.com/OneByJorah/telnoc/compare/v0.1.0...v0.1.1) (2026-10-18)


### Bug Fixes

* **audit:** add standard project files ([8d0d9be](https://github.com/OneByJorah/telnoc/commit/8d0d9bedf578fc859419726f36d4ba1f1e0c4f30))
* **ci:** make the flake8 lint step pass ([#39](https://github.com/OneByJorah/telnoc/issues/39)) ([dd87b28](https://github.com/OneByJorah/telnoc/commit/dd87b2813a6a69847a96182a6499dc8127ed4b3f))
* **compose:** bind published ports to localhost only ([#38](https://github.com/OneByJorah/telnoc/issues/38)) ([4be2e61](https://github.com/OneByJorah/telnoc/commit/4be2e6125093ba844419a92ce9652bdd0b6f385c))
* rename misnamed agent.py (compose file) to docker-compose.yml ([7ee729e](https://github.com/OneByJorah/telnoc/commit/7ee729e334d904978ed0a6b38f838fb315925eb7))
* resolve container boot issues — entrypoint TTY detection, SQLAlchemy URI, non-root permissions ([95a5da7](https://github.com/OneByJorah/telnoc/commit/95a5da701d0e83f44080611159cdfd937d44ad98))

## [1.0.0] - 2026-07-07
### Added
- Initial release
- Dockerfile improvements
- .env.example with placeholder values
- First-run setup wizard / docker-entrypoint.sh
