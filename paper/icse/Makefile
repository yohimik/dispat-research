# Build the conference paper with tectonic.
#
# acmart reads its own transcript back during the run, so tectonic classifies
# main.log as an intermediate and does not persist it even under --keep-logs.
# The engine chatter printed by --print carries the same warnings, so the pdf
# target captures it into build/main.log for the check target to grep.

SHELL := /bin/bash

.PHONY: pdf check clean

pdf:
	@mkdir -p build
	set -o pipefail; \
	tectonic --outdir build --keep-logs --print main.tex 2>&1 | tee build/main.log

# Early TeX passes legitimately report every forward reference as undefined;
# only the final pass's verdict matters, so the check reads the log from the
# last "(Re)running TeX" marker onward.
check: pdf
	@awk '/^note: (Running|Rerunning) TeX/{n=NR} {l[NR]=$$0} END{for(i=n;i<=NR;i++) print l[i]}' \
		build/main.log > build/lastpass.log
	@if grep -E "Reference .* undefined|There were undefined" build/lastpass.log; then \
		echo "check failed: undefined references"; exit 1; fi
	@if grep -E "multiply.defined" build/lastpass.log; then \
		echo "check failed: multiply defined labels"; exit 1; fi
	@echo "check passed: no undefined references, no multiply defined labels"
	@echo "overfull boxes in final pass: $$(grep -c 'Overfull' build/lastpass.log || true)"

clean:
	rm -rf build
