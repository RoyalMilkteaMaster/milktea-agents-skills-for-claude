#!/usr/bin/env node

"use strict";

const fs = require("fs");
const os = require("os");
const path = require("path");
const { spawnSync } = require("child_process");

const PINNED_VERSION = "1.8.6";
const PACKAGE_SPEC = `@alibaba-group/open-code-review@${PINNED_VERSION}`;
const DEFAULT_TIMEOUT_MS = 30000;

function parseArguments(argv) {
  const command = argv[0];
  if (!command || !["check", "install"].includes(command)) {
    throw new Error("first argument must be check or install");
  }

  const options = {
    command,
    confirmed: false,
    repo: process.cwd(),
  };

  for (let index = 1; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === "--confirmed") {
      options.confirmed = true;
      continue;
    }
    if (argument === "--repo") {
      const value = argv[index + 1];
      if (!value) {
        throw new Error("--repo requires a path");
      }
      options.repo = path.resolve(value);
      index += 1;
      continue;
    }
    throw new Error(`unsupported argument: ${argument}`);
  }

  return options;
}

function fileIsExecutable(candidate) {
  if (!candidate) {
    return false;
  }

  try {
    fs.accessSync(candidate, fs.constants.X_OK);
    return fs.statSync(candidate).isFile();
  } catch {
    return false;
  }
}

function executableExtensions() {
  if (process.platform !== "win32") {
    return [""];
  }

  const configured = (process.env.PATHEXT || ".COM;.EXE;.BAT;.CMD")
    .split(";")
    .filter(Boolean);
  return [...configured, ""];
}

function findExecutable(name) {
  const directories = (process.env.PATH || "")
    .split(path.delimiter)
    .filter(Boolean);
  const hasExtension = Boolean(path.extname(name));
  const extensions = hasExtension ? [""] : executableExtensions();

  for (const directory of directories) {
    for (const extension of extensions) {
      const candidate = path.join(directory, `${name}${extension}`);
      if (fileIsExecutable(candidate)) {
        return candidate;
      }
    }
  }

  return null;
}

function run(program, args, options = {}) {
  let actualProgram = program;
  let actualArguments = args;

  if (process.platform === "win32" && /\.(?:cmd|bat)$/i.test(program)) {
    actualProgram = process.env.ComSpec || "cmd.exe";
    actualArguments = ["/d", "/s", "/c", "call", program, ...args];
  }

  const result = spawnSync(actualProgram, actualArguments, {
    cwd: options.cwd,
    encoding: "utf8",
    env: options.env || process.env,
    maxBuffer: 2 * 1024 * 1024,
    shell: false,
    timeout: options.timeout || DEFAULT_TIMEOUT_MS,
    windowsHide: true,
  });

  return {
    status: Number.isInteger(result.status) ? result.status : 1,
    stdout: String(result.stdout || "").trim(),
    stderr: String(result.stderr || "").trim(),
    error: result.error ? result.error.message : null,
  };
}

function semanticVersion(text) {
  const match = String(text || "").match(/(?:^|\D)(\d+)\.(\d+)\.(\d+)(?:\D|$)/u);
  if (!match) {
    return null;
  }
  return `${Number(match[1])}.${Number(match[2])}.${Number(match[3])}`;
}

function versionAtLeast(actual, minimum) {
  if (!actual) {
    return false;
  }
  const left = actual.split(".").map(Number);
  const right = minimum.split(".").map(Number);
  for (let index = 0; index < 3; index += 1) {
    if (left[index] !== right[index]) {
      return left[index] > right[index];
    }
  }
  return true;
}

function environmentDetails() {
  const wsl = process.platform === "linux"
    && (process.env.WSL_DISTRO_NAME || process.env.WSL_INTEROP || isMicrosoftKernel());
  return {
    kind: process.platform === "win32" ? "windows" : wsl ? "wsl" : process.platform,
    distribution: wsl ? process.env.WSL_DISTRO_NAME || null : null,
    shell: process.env.SHELL || (process.platform === "win32" ? "windows" : null),
  };
}

function isMicrosoftKernel() {
  try {
    return /microsoft/i.test(fs.readFileSync("/proc/version", "utf8"));
  } catch {
    return false;
  }
}

