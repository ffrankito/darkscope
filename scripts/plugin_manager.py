#!/usr/bin/env python3
"""
DarkScope plugin system for custom security checks.
Allows teams to extend DarkScope with organization-specific probes.
"""

import importlib.util
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Any, Optional

class DarkScopePlugin(ABC):
    """Base class for DarkScope plugins"""

    # Override these in subclasses
    name: str = "Unnamed Plugin"
    description: str = "No description"
    level_required: int = 2  # Minimum assessment level to run this plugin
    version: str = "1.0.0"

    @abstractmethod
    def run(self, target: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Execute plugin and return findings.

        Args:
            target: Target URL or system
            **kwargs: Additional context (auth, previous_findings, etc.)

        Returns:
            List of finding dicts with keys: title, severity, evidence, recommendation
        """
        pass

    def validate(self) -> bool:
        """Validate plugin is ready to run"""
        return True

    def cleanup(self):
        """Cleanup resources after plugin execution"""
        pass


class PluginManager:
    """Manage loading and executing DarkScope plugins"""

    def __init__(self, plugins_dir: Optional[Path] = None):
        self.plugins_dir = plugins_dir or Path('./plugins')
        self.plugins: Dict[str, DarkScopePlugin] = {}
        self.load_all()

    def load_all(self):
        """Load all plugins from plugins directory"""
        if not self.plugins_dir.exists():
            print(f"ℹ️  No plugins directory found at {self.plugins_dir}")
            return

        for plugin_file in self.plugins_dir.glob('*.py'):
            if plugin_file.name.startswith('_'):
                continue

            self.load_plugin(plugin_file)

    def load_plugin(self, plugin_file: Path) -> bool:
        """Load a single plugin from a file"""
        try:
            spec = importlib.util.spec_from_file_location(
                plugin_file.stem,
                plugin_file
            )
            if not spec or not spec.loader:
                print(f"❌ Failed to load {plugin_file.name}")
                return False

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # Find DarkScopePlugin subclasses in module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and
                    issubclass(attr, DarkScopePlugin) and
                    attr is not DarkScopePlugin):

                    instance = attr()
                    if instance.validate():
                        self.plugins[instance.name] = instance
                        print(f"✅ Loaded plugin: {instance.name} (v{instance.version})")
                        return True

            print(f"⚠️  No valid plugin found in {plugin_file.name}")
            return False

        except Exception as e:
            print(f"❌ Error loading {plugin_file.name}: {e}")
            return False

    def get_plugins_for_level(self, level: int) -> List[DarkScopePlugin]:
        """Get all plugins applicable for assessment level"""
        return [p for p in self.plugins.values() if p.level_required <= level]

    def run_all(self, target: str, level: int, **kwargs) -> List[Dict[str, Any]]:
        """Run all applicable plugins and return combined findings"""
        findings = []
        applicable_plugins = self.get_plugins_for_level(level)

        print(f"\n🔌 Running {len(applicable_plugins)} plugins...\n")

        for plugin in applicable_plugins:
            try:
                print(f"  ▶ {plugin.name}...", end=' ', flush=True)
                plugin_findings = plugin.run(target, **kwargs)
                findings.extend(plugin_findings)
                print(f"✅ ({len(plugin_findings)} findings)")
            except Exception as e:
                print(f"❌ Error: {e}")
            finally:
                plugin.cleanup()

        return findings

    def list_plugins(self) -> str:
        """List available plugins"""
        if not self.plugins:
            return "No plugins installed."

        output = "Installed Plugins:\n"
        output += "=" * 60 + "\n"

        for name, plugin in sorted(self.plugins.items()):
            output += f"  {name}\n"
            output += f"    Description: {plugin.description}\n"
            output += f"    Version: {plugin.version}\n"
            output += f"    Min Level: {plugin.level_required}\n\n"

        return output


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Manage DarkScope plugins.")
    parser.add_argument("--list", action="store_true", help="List installed plugins")
    parser.add_argument("--plugins-dir", help="Plugins directory (default: ./plugins)")
    parser.add_argument("--run", help="Run plugins for target")
    parser.add_argument("--level", type=int, default=2, help="Assessment level")
    args = parser.parse_args()

    manager = PluginManager(Path(args.plugins_dir) if args.plugins_dir else None)

    if args.list:
        print(manager.list_plugins())
    elif args.run:
        findings = manager.run_all(args.run, args.level)
        print(f"\n✅ Total findings from plugins: {len(findings)}")
        for finding in findings:
            print(f"  - {finding.get('title')}: {finding.get('severity')}")
    else:
        print("Use --list or --run <target>")


if __name__ == "__main__":
    main()
