import os
import importlib.util
from core.config import PLUGINS_DIR

class PluginManager:
    def __init__(self):
        self.plugins = {}

    def load_plugins(self):
        for item in os.listdir(PLUGINS_DIR):
            plugin_path = PLUGINS_DIR / item
            if plugin_path.is_dir() and (plugin_path / "main.py").exists():
                self._load_plugin(item, plugin_path / "main.py")

    def _load_plugin(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, "setup"):
            self.plugins[name] = module.setup()

    def execute_plugin(self, name, *args, **kwargs):
        if name in self.plugins:
            return self.plugins[name].run(*args, **kwargs)
        return f"Plugin {name} not found."
