# Issue tracker: GitHub

対象リポジトリ：makitagithub/auto-create-cyberrange

課題と仕様はGitHub Issuesで管理する。操作にはgh CLIを使用し、--repo makitagithub/auto-create-cyberrange を明示する。
作成は gh issue create、閲覧は gh issue view <番号> --comments、一覧は gh issue list、
更新は gh issue edit <番号>、コメントは gh issue comment <番号>、完了は gh issue close <番号> を使用する。
複数行の本文はファイルに保存し、--body-fileで渡す。
スキルが課題管理先への公開を指示した場合は、GitHub Issueを作成する。

## Pull requests as a triage surface

PRs as a request surface: no.
