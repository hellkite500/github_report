# github_report

Use the GitHub Event API to summarize GitHub activity in recent history.

# Usage
Simply create a configuration file, an example is provided in [example_config.yaml](example_config.yaml) and pass it to the module.

```python -m github_report --config-yaml config.yaml```

If `--config-yaml ` is not passed, will look for `config.yaml` in the current working directory.  