function toolState(program, versionArguments) {
  if (!program) {
    return {
      installed: false,
      path: null,
      version: null,
      version_text: null,
    };
  }

  const result = run(program, versionArguments);
  const versionText = [result.stdout, result.stderr].filter(Boolean).join("\n");
  return {
    installed: true,
    path: program,
    version: result.status === 0 ? semanticVersion(versionText) : null,
    version_text: versionText || null,
  };
}

function locateOcr(npmPath) {
  const onPath = findExecutable("ocr");
  if (onPath) {
    return onPath;
  }

  const candidates = [];
  if (process.platform !== "win32") {
    candidates.push(path.join(os.homedir(), ".local", "bin", "ocr"));
  }

  if (npmPath) {
    const prefixResult = run(npmPath, ["prefix", "--global"]);
    if (prefixResult.status === 0 && prefixResult.stdout) {
      candidates.push(
        path.join(prefixResult.stdout, "ocr"),
        path.join(prefixResult.stdout, "ocr.cmd"),
        path.join(prefixResult.stdout, "ocr.exe"),
        path.join(prefixResult.stdout, "bin", "ocr"),
        path.join(prefixResult.stdout, "bin", "ocr.cmd"),
        path.join(prefixResult.stdout, "bin", "ocr.exe"),
      );
    }
  }

  return candidates.find(fileIsExecutable) || null;
}

function check(repo) {
  const reasons = [];
  const gitPath = findExecutable("git");
  const nodePath = process.execPath && fileIsExecutable(process.execPath)
    ? process.execPath
    : findExecutable("node");
  const npmPath = findExecutable("npm");
  const git = toolState(gitPath, ["--version"]);
  const node = toolState(nodePath, ["--version"]);
  const npm = toolState(npmPath, ["--version"]);

  if (!git.installed) {
    reasons.push("git_missing");
  } else if (!git.version) {
    reasons.push("git_version_unreadable");
  } else if (!versionAtLeast(git.version, "2.41.0")) {
    reasons.push("git_too_old");
  }

  let insideGitWorktree = false;
  if (gitPath) {
    const worktree = run(gitPath, ["-C", repo, "rev-parse", "--is-inside-work-tree"]);
    insideGitWorktree = worktree.status === 0 && worktree.stdout === "true";
  }
  if (!insideGitWorktree) {
    reasons.push("not_git_worktree");
  }

  if (!node.installed) {
    reasons.push("node_missing");
  } else if (!node.version) {
    reasons.push("node_version_unreadable");
  } else if (!versionAtLeast(node.version, "18.0.0")) {
    reasons.push("node_too_old");
  }

  if (!npm.installed) {
    reasons.push("npm_missing");
  } else if (!npm.version) {
    reasons.push("npm_version_unreadable");
  }

  const ocrPath = locateOcr(npmPath);
  let ocr = {
    installed: false,
    path: null,
    version: null,
    version_text: null,
    delegate_available: false,
  };

  if (!ocrPath) {
    reasons.push("ocr_missing");
  } else {
    const childEnvironment = { ...process.env, OCR_NO_UPDATE: "1" };
    const versionResult = run(ocrPath, ["version"], { env: childEnvironment });
    const versionText = [versionResult.stdout, versionResult.stderr]
      .filter(Boolean)
      .join("\n");
    const delegateResult = run(ocrPath, ["delegate", "--help"], {
      env: childEnvironment,
    });
    ocr = {
      installed: true,
      path: ocrPath,
      version: versionResult.status === 0 ? semanticVersion(versionText) : null,
      version_text: versionText || null,
      delegate_available: delegateResult.status === 0,
    };
    if (!ocr.version) {
      reasons.push("ocr_version_unreadable");
    }
    if (!ocr.delegate_available) {
      reasons.push("ocr_delegate_unavailable");
    }
  }

  const gitReady = versionAtLeast(git.version, "2.41.0");
  const nodeReady = versionAtLeast(node.version, "18.0.0");
  const npmReady = Boolean(npm.version);
  const delegateReady = gitReady
    && insideGitWorktree
    && Boolean(ocr.version)
    && ocr.delegate_available;

  return {
    schema_version: 2,
    environment: environmentDetails(),
    repo,
    git,
    node,
    npm,
    ocr,
    inside_git_worktree: insideGitWorktree,
    delegate_ready: delegateReady,
    npm_install_ready: gitReady && nodeReady && npmReady,
    reason_codes: reasons,
  };
}

