from __future__ import annotations


class ProjectNotInitializedError(RuntimeError):
    def __init__(self, project: object):
        self.project = project
        super().__init__(
            f"RIFT project is not initialized at {project}. Run `rift init <project_name>` first, "
            "or pass `--project` pointing to an initialized RIFT project."
        )
