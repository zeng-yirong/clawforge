import re
import shlex
from pathlib import Path, PurePath
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from swerex.exceptions import BashIncorrectSyntaxError, CommandTimeoutError
from swerex.runtime.abstract import (
    BashAction,
    BashInterruptAction,
    Command,
    ReadFileRequest,
    UploadRequest,
    WriteFileRequest,
)

from uni_agent.async_logging import get_logger
from uni_agent.deployment import DeployConfig
from uni_agent.interaction.install_utils import normalize_uploaded_text_file_cmd
from uni_agent.interaction.permissions import (
    ActionPermissionError,
    WORKSPACE_PATH_TOOL_NAMES,
    split_action_command,
    tool_name_from_tokens,
    validate_no_shell_composition,
    validate_restricted_bash_command,
    validate_workspace_tool_command,
)
from uni_agent.skills.manager import SkillsManager
from uni_agent.tools.base import AbstractTool
from uni_agent.utils import auto_await


class ActionTimeoutError(Exception):
    pass


class ActionIncorrectSyntaxError(Exception):
    pass


class TerminalNotAliveError(Exception):
    pass


class AgentEnvConfig(BaseModel):
    deployment: DeployConfig = Field(description="Deployment configuration")
    env_variables: dict[str, str] | None = Field(
        default=None, description="Optional environment variables to set after start"
    )
    post_setup_cmd: str | None = Field(default=None, description="Command to run after environment startup")
    tool_install_dir: Path = Field(
        default=Path("/usr/local/bin"), description="Directory where tool scripts are installed"
    )
    restrict_workspace: bool = Field(
        default=False,
        description="When true, file-tool --path arguments must stay under workspace_env_var.",
    )
    workspace_env_var: str = Field(
        default="CLAW_WORKSPACE",
        description="Shell variable holding the per-rollout workspace root.",
    )
    restrict_bash_commands: bool = Field(
        default=False,
        description="When true, execute_bash permits configured environment CLIs and safe workspace shell commands only.",
    )
    allowed_bash_command_prefixes: list[str] = Field(
        default_factory=list,
        description="Allowed environment CLI prefixes; safe workspace shell commands are handled separately.",
    )
    blocked_bash_subcommands: list[str] = Field(
        default_factory=lambda: ["prepare-rollout", "reset-rollout", "create-session", "reset-session"],
        description="CLI subcommands the model must not run even when the command prefix is allowed.",
    )
    model_config = ConfigDict(extra="forbid")


