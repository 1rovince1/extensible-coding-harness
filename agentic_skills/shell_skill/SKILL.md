---
description: |
  Use the workspace shell for inspecting files, creating and modifying
  files, manipulating directories, and performing other permitted
  filesystem operations. Prefer inspection before modification,
  patch-based edits for existing files, and verification after changes.
  This skill applies whenever the agent needs to interact with the
  coding workspace through the shell.
name: shell_skill
---

# Shell Skill

Use the shell tool to interact with the agent workspace.

## Workspace

-   All shell commands execute with the agent workspace as the current
    working directory.
-   Prefer relative paths within the workspace.
-   Treat the workspace as the boundary for normal file operations.
-   Do not assume that a command has succeeded merely because the shell
    invocation returned; inspect its output when appropriate.

## Available Commands

The shell tool currently permits these command names:

-   `ls` --- list files and directories
-   `grep` --- search text
-   `cat` --- read or create file contents
-   `echo` --- print text
-   `sed` --- perform simple text transformations
-   `mkdir` --- create directories
-   `find` --- locate files and directories
-   `cp` --- copy files
-   `mv` --- move or rename files
-   `head` --- inspect the beginning of files
-   `tail` --- inspect the end of files
-   `patch` --- apply unified patches to files

Do not attempt to use commands that are not available through the shell
tool.

## General Workflow

For code or configuration changes, prefer this workflow:

1.  **Inspect** --- locate the relevant files and symbols.
2.  **Read** --- inspect enough surrounding content to understand the
    existing implementation.
3.  **Modify** --- make the smallest change necessary.
4.  **Verify** --- inspect the resulting file or patch.
5.  **Validate** --- when another available tool or mechanism provides
    validation, use it.

Do not modify files blindly when the relevant existing content can first
be inspected.

## Inspecting Files

Prefer targeted inspection rather than dumping very large files.

Examples:

``` bash
ls
```

``` bash
find . -name "*.py"
```

``` bash
grep -R "function_name" .
```

``` bash
head -100 path/to/file.py
```

``` bash
tail -100 path/to/file.py
```

``` bash
cat path/to/file.py
```

When searching a project, first identify likely files and then read the
relevant portions.

## Creating Files

For a new file, a quoted heredoc is a convenient approach:

``` bash
cat > path/to/file.py <<'EOF'
file contents go here
EOF
```

Prefer a quoted delimiter such as `<<'EOF'` so that shell expansion does
not alter the file contents.

Do not unnecessarily reconstruct an existing large file with `cat`. Use
a targeted modification instead.

## Editing Existing Files

### Preferred: `patch`

For modifications to existing files, prefer a unified patch when
practical.

Example:

``` bash
patch path/to/file.py <<'EOF'
--- path/to/file.py
+++ path/to/file.py
@@ -10,7 +10,8 @@
 def process(data):
     validate(data)
-    result = transform(data)
+    result = transform(data)
+    log_result(result)
     return result
EOF
```

Use enough surrounding context in the patch to make the intended
location unambiguous.

Keep patches as small and focused as possible.

If the workspace is a Git repository, the resulting change can be
inspected with the available file tools. Do not assume Git commands are
available through the current shell allowlist.

### `sed`

Use `sed` for simple, deterministic substitutions where it is clearer
than a patch.

Example:

``` bash
sed -i 's/timeout = 10/timeout = 30/' config.py
```

Avoid complicated `sed` expressions for substantial source-code changes.
Prefer a patch instead.

### Rewriting a File

Avoid replacing the entire contents of an existing file unless the task
genuinely requires a complete rewrite.

A full rewrite can accidentally remove unrelated code or changes.

## Creating Directories and Moving Files

Create directories with:

``` bash
mkdir -p path/to/directory
```

Copy files with:

``` bash
cp source.py destination.py
```

Move or rename files with:

``` bash
mv old_name.py new_name.py
```

Before destructive or potentially irreversible operations, verify the
paths carefully.

## Deletion

The `rm` command is currently unavailable.

Do not attempt to work around this restriction with another command or
destructive shell construct.

## Verification After Edits

After modifying a file:

1.  Inspect the modified section.
2.  Confirm that the intended change was applied.
3.  Check for accidental changes elsewhere when practical.
4.  If the modification affects source code, validate it using whatever
    validation capability is available to the agent.

For example:

``` bash
grep -n "changed_symbol" path/to/file.py
```

or:

``` bash
cat path/to/file.py
```

For patches, a successful patch application is useful evidence, but
still inspect the resulting content when the change is important.

## Shell Usage Guidelines

-   Prefer one clear operation per shell invocation.
-   Use explicit paths rather than relying on implicit shell state.
-   Quote paths containing spaces or shell-special characters.
-   Avoid unnecessarily complex shell expressions.
-   Do not use shell commands to access unrelated parts of the
    filesystem.
-   Do not invent unavailable commands.
-   Do not repeatedly execute the same failed command without first
    understanding the error.
-   When a command fails, use the returned stdout/stderr to determine
    the next action.

## Editing Strategy

Use the following preference order:

1.  New file → `cat <<'EOF'`
2.  Small deterministic text replacement → `sed`
3.  Existing source/config modification → `patch`
4.  Large rewrite → recreate the file only when genuinely necessary

The goal is to make **small, explicit, reviewable changes** rather than
repeatedly rewriting entire files.

## Important Tool Limitation

The shell implementation validates the first command token before
executing the command through the shell. Therefore, the command
allowlist should not be treated as a complete security boundary by
itself.

The agent should still keep commands simple and operate only on the
intended workspace.

The shell tool also has a finite execution timeout. Commands that take
longer than the configured timeout may be terminated.