function install(repo, confirmed) {
  if (!confirmed) {
    return {
      result: {
        schema_version: 2,
        environment: environmentDetails(),
        status: "refused",
        package: PACKAGE_SPEC,
        installed: false,
        llm_configured: false,
        reason_codes: ["confirmation_required"],
      },
      exitCode: 2,
    };
  }

  const before = check(repo);
  if (!before.npm_install_ready) {
    const prerequisiteReasons = before.reason_codes.filter((reason) => [
      "git_missing",
      "git_version_unreadable",
      "git_too_old",
      "node_missing",
      "node_version_unreadable",
      "node_too_old",
      "npm_missing",
      "npm_version_unreadable",
    ].includes(reason));
    return {
      result: {
        schema_version: 2,
        environment: environmentDetails(),
        status: "prerequisites_missing",
        package: PACKAGE_SPEC,
        installed: false,
        llm_configured: false,
        reason_codes: prerequisiteReasons,
      },
      exitCode: 20,
    };
  }

  const npmPath = before.npm.path;
  const installPrefix = process.platform === "win32"
    ? null
    : path.join(os.homedir(), ".local");
  const argumentsList = ["install", "--global"];
  if (installPrefix) {
    argumentsList.push("--prefix", installPrefix);
  }
  argumentsList.push("--no-audit", "--no-fund", PACKAGE_SPEC);

  const installResult = run(npmPath, argumentsList, { timeout: 180000 });
  if (installResult.status !== 0) {
    const errorMessage = [installResult.error, installResult.stderr, installResult.stdout]
      .filter(Boolean)
      .join("\n")
      .slice(0, 2000);
    return {
      result: {
        schema_version: 2,
        environment: environmentDetails(),
        status: "install_failed",
        package: PACKAGE_SPEC,
        install_prefix: installPrefix,
        installed: false,
        llm_configured: false,
        reason_codes: ["npm_install_failed"],
        error_message: errorMessage || null,
      },
      exitCode: 30,
    };
  }

  const after = check(repo);
  if (!after.ocr.installed || !after.ocr.version || !after.ocr.delegate_available) {
    return {
      result: {
        schema_version: 2,
        environment: environmentDetails(),
        status: "verification_failed",
        package: PACKAGE_SPEC,
        install_prefix: installPrefix,
        installed: after.ocr.installed,
        ocr_path: after.ocr.path,
        version_text: after.ocr.version_text,
        llm_configured: false,
        reason_codes: after.reason_codes.filter((reason) => reason.startsWith("ocr_")),
      },
      exitCode: 40,
    };
  }

  return {
    result: {
      schema_version: 2,
      environment: environmentDetails(),
      status: "installed",
      package: PACKAGE_SPEC,
      install_prefix: installPrefix,
      installed: true,
      ocr_path: after.ocr.path,
      version: after.ocr.version,
      version_text: after.ocr.version_text,
      delegate_ready: after.delegate_ready,
      llm_configured: false,
      reason_codes: after.delegate_ready ? [] : after.reason_codes,
    },
    exitCode: 0,
  };
}

function writeResult(result, exitCode) {
  process.stdout.write(`${JSON.stringify(result)}\n`);
  process.exitCode = exitCode;
}

function main() {
  try {
    const options = parseArguments(process.argv.slice(2));
    if (options.command === "check") {
      const result = check(options.repo);
      writeResult(result, result.delegate_ready ? 0 : 10);
      return;
    }

    const installation = install(options.repo, options.confirmed);
    writeResult(installation.result, installation.exitCode);
  } catch (error) {
    writeResult({
      schema_version: 2,
      status: "invalid_arguments",
      reason_codes: ["invalid_arguments"],
      error_message: error.message,
    }, 2);
  }
}

main();
