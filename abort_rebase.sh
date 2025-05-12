#!/bin/bash
cd "$(dirname "$0")"
git rebase --abort
echo "Rebase aborted"