class AgentEnv:
    def __init__(
        self,
        run_id: str,
        env_config: AgentEnvConfig,
    ):
        """
        This class represents the environment in which we solve the tasks.
        Args:
            run_id: Run ID for the environment
            env_config: environment configuration
        """
        super().__init__()
        self.run_id = run_id
        self.deployment = env_config.deployment.get_deployment(run_id)
        self.env_variables = env_config.env_variables
        self.post_setup_cmd = env_config.post_setup_cmd
        self.tool_install_dir = env_config.tool_install_dir.expanduser()
        self.restrict_workspace = env_config.restrict_workspace
        self.workspace_env_var = env_config.workspace_env_var
        self.restrict_bash_commands = env_config.restrict_bash_commands
        self.allowed_bash_command_prefixes = env_config.allowed_bash_command_prefixes
        self.blocked_bash_subcommands = env_config.blocked_bash_subcommands
        self.logger = get_logger("environment", run_id)

    @auto_await
    async def start(self, max_retries: int = 5) -> None:
        """Start the environment"""

        self.logger.info("Beginning environment startup...")

        await self.deployment.start(max_retries=max_retries)
        self.logger.info("Runtime initialized")
        if self.env_variables:
            await self.set_env_variables(self.env_variables)
        if self.post_setup_cmd:
            await self.communicate(self.post_setup_cmd, check="raise")

    @auto_await
    async def install_tools(self, tools: list[AbstractTool]) -> None:
        install_dir = self.tool_install_dir
        install_dir_q = shlex.quote(install_dir.as_posix())
        self.logger.info(f"Installing tools into {install_dir}")
        await self.communicate(f"mkdir -p {install_dir_q} && export PATH={install_dir_q}:$PATH", check="raise")
        for tool in tools:
            tool_name = tool.name
            runtime_name = tool.runtime_name
            runtime_name_q = shlex.quote(runtime_name)
            if tool.copy_to_remote:
                local_tool_path = tool.local_path
                assert local_tool_path is not None and local_tool_path.is_file(), (
                    f"Tool {tool_name} has copy_to_remote=True but local_path={local_tool_path!r} is not a file"
                )
                container_tool_path = install_dir / runtime_name
                tmp_tool_path = install_dir / f".{runtime_name}.{self.run_id}.tmp"
                await self.copy_to_container(
                    src=local_tool_path,
                    tgt=tmp_tool_path,
                )
                # Normalize shebang line endings after upload so CRLF-synced
                # scripts remain executable on Linux runtimes.
                await self.communicate(normalize_uploaded_text_file_cmd(tmp_tool_path), check="raise")
                await self.communicate(f"chmod +x {shlex.quote(tmp_tool_path.as_posix())}", check="raise")

                replace_script = """
import os
import shutil
import sys
from pathlib import Path
tmp = Path(sys.argv[1])
target = Path(sys.argv[2])
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists() and target.is_dir() and not target.is_symlink():
    shutil.rmtree(target)
os.replace(tmp, target)
""".strip()
                await self.communicate(
                    (
                        f"python3 -c {shlex.quote(replace_script)} "
                        f"{shlex.quote(tmp_tool_path.as_posix())} "
                        f"{shlex.quote(container_tool_path.as_posix())}"
                    ),
                    check="raise",
                    error_msg=f"Failed to atomically install tool {tool_name}",
                )
            install_cmd = tool.get_install_command()
            if install_cmd:
                await self.communicate(install_cmd, check="raise")
            # check if tool is installed
            if tool.copy_to_remote:
                container_tool_path = install_dir / runtime_name
                container_tool_path_q = shlex.quote(container_tool_path.as_posix())
                verify_cmd = (
                    f"test -f {container_tool_path_q} && "
                    f"test -x {container_tool_path_q} && "
                    f"command -v {runtime_name_q}"
                )
            else:
                verify_cmd = f"command -v {runtime_name_q}"
            await self.communicate(
                verify_cmd,
                check="raise",
                error_msg=f"Failed to install tool {tool_name}",
            )
            self.logger.info(f"Tool {tool_name} successfully installed")

    @auto_await
    async def copy_to_container(self, src: Path, tgt: Path) -> None:
        await self.deployment.runtime.execute(Command(command=["mkdir", "-p", str(tgt.parent)]))
        await self.deployment.runtime.upload(UploadRequest(source_path=str(src), target_path=str(tgt)))

    @auto_await
    async def install_skills(self, skills_manager: "SkillsManager") -> None:
        """Resolve each skill's runtime path and (if needed) copy it in.
        Mutates ``skills_manager.runtime_paths`` so the subsequent
        ``build_manifest`` call renders the right ``<location>`` for each
        skill:
        - **Host-style runtime** (``HostDeployment`` / ``LocalNativeDeployment``):
          skills are read in place from their host ``source_dir``; no copy.
        - **Container runtime** (everything else): each skill directory is
          uploaded to ``/opt/uni-agent/skills/<name>``.
        """
        from uni_agent.deployment.host.deployment import HostDeployment

        host_types: tuple[type, ...] = (HostDeployment,)
        try:
            from uni_agent.deployment.local_native.deployment import LocalNativeDeployment

            host_types = host_types + (LocalNativeDeployment,)
        except ImportError:
            pass

        if isinstance(self.deployment, host_types):
            for skill in skills_manager.skills:
                skills_manager.runtime_paths[skill.name] = skill.source_dir
            names = "\n".join(s.name for s in skills_manager.skills)
            self.logger.info(f"Host runtime: {len(skills_manager.skills)} skill(s) read in place, no copy\n{names}")
            return

        for skill in skills_manager.skills:
            tgt = Path("/opt/uni-agent/skills") / skill.name
            await self.copy_to_container(src=skill.source_dir, tgt=tgt)
            skills_manager.runtime_paths[skill.name] = tgt
            self.logger.info(f"Skill {skill.name} installed at {tgt}")
        self.logger.info(f"Installed {len(skills_manager.skills)} skill(s) into runtime")

    @auto_await
    async def close(self) -> None:
        """Shutdown SWE-ReX deployment etc."""
        self.logger.info("Beginning environment shutdown...")
        try:
            await self.deployment.stop()
        except Exception as e:
            self.logger.error(f"Failed to stop environment deployment: {e}")
            return
        self.logger.info("Environment shutdown completed")

    @auto_await
    async def run_action(self, action_cmd: str, action_timeout: int, max_observation_length: int = 100_000) -> str:
        result = await self.run_action_with_status(
            action_cmd=action_cmd,
            action_timeout=action_timeout,
            max_observation_length=max_observation_length,
        )
        return result["observation"]

    @auto_await
    async def run_action_with_status(
        self,
        action_cmd: str,
        action_timeout: int,
        max_observation_length: int = 100_000,
    ) -> dict[str, int | str]:
        try:
            await self._enforce_action_policy(action_cmd)
            r = await self.deployment.runtime.run_in_session(BashAction(command=action_cmd, timeout=action_timeout, check="silent"))
            output = re.sub(r"\x1b\[[0-9;]*m|\r", "", r.output)
            if r.exit_code != 0:
                if output.strip() == "":
                    observation = f"Observation:\nCommand exited with status {r.exit_code} and did not produce any output."
                else:
                    observation = f"Observation:\nCommand exited with status {r.exit_code}.\n{output}"
            elif output.strip() == "":
                observation = "Your command ran successfully and did not produce any output."
            elif len(output) > max_observation_length:
                observation = (
                    f"Observation:\n{output[:max_observation_length]}<response clipped>\n"
                    f"<NOTE>Observations should not exceeded {max_observation_length} characters. "
                    f"{max_observation_length - len(output)} characters were elided. "
                    "Please try a different command that produces less output or "
                    "use head/tail/grep/redirect the output to a file. Do not use interactive pagers.</NOTE>"
                )
            else:
                observation = f"Observation:\n{output}"
            return {"observation": observation, "exit_code": int(r.exit_code)}
        except CommandTimeoutError:
            # interrupt timeout action
            # if terminal is still alive after interrupt, raise error
            try:
                await self.interrupt_session()
            except Exception:
                self.logger.error("Failed to interrupt session after command timeout")
                # check current terminal is still alive
                terminal_alive = False
                for _ in range(5):
                    probe_output = await self.communicate("echo 'terminal still alive'", check="ignore")
                    # Use substring match on stripped lines so residual marker
                    # noise from a recovering session does not fail the probe.
                    if isinstance(probe_output, str) and any(
                        line.strip() == "terminal still alive" for line in probe_output.splitlines()
                    ):
                        terminal_alive = True
                        break
                if not terminal_alive:
                    error_message = "Terminal did not respond to health checks"
                    self.logger.critical(error_message)
                    raise TerminalNotAliveError(error_message) from None

            # if terminal is still alive, return timeout observation
            observation = (
                f"The command '{action_cmd}' was cancelled because it took more than {action_timeout} seconds. "
                "Please try a different command that completes more quickly. Note: A common source of this error is "
                "if the command is interactive or requires user input (it is impossible to receive user input "
                "in the current environment, so the command will never complete)."
            )
            raise ActionTimeoutError(observation) from None

        except BashIncorrectSyntaxError as e:
            # this should not happen, so add critical logs here
            self.logger.error("Action command has incorrect syntax")
            error_message = (
                "Your bash command contained syntax errors and was NOT executed. "
                "Please fix the syntax errors and try again. This can be the result "
                "of not adhering to the syntax for multi-line commands. Here is the output of `bash -n`:\n"
                f"{e.extra_info['bash_stdout']}\n{e.extra_info['bash_stderr']}"
            )
            raise ActionIncorrectSyntaxError(error_message) from None

    @auto_await
    async def _enforce_action_policy(self, action_cmd: str) -> None:
        tokens = split_action_command(action_cmd)
        tool_name = tool_name_from_tokens(tokens)
        workspace = None
        cwd = None

        if (self.restrict_workspace or self.restrict_bash_commands) and tool_name is not None:
            validate_no_shell_composition(action_cmd)

        if self.restrict_workspace and tool_name in WORKSPACE_PATH_TOOL_NAMES:
            workspace = (await self.communicate(f'printf %s "${{{self.workspace_env_var}}}"', check="ignore")).strip()
            cwd = (await self.communicate("pwd", check="ignore")).strip()
            if not workspace:
                raise ActionPermissionError(
                    f"Workspace restriction is enabled but ${self.workspace_env_var} is not set."
                )
            validate_workspace_tool_command(action_cmd, workspace=workspace, cwd=cwd)

        if self.restrict_bash_commands and tool_name is None:
            if self.restrict_workspace:
                if workspace is None:
                    workspace = (
                        await self.communicate(f'printf %s "${{{self.workspace_env_var}}}"', check="ignore")
                    ).strip()
                if cwd is None:
                    cwd = (await self.communicate("pwd", check="ignore")).strip()
                if not workspace:
                    raise ActionPermissionError(
                        f"Workspace restriction is enabled but ${self.workspace_env_var} is not set."
                    )
            validate_restricted_bash_command(
                action_cmd,
                allowed_prefixes=self.allowed_bash_command_prefixes,
                blocked_subcommands=self.blocked_bash_subcommands,
                workspace=workspace,
                cwd=cwd,
            )

    @auto_await
    async def interrupt_session(self):
        self.logger.info("Interrupting session")
        await self.deployment.runtime.run_in_session(BashInterruptAction(timeout=10))

    @auto_await
    async def communicate(
        self,
        input: str,
        timeout: int | float = 60,
        check: Literal["warn", "ignore", "raise"] = "ignore",
        error_msg: str = "Command failed",
    ) -> str:
        """Executes a command in the running shell. The details of this are handled by
        the SWE-ReX deployment/runtime.
        Args:
            input: input to send to container
            timeout_duration: duration to wait for output
            check: `ignore`: do not extract exit code (more stable), `warn`: extract exit code and log error if
                exit code is non-zero, `raise`: raise error if exit code is non-zero
            error_msg: error message to raise if the command fails
        Returns:
            output: output from container
        """
        self.logger.debug(f"Input:\n{input}")
        rex_check = "silent" if check else "ignore"
        r = await self.deployment.runtime.run_in_session(BashAction(command=input, timeout=timeout, check=rex_check))
        output = r.output
        self.logger.debug(f"Output:\n{output}")
        if check != "ignore" and r.exit_code != 0:
            self.logger.error(f"{error_msg}:\n{output}")
            msg = f"Command {input!r} failed ({r.exit_code=}): {error_msg}"
            if check == "raise":
                await self.close()
                raise RuntimeError(msg)
        return output

    @auto_await
    async def read_file(self, path: str | PurePath, encoding: str | None = None, errors: str | None = None) -> str:
        """Read file contents from container
        Args:
            path: Absolute path to file
            encoding: Encoding to use when reading the file. None means default encoding.
                This is the same as the `encoding` argument of `Path.read_text()`
            errors: Error handling to use when reading the file. None means default error handling.
                This is the same as the `errors` argument of `Path.read_text()`
        Returns:
            file_contents: Contents of file as string
        """
        r = await self.deployment.runtime.read_file(ReadFileRequest(path=str(path), encoding=encoding, errors=errors))
        return r.content

    @auto_await
    async def write_file(self, path: str | PurePath, content: str) -> None:
        """Write content to file in container"""
        await self.deployment.runtime.write_file(WriteFileRequest(path=str(path), content=content))

    @auto_await
    async def set_env_variables(self, env_variables: dict[str, str]) -> None:
        """Set environment variables in the environment."""
        _env_setters = [f"export {k}={shlex.quote(str(v))}" for k, v in env_variables.items()]
        command = " && ".join(_env_setters)
        await self.communicate(command, check="raise")
