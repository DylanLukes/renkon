from typing import Any

from hatchling.builders.config import BuilderConfigBound
from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class WebAssetsBuildHook(BuildHookInterface[BuilderConfigBound]):
    PLUGIN_NAME = "web_assets"

    # def __init__(
    #         self,
    #         root: str,
    #         config: dict[str, Any],
    #         build_config: BuilderConfigBound,
    #         metadata: ProjectMetadata[PluginManagerBound],
    #         directory: str,
    #         target_name: str,
    #         app: Application | None = None
    # ) -> None:
    #     super().__init__(root, config, build_config, metadata, directory, target_name, app)

    def initialize(self, version: str, build_data: dict[str, Any]) -> None:
        super().initialize(version, build_data)
